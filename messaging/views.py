from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message


@login_required
def inbox(request):
    """Boîte de réception"""
    conversations = request.user.conversations.all()
    return render(request, 'messaging/inbox.html', {'conversations': conversations})


@login_required
def conversation(request, pk):
    """Détail d'une conversation"""
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    messages = conversation.messages.all()
    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'messages': messages
    })

