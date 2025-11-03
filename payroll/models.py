from django.db import models
from django.utils import timezone
from master.models import Employee

class SalaryComponent(models.Model):
    COMPONENT_TYPES = [
        ('earning', 'Earning'),
        ('deduction', 'Deduction'),
    ]

    component_id = models.AutoField(primary_key=True)
    component_name = models.CharField(max_length=100, unique=True)
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    description = models.TextField(blank=True)
    is_taxable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.component_name} ({self.get_component_type_display()})"

class EmployeeSalary(models.Model):
    salary_id = models.AutoField(primary_key=True)
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    effective_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.employee.employee_code} - ₹{self.basic_salary}"

class SalaryComponentValue(models.Model):
    value_id = models.AutoField(primary_key=True)
    employee_salary = models.ForeignKey(EmployeeSalary, on_delete=models.CASCADE)
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_percentage = models.BooleanField(default=False)
    percentage_of_basic = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ['employee_salary', 'component']

    def __str__(self):
        return f"{self.employee_salary.employee.employee_code} - {self.component.component_name}: ₹{self.amount}"

class PayrollPeriod(models.Model):
    period_id = models.AutoField(primary_key=True)
    period_name = models.CharField(max_length=50, unique=True)  # e.g., "January 2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.period_name

class PayrollRun(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    run_id = models.AutoField(primary_key=True)
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)
    run_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_employees = models.IntegerField(default=0)
    total_gross_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_net_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    processed_by = models.ForeignKey('core.UserProfile', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.period.period_name} - {self.get_status_display()}"

class Payslip(models.Model):
    payslip_id = models.AutoField(primary_key=True)
    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    generated_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['payroll_run', 'employee']

    def __str__(self):
        return f"{self.employee.employee_code} - {self.payroll_run.period.period_name}"

class PayslipDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    payslip = models.ForeignKey(Payslip, on_delete=models.CASCADE)
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.payslip.employee.employee_code} - {self.component.component_name}: ₹{self.amount}"
