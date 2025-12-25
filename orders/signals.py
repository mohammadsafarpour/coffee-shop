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
        
        notification_message = f"سفارش جدید #{instance.id} توسط کاربر {instance.customer.phone} ثبت شد."
        
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=notification_message
            )