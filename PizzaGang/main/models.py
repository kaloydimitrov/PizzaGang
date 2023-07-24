from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from phonenumber_field.modelfields import PhoneNumberField
from .validators import validate_positive


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='static/images/avatars/', null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"


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
    duplication_count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.FloatField(validators=[validate_positive], default=0.00)

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
    final_price = models.FloatField(validators=[validate_positive], default=0.00)
    is_small = models.BooleanField(default=False)
    is_big = models.BooleanField(default=True)
    is_large = models.BooleanField(default=False)
    is_half_price = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.cart:
            return f"{self.pizza.name} | ({self.cart.user.username})"
        elif self.offer.in_progress:
            return f"{self.pizza.name} | In progress"
        elif not self.offer.in_progress and self.offer.name:
            return f"{self.pizza.name} | Offer - {self.offer.name}"
        else:
            return f"{self.pizza.name}"


class Offer(models.Model):
    name = models.CharField(max_length=80, blank=True, null=True)
    image = models.ImageField(upload_to='static/images/offers/', blank=True, null=True)
    total_price = models.FloatField(validators=[validate_positive], default=0.00)
    final_price = models.FloatField(validators=[validate_positive], default=0.00)
    is_active = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=True)


class OfferItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_finished = models.BooleanField(default=False)
    cart_items = models.TextField()
    total_price = models.FloatField(validators=[validate_positive], default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Order ({self.pk})"
