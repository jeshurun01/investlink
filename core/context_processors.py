from django.db.models import Q, Count


def unread_messages_count(request):
    """Context processor pour le compteur de messages non lus"""
    if request.user.is_authenticated:
        unread_count = 0
        try:
            from messaging.models import Message
            # Compter les messages non lus où l'utilisateur n'est pas l'expéditeur
            unread_count = Message.objects.filter(
                conversation__participants=request.user,
                is_read=False
            ).exclude(
                sender=request.user
            ).count()
        except:
            pass
        
        return {
            'unread_messages_count': unread_count
        }
    return {
        'unread_messages_count': 0
    }


def unread_notifications_count(request):
    """Context processor pour le compteur de notifications non lues"""
    if request.user.is_authenticated:
        unread_count = 0
        try:
            from notifications.models import Notification
            unread_count = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
        except:
            pass
        
        return {
            'unread_notifications_count': unread_count
        }
    return {
        'unread_notifications_count': 0
    }
