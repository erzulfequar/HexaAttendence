from django.contrib import admin
from .models import Department, Designation, Shift, Employee, Device, Holiday, Task, TaskSubmission

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_id', 'department_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('department_name',)

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ('designation_id', 'designation_name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('designation_name',)

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('shift_id', 'shift_name', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('shift_name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'employee_code', 'first_name', 'last_name', 'department', 'designation', 'status')
    list_filter = ('department', 'designation', 'status')
    search_fields = ('employee_code', 'first_name', 'last_name', 'email')

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'device_name', 'serial_number', 'ip_address', 'status', 'last_seen')
    list_filter = ('status',)
    search_fields = ('device_name', 'serial_number', 'ip_address')

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('holiday_id', 'holiday_date', 'description')
    search_fields = ('description',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'task_type', 'allotted_employee', 'approved_by', 'date_assigned', 'status')
    list_filter = ('status', 'task_type', 'approved_by')
    search_fields = ('task_type', 'task_description', 'visiting_company_name')
    readonly_fields = ('date_assigned',)

@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'task', 'submitted_by', 'submitted_at', 'verified')
    list_filter = ('verified', 'submitted_at')
    search_fields = ('task__task_type', 'submitted_by__first_name', 'submitted_by__last_name')
    readonly_fields = ('submitted_at',)
