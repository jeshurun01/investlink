from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Pages publiques
    path('', views.project_list, name='list'),
    path('submit/', views.submit_project, name='submit'),
    path('my-projects/', views.my_projects, name='my_projects'),
    
    # Favoris
    path('favorites/', views.my_favorites, name='my_favorites'),
    path('favorites/<int:project_id>/toggle/', views.toggle_favorite, name='toggle_favorite'),
    
    # Investissements
    path('investments/', views.my_investments, name='my_investments'),
    path('investments/<int:project_id>/declare/', views.declare_investment, name='declare_investment'),
    path('financial-dashboard/', views.financial_dashboard, name='financial_dashboard'),
    
    # Administration - Validation des projets
    path('admin/pending/', views.admin_pending_projects, name='admin_pending'),
    path('admin/all/', views.admin_all_projects, name='admin_all'),
    path('admin/<slug:slug>/validate/', views.admin_validate_project, name='admin_validate'),
    
    # Détails et édition (doivent être en dernier pour éviter les conflits)
    path('<slug:slug>/', views.project_detail, name='detail'),
    path('<slug:slug>/edit/', views.edit_project, name='edit'),
    path('<slug:slug>/delete/', views.delete_project, name='delete'),
]


