from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal


class Project(models.Model):
    """Modèle pour les projets soumis par les porteurs"""
    
    STATUS_CHOICES = (
        ('submitted', 'Soumis'),
        ('under_review', 'En cours d\'examen'),
        ('revision_requested', 'Révision demandée'),
        ('approved', 'Validé'),
        ('rejected', 'Refusé'),
    )
    
    SECTOR_CHOICES = (
        ('tech', 'Technologies'),
        ('health', 'Santé'),
        ('education', 'Éducation'),
        ('agriculture', 'Agriculture'),
        ('energy', 'Énergie'),
        ('finance', 'Finance'),
        ('real_estate', 'Immobilier'),
        ('commerce', 'Commerce'),
        ('industry', 'Industrie'),
        ('services', 'Services'),
        ('other', 'Autre'),
    )
    
    FUNDING_STAGE_CHOICES = (
        ('idea', 'Idée'),
        ('prototype', 'Prototype'),
        ('mvp', 'MVP'),
        ('early', 'Phase initiale'),
        ('growth', 'Croissance'),
        ('expansion', 'Expansion'),
    )
    
    # Informations de base
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='Porteur du projet'
    )
    title = models.CharField(max_length=200, verbose_name='Titre du projet')
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    
    # Description
    summary = models.TextField(max_length=500, verbose_name='Résumé court')
    description = models.TextField(verbose_name='Description détaillée')
    
    # Détails du projet
    sector = models.CharField(
        max_length=50,
        choices=SECTOR_CHOICES,
        verbose_name='Secteur d\'activité'
    )
    funding_stage = models.CharField(
        max_length=20,
        choices=FUNDING_STAGE_CHOICES,
        verbose_name='Stade de financement'
    )
    location = models.CharField(max_length=200, verbose_name='Localisation')
    
    # Financement
    funding_goal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Montant recherché ($)'
    )
    current_funding = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Financement actuel ($)'
    )
    min_investment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Investissement minimum ($)'
    )
    
    # Médias
    featured_image = models.ImageField(
        upload_to='projects/images/',
        blank=True,
        null=True,
        verbose_name='Image principale'
    )
    video_url = models.URLField(blank=True, verbose_name='Lien vidéo')
    
    # Workflow de validation
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted',
        verbose_name='Statut'
    )
    admin_notes = models.TextField(blank=True, verbose_name='Notes de l\'administrateur')
    rejection_reason = models.TextField(blank=True, verbose_name='Motif de refus')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Dernière modification')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='Date de publication')
    
    # Métriques
    views_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    favorites_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de favoris')
    
    class Meta:
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['sector']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'slug': self.slug})
    
    @property
    def funding_percentage(self):
        """Pourcentage du financement atteint"""
        if self.funding_goal > 0:
            return (self.current_funding / self.funding_goal) * 100
        return 0
    
    @property
    def is_approved(self):
        """Vérifie si le projet est validé"""
        return self.status == 'approved'


class ProjectDocument(models.Model):
    """Documents attachés à un projet (business plan, etc.)"""
    
    DOCUMENT_TYPE_CHOICES = (
        ('business_plan', 'Business Plan'),
        ('financial', 'Document financier'),
        ('legal', 'Document juridique'),
        ('presentation', 'Présentation'),
        ('other', 'Autre'),
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Projet'
    )
    title = models.CharField(max_length=200, verbose_name='Titre du document')
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Type de document'
    )
    file = models.FileField(upload_to='projects/documents/', verbose_name='Fichier')
    description = models.TextField(blank=True, verbose_name='Description')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'upload')
    
    class Meta:
        verbose_name = 'Document de projet'
        verbose_name_plural = 'Documents de projets'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"


class ProjectFavorite(models.Model):
    """Projets favoris des investisseurs"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_projects',
        verbose_name='Utilisateur'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Projet'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ajouté le')
    
    class Meta:
        verbose_name = 'Projet favori'
        verbose_name_plural = 'Projets favoris'
        unique_together = ['user', 'project']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.title}"


class Investment(models.Model):
    """Investissements réalisés dans les projets"""
    
    STATUS_CHOICES = (
        ('pending', 'En attente de validation'),
        ('confirmed', 'Confirmé'),
        ('rejected', 'Rejeté'),
    )
    
    investor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='investments',
        verbose_name='Investisseur'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='investments',
        verbose_name='Projet'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Montant investi ($)'
    )
    current_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valeur actuelle ($)',
        help_text='Valeur actuelle de l\'investissement (mise à jour périodiquement)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Statut'
    )
    investment_date = models.DateField(verbose_name='Date d\'investissement')
    
    # Informations additionnelles
    notes = models.TextField(blank=True, verbose_name='Notes')
    admin_notes = models.TextField(blank=True, verbose_name='Notes administrateur')
    
    # Dates de suivi
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de déclaration')
    validated_at = models.DateTimeField(null=True, blank=True, verbose_name='Date de validation')
    
    class Meta:
        verbose_name = 'Investissement'
        verbose_name_plural = 'Investissements'
        ordering = ['-investment_date']
        indexes = [
            models.Index(fields=['-investment_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.investor.username} - {self.project.title} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        """Initialiser current_value avec amount si non défini"""
        if not self.current_value or self.current_value == 0:
            self.current_value = self.amount
        super().save(*args, **kwargs)
    
    def update_current_value(self):
        """Mettre à jour la valeur actuelle basée sur les dernières performances"""
        latest_performance = self.project.performances.order_by('-report_date').first()
        if latest_performance and latest_performance.roi_percentage is not None:
            self.current_value = self.amount * (Decimal('1') + latest_performance.roi_percentage / Decimal('100'))
            self.save(update_fields=['current_value'])
    
    @property
    def roi_amount(self):
        """Montant du retour sur investissement"""
        return self.current_value - self.amount
    
    @property
    def roi_percentage(self):
        """Pourcentage du retour sur investissement"""
        if self.amount > 0:
            return (self.roi_amount / self.amount) * 100
        return Decimal('0')


class ProjectPerformance(models.Model):
    """Performances mensuelles des projets"""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='performances',
        verbose_name='Projet'
    )
    report_date = models.DateField(verbose_name='Date du rapport')
    
    # Métriques financières
    revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Chiffre d\'affaires ($)'
    )
    profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Bénéfice ($)'
    )
    roi_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='ROI (%)',
        help_text='Retour sur investissement en pourcentage'
    )
    
    # Métriques d'activité
    active_users = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Utilisateurs actifs'
    )
    growth_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Taux de croissance (%)'
    )
    
    # Informations qualitatives
    summary = models.TextField(blank=True, verbose_name='Résumé des performances')
    challenges = models.TextField(blank=True, verbose_name='Défis rencontrés')
    next_objectives = models.TextField(blank=True, verbose_name='Prochains objectifs')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Dernière mise à jour')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performance_reports',
        verbose_name='Créé par'
    )
    
    class Meta:
        verbose_name = 'Performance de projet'
        verbose_name_plural = 'Performances de projets'
        ordering = ['-report_date']
        unique_together = ['project', 'report_date']
        indexes = [
            models.Index(fields=['-report_date']),
            models.Index(fields=['project', '-report_date']),
        ]
    
    def __str__(self):
        return f"{self.project.title} - {self.report_date.strftime('%B %Y')}"
