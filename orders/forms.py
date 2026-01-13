from django import forms
from .models import Order, Bid


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['title', 'description', 'deadline', 'budget']


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['message', 'price_proposal']