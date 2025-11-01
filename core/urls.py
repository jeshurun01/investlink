from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('legal/', views.legal, name='legal'),
    
    # Admin - Gestion du contenu
    path('content/dashboard/', views.admin_content_dashboard, name='admin_content_dashboard'),
    path('content/blog/posts/', views.admin_blog_posts, name='admin_blog_posts'),
    path('content/blog/post/create/', views.admin_blog_post_create, name='admin_blog_post_create'),
    path('content/blog/post/<int:post_id>/edit/', views.admin_blog_post_edit, name='admin_blog_post_edit'),
    path('content/blog/post/<int:post_id>/delete/', views.admin_blog_post_delete, name='admin_blog_post_delete'),
    path('content/blog/categories/', views.admin_categories, name='admin_categories'),
    path('content/blog/category/create/', views.admin_category_create, name='admin_category_create'),
    path('content/blog/category/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('content/blog/category/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # Admin - Logs
    path('content/logs/', views.admin_activity_logs, name='admin_activity_logs'),
    
    # Admin - Messages de contact
    path('content/messages/', views.admin_contact_messages, name='admin_contact_messages'),
    path('content/messages/<int:message_id>/', views.admin_contact_message_detail, name='admin_contact_message_detail'),
]
