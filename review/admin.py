from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'rating')
    list_editable = ('is_approved',)
    search_fields = ('product__name', 'user__email', 'user__phone')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} نظر تأیید شد.')
    approve_reviews.short_description = 'تأیید دسته‌ای نظرها'
