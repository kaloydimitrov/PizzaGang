from django import forms
from PizzaGang.main.models import Pizza, Offer


class PizzaForm(forms.ModelForm):
    class Meta:
        model = Pizza
        fields = '__all__'


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ('final_price', 'name', 'image', 'is_active')
