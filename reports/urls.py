from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_view, name='reports'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('print/', views.print_report, name='print_report'),
]