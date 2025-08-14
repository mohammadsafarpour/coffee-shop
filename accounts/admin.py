from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile
from django.utils.html import format_html


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "phone",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active", "groups")
    search_fields = ("phone", "email", "first_name", "last_name")
    ordering = ("phone",)

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("اطلاعات شخصی", {"fields": ("first_name", "last_name", "email")}),
        (
            "دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("تاریخ‌های مهم", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "email", "password", "password2"),
            },
        ),
    )
    
    filter_horizontal = ("groups", "user_permissions",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'user_phone')
    search_fields = ('first_name', 'last_name', 'user__phone', 'user__email')
    list_filter = ('user__is_active',)
    readonly_fields = ('user', 'user_phone')

    fieldsets = (
        ('اطلاعات کاربری', {'fields': ('user', 'user_phone', 'avatar')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name')}),
        ('علاقه‌مندی‌ها', {'fields': ('favorites',)}),
    )


    @admin.display(description='شماره تلفن')
    def user_phone(self, obj):
        return obj.user.phone
    