from django.contrib import admin
from .models import CompanyProfile, AttendanceRule, WorkWeek

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_email')

@admin.register(AttendanceRule)
class AttendanceRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'rule_name', 'grace_minutes', 'rounding_policy')

@admin.register(WorkWeek)
class WorkWeekAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'is_working_day')
    list_filter = ('is_working_day',)
