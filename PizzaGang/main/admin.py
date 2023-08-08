from django.contrib import admin
from .models import Profile, Pizza, Cart, CartItem, Order, Offer, OfferItem, Review, ProductImage
from django.utils.html import format_html


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'phone_number', 'address')
    list_display = ('user', 'phone_number', 'address', 'avatar_preview')
    list_filter = ('user__email', 'user__username', 'address')
    ordering = ('user',)
    date_hierarchy = 'user__date_joined'

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;">',
                               obj.avatar.url)
        else:
            return "No Avatar"

    avatar_preview.short_description = 'Avatar Preview'


admin.site.register(Profile, ProfileAdmin)


class PizzaAdmin(admin.ModelAdmin):
    search_fields = ('name', 'ingredients')
    list_display = ('name', 'price', 'ingredients', 'is_special', 'is_offer', 'is_vege')
    list_filter = ('is_special', 'is_offer', 'is_vege')
    ordering = ('price', 'name')


admin.site.register(Pizza, PizzaAdmin)


class CartAdmin(admin.ModelAdmin):
    search_fields = ('user__username',)
    list_display = ('user_username', 'total_price')
    list_filter = ('total_price',)

    def user_username(self, obj):
        return obj.user.username

    user_username.short_description = "User"


admin.site.register(Cart, CartAdmin)


class CartItemAdmin(admin.ModelAdmin):
    search_fields = ('cart__user__username', 'offer__name')
    list_display = ('pizza', 'quantity', 'cart', 'offer', 'final_price', 'created_at', 'user_username')
    list_filter = ('pizza', 'cart', 'offer', 'created_at')
    ordering = ('-created_at',)

    def user_username(self, obj):
        if not obj.offer:
            return obj.cart.user.username


admin.site.register(CartItem, CartItemAdmin)


class OfferAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'final_price', 'total_price', 'is_active', 'in_progress', 'image_preview')
    list_filter = ('is_active', 'in_progress')
    ordering = ('name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;">',
                               obj.image.url)
        else:
            return "No Image"

    image_preview.short_description = 'Image Preview'


admin.site.register(Offer, OfferAdmin)


class OfferItemAdmin(admin.ModelAdmin):
    search_fields = ('offer__name',)
    list_display = ('offer_name', 'image_preview', 'user_username')
    list_filter = ('offer__name',)
    ordering = ('offer__name',)

    def offer_name(self, obj):
        return obj.offer.name

    def user_username(self, obj):
        return obj.cart.user.username

    def image_preview(self, obj):
        if obj.offer.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;">',
                               obj.offer.image.url)
        else:
            return "No Image"

    image_preview.short_description = 'Image Preview'


admin.site.register(OfferItem, OfferItemAdmin)


class OrderAdmin(admin.ModelAdmin):
    search_fields = ('user__username',)
    list_display = ('user', 'cart_items', 'is_finished', 'total_price', 'created_at')
    list_filter = ('user', 'is_finished', 'created_at')
    ordering = ('-created_at',)


admin.site.register(Order, OrderAdmin)


class ReviewAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'text')
    list_display = ('user', 'rating', 'text', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)


admin.site.register(Review, ReviewAdmin)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview',)

    def image_preview(self, obj):
        return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;">',
                           obj.image.url)

    image_preview.short_description = 'Image Preview'


admin.site.register(ProductImage, ProductImageAdmin)
