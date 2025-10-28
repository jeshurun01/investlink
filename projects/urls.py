from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='list'),
    path('submit/', views.submit_project, name='submit'),
    path('my-projects/', views.my_projects, name='my_projects'),
    path('<slug:slug>/', views.project_detail, name='detail'),
    path('<slug:slug>/edit/', views.edit_project, name='edit'),
    path('<slug:slug>/delete/', views.delete_project, name='delete'),
]

