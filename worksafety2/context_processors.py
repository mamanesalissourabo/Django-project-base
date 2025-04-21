from django.utils.translation import get_language
from django.shortcuts import render
from base.models import Notification

def language_code(request):
    return {
        'LANGUAGE_CODE': get_language(),
    }

def base_context(request):
    if request.user.is_authenticated:
        # Récupérer uniquement les notifications non lues
        unread_notifications = Notification.objects.filter(user=request.user, read_at__isnull=True).order_by('-created_at')[:5]
        unread_notifications_count = unread_notifications.count()
    else:
        unread_notifications = []
        unread_notifications_count = 0

    return {
        'unread_notifications': unread_notifications,
        'unread_notifications_count': unread_notifications_count,
    }