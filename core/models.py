import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser, User
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.shortcuts import reverse

from .managers import CustomUserManager


class User(AbstractUser):
    username = None
    photo_name = models.CharField(max_length=100, blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)
    phone_number = models.CharField(validators=[RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )], max_length=17, blank=True)
    email = models.EmailField(unique=True)
    twitter = models.CharField(max_length=500, null=True, blank=True)
    facebook = models.CharField(max_length=500, null=True, blank=True)
    instagram = models.CharField(max_length=500, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name

class House(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    price = models.PositiveIntegerField()
    forsale = models.BooleanField(default=True)
    rooms = models.PositiveIntegerField(default=0)
    garages = models.PositiveIntegerField(default=0)
    sitting_rooms = models.PositiveIntegerField(default=0)
    dining_rooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=1)
    kitchen = models.PositiveIntegerField(default=1)
    year_built = models.CharField(max_length=5)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"House {self.id}"

    def get_absolute_url(self):
        return reverse("property-detail", args=(self.pk,))


class Image(models.Model):
    name = models.CharField(max_length=100)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    url = models.URLField()

    def __str__(self):
        return f"House {self.house.id} images"


class Message(models.Model):
    agent = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100)
    message = models.TextField()

    def __str__(self):
        return f"Message from {self.email} for agent @ {self.agent.email}" if self.agent else f"Message from {self.email}"

