from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    username = None
    email = models.EmailField(unique=True, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    phone = models.CharField(max_length=11, unique=True)
    # password = models.CharField(max_length=11, unique=True)
    # password_confirmation = models.CharField(max_length=11, unique=True)
    photo = models.ImageField(upload_to="avatars/", null=True, blank=True)
    
    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

