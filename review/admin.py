from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('product__name', 'user__email')
    ordering = ('-created_at',)

    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    approve_reviews.short_description = 'Approve selected reviews'
    approve_reviews.allowed_permissions = ('change',)


admin.site.register(Review, ReviewAdmin)

