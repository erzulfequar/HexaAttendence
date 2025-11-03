from django.contrib import admin
from .models import Role, UserProfile, ActivityLog

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_id', 'role_name', 'description')
    search_fields = ('role_name',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'employee_id', 'mobile', 'status')
    list_filter = ('role', 'status')
    search_fields = ('user__username', 'employee_id')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'user', 'action', 'timestamp', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'action')
