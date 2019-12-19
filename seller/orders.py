from __future__ import absolute_import
import time
import json
import logging
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.models import User
from channels import Channel
from celery import shared_order
from celery.utils.log import get_order_logger
from seller.models import Seller, Order, DeliveryMan
from seller.serializers import OrderSerializer
from gobdWeb.celery import app


log = logging.getLogger(__name__)
logger = get_order_logger(__name__)


@app.order
def deliver_order_accept_notification(order_id, reply_channel):
	order = Order.objects.get(pk=order_id)
	log.debug("Running Order_name=%s", Order.title)
	order.status = Order.ACCEPTED
	order.save()

	# send status update back to browser client

	if reply_channel is not None:
		Channel(replay_channel).send({
			"text": json.dumps({
					"action": "deliver_order_accept_notification",
					"order_id": order_id,
					"order_name": order.title,
					"order_status": order.status,
					"order_preiority": order.preiority,
					"order_seller": order.seller,
				})
			})


@app.order
def seller_manager_created_new_order(order_id, reply_channel):
	order = Order.objects.get(pk=order_id)
	log.debug("Running order Name=%s", order.title)
	if reply_channel is not None:
		Channel(reply_channel).send({
				"text": json.dumps({
					"action": "order_created",
					"order_id": order_id,
					"order_title": order.title,
					"order_status": order.status,
					"order_preiority": order.preiority,
					"order_seller": order.seller,
				})
			})


@app.order
def deliver_order_reject_notification(order_id, reply_channel):
	order = Order.objects.get(pk=order_id)
	log.debug("Running order Name=%s", order.title)
	if reply_channel is not None:
		Channel(reply_channel).send({
				"text": json.dumps({
					"action": "order_created",
					"order_id": order_id,
					"order_name": order.title,
					"order_status": order.status,
					"order_preiority": order.preiority,
					"order_seller": order.seller,
				})
			})


@app.order
def deliver_order_completed_notification(order_id, reply_channel):
	order = Order.objects.get(pk=order_id)
	log.debug("Running order Name=%s", order.title)
	if reply_channel is not None:
		Channel(reply_channel).send({
				"text": json.dumps({
					"action": "accepted",
					"order_id": order_id,
					"order_name": order.title,
					"order_status": order.status,
					"order_preiority": order.preiority,
					"order_seller": order.seller,
				})
		})