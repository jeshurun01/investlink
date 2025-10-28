from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Notification


@login_required
def notification_list(request):
    """Liste des notifications avec filtres"""
    notifications_query = request.user.notifications.all()
    
    # Filtres
    filter_type = request.GET.get('type', 'all')
    if filter_type == 'unread':
        notifications_query = notifications_query.filter(is_read=False)
    elif filter_type == 'read':
        notifications_query = notifications_query.filter(is_read=True)
    
    # Statistiques
    total_count = request.user.notifications.count()
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications_query[:50],  # Limiter à 50 notifications
        'total_count': total_count,
        'unread_count': unread_count,
        'filter_type': filter_type,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def mark_as_read(request, pk):
    """Marquer une notification comme lue et rediriger vers le lien"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    
    # Rediriger vers le lien de la notification s'il existe
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')


@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """Marquer toutes les notifications comme lues"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, 'Toutes les notifications ont été marquées comme lues.')
    return redirect('notifications:list')


@login_required
@require_http_methods(["POST"])
def delete_notification(request, pk):
    """Supprimer une notification"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.delete()
    messages.success(request, 'Notification supprimée.')
    return redirect('notifications:list')


@login_required
@require_http_methods(["POST"])
def delete_all_read(request):
    """Supprimer toutes les notifications lues"""
    deleted_count = request.user.notifications.filter(is_read=True).delete()[0]
    messages.success(request, f'{deleted_count} notification(s) supprimée(s).')
    return redirect('notifications:list')


@login_required
def notifications_dropdown(request):
    """API pour le dropdown des notifications (AJAX)"""
    notifications = request.user.notifications.filter(is_read=False)[:5]
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    notifications_data = [{
        'id': notif.id,
        'title': notif.title,
        'message': notif.message[:100],
        'type': notif.notification_type,
        'created_at': notif.created_at.strftime('%d/%m/%Y %H:%M'),
        'link': notif.link,
    } for notif in notifications]
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count,
    })
