import django_filters
from django_filters import CharFilter

from .models import Pizza


class PizzaOrderFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    ingredients = CharFilter(field_name='ingredients', lookup_expr='icontains')

    class Meta:
        model = Pizza
        fields = ('name', 'ingredients', 'price', 'is_special', 'is_offer', 'is_vege')
