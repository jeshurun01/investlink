from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q, Count, Max, Prefetch
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Conversation, Message
from notifications.models import Notification

User = get_user_model()


@login_required
def inbox(request):
    """Boîte de réception avec statistiques"""
    # Récupérer toutes les conversations de l'utilisateur avec le dernier message
    conversations = request.user.conversations.annotate(
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
        ),
        last_message_time=Max('messages__created_at')
    ).select_related().prefetch_related(
        'participants',
        Prefetch(
            'messages',
            queryset=Message.objects.select_related('sender').order_by('-created_at')[:1],
            to_attr='latest_message'
        )
    ).order_by('-last_message_time')
    
    # Ajouter l'autre participant à chaque conversation
    for conversation in conversations:
        conversation.other_user = conversation.get_other_participant(request.user)
    
    # Statistiques
    total_unread = sum(conv.unread_count for conv in conversations)
    
    context = {
        'conversations': conversations,
        'total_unread': total_unread,
    }
    return render(request, 'messaging/inbox.html', context)


@login_required
def conversation_detail(request, pk):
    """Détail d'une conversation avec envoi de message"""
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related('participants'),
        pk=pk,
        participants=request.user
    )
    
    # Marquer les messages non lus comme lus
    unread_messages = conversation.messages.filter(
        is_read=False
    ).exclude(sender=request.user)
    
    for msg in unread_messages:
        msg.mark_as_read()
    
    # Récupérer les messages
    messages_list = conversation.messages.select_related('sender').order_by('created_at')
    
    # Traiter l'envoi d'un nouveau message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            # Créer le message
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Créer une notification pour l'autre participant
            other_participant = conversation.get_other_participant(request.user)
            if other_participant:
                Notification.objects.create(
                    recipient=other_participant,
                    notification_type='new_message',
                    title='Nouveau message',
                    message=f'{request.user.get_full_name()} vous a envoyé un message',
                    link=conversation.get_absolute_url()
                )
            
            return redirect('messaging:conversation', pk=pk)
    
    # Récupérer l'autre participant
    other_participant = conversation.get_other_participant(request.user)
    
    context = {
        'conversation': conversation,
        'conversation_messages': messages_list,
        'other_participant': other_participant,
    }
    return render(request, 'messaging/conversation.html', context)


@login_required
def start_conversation(request, username):
    """Démarrer une nouvelle conversation avec un utilisateur"""
    other_user = get_object_or_404(User, username=username)
    
    # Ne pas permettre de se parler à soi-même
    if other_user == request.user:
        django_messages.error(request, 'Vous ne pouvez pas vous envoyer un message à vous-même.')
        return redirect('messaging:inbox')
    
    # Vérifier si une conversation existe déjà entre ces deux utilisateurs
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()
    
    if existing_conversation:
        return redirect('messaging:conversation', pk=existing_conversation.pk)
    
    # Créer une nouvelle conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    return redirect('messaging:conversation', pk=conversation.pk)


@login_required
def start_conversation_about_project(request, project_slug):
    """Démarrer une conversation à propos d'un projet"""
    from projects.models import Project
    
    project = get_object_or_404(Project, slug=project_slug)
    project_owner = project.owner
    
    # Ne pas permettre au porteur de se contacter lui-même
    if project_owner == request.user:
        django_messages.error(request, 'Vous ne pouvez pas vous contacter vous-même.')
        return redirect('projects:detail', slug=project_slug)
    
    # Vérifier si une conversation existe déjà pour ce projet entre ces utilisateurs
    existing_conversation = Conversation.objects.filter(
        participants=request.user,
        project=project
    ).filter(
        participants=project_owner
    ).first()
    
    if existing_conversation:
        return redirect('messaging:conversation', pk=existing_conversation.pk)
    
    # Créer une nouvelle conversation liée au projet
    conversation = Conversation.objects.create(project=project)
    conversation.participants.add(request.user, project_owner)
    
    return redirect('messaging:conversation', pk=conversation.pk)


@login_required
def delete_conversation(request, pk):
    """Supprimer une conversation (retirer l'utilisateur)"""
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    
    if request.method == 'POST':
        # Retirer l'utilisateur de la conversation
        conversation.participants.remove(request.user)
        
        # Si plus aucun participant, supprimer la conversation
        if conversation.participants.count() == 0:
            conversation.delete()
        
        return redirect('messaging:inbox')
    
    return render(request, 'messaging/confirm_delete.html', {'conversation': conversation})


