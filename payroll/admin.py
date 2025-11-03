from django.contrib import admin
from .models import (
    SalaryComponent, EmployeeSalary, SalaryComponentValue,
    PayrollPeriod, PayrollRun, Payslip, PayslipDetail
)

@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ['component_id', 'component_name', 'component_type', 'is_taxable', 'is_active']
    list_filter = ['component_type', 'is_taxable', 'is_active']
    search_fields = ['component_name', 'description']

@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ['salary_id', 'employee', 'basic_salary', 'effective_date', 'is_active']
    list_filter = ['is_active', 'effective_date']
    search_fields = ['employee__employee_code', 'employee__first_name', 'employee__last_name']
    raw_id_fields = ['employee']

@admin.register(SalaryComponentValue)
class SalaryComponentValueAdmin(admin.ModelAdmin):
    list_display = ['value_id', 'employee_salary', 'component', 'amount', 'is_percentage']
    list_filter = ['component__component_type', 'is_percentage']
    search_fields = ['employee_salary__employee__employee_code', 'component__component_name']
    raw_id_fields = ['employee_salary', 'component']

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['period_id', 'period_name', 'start_date', 'end_date', 'is_closed']
    list_filter = ['is_closed']
    search_fields = ['period_name']

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ['run_id', 'period', 'run_date', 'status', 'total_employees', 'total_net_pay']
    list_filter = ['status', 'run_date']
    search_fields = ['period__period_name']
    readonly_fields = ['run_date']

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['payslip_id', 'payroll_run', 'employee', 'net_pay', 'generated_date']
    list_filter = ['generated_date']
    search_fields = ['employee__employee_code', 'employee__first_name', 'employee__last_name']
    raw_id_fields = ['payroll_run', 'employee']
    readonly_fields = ['generated_date']

@admin.register(PayslipDetail)
class PayslipDetailAdmin(admin.ModelAdmin):
    list_display = ['detail_id', 'payslip', 'component', 'amount']
    list_filter = ['component__component_type']
    search_fields = ['payslip__employee__employee_code', 'component__component_name']
    raw_id_fields = ['payslip', 'component']
