from rest_framework import serializers
from seller.models import Seller, Order, DeliveryMan



class SellerSerializer(serializers.ModelSerializer):

	class Meta:
		model = Seller
		fields = ("id", "seller_name", "contact_number")


class OrderSellerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Seller
		fields = ("id", "seller_name", "contact_number")


class OrderDeliverManSerializer(serializers.ModelSerializer):
	name = serializers.ReadOnlyField(source="user.get_full_name")

	class Meta:
		model = DeliveryMan
		fields = ("id", "delivery_man_name", "number")

class OrderSerializer(serializers.ModelSerializer):

	delivery_man = OrderDeliverManSerializer()
	seller = OrderSellerSerializer()
	status = serializers.ReadOnlyField(source="get_status_display")

	class Meta:
		model = Order
		fields = ("id", "operation_key", "seller", "title", "delivery_man", "order_type", "preiority", "status", "customer_name", "payment_type")

