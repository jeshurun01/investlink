from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import BlogPost, BlogCategory, ActivityLog


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """Administration des catégories de blog"""
    list_display = ['name', 'slug', 'post_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        """Display the number of posts in this category"""
        return obj.posts.count()
    post_count.short_description = 'Nombre d\'articles'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Administration des articles de blog"""
    list_display = ['title', 'author', 'category', 'status', 'views_count', 'published_at', 'image_preview', 'created_at']
    list_filter = ['status', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'excerpt', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ['-created_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Contenu', {
            'fields': ('featured_image', 'image_preview_large', 'excerpt', 'content', 'tags')
        }),
        ('Dates', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'image_preview_large']
    
    def save_model(self, request, obj, form, change):
        """Définit l'auteur automatiquement lors de la création"""
        if not change:  # Si c'est une nouvelle création
            obj.author = request.user
        
        # Auto-set published_at when status changes to published
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()
        
        super().save_model(request, obj, form, change)
    
    def image_preview(self, obj):
        """Display small thumbnail in list view"""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.featured_image.url
            )
        return "Pas d'image"
    image_preview.short_description = 'Image'
    
    def image_preview_large(self, obj):
        """Display larger image in detail view"""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-width: 500px; max-height: 400px; object-fit: contain; border-radius: 8px;" />',
                obj.featured_image.url
            )
        return "Pas d'image téléchargée"
    image_preview_large.short_description = 'Aperçu de l\'image'
    
    # Bulk actions
    actions = ['make_published', 'make_draft']
    
    def make_published(self, request, queryset):
        """Mark selected posts as published"""
        updated = 0
        for post in queryset:
            if not post.published_at:
                post.published_at = timezone.now()
            post.status = 'published'
            post.save()
            updated += 1
        self.message_user(request, f'{updated} article(s) publié(s) avec succès.')
    make_published.short_description = 'Publier les articles sélectionnés'
    
    def make_draft(self, request, queryset):
        """Mark selected posts as draft"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} article(s) mis en brouillon.')
    make_draft.short_description = 'Mettre en brouillon les articles sélectionnés'


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Administration des logs d'activité"""
    list_display = ['created_at', 'user', 'action', 'entity_type', 'entity_name', 'ip_address']
    list_filter = ['action', 'entity_type', 'created_at']
    search_fields = ['user__email', 'entity_name', 'description', 'ip_address']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['user', 'action', 'entity_type', 'entity_id', 'entity_name', 
                      'description', 'ip_address', 'user_agent', 'created_at']
    
    def has_add_permission(self, request):
        """Empêcher la création manuelle de logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Empêcher la modification de logs"""
        return False
