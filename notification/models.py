from django.db import models
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
# from django.conf import settings
from accounts.models import CustomUser
from django.urls import reverse

CustomUser = get_user_model()

class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ('order', 'سفارش'),
        ('review', 'نظر'),
        ('system', 'سیستمی'),
        ('promotion', 'تخفیف'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='system'
    )
    related_id = models.PositiveIntegerField(
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"Notification for {self.user.phone} - {self.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'


    @classmethod
    def create_notification(cls, user, title, message, notif_type='system', related_id=None):
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notif_type,
            related_id=related_id
        )
    
    def get_absolute_url(self):
        if self.notification_type == 'review':
            return reverse('review:review-detail', kwargs={'pk': self.related_id})
        elif self.notification_type == 'order':
            return reverse('order:order-detail', kwargs={'pk': self.related_id})

        return reverse('notification:notification-list', kwargs={'pk': self.id})

    def short_message(self, length=100):
        if len(self.message) > length:
            return self.message[:length] + '...'
        return self.message

# def send_notification(user, title, message):
#     Notification.objects.create(user=Notification.user, title=Notification.title, message=message)

# send_notification(Notification.user, Notification.title, Notification.message)