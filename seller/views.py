import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.core.validators import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from rest_framework import viewsets
from django.views.generic import TemplateView, CreateView, DetailView
from seller.models import Seller, Order
from seller.forms import (UserForm,
                         UserEditForm,
                         SellerForm,
                         OrderForm,
                         DeliveryManForm)


# from store.orders import store_created_new_order_notification
# Create your views here.

def celery_order_checker(request):
    return render(request, 'celery.html')


def home(request):
    try:
        if request.user.seller:
            return redirect(seller_home)
    except Exception as e:
        return redirect(delivery_man_home)

def get_auth_token(request):
    return redirect(seller_home)


@login_required(login_url='/seller/signin')
def seller_home(request):
    return redirect(seller_orders)


def seller_signup(request):
    user_form = UserForm()
    seller_form = SellerForm()

    if request.method == "POST":
        user_form = UserForm(request.POST)
        seller_form = SellerForm(request.POST)

        if user_form.is_valid() and seller_form.is_valid():
            new_user_instance = User.objects.create_user(**user_form.cleaned_data)
            new_seller_instance = seller_form.save(commit=False)
            new_seller_instance.user = new_user_instance
            new_seller_instance.save()

            login(request, authenticate(
                username=user_form.cleaned_data["username"],
                password=user_form.cleaned_data["password"]
            ))
            return redirect(seller_home)
    return render(request, "seller/seller_signup.html",
                  {"user_form": user_form, "seller_form": seller_form})


@login_required(login_url='/seller/signin/')
def seller_account(request):
    user_form = UserEditForm(instance=request.user)
    seller_form = SellerForm(instance=request.user.seller)

    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user)
        seller_form = SellerForm(request.POST, instance=request.user.seller)
        if user_form.is_valid() and seller_form.is_valid():
            user_form.save()
            seller_form.save()
    return render(request, 'seller/seller_account.html',
                  {'user_form': user_form, 'seller_form': seller_form})


@login_required(login_url='/seller/signin/')
def create_order(request):
    order_form = OrderForm()
    if request.method == "POST":
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            #order_instance = Order.objects.create(**order_form.cleaned_data)
            order_instance = order_form.save(commit=False)
            order_instance.seller = request.user.seller
            order_instance.status = Order.ACCEPTED
            order_instance.save()
            messages.success(request, 'New Order Created')
            #seller_created_new_order_notification.delay(order_instance.id)
            return redirect(seller_home)

    return render(request, 'seller/create_order.html', {'order_form': order_form})


@login_required(login_url="/seller/signin")
def seller_orders(request):
    print("user")
    print(request.user.seller)
    if request.method == "POST":
        pass
    # orders = order.objects.filter(seller=request.user.seller).order_by("-id")
    orders = Order.objects.filter(seller=request.user.seller).order_by("-id")
    return render(request, "seller/orders.html", {"orders": orders})


@login_required(login_url="/seller/signin")
def seller_order(request, id):
    order = Order.objects.get(id=id, seller=request.user.seller).order_by("-id")
    return render(request, "seller/order.html", {"order": order})


def delivery_man_signup(request):
    user_form = UserForm()
    delivery_man_form = DeliveryManForm()

    if request.method == "POST":
        user_form = UserForm(request.POST)
        delivery_man_form = DeliveryManForm(request.POST)

        if user_form.is_valid() and delivery_man_form.is_valid():
            new_user_instance = User.objects.create_user(**user_form.cleaned_data)
            delivery_man_instance = delivery_man_form.save(commit=False)
            delivery_man_instance.user = new_user_instance
            delivery_man_instance.save()

            login(request, authenticate(
                username=user_form.cleaned_data['username'],
                password=user_form.cleaned_data['password']
            ))
            return redirect(delivery_man_home)
    return render(request, "deliver/delivery_man_signup.html",
                  {"user_form": user_form, "delivery_man_form": delivery_man_form})


@login_required(login_url='/deliver/signin')
def delivery_man_home(request):
    return redirect(deliver_orders)


@login_required(login_url='/deliver/signin')
def delivery_man_account(request):
    user_form = UserEditForm(instance=request.user)
    delivery_man_form = DeliveryManForm(
        instance=request.user.delivery_man)

    if request.method == "POST":
        user_form = UserEditForm(
            request.POST, instance=request.user)
        delivery_man_form = DeliveryManForm(
            request.POST, instance=request.user.delivery_man)
        if user_form.is_valid() and delivery_man_form.is_valid():
            user_form.save()
            delivery_man_form.save()
    return render(request, 'deliver/delivery_man_account.html',
                  {'user_form': user_form, 'delivery_man_form': delivery_man_form})


@login_required(login_url="/deliver/signin")
def deliver_orders(request):
    orders = Order.objects.filter(delivery_man=None).exclude(
        Q(status=Order.CANCELD) | Q(status=Order.DELIVERED)).order_by('-created_at')
    accepted_orders = Order.objects.filter(
        status=Order.ACCEPTED, delivery_man=request.user.delivery_man).order_by('-created_at')
    delivered_orders = Order.objects.filter(
        status=Order.DELIVERED, delivery_man=request.user.delivery_man).order_by('-created_at')
    return render(request, "deliver/orders.html",
                  {"orders": orders,
                   "accepted_orders": accepted_orders,
                   "delivered_orders": delivered_orders})


class OrderDetails(DetailView):
    template_name = 'seller/order_details.html'
    model = Order
    context_object_name = 'order'


def roothome(request):
    return render(request, 'index.html')

def services(request):
    return render(request, 'services.html')

def whygobd(request):
    return render(request, 'whygobd.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def contact(request):
    return render(request, 'contact.html')

# def handler404(request, *args, **argv):
#     response = render_to_response('custom_404_view.html', {},
#                                   context_instance=RequestContext(request))
#     response.status_code = 404
#     return response
#
# def handler500(request, *args, **argv):
#     response = render_to_response('custom_404_view.html', {},
#                                   context_instance=RequestContext(request))
#     response.status_code = 500
#     return response
