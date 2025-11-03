from django import forms
from .models import CompanyProfile, AttendanceRule, WorkWeek

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['name', 'address', 'contact_email', 'logo_url']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class AttendanceRuleForm(forms.ModelForm):
    class Meta:
        model = AttendanceRule
        fields = ['rule_name', 'grace_minutes', 'rounding_policy']

class WorkWeekForm(forms.ModelForm):
    class Meta:
        model = WorkWeek
        fields = ['day', 'is_working_day']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make day field readonly if editing existing record
        if self.instance and self.instance.pk:
            self.fields['day'].disabled = True