from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import OrderItem

@receiver(pre_save, sender=OrderItem)
def set_order_item_price(sender, instance, **kwargs):
    if instance.product:
        instance.price = instance.product.price * instance.quantity
        
print("OrderItem signal loaded!")
