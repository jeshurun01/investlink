from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('mark-read/<int:pk>/', views.mark_as_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('delete/<int:pk>/', views.delete_notification, name='delete'),
    path('delete-all-read/', views.delete_all_read, name='delete_all_read'),
    path('api/dropdown/', views.notifications_dropdown, name='dropdown_api'),
]
