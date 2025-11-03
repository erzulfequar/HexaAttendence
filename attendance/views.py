from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import AttendanceLog, AttendanceSummary
from master.models import Employee, Device
from datetime import date, datetime, time
from django.utils import timezone
import json

@login_required
def attendance_view(request):
    """Attendance management page"""
    today = date.today()

    # Get today's attendance logs
    today_logs = AttendanceLog.objects.select_related('employee', 'device').filter(
        punch_time__date=today
    ).order_by('-punch_time')

    # Get today's attendance summary
    today_summary = AttendanceSummary.objects.select_related('employee').filter(
        date=today
    ).order_by('employee__employee_code')

    # Recent attendance logs (last 50)
    recent_logs = AttendanceLog.objects.select_related('employee', 'device').order_by('-punch_time')[:50]

    # Attendance statistics
    total_logs_today = today_logs.count()
    present_today = today_summary.filter(status='present').count()
    absent_today = today_summary.filter(status='absent').count()
    late_today = today_summary.filter(late_by__gt=0).count()

    context = {
        'user_role': 'Admin',
        'today_logs': today_logs,
        'today_summary': today_summary,
        'recent_logs': recent_logs,
        'total_logs_today': total_logs_today,
        'present_today': present_today,
        'absent_today': absent_today,
        'late_today': late_today,
        'today': today,
    }
    return render(request, 'attendance/attendance.html', context)

@login_required
def mark_attendance_view(request):
    """View for marking attendance - supports both device and mobile"""
    if request.method == 'GET':
        # Get dummy employee for demo
        employee = Employee.objects.filter(status=True).first()
        if not employee:
            # Create dummy if none exists
            from master.models import Department, Designation, Shift
            dept = Department.objects.get_or_create(department_name='IT')[0]
            desig = Designation.objects.get_or_create(designation_name='Developer')[0]
            shift = Shift.objects.get_or_create(shift_name='Morning', start_time='09:00', end_time='17:00')[0]
            employee = Employee.objects.create(
                employee_code='EMP001',
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                department=dept,
                designation=desig,
                shift=shift,
                date_of_joining=date.today()
            )

        # Check today's attendance
        today = date.today()
        today_attendance = AttendanceSummary.objects.filter(employee=employee, date=today).first()

        # Determine if check-in or check-out
        last_punch = AttendanceLog.objects.filter(
            employee=employee,
            punch_time__date=today
        ).order_by('-punch_time').first()

        punch_type = 'IN' if not last_punch or last_punch.punch_type == 'OUT' else 'OUT'

        context = {
            'employee': employee,
            'today_attendance': today_attendance,
            'punch_type': punch_type,
            'today': today,
            'user_role': 'Employee',
        }
        return render(request, 'attendance/mark_attendance.html', context)

    return redirect('employee')


@csrf_exempt
@require_POST
def submit_attendance(request):
    """AJAX endpoint for submitting attendance with selfie and geo location"""
    try:
        data = json.loads(request.POST.get('data', '{}'))
        employee_id = data.get('employee_id')
        punch_type = data.get('punch_type')
        geo_lat = data.get('geo_lat')
        geo_long = data.get('geo_long')
        device_name = data.get('device_name', 'Mobile Device')

        # Get employee
        employee = Employee.objects.get(employee_code=employee_id)

        # Get or create device
        device, created = Device.objects.get_or_create(
            device_name=device_name,
            defaults={'device_type': 'Mobile', 'status': True}
        )

        # Handle selfie upload
        selfie_url = ''
        if 'selfie' in request.FILES:
            selfie_file = request.FILES['selfie']
            # Save to media directory
            import os
            from django.conf import settings
            filename = f"selfies/{employee.employee_code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(settings.MEDIA_ROOT, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'wb+') as destination:
                for chunk in selfie_file.chunks():
                    destination.write(chunk)

            selfie_url = f"{settings.MEDIA_URL}{filename}"

        # Create attendance log
        attendance_log = AttendanceLog.objects.create(
            employee=employee,
            punch_type=punch_type,
            punch_time=timezone.now(),
            device=device,
            geo_lat=geo_lat,
            geo_long=geo_long,
            selfie_url=selfie_url,
            status='approved'
        )

        # Update or create attendance summary
        today = date.today()
        summary, created = AttendanceSummary.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'status': 'present'}
        )

        if punch_type == 'IN':
            summary.in_time = attendance_log.punch_time.time()
            # Check if late
            shift_start = time.fromisoformat(employee.shift.start_time)
            if summary.in_time > shift_start:
                diff = datetime.combine(today, summary.in_time) - datetime.combine(today, shift_start)
                summary.late_by = int(diff.total_seconds() / 60)
        elif punch_type == 'OUT':
            summary.out_time = attendance_log.punch_time.time()
            # Calculate total hours
            if summary.in_time:
                in_datetime = datetime.combine(today, summary.in_time)
                out_datetime = datetime.combine(today, summary.out_time)
                duration = out_datetime - in_datetime
                summary.total_hours = round(duration.total_seconds() / 3600, 2)

                # Check early out
                shift_end = time.fromisoformat(employee.shift.end_time)
                if summary.out_time < shift_end:
                    diff = datetime.combine(today, shift_end) - datetime.combine(today, summary.out_time)
                    summary.early_out = int(diff.total_seconds() / 60)

        summary.save()

        return JsonResponse({
            'success': True,
            'message': f'Attendance {punch_type} marked successfully',
            'punch_time': attendance_log.punch_time.strftime('%H:%M:%S')
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
