from django.db import models
from master.models import Employee, Device

class AttendanceLog(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    punch_type = models.CharField(max_length=10, choices=[('IN', 'Check In'), ('OUT', 'Check Out')])
    punch_time = models.DateTimeField()
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True)
    geo_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geo_long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    selfie_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected')
    ], default='approved')

    def __str__(self):
        return f"{self.employee.employee_code} - {self.punch_type} at {self.punch_time}"

class AttendanceSummary(models.Model):
    summary_id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    in_time = models.TimeField(null=True, blank=True)
    out_time = models.TimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    late_by = models.IntegerField(default=0, help_text="Late by minutes")
    early_out = models.IntegerField(default=0, help_text="Early out by minutes")
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('leave', 'On Leave')
    ], default='present')

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.employee_code} - {self.date} - {self.status}"
