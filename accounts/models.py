from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    name = models.CharField()
    username = None
    email = models.EmailField()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    phone = models.CharField(max_length=11, unique=True)
    password = models.CharField(max_length=11, unique=True)
    password_confirmation = models.CharField(max_length=11, unique=True)
    photo = models.ImageField(null=True, blank=True)


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

