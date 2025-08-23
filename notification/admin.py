from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'notification_type', 'short_message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__phone', 'user__email', 'title', 'message')
    ordering = ('-created_at',)
    list_select_related = ('user',)
    actions = ['mark_as_read', 'mark_as_unread', 'delete_notifications']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} اعلان خوانده شد.")

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} اعلان به حالت خوانده‌نشده برگشت.")

    def delete_notifications(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} اعلان حذف شد.")

    delete_notifications.short_description = "حذف اعلان‌ها"

    def short_message(self, obj):
        return obj.message[:50]
    
    