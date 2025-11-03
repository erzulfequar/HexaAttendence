from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.role_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True)
    status = models.BooleanField(default=True)

    USERNAME_FIELD = 'user'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.user.username} - {self.role.role_name if self.role else 'No Role'}"

class ActivityLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
