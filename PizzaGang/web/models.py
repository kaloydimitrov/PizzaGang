from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import AppUserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    avatar = models.ImageField(upload_to='static/images/avatars/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=True)

    objects = AppUserManager()

    USERNAME_FIELD = 'email'


class Pizza(models.Model):
    PE = "PE"
    SM = "SM"
    ME = "ME"
    LA = "LA"
    SIZE = [
        (PE, "Personal"),
        (SM, "Small"),
        (ME, "Medium"),
        (LA, "Large"),
    ]

    name = models.CharField(max_length=30)
    ingredients = models.TextField()
    image = models.ImageField(upload_to='static/pictures/pizza/')
    size = models.CharField(max_length=30, choices=SIZE, default=PE)
    price = models.FloatField()

    is_special = models.BooleanField(blank=True, null=True)
    is_offer = models.BooleanField(blank=True, null=True)
    is_vege = models.BooleanField(blank=True, null=True)
    discount = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"
