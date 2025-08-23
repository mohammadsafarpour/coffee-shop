from .models import Notification

def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.for_user(request.user).unread().count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
