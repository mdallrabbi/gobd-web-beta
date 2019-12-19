from django import forms
from django.utils.translation import ugettext as _
from django.core.validators import ValidationError
from django.contrib.auth.models import User
from seller.models import Order, Seller, DeliveryMan


class UserForm(forms.ModelForm):
    """
        Simple Django authentication User form for signup
    """

    email = forms.EmailField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})


class UserEditForm(forms.ModelForm):
    """
        user edit form for profile section
    """
    email = forms.EmailField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})


class SellerForm(forms.ModelForm):
    """
        store form for store managers
    """
    validation_messages = {
        "duplicate_seller": "Seller Name Already exists",
        "dupicate_number": "Number Already exists with Seller"
    }

    class Meta:
        model = Seller
        fields = ('seller_name', 'contact_number', 'verification_image')

        labels = {
            'seller_name': "Enter Seller Name",
            'contact_number': "Enter Contact Number",
            'verification_image': "Please Upload a Complete Scanned Copy of your NID/PASSPORT/TIN/TRADE LICENCE"
        }

    def __init__(self, *args, **kwargs):
        super(SellerForm, self).__init__(*args, **kwargs)
        self.fields['seller_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['verification_image'].widget.attrs.update({'class': 'form-control'})

    def clean_seller_name(self):
        sn_instance = self.cleaned_data.get("seller_name")
        validate = self.__class__._meta.model._default_manager.filter(seller_name=sn_instance).exists()
        if validate:
            raise ValidationError(self.validation_messages.get("duplicate_seller"))

    def clean_contact_number(self):
        cn_instance = self.cleaned_data.get("contact_number")
        validate = self.__class__._meta.model._default_manager.filter(contact_number=cn_instance).exists()
        if validate:
            raise ValidationError(self.validation_messages.get("dupicate_number"))


class DeliveryManForm(forms.ModelForm):
    """
        Delivery boy signup form
    """
    validation_messages = {
        "duplicate_number": "Number Already exists with this seller"
    }

    class Meta:
        model = DeliveryMan
        fields = ('delivery_man_name','number','verification_image')

        labels = {
            'delivery_man_name': "Enter Delivery Man Name",
            'number': "Enter Contact Number",
            'verification_image': "Please Upload a Complete Scanned Copy of your NID/PASSPORT"
        }

    def __init__(self, *args, **kwargs):
        super(DeliveryManForm, self).__init__(*args, **kwargs)
        self.fields['delivery_man_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['number'].widget.attrs.update({'class': 'form-control'})
        self.fields['verification_image'].widget.attrs.update({'class': 'form-control'})

    def clean_contact_number(self):
        cn_instance = self.cleaned_data.get("number")
        validate = self.__class__._meta.model._default_manager.filter(number=cn_instance).exists()
        if validate:
            raise ValidationError(self.validation_messages.get("duplicate_number"))


class OrderForm(forms.ModelForm):
    """
        order creation form store managers
    """
    # validation_messages = {
    #     "Title_Error": "Please Enter Some Other Title For Your Order"
    # }

    class Meta:
        model = Order
        fields = ('title','order_type', 'preiority','customer_name','delivery_location',
                  'delivery_note','customer_contact_no', 'product_price', 'payment_type')

        labels = {
            #"operation_key": "Automatically Generated Order Tracking Code",
            "title": "Enter Your Order Title",
            "order_type": "Select Your Order Type",
            "preiority": "Select Order Priority",
            "customer_name": "Your Customer Name",
            "delivery_location": "Product Delivery Location",
            "delivery_note": "Any Additional Notes During The Delivery",
            "customer_contact_no": "Contact Number of The Customer",
            "product_price": "Price of Your Product",
            "payment_type": "Select Payment Type"

        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        #self.fields['operation_key'].widget.attrs.update({'class': 'form-control'})
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['order_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['preiority'].widget.attrs.update({'class': 'form-control'})
        self.fields['customer_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['delivery_location'].widget.attrs.update({'class': 'form-control'})
        self.fields['delivery_note'].widget.attrs.update({'class': 'form-control'})
        self.fields['customer_contact_no'].widget.attrs.update({'class': 'form-control'})
        self.fields['product_price'].widget.attrs.update({'class': 'form-control'})
        self.fields['payment_type'].widget.attrs.update({'class': 'form-control'})

    def clean_title(self):
        title_instance = self.cleaned_data.get("title")
        validate = Order.objects.filter(title=title_instance, status=Order.ACCEPTED).exists()
        if validate:
            raise ValidationError(["Title_Error"])
        return title_instance

