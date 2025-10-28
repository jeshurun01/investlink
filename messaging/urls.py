from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation'),
    path('start/<str:username>/', views.start_conversation, name='start_conversation'),
    path('start-project/<slug:project_slug>/', views.start_conversation_about_project, name='start_project_conversation'),
    path('delete/<int:pk>/', views.delete_conversation, name='delete_conversation'),
]
