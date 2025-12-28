from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
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
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Auteur", 
        related_name='authored_blog_posts'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Catégorie", 
        related_name='blog_posts'
    )
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
        return reverse('blog:blog_detail', kwargs={'slug': self.slug})
    
    def get_tags_list(self):
        """Retourne la liste des tags"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def increment_views(self):
        """Incrémente le compteur de vues"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
