import datetime
import logging
import traceback
import uuid
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver
from django.urls import reverse
from django.core.validators import ValidationError
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from seller.consts import validation_messages

class GBLUUID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Seller(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='seller')
    seller_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=12)
    verification_image = models.ImageField(upload_to='images/seller/')


    def __str__(self):
        return self.seller_name
    def __repr__(self):
        return self.seller_name

    def validate_unique(self, *args, **kwargs):
        super(Seller, self).validate_unique(*args, **kwargs)
        sn_qs = self.__class__._default_manager.filter(
            seller_name=self.seller_name).exists()
        cn_qs = self.__class__._default_manager.filter(
            contact_number=self.contact_number).exists()
        if sn_qs:
            raise ValidationError(validation_messages.get("DUPLICATE_SELLER"))
        if cn_qs:
            raise ValidationError(validation_messages.get("DUPLICATE_NUMBER"))

    def clean(self, *args, **kwargs):
        if self.seller_name:
            self.seller_name = self.seller_name.lower()

    def save(self, *args, **kwargs):
        super(Seller, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Seller Manager")
        verbose_name_plural = _("Seller Managers")


class DeliveryMan(models.Model):
    """
        delivery boy model
    """
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='delivery_man')
    delivery_man_name = models.CharField(max_length=150)
    number = models.CharField(max_length=12, unique=True)
    verification_image = models.ImageField(upload_to='images/deliveryMan/')

    def __str__(self):
        return self.user.get_full_name()

    def __repr__(self):
        return self.user.get_full_name()

    def validate_unique(self, *args, **kwargs):
        super(DeliveryMan, self).validate_unique(*args, **kwargs)
        # qs = self.__class__._default_manger.filter(number=self.number).exists()
        qs = DeliveryMan.objects.filter(number=self.number).exists()
        if qs:
            raise ValidationError(validation_messages.get("DUPLICATE_NUMBER"))

    class Meta:
        verbose_name = _("Delivery Man")
        verbose_name_plural = _("Delivery Men")


class Order(models.Model):
    """
        Order model
    """
    B2B = 'B2B'
    B2C = 'B2C'

    ONDEMAND = 'ONDEMAND'
    SAMEDAY = 'SAMEDAY'
    NEXTEDAY = 'NEXTEDAY'

    ACCEPTED = 'ACCEPTED'
    PICKEDUP = 'PICKEDUP'
    DELIVERED = 'DELIVERED'
    CANCELD = 'CANCELD'
    REJECTED = 'REJECTED'

    CASH_ON_PAYMENT = 'CASH'
    ONLINE_PAYMENT = 'ONLINE'

    ORDER_TYPE = (
        (B2B, 'Business To Business'),
        (B2C, 'Business To Customer')
    )

    PREIORITY_CHOICES = (
        (ONDEMAND, 'ONDEMAND'),
        (SAMEDAY, 'SAMEDAY'),
        (NEXTEDAY, 'NEXTEDAY'),
    )

    STATUS_CHOICES = (
        (ACCEPTED, 'Accepted'),
        (PICKEDUP, 'Pickedup'),
        (DELIVERED, 'Delivered'),
        (REJECTED, 'Rejected'),
        (CANCELD, 'Canceld')
    )

    PAYMENT_TYPE = (
        (CASH_ON_PAYMENT, 'Pay in Cash'),
        (ONLINE_PAYMENT, 'Pay Online')
    )

    operation_key = models.OneToOneField(GBLUUID, unique=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    delivery_man = models.ForeignKey(DeliveryMan,
                                     on_delete=models.CASCADE,
                                     blank=True, null=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE, default=B2C)
    preiority = models.CharField(max_length=10, choices=PREIORITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACCEPTED)
    customer_name = models.CharField(max_length=100, null=False, help_text='name of the client')
    delivery_location = models.CharField(max_length=100, null=False, help_text='delivery location of the client')
    delivery_note = models.CharField(max_length=30, null=False, help_text='any extra thing to mention')
    customer_contact_no = models.CharField(max_length=11, blank=False, help_text='ex : 01XXXXXXXXXXX')
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, help_text='price of the product')
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE, default=CASH_ON_PAYMENT)
    created_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    edited_at = models.DateTimeField(auto_now_add=True)
    celery_id = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('order_details', args=[str(self.id)])

    class Meta:
        verbose_name = _("Delivery Order")
        verbose_name_plural = _("Delivery Orders")
        ordering = ('created_at',)



