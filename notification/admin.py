from django.contrib import admin

from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title','user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'message')
    ordering = ('-created_at',)

    # def has_view_permission(self, request, obj=None):
    #     return True

    # def has_module_permission(self, request):
    #     return True

# class PusherAdmin(admin.ModelAdmin):
#     list_display = ('user', 'token')
#     search_fields = ('user__email',)


admin.site.register(Notification, NotificationAdmin)
# admin.site.register(Pusher, PusherAdmin)
