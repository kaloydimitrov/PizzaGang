import django_filters
from django_filters import CharFilter
from django.forms.widgets import TextInput

from .models import Pizza


class PizzaOrderFilter(django_filters.FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=TextInput(attrs={'placeholder': 'Search name'})
    )
    ingredients = CharFilter(
        field_name='ingredients',
        lookup_expr='icontains',
        widget=TextInput(attrs={'placeholder': 'Search ingredients'})
    )

    class Meta:
        model = Pizza
        fields = ('name', 'ingredients', 'is_special', 'is_offer', 'is_vege')
