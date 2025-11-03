from django.db import models
from master.models import Employee
from django.contrib.auth.models import User

class LeaveType(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    max_days = models.IntegerField(default=30)

    def __str__(self):
        return self.type_name

class LeaveApplication(models.Model):
    leave_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    applied_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee.employee_code} - {self.leave_type.type_name} ({self.start_date} to {self.end_date})"
