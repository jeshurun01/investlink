from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('legal/', views.legal, name='legal'),
    
    # Admin - Logs
    path('content/logs/', views.admin_activity_logs, name='admin_activity_logs'),
    
    # Admin - Messages de contact
    path('contact/message/<int:message_id>/', views.contact_message_detail, name='contact_message_detail'),
    path('contact/message/<int:message_id>/update-status/', views.contact_message_update_status, name='contact_message_update_status'),
]
