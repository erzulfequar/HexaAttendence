from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_view, name='attendance'),
    path('mark/', views.mark_attendance_view, name='mark_attendance'),
    path('submit/', views.submit_attendance, name='submit_attendance'),
]