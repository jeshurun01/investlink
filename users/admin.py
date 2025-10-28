from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ProjectOwnerProfile, InvestorProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'email_verified', 'is_staff']
    list_filter = ['user_type', 'email_verified', 'is_staff', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('user_type', 'phone', 'avatar', 'bio', 'email_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('user_type', 'email', 'phone')
        }),
    )


@admin.register(ProjectOwnerProfile)
class ProjectOwnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'website']
    search_fields = ['user__username', 'company_name', 'company_registration']
    raw_id_fields = ['user']


@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'investment_range', 'risk_level', 'investment_count']
    list_filter = ['investment_range', 'risk_level']
    search_fields = ['user__username', 'preferred_sectors']
    raw_id_fields = ['user']

