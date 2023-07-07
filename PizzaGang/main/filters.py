import django_filters

from .models import Pizza


class PizzaOrderFilter(django_filters.FilterSet):
    class Meta:
        model = Pizza
        fields = ('name', 'ingredients', 'price', 'is_special')
