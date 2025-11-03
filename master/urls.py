from django.urls import path
from . import views

urlpatterns = [
    path('', views.master_view, name='master'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/update-status/', views.update_task_status, name='update_task_status'),
]