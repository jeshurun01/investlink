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
    path('content/messages/', views.admin_contact_messages, name='admin_contact_messages'),
    path('content/messages/<int:message_id>/', views.admin_contact_message_detail, name='admin_contact_message_detail'),
]
