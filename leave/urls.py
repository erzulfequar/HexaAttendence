from django.urls import path
from . import views

urlpatterns = [
    path('', views.leave_view, name='leave'),
    path('apply/', views.apply_leave_view, name='apply_leave'),
]