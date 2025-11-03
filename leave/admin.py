from django.contrib import admin
from .models import LeaveType, LeaveApplication

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('type_id', 'type_name', 'max_days')
    search_fields = ('type_name',)

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('leave_id', 'employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'approved_by')
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = ('employee__employee_code', 'employee__first_name')
