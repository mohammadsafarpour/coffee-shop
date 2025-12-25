from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from products.models import Product

class CustomUserManager(BaseUserManager):

    def create_user(self, phone, email=None, password=None, **extra_fields):
        if not phone:
            raise ValueError('برای ثبت‌نام، وارد کردن شماره تلفن الزامی است.')
        email = self.normalize_email(email) if email else None
        user = self.model(phone=phone, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

        # if not email:
        #     raise ValueError('برای ثبت‌نام، وارد کردن ایمیل الزامی است.')

    email = models.EmailField(unique=True, null=True, blank=True)    

    def create_superuser(self, phone, email, password=None, **extra_fields):        
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

            
        return self.create_user(phone, email, password, **extra_fields)


class CustomUser(AbstractUser):

    username = None
    email = models.EmailField(unique=True, null=True, blank=True)
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']
    phone = models.CharField(max_length=11, unique=True)
    # photo = models.ImageField(upload_to="avatars/", null=True, blank=True)  
    objects = CustomUserManager()

    def __str__(self):
        return self.phone

class Profile(models.Model):

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to="profiles/avatars/", null=True, blank=True)
    favorites = models.ManyToManyField(Product, related_name="user_favorites", blank=True, verbose_name="علاقه‌مندی‌ها")
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)    

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل‌ها'
        ordering = ['user']
        # unique_together = ('user', 'first_name', 'last_name')


    # def __str__(self):
    #     return f"پروفایل {self.user.first_name} { self.user.last_name}"
    
    def __str__(self):
        try:
            return f"پروفایل {self.user.first_name} {self.user.last_name}"
        except AttributeError:
            return "پروفایل خالی"


def create_user_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)

    instance.profile.save()

post_save.connect(create_user_profile, sender=CustomUser)

# receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

class OTPRequest(models.Model):
    phone = models.CharField(max_length=11)
    otp_secret = models.CharField(max_length=32) # کلید مخفی برای تولید و تایید OTP
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP request for {self.phone}"
