from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    """Modèle utilisateur personnalisé avec types de profils"""
    
    USER_TYPE_CHOICES = (
        ('porteur', 'Porteur de projet'),
        ('investisseur', 'Investisseur'),
        ('admin', 'Administrateur'),
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='porteur',
        verbose_name='Type d\'utilisateur'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    avatar = models.ImageField(
        upload_to='profiles/avatars/',
        blank=True,
        null=True,
        verbose_name='Photo de profil'
    )
    bio = models.TextField(blank=True, verbose_name='Biographie')
    email_verified = models.BooleanField(default=False, verbose_name='Email vérifié')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'inscription')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Dernière modification')
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
    
    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'pk': self.pk})
    
    def can_access_porteur_features(self):
        """Vérifie si l'utilisateur peut accéder aux fonctionnalités porteur"""
        return self.user_type in ['porteur', 'admin'] or self.is_staff
    
    def can_access_investisseur_features(self):
        """Vérifie si l'utilisateur peut accéder aux fonctionnalités investisseur"""
        return self.user_type in ['investisseur', 'admin'] or self.is_staff
    
    def is_admin_user(self):
        """Vérifie si l'utilisateur est admin"""
        return self.user_type == 'admin' or self.is_staff or self.is_superuser


class ProjectOwnerProfile(models.Model):
    """Profil spécifique aux porteurs de projets"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='porteur_profile',
        verbose_name='Utilisateur'
    )
    company_name = models.CharField(max_length=200, blank=True, verbose_name='Nom de l\'entreprise')
    company_registration = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Numéro d\'enregistrement'
    )
    website = models.URLField(blank=True, verbose_name='Site web')
    linkedin = models.URLField(blank=True, verbose_name='LinkedIn')
    experience = models.TextField(blank=True, verbose_name='Expérience')
    achievements = models.TextField(blank=True, verbose_name='Réalisations')
    
    class Meta:
        verbose_name = 'Profil Porteur de projet'
        verbose_name_plural = 'Profils Porteurs de projets'
    
    def __str__(self):
        return f"Profil porteur - {self.user.get_full_name()}"


class InvestorProfile(models.Model):
    """Profil spécifique aux investisseurs"""
    
    INVESTMENT_RANGE_CHOICES = (
        ('0-10k', '0 - 10 000 $'),
        ('10k-50k', '10 000 - 50 000 $'),
        ('50k-100k', '50 000 - 100 000 $'),
        ('100k-500k', '100 000 - 500 000 $'),
        ('500k+', '500 000 $ et plus'),
    )
    
    RISK_LEVEL_CHOICES = (
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='investisseur_profile',
        verbose_name='Utilisateur'
    )
    investment_range = models.CharField(
        max_length=20,
        choices=INVESTMENT_RANGE_CHOICES,
        blank=True,
        verbose_name='Fourchette d\'investissement'
    )
    preferred_sectors = models.TextField(blank=True, verbose_name='Secteurs préférés')
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVEL_CHOICES,
        default='medium',
        verbose_name='Niveau de risque accepté'
    )
    location_preference = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Préférence de localisation'
    )
    investment_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Nombre d\'investissements réalisés'
    )
    
    class Meta:
        verbose_name = 'Profil Investisseur'
        verbose_name_plural = 'Profils Investisseurs'
    
    def __str__(self):
        return f"Profil investisseur - {self.user.get_full_name()}"

