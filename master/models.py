from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.department_name

class Designation(models.Model):
    designation_id = models.AutoField(primary_key=True)
    designation_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.designation_name

class Shift(models.Model):
    shift_id = models.AutoField(primary_key=True)
    shift_name = models.CharField(max_length=50, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_in = models.IntegerField(default=0, help_text="Grace time in minutes for check-in")
    grace_out = models.IntegerField(default=0, help_text="Grace time in minutes for check-out")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.shift_name} ({self.start_time} - {self.end_time})"

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    employee_code = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    date_of_joining = models.DateField()
    status = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name}"

class Device(models.Model):
    device_id = models.AutoField(primary_key=True)
    device_name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=50, unique=True)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17, blank=True)
    status = models.CharField(max_length=20, choices=[('online', 'Online'), ('offline', 'Offline')], default='offline')
    last_seen = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.device_name} - {self.serial_number}"

class Holiday(models.Model):
    holiday_id = models.AutoField(primary_key=True)
    holiday_date = models.DateField(unique=True)
    description = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.holiday_date} - {self.description}"

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_type = models.CharField(max_length=100, help_text="Type of task, e.g., Field Visit")
    task_description = models.TextField()
    allotted_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='tasks')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_assigned = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    visiting_company_name = models.CharField(max_length=200, blank=True)
    company_location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')

    def __str__(self):
        return f"Task {self.task_id} - {self.task_type} for {self.allotted_employee}"

class TaskSubmission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey(Employee, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    selfie = models.ImageField(upload_to='task_selfies/', null=True, blank=True)
    notes = models.TextField(blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Submission for Task {self.task.task_id} by {self.submitted_by}"
