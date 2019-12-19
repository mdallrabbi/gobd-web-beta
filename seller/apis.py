import json

import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from oauth2_provider.models import AccessToken
from rest_framework import status
from seller.models import Order, Seller, DeliveryMan
from seller.serializers import (SellerSerializer,
                               OrderSellerSerializer,
                               OrderDeliverManSerializer,
                               OrderSerializer)


# from store.orders import (deliver_order_accept_notification,
# 						deliver_order_reject_notification,
# 						deliver_order_DELIVERED_notification,
# 						store_created_new_order_notification)


###############
#   store     #
###############

def seller_order_notification(request, last_request_time):
    notification = Order.objects.get(created_at__gt=last_request_time, status=Order.PICKEDUP)
    return JsonResponse({"notification": notification})


def seller_manager_cancel_order(request):
    """
        end point for store manager can cancel order which is no longer accepted
    """
    with transaction.atomic():
        # using atomic transations may be store manager and deliver boy
        # performs certain action at same time
        try:
            order_id = request.GET.get('order_id', None)
            order_instance = Seller.objects.get(id=order_id,
                                             seller =request.user.seller,
                                             delivery_man=None,
                                             status=Order.ACCEPTED)
            order_instance.status = Order.CANCELD
            order_instance.save()
            success_data = {
                'result': 'OK'
            }
            return JsonResponse(success_data,
                                status=status.HTTP_200_OK)
        except ValueError:
            return JsonResponse(
                {"status": "failed",
                 "error": "Order accepted by delivery man"})


def get_seller_manager_all_orders(request):
    """
        end point for store manager to retrive all orders
    """
    orders = OrderSerializer(
        Order.objects.filter(seller=request.user.seller).order_by("-id"),
        many=True
    ).data
    return JsonResponse({"orders": orders})


def delivery_man_accept_order(request):
    """
        end point for deliver boy can accpet order
    """
    order_id = request.GET.get('order_id', None)
    if Order.objects.filter(delivery_man=request.user.delivery_man, status=Order.ACCEPTED).count() >= 3:
        return JsonResponse({"status": "failed", "error": "reaced maximum limit"})

    with transaction.atomic():
        # using atomic transactions to avoid race conditions
        # may two users can access same resource at a time to avoid that
        try:
            order_instance = Order.objects.get(id=order_id, delivery_man=None)
            order_instance.status = Order.ACCEPTED
            order_instance.delivery_man = request.user.delivery_man
            order_instance.accepted_at = datetime.datetime.now()
            order_instance.save()
            success_data = {
                "result": "success"
            }
            # delivery_man_accept_order.delay(order_instance.id)
            return JsonResponse(success_data, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "order accepted by another delivery man"})


def delivery_man_reject_order(request):
    """
        endpoint for deliver boy for rejecting order
    """
    order_id = request.GET.get('order_id', None)
    d_boy = request.user.delivery_man
    order = Order.objects.get(id=order_id,
                            delivery_man=d_boy,
                            status=Order.ACCEPTED)
    order.status = Order.PICKEDUP
    order.delivery_man = None
    order_id = order.id
    order.save()
    delivery_man_reject_order.delay(order_id)
    return JsonResponse({"status": "success"}, status=status.HTTP_200_OK)


def delivery_man_complete_order(request):
    """
        end point for deliver boy for DELIVERED order
    """
    order_id = request.GET.get('order_id', None)
    d_boy = request.user.delivery_man
    order = Order.objects.get(id=order_id, delivery_man=d_boy)
    order.status = Order.DELIVERED
    order_id = order.id
    order.save()
    # deliver_order_DELIVERED_notification.delay(order_id)
    return JsonResponse({"status": "success"}, status=status.HTTP_200_OK)


def get_delivery_man_completed_orders(request):
    access_token = AccessToken.objects.get(
        token=request.GET.get("access_token"),
        expires__gt=timezone.now())
    d_man = access_token.user.delivery_man
    orders = OrderSerializer(
        Order.objects.filter(status=Order.DELIVERED, delivery_man=d_man).order_by("-id"),
        many=True
    ).data
    return JsonResponse({"orders": orders})


def delivery_man_ready_new_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status=Order.PICKEDUP, delivery_man=None).order_by("-id"),
        many=True
    ).data
    return JsonResponse({"orders": orders})


def delivery_man_get_latest_order(request):
    access_token = AccessToken.objects.get(token=request.GET.get("access_token"), expires__gt=timezone.now())
    d_man = access_token.user.delivery_man
    orders = OrderSerializer(Order.objects.get.filter(delivery_man=d_man).order_by("-created_at").last()).data
    return JsonResponse({"order": orders})


#######################
#	token end points  #
#######################

@csrf_exempt
def delivery_man_accept_order_token(request):
    if request.method == 'POST':
        access_token = AccessToken.objects.get(token=request.POST.get("access_token"), expires__gt=timezone.now())
        d_man = access_token.user.delivery_man

        if Order.objects.filter(delivery_man=d_man).exclude(status=Order.ACCEPTED):
            return JsonResponse({"status": "failed", "error": "You can accept one order at a time"})

        with transaction.atomic():
            try:
                order = Order.objects.select_for_update().get(
                    id=request.POST["order_id"],
                    delivery_man=None)
                order.delivery_man = d_man
                order.status = Order.ACCEPTED
                # implement push notification here store manager
                order.save()
                return JsonResponse({"status": "success"})

            except Order.DoesNotExist:
                return JsonResponse({"status": "failed", "error": "order accepted by another delivery boy"})


def delivery_man_complete_order_token(request):
    access_token = AccessToken.objects.get(token=request.POST.get("access_token"), expires__gt=timezone.now())
    d_man = access_token.user.delivery_man
    order = Order.objects.get(id=request.POST["order_id"], delivery_man=d_man)
    order.status = Order.DELIVERED
    # implement push notification here store manager
    order.save()
    return JsonResponse({"status": "success"})


def delivery_man_reject_order_token(request):
    access_token = AccessToken.objects.get(token=request.POST.get("access_token"), expires__gt=timezone.now())
    d_man = access_token.user.delivery_man
    order = Order.objects.get(id=request.POST["order_id"], delivery_man=d_man, status=Order.ACCEPTED)
    order.status = Order.PICKEDUP
    # implement push notification here store manager
    order.save()
    return JsonResponse({"status": "success"})