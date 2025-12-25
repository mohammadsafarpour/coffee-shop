# import os
# from django.db.models.signals import pre_save, post_delete
# from django.dispatch import receiver
# from .models import Product, ProductImage


# def _delete_file(path):
#     if path and os.path.isfile(path):
#         try:
#             os.remove(path)
#         except OSError:
#             pass

# @receiver(pre_save, sender=Product)
# def auto_delete_old_main_image(sender, instance, **kwargs):
#     if not instance.pk:
#         return
#     try:
#         old = Product.objects.get(pk=instance.pk)
#     except Product.DoesNotExist:
#         return
#     old_file = getattr(old.image, 'path', None)
#     new_file = getattr(instance.image, 'path', None)
#     if old_file and old_file != new_file:
#         _delete_file(old_file)

# @receiver(post_delete, sender=Product)
# def delete_main_image_on_delete(sender, instance, **kwargs):
#     _delete_file(getattr(instance.image, 'path', None))

# @receiver(pre_save, sender=ProductImage)
# def auto_delete_old_extra_image(sender, instance, **kwargs):
#     if not instance.pk:
#         return
#     try:
#         old = ProductImage.objects.get(pk=instance.pk)
#     except ProductImage.DoesNotExist:
#         return
#     old_file = getattr(old.image, 'path', None)
#     new_file = getattr(instance.image, 'path', None)
#     if old_file and old_file != new_file:
#         _delete_file(old_file)

# @receiver(post_delete, sender=ProductImage)
# def delete_extra_image_on_delete(sender, instance, **kwargs):
#     _delete_file(getattr(instance.image, 'path', None))

#======================new one=================================

import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Product, ProductImage


def _delete_file(path):
    """Deletes file from filesystem."""
    if path and os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            # Handle error, e.g., log it
            pass

@receiver(pre_save, sender=Product)
def auto_delete_old_main_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return
    if not old_instance.image:
        return
    if old_instance.image != instance.image:
        _delete_file(old_instance.image.path)

@receiver(post_delete, sender=Product)
def delete_main_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        _delete_file(instance.image.path)

@receiver(pre_save, sender=ProductImage)
def auto_delete_old_extra_image(sender, instance, **kwargs):
    """
    Deletes old extra image file from filesystem when a ProductImage object is updated.
    """
    if not instance.pk:
        return
    try:
        old_instance = ProductImage.objects.get(pk=instance.pk)
    except ProductImage.DoesNotExist:
        return
    
    if not old_instance.image:
        return
 

    if old_instance.image != instance.image:
        _delete_file(old_instance.image.path)

@receiver(post_delete, sender=ProductImage)
def delete_extra_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        _delete_file(instance.image.path)