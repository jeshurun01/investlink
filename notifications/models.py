from django.db import models
from django.conf import settings
from django.urls import reverse


class Notification(models.Model):
    """Notifications pour les utilisateurs"""
    
    NOTIFICATION_TYPES = (
        ('project_submitted', 'Projet soumis'),
        ('project_approved', 'Projet validé'),
        ('project_rejected', 'Projet refusé'),
        ('project_revision', 'Révision demandée'),
        ('new_message', 'Nouveau message'),
        ('project_favorite', 'Projet ajouté aux favoris'),
        ('profile_update', 'Mise à jour du profil'),
        ('system', 'Notification système'),
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinataire'
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        verbose_name='Type de notification'
    )
    title = models.CharField(max_length=200, verbose_name='Titre')
    message = models.TextField(verbose_name='Message')
    link = models.CharField(max_length=500, blank=True, verbose_name='Lien')
    is_read = models.BooleanField(default=False, verbose_name='Lue')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créée le')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Lue le')
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Marquer la notification comme lue"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, link=''):
        """Créer une nouvelle notification"""
        notification = cls.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link
        )
        return notification

