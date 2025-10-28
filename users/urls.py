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
]
