from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification
from django.core.paginator import Paginator


@login_required
def notification_list(request):

    unread_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    )
    unread_notifications.update(is_read=True)
    
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notifications/notification_list.html', {
        'page_obj': page_obj
    })

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, 'اعلان با موفقیت بروزرسانی شد.')
    return redirect('notification:notification-list')

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    messages.success(request, 'اعلان با موفقیت حذف شد.')
    return redirect('notification:notification-list')

@login_required
def mark_all_notifications_as_read(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    notifications.update(is_read=True)
    messages.success(request, 'تمامی اعلان‌ها با موفقیت بروزرسانی شد.')
    return redirect('notification:notification-list')

@login_required
def mark_notification_as_unread(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = False
    notification.save()
    messages.success(request, 'اعلان با موفقیت به حالت خوانده نشده تغییر یافت.')
    return redirect('notification:notification-list')

@login_required
def clear_all_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    notifications.delete()
    messages.success(request, 'تمامی اعلان‌ها با موفقیت حذف شد.')
    return redirect('notification:notification-list')
