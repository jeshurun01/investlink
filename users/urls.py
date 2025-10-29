from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Inscription
    path('register/', views.register, name='register'),
    path('register/choice/', views.register_choice, name='register_choice'),
    path('register/porteur/', views.register_porteur, name='register_porteur'),
    path('register/investisseur/', views.register_investisseur, name='register_investisseur'),
    
    # Authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profil et dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Interface administrateur
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<int:user_id>/toggle-status/', views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin/users/<int:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/users/<int:user_id>/change-type/', views.admin_change_user_type, name='admin_change_user_type'),
]
