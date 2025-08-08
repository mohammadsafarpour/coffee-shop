from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
# from django.conf import settings
from accounts.models import CustomUser

CustomUser = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.phone} - {self.title}"

    class Meta:
        ordering = ['-created_at']

# class Pusher(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     token = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)


# def send_notification(user, title, message):
#     Notification.objects.create(user=Notification.user, title=Notification.title, message=message)

# send_notification(Notification.user, Notification.title, Notification.message)