from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    raw_id_fields = ['recipient']
    readonly_fields = ['created_at', 'read_at']
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f'{count} notification(s) marquée(s) comme lue(s).')
    mark_as_read.short_description = 'Marquer comme lues'
    
    def mark_as_unread(self, request, queryset):
        count = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{count} notification(s) marquée(s) comme non lue(s).')
    mark_as_unread.short_description = 'Marquer comme non lues'

