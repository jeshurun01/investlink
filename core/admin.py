from django.contrib import admin
from .models import BlogPost, BlogCategory, ActivityLog


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """Administration des catégories de blog"""
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Administration des articles de blog"""
    list_display = ['title', 'author', 'category', 'status', 'views_count', 'published_at', 'created_at']
    list_filter = ['status', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'excerpt', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Contenu', {
            'fields': ('featured_image', 'excerpt', 'content', 'tags')
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
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['views_count']
    
    def save_model(self, request, obj, form, change):
        """Définit l'auteur automatiquement lors de la création"""
        if not change:  # Si c'est une nouvelle création
            obj.author = request.user
        super().save_model(request, obj, form, change)


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
