from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectDocument, ProjectFavorite


class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'sector', 'status_badge', 'funding_goal', 'created_at']
    list_filter = ['status', 'sector', 'funding_stage', 'created_at']
    search_fields = ['title', 'description', 'owner__username', 'owner__email']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    raw_id_fields = ['owner']
    inlines = [ProjectDocumentInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('owner', 'title', 'slug', 'summary', 'description')
        }),
        ('Détails du projet', {
            'fields': ('sector', 'funding_stage', 'location')
        }),
        ('Financement', {
            'fields': ('funding_goal', 'current_funding', 'min_investment')
        }),
        ('Médias', {
            'fields': ('featured_image', 'video_url')
        }),
        ('Validation', {
            'fields': ('status', 'admin_notes', 'rejection_reason', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('views_count', 'favorites_count'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'submitted': 'orange',
            'under_review': 'blue',
            'revision_requested': 'purple',
            'approved': 'green',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    actions = ['approve_projects', 'reject_projects', 'request_revision']
    
    def approve_projects(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(status='approved', published_at=timezone.now())
        self.message_user(request, f'{count} projet(s) validé(s).')
    approve_projects.short_description = 'Valider les projets sélectionnés'
    
    def reject_projects(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} projet(s) refusé(s).')
    reject_projects.short_description = 'Refuser les projets sélectionnés'
    
    def request_revision(self, request, queryset):
        count = queryset.update(status='revision_requested')
        self.message_user(request, f'{count} projet(s) en révision.')
    request_revision.short_description = 'Demander une révision'


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'project__title']
    raw_id_fields = ['project']


@admin.register(ProjectFavorite)
class ProjectFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'project__title']
    raw_id_fields = ['user', 'project']

