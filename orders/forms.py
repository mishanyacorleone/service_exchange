from django import forms
from django.utils import timezone
from .models import Order, Bid


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['title', 'description', 'deadline', 'budget']

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline <= timezone.now():
            raise forms.ValidationError('Срок выполнения не может быть в прошлом.')
        return deadline

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget is not None and budget < 1000:
            raise forms.ValidationError('Бюджет должен быть не менее 1000.')
        return budget


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['message', 'price_proposal']

    def clean_budget(self):
        price_proposal = self.cleaned_data.get('price_proposal')
        if price_proposal is not None and price_proposal < 1000:
            raise forms.ValidationError('Предлагаемая цена должна быть не менее 1000.')
        return price_proposal