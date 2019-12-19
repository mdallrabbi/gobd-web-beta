import json
import logging
from channels import Channel
from channels.sessions import channel_session
from gobdWeb.celery import app
from seller.models import Order
from seller.orders import deliver_order_accept_notification

log = logging.getLogger(__name__)


@channel_session
def ws_connect(message):
	message.reply_channel.send({
			"text": json.dumps({
				"action": "reply_channel",
				"reply_channel": message.reply_channel.name,
			})
	})


@channel_session
def ws_receive(message):
	try:
		data = json.loads(message['text'])
	except ValueError:
		log.debug("websocket message is not json text=%s", message['text'])
		return

	if data:
		reply_channel = models.reply_channel.name
		if data['action'] == 'push_task_accepted_notification':
			push_order_accepted_notification(data, reply_channel)
		if data['action'] == ''


def push_order_accepted_notification(data, reply_channel):
	log.debug("Order Name:%s", data['order_title'])
	# save model to our data base
	order = Order(
		title=data['order_title'],
		status=Order.PICKEDUP,
		seller = data['order_seller'],
		preiority=data['order_preiority'],
	)
	order.save()
	# fireup celery task 
	accept_order = deliver_order_accept_notification.delay(order.id, reply_channel)
	# store celery task id for future ref
	order.celery_id = accept_order.id
	order.save()

	# info client about task
	Channel(reply_channel).send({
		"text": json.dumps({
			"action": "started",
			"order_id": order.id,
			"order_name": order.title,
			"order_status": order.status,

		})
	})