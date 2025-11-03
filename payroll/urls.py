from django.urls import path
from . import views

urlpatterns = [
    path('', views.payroll_dashboard, name='payroll_dashboard'),
    path('salary-components/', views.salary_components, name='salary_components'),
    path('salary-components/add/', views.add_salary_component, name='add_salary_component'),
    path('salary-components/<int:component_id>/edit/', views.edit_salary_component, name='edit_salary_component'),
    path('salary-components/<int:component_id>/delete/', views.delete_salary_component, name='delete_salary_component'),
    path('employee-salaries/', views.employee_salaries, name='employee_salaries'),
    path('employee-salaries/add/', views.add_employee_salary, name='add_employee_salary'),
    path('employee-salaries/<int:salary_id>/edit/', views.edit_employee_salary, name='edit_employee_salary'),
    path('employee-salaries/<int:salary_id>/delete/', views.delete_employee_salary, name='delete_employee_salary'),
    path('employee-salaries/<int:salary_id>/components/', views.manage_salary_components, name='manage_salary_components'),
    path('component-values/<int:value_id>/delete/', views.delete_salary_component_value, name='delete_salary_component_value'),
    path('payroll-periods/', views.payroll_periods, name='payroll_periods'),
    path('payroll-periods/add/', views.add_payroll_period, name='add_payroll_period'),
    path('payroll-periods/<int:period_id>/edit/', views.edit_payroll_period, name='edit_payroll_period'),
    path('payroll-periods/<int:period_id>/delete/', views.delete_payroll_period, name='delete_payroll_period'),
    path('payroll-periods/<int:period_id>/close/', views.close_payroll_period, name='close_payroll_period'),
    path('payroll-runs/', views.payroll_runs, name='payroll_runs'),
    path('payroll-runs/create/', views.create_payroll_run, name='create_payroll_run'),
    path('payroll-runs/<int:run_id>/process/', views.process_payroll_run, name='process_payroll_run'),
    path('payslips/', views.payslips, name='payslips'),
    path('payslips/<int:payslip_id>/view/', views.view_payslip, name='view_payslip'),
]