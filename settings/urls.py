from django.urls import path
from . import views

urlpatterns = [
    path('', views.settings_view, name='settings'),
    path('company-profile/edit/', views.edit_company_profile, name='edit_company_profile'),
    path('attendance-rules/add/', views.add_attendance_rule, name='add_attendance_rule'),
    path('attendance-rules/<int:rule_id>/edit/', views.edit_attendance_rule, name='edit_attendance_rule'),
    path('attendance-rules/<int:rule_id>/delete/', views.delete_attendance_rule, name='delete_attendance_rule'),
    path('work-week/edit/', views.edit_work_week, name='edit_work_week'),
    path('work-week/<int:day_id>/update/', views.update_work_week_day, name='update_work_week_day'),
]