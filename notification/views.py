from django.shortcuts import render
from .models import Notification

def notification_list(request):
    notification = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notification/notification_list.html', {'notification': notification})
