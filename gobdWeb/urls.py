"""gobdWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include, handler404, handler500
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth import views as deliver_views
from seller import views, apis



urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^celery/', views.celery_order_checker, name='celery_order_checker'),

    url(r'^api_auth_token/', views.get_auth_token, name='gblapi'),

    url(r'^seller/signin/', auth_views.LoginView.as_view(),{'template_name':'seller/signin.html'}, name="seller-signin" ),
    url(r'^seller/signout', auth_views.LogoutView.as_view(),{'next_page': '/seller/signin'}, name="seller-signout"),
    url(r'^seller/signup', views.seller_signup, name="seller-signup"),
    url(r'^seller/$', views.seller_home, name='seller_home'),

    url(r'^seller/accounts/$', views.seller_account, name='seller_account'),
    url(r'^seller/orders/$', views.seller_orders, name="seller_orders"),
    url(r'^seller/orders/details/(?P<pk>\d+)/', views.OrderDetails.as_view(), name="order_details"),
    url(r'^seller/create_order/$', views.create_order, name="create_order"),
    url(r'^api/seller/cancel_order/$', apis.seller_manager_cancel_order),

    url(r'^api/seller/order/notification/(?P<last_request_time>.+)/$', apis.seller_order_notification),


    url(r'^deliver/signin/', deliver_views.LoginView.as_view(),{'template_name':'deliver/signin.html'}, name="delivery_man-signin" ),
    url(r'^deliver/signout', auth_views.LogoutView.as_view(),{'next_page': '/deliver/signin'}, name="delivery_man-signout"),
    url(r'^deliver/signup', views.delivery_man_signup, name="delivery_man-signup"),
    url(r'^deliver/$', views.delivery_man_home, name='delivery_man_home'),

    url(r'^deliver/accounts/$', views.delivery_man_account, name='delivery_man_account'),
    url(r'^deliver/orders/$', views.deliver_orders, name="deliver_orders"),
    #APIs for Deliver man


    url(r'^api/deliver/order/ready/$', apis.delivery_man_ready_new_orders),
    url(r'^api/deliver/order/accept/$', apis.delivery_man_accept_order),
    url(r'^api/deliver/order/latest/$', apis.delivery_man_get_latest_order),
    url(r'^api/deliver/order/complete/$', apis.delivery_man_complete_order),
    url(r'^api/deliver/order/reject/$', apis.delivery_man_reject_order),
    url(r'^api/deliver/order/completed_orders/$', apis.get_delivery_man_completed_orders),

#    url(r'^$',views.home,name="home"),

    url(r'^$',views.roothome,name="home"),
    url(r'^services/', views.services, name='services'),
    url(r'^whygobd/', views.whygobd, name='whygobd'),
    url(r'^aboutus/', views.aboutus, name='aboutus'),
    url(r'^contact/', views.contact, name='contact'),
    url(r'^djga/', include('google_analytics.urls')),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# handler404 = 'views.views.handler404'
# handler500 = 'views.views.handler500'