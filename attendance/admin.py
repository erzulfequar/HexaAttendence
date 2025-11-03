from django.contrib import admin
from .models import AttendanceLog, AttendanceSummary

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('attendance_id', 'employee', 'punch_type', 'punch_time', 'device', 'status')
    list_filter = ('punch_type', 'status', 'punch_time')
    search_fields = ('employee__employee_code', 'employee__first_name')

@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('summary_id', 'employee', 'date', 'in_time', 'out_time', 'total_hours', 'status')
    list_filter = ('status', 'date')
    search_fields = ('employee__employee_code', 'employee__first_name')
