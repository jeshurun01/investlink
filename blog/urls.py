from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Public blog pages
    path('', views.blog, name='blog'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Admin - Gestion du contenu (note: these will be accessed as /blog/content/...)
    path('admin/dashboard/', views.admin_content_dashboard, name='admin_content_dashboard'),
    path('admin/posts/', views.admin_blog_posts, name='admin_blog_posts'),
    path('admin/post/create/', views.admin_blog_post_create, name='admin_blog_post_create'),
    path('admin/post/<int:post_id>/edit/', views.admin_blog_post_edit, name='admin_blog_post_edit'),
    path('admin/post/<int:post_id>/delete/', views.admin_blog_post_delete, name='admin_blog_post_delete'),
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/category/create/', views.admin_category_create, name='admin_category_create'),
    path('admin/category/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin/category/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
]
