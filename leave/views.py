from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import LeaveType, LeaveApplication
from master.models import Employee
from datetime import date

@login_required
def leave_view(request):
    """Leave management page"""
    leave_types = LeaveType.objects.all()
    leave_applications = LeaveApplication.objects.select_related('employee', 'leave_type', 'approved_by').order_by('-applied_date')

    # Statistics
    total_applications = leave_applications.count()
    pending_applications = leave_applications.filter(status='pending').count()
    approved_applications = leave_applications.filter(status='approved').count()
    rejected_applications = leave_applications.filter(status='rejected').count()

    # Add approved count for each leave type
    for leave_type in leave_types:
        leave_type.approved_count = leave_applications.filter(leave_type=leave_type, status='approved').count()

    context = {
        'user_role': 'Admin',
        'leave_types': leave_types,
        'leave_applications': leave_applications[:50],  # Show last 50 applications
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'rejected_applications': rejected_applications,
    }
    return render(request, 'leave/leave.html', context)

@login_required
def apply_leave_view(request):
    """Employee leave application page"""
    if request.method == 'POST':
        # Get employee linked to user
        try:
            employee = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            # Try to link user to employee via employee_id in profile
            try:
                user_profile = request.user.userprofile
                if user_profile.employee_id:
                    employee = Employee.objects.get(employee_code=user_profile.employee_id)
                    employee.user = request.user
                    employee.save()
                else:
                    messages.error(request, 'Employee ID not set in your profile.')
                    return redirect('employee_leave')
            except (UserProfile.DoesNotExist, Employee.DoesNotExist):
                messages.error(request, 'Employee profile not found. Please contact administrator.')
                return redirect('employee_leave')

        leave_type_id = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        try:
            leave_type = LeaveType.objects.get(type_id=leave_type_id)
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
            total_days = (end - start).days + 1

            LeaveApplication.objects.create(
                employee=employee,
                leave_type=leave_type,
                start_date=start,
                end_date=end,
                total_days=total_days,
                reason=reason
            )

            messages.success(request, 'Leave application submitted successfully!')
            return redirect('employee')

        except Exception as e:
            messages.error(request, f'Error submitting leave application: {str(e)}')

    # Get leave types for the form
    leave_types = LeaveType.objects.all()

    context = {
        'leave_types': leave_types,
        'user_role': 'Employee',
    }
    return render(request, 'leave/apply_leave.html', context)
