from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import (
    SalaryComponent, EmployeeSalary, SalaryComponentValue,
    PayrollPeriod, PayrollRun, Payslip, PayslipDetail
)
from master.models import Employee
from .forms import (
    SalaryComponentForm, EmployeeSalaryForm, SalaryComponentValueForm,
    PayrollPeriodForm, PayrollRunForm
)

@login_required
def payroll_dashboard(request):
    """Payroll dashboard view"""
    total_employees = Employee.objects.count()
    active_payroll_runs = PayrollRun.objects.filter(status__in=['draft', 'processing']).count()
    completed_runs = PayrollRun.objects.filter(status='completed').count()
    total_net_pay = Payslip.objects.aggregate(total=Sum('net_pay'))['total'] or 0

    context = {
        'user_role': 'Admin',
        'total_employees': total_employees,
        'active_payroll_runs': active_payroll_runs,
        'completed_runs': completed_runs,
        'total_net_pay': total_net_pay,
    }
    return render(request, 'payroll/dashboard.html', context)

@login_required
def salary_components(request):
    """Manage salary components"""
    components = SalaryComponent.objects.all()
    context = {
        'user_role': 'Admin',
        'components': components,
    }
    return render(request, 'payroll/salary_components.html', context)

@login_required
def employee_salaries(request):
    """Manage employee salaries"""
    salaries = EmployeeSalary.objects.select_related('employee').filter(is_active=True)
    context = {
        'user_role': 'Admin',
        'salaries': salaries,
    }
    return render(request, 'payroll/employee_salaries.html', context)

@login_required
def payroll_periods(request):
    """Manage payroll periods"""
    periods = PayrollPeriod.objects.all().order_by('-start_date')
    context = {
        'user_role': 'Admin',
        'periods': periods,
    }
    return render(request, 'payroll/payroll_periods.html', context)

@login_required
def payroll_runs(request):
    """Manage payroll runs"""
    runs = PayrollRun.objects.select_related('period').order_by('-run_date')
    context = {
        'user_role': 'Admin',
        'runs': runs,
    }
    return render(request, 'payroll/payroll_runs.html', context)

@login_required
def payslips(request):
    """View payslips"""
    payslips_list = Payslip.objects.select_related('payroll_run__period', 'employee').order_by('-generated_date')
    context = {
        'user_role': 'Admin',
        'payslips': payslips_list,
    }
    return render(request, 'payroll/payslips.html', context)

# Salary Components CRUD
@login_required
def add_salary_component(request):
    if request.method == 'POST':
        form = SalaryComponentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary component added successfully.')
            return redirect('salary_components')
    else:
        form = SalaryComponentForm()
    return render(request, 'payroll/add_salary_component.html', {'form': form, 'user_role': 'Admin'})

@login_required
def edit_salary_component(request, component_id):
    component = get_object_or_404(SalaryComponent, component_id=component_id)
    if request.method == 'POST':
        form = SalaryComponentForm(request.POST, instance=component)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary component updated successfully.')
            return redirect('salary_components')
    else:
        form = SalaryComponentForm(instance=component)
    return render(request, 'payroll/edit_salary_component.html', {'form': form, 'component': component, 'user_role': 'Admin'})

@login_required
@require_POST
def delete_salary_component(request, component_id):
    component = get_object_or_404(SalaryComponent, component_id=component_id)
    component.delete()
    messages.success(request, 'Salary component deleted successfully.')
    return redirect('salary_components')

# Employee Salaries CRUD
@login_required
def add_employee_salary(request):
    if request.method == 'POST':
        form = EmployeeSalaryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee salary added successfully.')
            return redirect('employee_salaries')
    else:
        form = EmployeeSalaryForm()
    return render(request, 'payroll/add_employee_salary.html', {'form': form, 'user_role': 'Admin'})

@login_required
def edit_employee_salary(request, salary_id):
    salary = get_object_or_404(EmployeeSalary, salary_id=salary_id)
    if request.method == 'POST':
        form = EmployeeSalaryForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee salary updated successfully.')
            return redirect('employee_salaries')
    else:
        form = EmployeeSalaryForm(instance=salary)
    return render(request, 'payroll/edit_employee_salary.html', {'form': form, 'salary': salary, 'user_role': 'Admin'})

@login_required
@require_POST
def delete_employee_salary(request, salary_id):
    salary = get_object_or_404(EmployeeSalary, salary_id=salary_id)
    salary.delete()
    messages.success(request, 'Employee salary deleted successfully.')
    return redirect('employee_salaries')

# Salary Component Values Management
@login_required
def manage_salary_components(request, salary_id):
    salary = get_object_or_404(EmployeeSalary, salary_id=salary_id)
    component_values = SalaryComponentValue.objects.filter(employee_salary=salary).select_related('component')

    # Calculate actual amounts for display
    for comp_val in component_values:
        if comp_val.is_percentage:
            comp_val.calculated_amount = (salary.basic_salary * comp_val.percentage_of_basic) / 100
        else:
            comp_val.calculated_amount = comp_val.amount

    if request.method == 'POST':
        form = SalaryComponentValueForm(request.POST)
        if form.is_valid():
            component_value = form.save(commit=False)
            component_value.employee_salary = salary
            component_value.save()
            messages.success(request, 'Salary component value added successfully.')
            return redirect('manage_salary_components', salary_id=salary_id)
    else:
        form = SalaryComponentValueForm()

    context = {
        'salary': salary,
        'component_values': component_values,
        'form': form,
        'user_role': 'Admin',
    }
    return render(request, 'payroll/manage_salary_components.html', context)

@login_required
@require_POST
def delete_salary_component_value(request, value_id):
    component_value = get_object_or_404(SalaryComponentValue, value_id=value_id)
    salary_id = component_value.employee_salary.salary_id
    component_value.delete()
    messages.success(request, 'Salary component value deleted successfully.')
    return redirect('manage_salary_components', salary_id=salary_id)

# Payroll Periods CRUD
@login_required
def add_payroll_period(request):
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll period added successfully.')
            return redirect('payroll_periods')
    else:
        form = PayrollPeriodForm()
    return render(request, 'payroll/add_payroll_period.html', {'form': form, 'user_role': 'Admin'})

@login_required
def edit_payroll_period(request, period_id):
    period = get_object_or_404(PayrollPeriod, period_id=period_id)
    if request.method == 'POST':
        form = PayrollPeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll period updated successfully.')
            return redirect('payroll_periods')
    else:
        form = PayrollPeriodForm(instance=period)
    return render(request, 'payroll/edit_payroll_period.html', {'form': form, 'period': period, 'user_role': 'Admin'})

@login_required
@require_POST
def delete_payroll_period(request, period_id):
    period = get_object_or_404(PayrollPeriod, period_id=period_id)
    period.delete()
    messages.success(request, 'Payroll period deleted successfully.')
    return redirect('payroll_periods')

@login_required
@require_POST
def close_payroll_period(request, period_id):
    period = get_object_or_404(PayrollPeriod, period_id=period_id)
    period.is_closed = True
    period.save()
    messages.success(request, 'Payroll period closed successfully.')
    return redirect('payroll_periods')

# Payroll Runs
@login_required
def create_payroll_run(request):
    if request.method == 'POST':
        form = PayrollRunForm(request.POST)
        if form.is_valid():
            payroll_run = form.save()
            messages.success(request, 'Payroll run created successfully.')
            return redirect('process_payroll_run', run_id=payroll_run.run_id)
    else:
        form = PayrollRunForm()
    return render(request, 'payroll/create_payroll_run.html', {'form': form, 'user_role': 'Admin'})

@login_required
def process_payroll_run(request, run_id):
    payroll_run = get_object_or_404(PayrollRun, run_id=run_id)
    if payroll_run.status != 'draft':
        messages.error(request, 'Payroll run is not in draft status.')
        return redirect('payroll_runs')

    # Get all active employee salaries
    employee_salaries = EmployeeSalary.objects.filter(is_active=True).select_related('employee')

    total_employees = 0
    total_gross_pay = 0
    total_deductions = 0
    total_net_pay = 0

    for emp_salary in employee_salaries:
        # Calculate earnings and deductions
        component_values = SalaryComponentValue.objects.filter(employee_salary=emp_salary).select_related('component')

        basic_salary = emp_salary.basic_salary
        total_earnings = basic_salary
        total_deductions_val = 0

        for comp_val in component_values:
            if comp_val.is_percentage:
                amount = (comp_val.percentage_of_basic / 100) * basic_salary
            else:
                amount = comp_val.amount

            if comp_val.component.component_type == 'earning':
                total_earnings += amount
            else:
                total_deductions_val += amount

        net_pay = total_earnings - total_deductions_val

        # Create payslip
        payslip = Payslip.objects.create(
            payroll_run=payroll_run,
            employee=emp_salary.employee,
            basic_salary=basic_salary,
            total_earnings=total_earnings,
            total_deductions=total_deductions_val,
            net_pay=net_pay
        )

        # Create payslip details
        for comp_val in component_values:
            if comp_val.is_percentage:
                amount = (comp_val.percentage_of_basic / 100) * basic_salary
            else:
                amount = comp_val.amount

            PayslipDetail.objects.create(
                payslip=payslip,
                component=comp_val.component,
                amount=amount
            )

        total_employees += 1
        total_gross_pay += total_earnings
        total_deductions += total_deductions_val
        total_net_pay += net_pay

    # Update payroll run
    payroll_run.status = 'completed'
    payroll_run.total_employees = total_employees
    payroll_run.total_gross_pay = total_gross_pay
    payroll_run.total_deductions = total_deductions
    payroll_run.total_net_pay = total_net_pay
    payroll_run.save()

    messages.success(request, f'Payroll run processed successfully for {total_employees} employees.')
    return redirect('payroll_runs')

@login_required
def view_payslip(request, payslip_id):
    payslip = get_object_or_404(Payslip, payslip_id=payslip_id)
    details = PayslipDetail.objects.filter(payslip=payslip).select_related('component')
    context = {
        'payslip': payslip,
        'details': details,
        'user_role': 'Admin',
    }
    return render(request, 'payroll/view_payslip.html', context)
