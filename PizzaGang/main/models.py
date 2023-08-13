from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from phonenumber_field.modelfields import PhoneNumberField
from .validators import validate_positive


def get_cart_item_price(cart_item):
    price = 0

    if cart_item.is_small:
        price = cart_item.pizza.final_price * 0.75
    elif cart_item.is_big:
        price = cart_item.pizza.final_price
    elif cart_item.is_large:
        price = cart_item.pizza.final_price * 1.25

    if cart_item.is_half_price:
        return price / 2
    return price


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='static/images/avatars/', null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Creates Profile when a new user signs up
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()


post_save.connect(create_profile, sender=User)


class Pizza(models.Model):
    name = models.CharField(max_length=30)
    ingredients = models.TextField()
    image = models.ImageField(upload_to='static/images/pizza/')
    price = models.FloatField(validators=[validate_positive])

    is_special = models.BooleanField(blank=True, null=True)
    is_offer = models.BooleanField(blank=True, null=True)
    is_vege = models.BooleanField(blank=True, null=True)
    discount = models.IntegerField(blank=True, null=True)

    @property
    def final_price(self):
        if self.discount:
            return (1 - self.discount / 100) * self.price
        return self.price

    def __str__(self):
        return f"{self.name}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def total_price(self):
        total_price = 0

        cart_items = CartItem.objects.filter(cart=self)
        for cart_item in cart_items:
            total_price += get_cart_item_price(cart_item)

        offer_items = OfferItem.objects.filter(cart=self)
        for offer_item in offer_items:
            total_price += offer_item.offer.final_price

        return total_price

    def __str__(self):
        return f"{self.user.username}'s Cart"


# Creates Cart when a new user signs up
def create_cart(sender, instance, created, **kwargs):
    if created:
        user_cart = Cart(user=instance)
        user_cart.save()


post_save.connect(create_cart, sender=User)


class CartItem(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, blank=True, null=True)
    offer = models.ForeignKey('Offer', on_delete=models.CASCADE, blank=True, null=True)
    is_small = models.BooleanField(default=False)
    is_big = models.BooleanField(default=True)
    is_large = models.BooleanField(default=False)
    is_half_price = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def final_price(self):
        return get_cart_item_price(self)

    def __str__(self):
        if self.cart:
            return f"{self.pizza.name} ({self.cart.user.username})"
        elif self.offer.in_progress:
            return f"{self.pizza.name} | In progress"
        elif not self.offer.in_progress and self.offer.name:
            return f"{self.pizza.name} | Offer - {self.offer.name}"
        else:
            return f"{self.pizza.name}"


class Offer(models.Model):
    name = models.CharField(max_length=80, blank=True, null=True)
    image = models.ImageField(upload_to='static/images/offers/', blank=True, null=True)
    final_price = models.FloatField(validators=[validate_positive], default=0.00)
    is_active = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=True)

    @property
    def total_price(self):
        total_price = 0

        cart_items = CartItem.objects.filter(offer=self)
        for cart_item in cart_items:
            total_price += get_cart_item_price(cart_item)

        return total_price

    def __str__(self):
        return f"{self.name} | {self.final_price} lv."


class OfferItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.offer.name} | {self.offer.final_price} lv. ({self.cart.user.username})"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_finished = models.BooleanField(default=False)
    cart_items = models.TextField()
    total_price = models.FloatField(validators=[validate_positive], default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Order ({self.pk})"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Review"


class ProductImage(models.Model):
    image = models.ImageField(upload_to='static/images/products/')

    def __str__(self):
        return f"{self.image.name}"
