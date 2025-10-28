from django.db import models
from django.conf import settings
from django.urls import reverse


class Conversation(models.Model):
    """Conversation entre deux utilisateurs"""
    
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations',
        verbose_name='Participants'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations',
        verbose_name='Projet concerné'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créée le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Dernière activité')
    
    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']
    
    def __str__(self):
        participants_names = ', '.join([user.username for user in self.participants.all()])
        return f"Conversation: {participants_names}"
    
    def get_absolute_url(self):
        return reverse('messaging:conversation', kwargs={'pk': self.pk})
    
    def get_other_participant(self, current_user):
        """Retourne l'autre participant de la conversation"""
        return self.participants.exclude(pk=current_user.pk).first()


class Message(models.Model):
    """Message dans une conversation"""
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Conversation'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Expéditeur'
    )
    content = models.TextField(verbose_name='Contenu')
    is_read = models.BooleanField(default=False, verbose_name='Lu')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Envoyé le')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Lu le')
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    def mark_as_read(self):
        """Marquer le message comme lu"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

