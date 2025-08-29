from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

User = get_user_model()

class NotificationQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)
    def unread(self):
        return self.filter(is_read=False)
    def read(self):
        return self.filter(is_read=True)

class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)
    def for_user(self, user):
        return self.get_queryset().for_user(user)
    def create_notification(
        self, *, user, title, message, notif_type='system',
        target_url=None, content_object=None, related_id=None, is_read=False
    ):
        obj = self.model(
            user=user, title=title, message=message,
            notification_type=notif_type, target_url=target_url,
            is_read=is_read, related_id=related_id
        )
        if content_object is not None:
            obj.content_object = content_object
        obj.save()
        return obj

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('order', 'سفارش'),
        ('review', 'نظر'),
        ('system', 'سیستمی'),
        ('promotion', 'تخفیف'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', db_index=True)
    title = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system', db_index=True)

    target_url = models.URLField(blank=True, null=True)


    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')


    related_id = models.PositiveIntegerField(null=True, blank=True)

    objects = NotificationManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.title}"

    @classmethod
    def create_notification(cls, user, title, message, notif_type='system', related_id=None, target_url=None):

        return cls.objects.create_notification(
            user=user, title=title, message=message,
            notif_type=notif_type, related_id=related_id, target_url=target_url
        )

    def get_absolute_url(self):
        if self.target_url:
            return self.target_url
        if self.content_object and hasattr(self.content_object, 'get_absolute_url'):
            return self.content_object.get_absolute_url()
        return reverse('notification:notification-detail', kwargs={'notification_id': self.id})

    # def short_message(self, length=70):
    #     text = self.message or ''
    #     return f"{text[:length]}..." if len(text) > length else text
