from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_type', 'task_description', 'allotted_employee', 'due_date', 'visiting_company_name', 'company_location']
        widgets = {
            'task_description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }