from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='static/images/avatars/', null=True, blank=True)
    address = models.TextField(null=True, blank=True)

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
    price = models.FloatField()

    is_special = models.BooleanField(blank=True, null=True)
    is_offer = models.BooleanField(blank=True, null=True)
    is_vege = models.BooleanField(blank=True, null=True)
    discount = models.IntegerField(blank=True, null=True)
    duplication_count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.name}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.FloatField(default=0.00)

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
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    final_price = models.FloatField(default=0.00)
    is_small = models.BooleanField(default=False)
    is_big = models.BooleanField(default=True)
    is_large = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pizza.name} | {self.quantity} ({self.cart.user.username})"
