from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Notification

@login_required
def notification_list(request):
    qs = Notification.objects.for_user(request.user).order_by('-created_at')
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'notifications': page_obj,   # برای حلقه
        'total_count': qs.count(),   # برای نمایش تعداد کل
    }
    return render(request, 'notifications/notification_list.html', context)

@login_required
def notification_detail(request, notification_id):
    note = get_object_or_404(Notification, id=notification_id, user=request.user)
    if not note.is_read:
        note.is_read = True
        note.save(update_fields=['is_read'])
    return render(request, 'notifications/notification_detail.html', {'notification': note})

@require_POST
@login_required
def mark_notification_as_read(request, notification_id):
    note = get_object_or_404(Notification, id=notification_id, user=request.user)
    if not note.is_read:
        note.is_read = True
        note.save(update_fields=['is_read'])
        messages.success(request, 'اعلان خوانده شد.')
    return redirect(request.META.get('HTTP_REFERER', 'notification:notification-list'))

@require_POST
@login_required
def mark_notification_as_unread(request, notification_id):
    note = get_object_or_404(Notification, id=notification_id, user=request.user)
    if note.is_read:
        note.is_read = False
        note.save(update_fields=['is_read'])
        messages.success(request, 'اعلان به حالت خوانده‌نشده برگشت.')
    return redirect(request.META.get('HTTP_REFERER', 'notification:notification-list'))

@require_POST
@login_required
def delete_notification(request, notification_id):
    note = get_object_or_404(Notification, id=notification_id, user=request.user)
    note.delete()
    messages.success(request, 'اعلان حذف شد.')
    return redirect('notification:notification-list')

@require_POST
@login_required
def mark_all_notifications_as_read(request):
    updated = Notification.objects.for_user(request.user).unread().update(is_read=True)
    messages.success(request, f'{updated} اعلان خوانده شد.')
    return redirect('notification:notification-list')

@require_POST
@login_required
def clear_all_notifications(request):
    qs = Notification.objects.for_user(request.user)
    count = qs.count()
    qs.delete()
    messages.success(request, f'{count} اعلان حذف شد.')
    return redirect('notification:notification-list')
