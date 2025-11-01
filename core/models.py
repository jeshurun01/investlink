from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

User = get_user_model()


class BlogCategory(models.Model):
    """Catégorie d'article de blog"""
    name = models.CharField("Nom", max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField("Description", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Article de blog"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    ]
    
    title = models.CharField("Titre", max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur", related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, 
                                  verbose_name="Catégorie", related_name='posts')
    featured_image = models.ImageField("Image à la une", upload_to='blog/', blank=True, null=True)
    excerpt = models.TextField("Extrait", max_length=300, help_text="Résumé court de l'article")
    content = models.TextField("Contenu")
    status = models.CharField("Statut", max_length=10, choices=STATUS_CHOICES, default='draft')
    
    views_count = models.PositiveIntegerField("Nombre de vues", default=0)
    
    created_at = models.DateTimeField("Date de création", auto_now_add=True)
    updated_at = models.DateTimeField("Date de mise à jour", auto_now=True)
    published_at = models.DateTimeField("Date de publication", null=True, blank=True)
    
    tags = models.CharField("Tags", max_length=200, blank=True, 
                           help_text="Séparez les tags par des virgules")
    
    meta_description = models.CharField("Meta description", max_length=160, blank=True,
                                       help_text="Pour le référencement SEO")
    
    class Meta:
        verbose_name = "Article de blog"
        verbose_name_plural = "Articles de blog"
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('core:blog_detail', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        """Retourne la liste des tags"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def increment_views(self):
        """Incrémente le compteur de vues"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ActivityLog(models.Model):
    """Journal des activités pour traçabilité"""
    ACTION_CHOICES = [
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('validate', 'Validation'),
        ('reject', 'Rejet'),
        ('publish', 'Publication'),
        ('view', 'Consultation'),
    ]
    
    ENTITY_CHOICES = [
        ('user', 'Utilisateur'),
        ('project', 'Projet'),
        ('investment', 'Investissement'),
        ('blog_post', 'Article de blog'),
        ('blog_category', 'Catégorie'),
        ('message', 'Message'),
        ('notification', 'Notification'),
        ('document', 'Document'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                            verbose_name="Utilisateur", related_name='activity_logs')
    action = models.CharField("Action", max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField("Type d'entité", max_length=20, choices=ENTITY_CHOICES)
    entity_id = models.PositiveIntegerField("ID de l'entité", null=True, blank=True)
    entity_name = models.CharField("Nom de l'entité", max_length=200, blank=True)
    
    description = models.TextField("Description", blank=True)
    ip_address = models.GenericIPAddressField("Adresse IP", null=True, blank=True)
    user_agent = models.CharField("User Agent", max_length=255, blank=True)
    
    created_at = models.DateTimeField("Date et heure", auto_now_add=True)
    
    class Meta:
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journal des activités"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['entity_type', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.get_entity_type_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def log(cls, user, action, entity_type, entity_id=None, entity_name='', 
            description='', request=None):
        """
        Méthode helper pour créer un log facilement
        
        Usage:
        ActivityLog.log(request.user, 'create', 'project', project.id, project.title, 
                       'Création d\'un nouveau projet', request)
        """
        log_data = {
            'user': user if user and user.is_authenticated else None,
            'action': action,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'entity_name': entity_name,
            'description': description,
        }
        
        if request:
            # Récupération de l'IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                log_data['ip_address'] = x_forwarded_for.split(',')[0].strip()
            else:
                log_data['ip_address'] = request.META.get('REMOTE_ADDR')
            
            # User Agent
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:255]
        
        return cls.objects.create(**log_data)


class ContactMessage(models.Model):
    """Messages reçus via le formulaire de contact"""
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('read', 'Lu'),
        ('in_progress', 'En cours'),
        ('resolved', 'Résolu'),
        ('archived', 'Archivé'),
    ]
    
    name = models.CharField("Nom complet", max_length=200)
    email = models.EmailField("Email")
    phone = models.CharField("Téléphone", max_length=20, blank=True)
    subject = models.CharField("Sujet", max_length=200)
    message = models.TextField("Message")
    
    status = models.CharField("Statut", max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField("Notes administrateur", blank=True)
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                            verbose_name="Utilisateur", related_name='contact_messages',
                            help_text="Si le message provient d'un utilisateur connecté")
    
    created_at = models.DateTimeField("Date d'envoi", auto_now_add=True)
    read_at = models.DateTimeField("Date de lecture", null=True, blank=True)
    resolved_at = models.DateTimeField("Date de résolution", null=True, blank=True)
    
    ip_address = models.GenericIPAddressField("Adresse IP", null=True, blank=True)
    
    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%d/%m/%Y')})"
    
    def mark_as_read(self):
        """Marquer le message comme lu"""
        from django.utils import timezone
        if self.status == 'new':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])
