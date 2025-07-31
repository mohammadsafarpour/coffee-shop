from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile


class CustomUserAdmin(UserAdmin):
    list_display = (
        "phone",
        "email",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_staff",
        "is_active",
    )

    search_fields = (
        "phone",
        "email",
    )

    ordering = ("phone",)

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("اطلاعات شخصی", {"fields": ("email",)}),
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


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
