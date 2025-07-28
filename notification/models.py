from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.models import CustomUser


class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
