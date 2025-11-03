from django import forms
from .models import SalaryComponent, EmployeeSalary, SalaryComponentValue, PayrollPeriod, PayrollRun

class SalaryComponentForm(forms.ModelForm):
    class Meta:
        model = SalaryComponent
        fields = ['component_name', 'component_type', 'description', 'is_taxable', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class EmployeeSalaryForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields = ['employee', 'basic_salary', 'effective_date']
        widgets = {
            'effective_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SalaryComponentValueForm(forms.ModelForm):
    class Meta:
        model = SalaryComponentValue
        fields = ['component', 'amount', 'is_percentage', 'percentage_of_basic']

class PayrollPeriodForm(forms.ModelForm):
    class Meta:
        model = PayrollPeriod
        fields = ['period_name', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PayrollRunForm(forms.ModelForm):
    class Meta:
        model = PayrollRun
        fields = ['period']