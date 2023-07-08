from django.contrib import admin
from .models import Profile, Pizza, Cart, CartItem

admin.site.register(Profile)
admin.site.register(Pizza)
admin.site.register(Cart)
admin.site.register(CartItem)
