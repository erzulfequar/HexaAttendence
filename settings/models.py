from django.db import models

class CompanyProfile(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_email = models.EmailField()
    logo_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class AttendanceRule(models.Model):
    id = models.AutoField(primary_key=True)
    rule_name = models.CharField(max_length=100)
    grace_minutes = models.IntegerField(default=15)
    rounding_policy = models.CharField(max_length=50, choices=[
        ('none', 'No Rounding'),
        ('nearest_15', 'Nearest 15 minutes'),
        ('nearest_30', 'Nearest 30 minutes')
    ], default='none')

    def __str__(self):
        return self.rule_name

class WorkWeek(models.Model):
    id = models.AutoField(primary_key=True)
    day = models.CharField(max_length=10, choices=[
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ])
    is_working_day = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.day} - {'Working' if self.is_working_day else 'Non-working'}"
