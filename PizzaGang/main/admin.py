from django.contrib import admin
from .models import Profile, Pizza, Cart, CartItem, Order, Offer

admin.site.register(Profile)
admin.site.register(Pizza)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Offer)
