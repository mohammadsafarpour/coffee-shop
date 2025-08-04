from django.db.models.signals import pre_save, post_save
from django.contrib.auth import get_user_model
from notification.models import Notification
from django.dispatch import receiver
from .models import Order, OrderItem

@receiver(pre_save, sender=OrderItem)
def set_order_item_price(sender, instance, **kwargs):
    if instance.product:
        instance.price = instance.product.price

User = get_user_model()

@receiver(post_save, sender=Order)
def notify_admin_on_new_order(sender, instance, created, **kwargs):
    if created:
        admins = User.objects.filter(is_superuser=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                title="سفارش جدید ثبت شد",
                message=f"سفارشی توسط {instance.customer} با شناسه {instance.id} ثبت شده است."
            )