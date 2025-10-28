from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notification_list(request):
    """Liste des notifications"""
    notifications = request.user.notifications.all()
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def mark_as_read(request, pk):
    """Marquer une notification comme lue"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    return redirect('notifications:list')

