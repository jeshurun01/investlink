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
    path('admin/content/', views.admin_content_dashboard, name='admin_content_dashboard'),
    path('admin/blog/posts/', views.admin_blog_posts, name='admin_blog_posts'),
    path('admin/blog/post/create/', views.admin_blog_post_create, name='admin_blog_post_create'),
    path('admin/blog/post/<int:post_id>/edit/', views.admin_blog_post_edit, name='admin_blog_post_edit'),
    path('admin/blog/post/<int:post_id>/delete/', views.admin_blog_post_delete, name='admin_blog_post_delete'),
    path('admin/blog/categories/', views.admin_categories, name='admin_categories'),
    path('admin/blog/category/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/blog/category/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/blog/category/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # Admin - Logs
    path('admin/logs/', views.admin_activity_logs, name='admin_activity_logs'),
]
