from django.contrib import admin

# Register your models here.
from seller.models import Seller,Order, DeliveryMan, GBLUUID

admin.site.register(GBLUUID)
admin.site.register(Seller)
admin.site.register(Order)
admin.site.register(DeliveryMan)
