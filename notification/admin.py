from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'notification_type')
    search_fields = ('user__phone', 'title', 'message')
    ordering = ('-created_at',)
    actions = ['mark_as_read', 'mark_as_unread', 'delete_notifications']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "اعلان‌ها به عنوان خوانده شده علامت‌گذاری شدند.")
    mark_as_read.short_description = "علامت‌گذاری به عنوان خوانده شده"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, "اعلان‌ها به عنوان خوانده نشده علامت‌گذاری شدند.")
    mark_as_unread.short_description = "علامت‌گذاری به عنوان خوانده نشده"

    def delete_notifications(self, request, queryset):
        queryset.delete()
        self.message_user(request, "اعلان‌ها با موفقیت حذف شدند.")
    delete_notifications.short_description = "حذف اعلان‌ها"



admin.site.register(Notification, NotificationAdmin)




    # def has_view_permission(self, request, obj=None):
    #     return True

    # def has_module_permission(self, request):
    #     return True

# class PusherAdmin(admin.ModelAdmin):
#     list_display = ('user', 'token')
#     search_fields = ('user__email',)

# admin.site.register(Pusher, PusherAdmin)
