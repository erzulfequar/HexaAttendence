from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Role, ActivityLog
from master.models import Employee, Task, TaskSubmission
from attendance.models import AttendanceSummary, AttendanceLog
from leave.models import LeaveApplication
from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import date, timedelta
from django.http import JsonResponse

def home(request):
    """Main login selection page"""
    return render(request, 'core/login_selection.html')
def login_selection_view(request):
    """Main login selection page"""
    return render(request, 'core/login_selection.html')
    return redirect('login')

def login_view(request):
    """Main login selection page"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'core/login_selection.html')

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                user_profile = user.userprofile
                if user_profile.role and user_profile.role.role_name == 'Admin':
                    login(request, user)
                    ActivityLog.objects.create(
                        user=user,
                        action='Admin Login',
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    return redirect('admin')
                else:
                    messages.error(request, 'Access denied. Admin privileges required.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact administrator.')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'core/admin_login.html')

def employee_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                user_profile = user.userprofile
                if user_profile.role and user_profile.role.role_name == 'Employee':
                    login(request, user)
                    ActivityLog.objects.create(
                        user=user,
                        action='Employee Login',
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    return redirect('employee')
                else:
                    messages.error(request, 'Access denied. Employee privileges required.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact administrator.')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'core/employee_login.html')

def manager_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                user_profile = user.userprofile
                if user_profile.role and user_profile.role.role_name == 'Manager':
                    # Check if Employee object exists, create if not
                    try:
                        employee = Employee.objects.get(user=user)
                    except Employee.DoesNotExist:
                        # Create dummy manager employee
                        from master.models import Department, Designation, Shift
                        dept = Department.objects.get_or_create(department_name='Management')[0]
                        desig = Designation.objects.get_or_create(designation_name='Manager')[0]
                        shift = Shift.objects.get_or_create(shift_name='Office', start_time='09:00', end_time='17:00')[0]
                        employee = Employee.objects.create(
                            employee_code=f'MGR{user.id}',
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=user.email,
                            department=dept,
                            designation=desig,
                            shift=shift,
                            date_of_joining=date.today()
                        )
                        employee.user = user
                        employee.save()

                    login(request, user)
                    ActivityLog.objects.create(
                        user=user,
                        action='Manager Login',
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    return redirect('manager')
                else:
                    messages.error(request, 'Access denied. Manager privileges required.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact administrator.')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'core/manager_login.html')
def admin_signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('admin_signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('admin_signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('admin_signup')

        # Create admin user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        # Get or create Admin role
        role, created = Role.objects.get_or_create(role_name='Admin')

        # Create user profile
        UserProfile.objects.create(
            user=user,
            role=role,
            employee_id=None,  # Set to None for admin signup
            status=True
        )

        messages.success(request, 'Admin account created successfully! You can now login.')
        return redirect('admin_login')

    return render(request, 'core/admin_signup.html')
    return render(request, 'core/manager_login.html')

@login_required
def logout_view(request):
    ActivityLog.objects.create(
        user=request.user,
        action='Logout',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user role"""
    try:
        user_profile = request.user.userprofile
        role = user_profile.role.role_name
        if role == 'Admin':
            return redirect('admin')
        elif role == 'Manager':
            return redirect('manager')
        elif role == 'Employee':
            return redirect('employee')
        else:
            return redirect('login')
    except UserProfile.DoesNotExist:
        return redirect('login')

@login_required
def admin_view(request):
    """Admin management page"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        user_role = 'Admin'
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get admin statistics
    total_users = User.objects.count()
    total_employees = Employee.objects.filter(status=True).count()
    total_departments = Employee.objects.values('department').distinct().count()
    total_roles = Role.objects.count()

    # Recent activity logs
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:20]

    # System statistics
    total_attendance_logs = AttendanceSummary.objects.count()
    total_leave_applications = LeaveApplication.objects.count()

    context = {
        'user_role': user_role,
        'total_users': total_users,
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_roles': total_roles,
        'recent_activities': recent_activities,
        'total_attendance_logs': total_attendance_logs,
        'total_leave_applications': total_leave_applications,
    }

    return render(request, 'core/admin.html', context)

@login_required
def add_user_view(request):
    """Add User page"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        user_role = 'Admin'
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role_name = request.POST.get('role')
        employee_id = request.POST.get('employee_id')
        mobile = request.POST.get('mobile')
        status = request.POST.get('status') == 'True'

        # Employee-specific fields
        department_id = request.POST.get('department')
        new_department = request.POST.get('new_department')
        manager_id = request.POST.get('manager')
        designation_id = request.POST.get('designation')
        new_designation = request.POST.get('new_designation')
        shift_id = request.POST.get('shift')
        date_of_joining = request.POST.get('date_of_joining')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('add_user')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('add_user')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('add_user')

        # Handle new department creation
        if department_id == 'new' and new_department:
            from master.models import Department
            department, created = Department.objects.get_or_create(
                department_name=new_department.strip(),
                defaults={'is_active': True}
            )
            department_id = department.department_id
        else:
            department = None

        # Handle new designation creation
        if designation_id == 'new' and new_designation:
            from master.models import Designation
            designation, created = Designation.objects.get_or_create(
                designation_name=new_designation.strip(),
                defaults={'is_active': True}
            )
            designation_id = designation.designation_id
        else:
            designation = None

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        # Get or create role
        role, created = Role.objects.get_or_create(role_name=role_name)

        # Create user profile
        UserProfile.objects.create(
            user=user,
            role=role,
            employee_id=employee_id if employee_id else None,
            mobile=mobile,
            status=status
        )

        # Create Employee object if role is Employee or Manager
        if role_name in ['Employee', 'Manager']:
            from master.models import Department, Designation, Shift
            from datetime import date

            if not department and department_id:
                department = Department.objects.get(pk=department_id)
            if not designation and designation_id:
                designation = Designation.objects.get(pk=designation_id)

            manager = Employee.objects.get(pk=manager_id) if manager_id else None
            shift = Shift.objects.get(pk=shift_id) if shift_id else None
            joining_date = date.fromisoformat(date_of_joining) if date_of_joining else date.today()

            employee_code = employee_id or f"{'MGR' if role_name == 'Manager' else 'EMP'}{user.id}"

            Employee.objects.create(
                user=user,
                employee_code=employee_code,
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile=mobile,
                department=department,
                manager=manager,
                designation=designation,
                shift=shift,
                date_of_joining=joining_date,
                status=status
            )

        messages.success(request, 'User created successfully')
        return redirect('manage_users')

    # Get data for dropdowns
    from master.models import Department, Designation, Shift
    departments = Department.objects.filter(is_active=True)
    designations = Designation.objects.filter(is_active=True)
    shifts = Shift.objects.filter(is_active=True)
    managers = Employee.objects.filter(status=True).exclude(user__userprofile__role__role_name='Employee')

    context = {
        'user_role': user_role,
        'departments': departments,
        'designations': designations,
        'shifts': shifts,
        'managers': managers
    }
    return render(request, 'core/add_user.html', context)

@login_required
def manage_users_view(request):
    """Manage Users page"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        user_role = 'Admin'
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get all users for management
    from django.contrib.auth.models import User
    users = User.objects.select_related('userprofile__role').all()
    context = {'user_role': user_role, 'users': users}
    return render(request, 'core/manage_users.html', context)

@login_required
def edit_user_view(request, user_id):
    """Edit User page"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        user_role = 'Admin'
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    try:
        user = User.objects.select_related('userprofile__role').get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('manage_users')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role_name = request.POST.get('role')
        employee_id = request.POST.get('employee_id')
        mobile = request.POST.get('mobile')
        status = request.POST.get('status') == 'True'

        # Check if username is taken by another user
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, 'Username already exists')
            return redirect('edit_user', user_id=user_id)

        # Check if email is taken by another user
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, 'Email already exists')
            return redirect('edit_user', user_id=user_id)

        # Update user
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Get or create role
        role, created = Role.objects.get_or_create(role_name=role_name)

        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.employee_id = employee_id if employee_id else None
        profile.mobile = mobile
        profile.status = status
        profile.save()

        messages.success(request, 'User updated successfully')
        return redirect('manage_users')

    context = {'user_role': user_role, 'user': user}
    return render(request, 'core/edit_user.html', context)

@login_required
def delete_user_view(request, user_id):
    """Delete User"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, 'User deleted successfully')
    except User.DoesNotExist:
        messages.error(request, 'User not found')
    return redirect('manage_users')

@login_required
def reset_password_view(request, user_id):
    """Reset User Password"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
        new_password = 'password123'  # Default reset password
        user.set_password(new_password)
        user.save()
        messages.success(request, f'Password reset successfully. New password: {new_password}')
    except User.DoesNotExist:
        messages.error(request, 'User not found')
    return redirect('manage_users')

@login_required
def view_user_details_view(request, user_id):
    """View User Details"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        user_role = 'Admin'
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    try:
        user = User.objects.select_related('userprofile__role').get(id=user_id)
        # Get recent activity logs for this user
        recent_logs = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:10]
        context = {'user_role': user_role, 'user': user, 'recent_logs': recent_logs}
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('manage_users')

    return render(request, 'core/view_user_details.html', context)

@login_required
def system_settings_view(request):
    """System Settings page"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        user_role = 'Admin'
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    context = {'user_role': user_role}
    return render(request, 'core/system_settings.html', context)

@login_required
def backup_data_view(request):
    """Backup Data page"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        user_role = 'Admin'
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    context = {'user_role': user_role}
    return render(request, 'core/backup_data.html', context)

@login_required
def employee_view(request):
    """Employee dashboard"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Employee':
            messages.error(request, 'Access denied. Employee privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')
    # Use dummy employee (first active employee)
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

    # Link employee to user if not already linked
    if not employee.user:
        employee.user = request.user
        employee.save()
        # Also update user profile with employee_id
        try:
            user_profile = request.user.userprofile
            user_profile.employee_id = employee.employee_code
            user_profile.save()
        except UserProfile.DoesNotExist:
            pass

    # Get employee's attendance summary (last 10 days)
    attendance = AttendanceSummary.objects.filter(employee=employee).order_by('-date')[:10]

    # Get employee's leave applications
    leaves = LeaveApplication.objects.filter(employee=employee).order_by('-applied_date')[:10]

    # Today's attendance status
    today = date.today()
    today_attendance = AttendanceSummary.objects.filter(employee=employee, date=today).first()

    context = {
        'user_role': 'Employee',
        'employee': employee,
        'attendance': attendance,
        'leaves': leaves,
        'today_attendance': today_attendance,
        'today': today,
    }
    return render(request, 'core/employee.html', context)

@login_required
def profile_view(request):
    """Employee profile page"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Employee':
            messages.error(request, 'Access denied. Employee privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

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
                return redirect('employee')
        except (UserProfile.DoesNotExist, Employee.DoesNotExist):
            messages.error(request, 'Employee profile not found.')
            return redirect('employee')

    if request.method == 'POST':
        # Handle profile update
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        username = request.POST.get('username')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')

        # Validate required fields
        if not all([first_name, last_name, email, username]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('employee_profile')

        # Check if email is already taken by another user
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'Email address is already in use.')
            return redirect('employee_profile')

        # Check if username is already taken by another user
        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('employee_profile')

        # Handle profile picture upload
        if profile_picture:
            # Validate file type
            if not profile_picture.content_type.startswith('image/'):
                messages.error(request, 'Please upload a valid image file.')
                return redirect('employee_profile')

            # Validate file size (max 5MB)
            if profile_picture.size > 5 * 1024 * 1024:
                messages.error(request, 'Profile picture must be less than 5MB.')
                return redirect('employee_profile')

            # Save the profile picture
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            import uuid

            # Delete old profile picture if exists
            if employee.profile_picture:
                try:
                    default_storage.delete(employee.profile_picture.path)
                except:
                    pass

            # Save new profile picture
            file_name = f"profile_{employee.employee_code}_{uuid.uuid4().hex[:8]}.{profile_picture.name.split('.')[-1]}"
            file_path = default_storage.save(f'profile_pictures/{file_name}', ContentFile(profile_picture.read()))
            employee.profile_picture = file_path

        # Update employee information
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        employee.mobile = mobile
        employee.save()

        # Update user information
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.username = username
        request.user.save()

        # Handle password change if provided
        if current_password or new_password or confirm_password:
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
                return redirect('employee_profile')

            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('employee_profile')

            if len(new_password) < 8:
                messages.error(request, 'New password must be at least 8 characters long.')
                return redirect('employee_profile')

            request.user.set_password(new_password)
            request.user.save()

            # Log the user out after password change
            from django.contrib.auth import logout
            logout(request)
            messages.success(request, 'Profile updated successfully! Please login with your new password.')
            return redirect('employee_login')

        messages.success(request, 'Profile updated successfully!')
        return redirect('employee_profile')

    # Get employee's attendance summary (last 10 days)
    attendance = AttendanceSummary.objects.filter(employee=employee).order_by('-date')[:10]

    # Get employee's leave applications
    leaves = LeaveApplication.objects.filter(employee=employee).order_by('-applied_date')[:10]

    # Today's attendance status
    today = date.today()
    today_attendance = AttendanceSummary.objects.filter(employee=employee, date=today).first()

    # Attendance statistics for current month
    start_of_month = today.replace(day=1)
    attendance_stats = AttendanceSummary.objects.filter(
        employee=employee,
        date__gte=start_of_month,
        date__lte=today
    ).aggregate(
        present_days=Count('summary_id', filter=Q(status='present')),
        absent_days=Count('summary_id', filter=Q(status='absent')),
        half_days=Count('summary_id', filter=Q(status='half_day')),
        total_hours=Sum('total_hours')
    )

    # Get employee's tasks
    tasks = Task.objects.filter(allotted_employee=employee).order_by('-date_assigned')[:10]

    context = {
        'employee': employee,
        'user_role': 'Employee',
        'attendance': attendance,
        'leaves': leaves,
        'today_attendance': today_attendance,
        'attendance_stats': attendance_stats,
        'tasks': tasks,
        'today': today,
    }
    return render(request, 'core/profile.html', context)

@login_required
def leave_view(request):
    """Employee leave page"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Employee':
            messages.error(request, 'Access denied. Employee privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get employee linked to user
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('dashboard')

    # Get employee's leave applications
    leaves = LeaveApplication.objects.filter(employee=employee).order_by('-applied_date')

    # Get employee's tasks
    tasks = Task.objects.filter(allotted_employee=employee).order_by('-date_assigned')

    context = {
        'employee': employee,
        'leaves': leaves,
        'tasks': tasks,
        'user_role': 'Employee',
    }
    return render(request, 'core/leave.html', context)

@login_required
def manager_view(request):
    """Manager/HR dashboard"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        # Create dummy manager employee if not exists
        from master.models import Department, Designation, Shift
        dept = Department.objects.get_or_create(department_name='Management')[0]
        desig = Designation.objects.get_or_create(designation_name='Manager')[0]
        shift = Shift.objects.get_or_create(shift_name='Office', start_time='09:00', end_time='17:00')[0]
        manager = Employee.objects.create(
            employee_code=f'MGR{request.user.id}',
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
            department=dept,
            designation=desig,
            shift=shift,
            date_of_joining=date.today()
        )
        manager.user = request.user
        manager.save()

    # Get department employees
    dept_employees = Employee.objects.filter(department=manager.department, status=True)

    # Today's attendance for department
    today = date.today()
    dept_attendance_today = AttendanceSummary.objects.filter(
        employee__in=dept_employees,
        date=today
    ).select_related('employee')

    # Leave applications for department
    dept_leaves_full = LeaveApplication.objects.filter(
        employee__in=dept_employees
    ).select_related('employee', 'leave_type').order_by('-applied_date')

    dept_leaves = dept_leaves_full[:20]

    # Department statistics
    total_employees = dept_employees.count()
    present_today = dept_attendance_today.filter(status='present').count()
    absent_today = dept_attendance_today.filter(status='absent').count()
    on_leave_today = dept_leaves_full.filter(
        start_date__lte=today,
        end_date__gte=today,
        status='approved'
    ).count()

    # Calculate percentages for chart
    present_percentage = round((present_today / total_employees * 100), 1) if total_employees > 0 else 0
    absent_percentage = round((absent_today / total_employees * 100), 1) if total_employees > 0 else 0

    # Get department tasks
    dept_tasks = Task.objects.filter(allotted_employee__in=dept_employees).select_related('allotted_employee').order_by('-date_assigned')

    # Task count for current month
    start_of_month = today.replace(day=1)
    task_count = dept_tasks.filter(date_assigned__gte=start_of_month, date_assigned__lte=today).count()

    context = {
        'manager': manager,
        'dept_employees': dept_employees,
        'dept_attendance_today': dept_attendance_today,
        'dept_leaves': dept_leaves,
        'dept_tasks': dept_tasks,
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'on_leave_today': on_leave_today,
        'present_percentage': present_percentage,
        'absent_percentage': absent_percentage,
        'task_count': task_count,
        'today': today,
        'user_role': 'Manager',
    }
    return render(request, 'core/manager.html', context)

@login_required
def submit_task(request, task_id):
    """Employee submits task completion with location and selfie"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Employee':
            messages.error(request, 'Access denied. Employee privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    task = get_object_or_404(Task, pk=task_id)
    # Verify task belongs to current user
    try:
        employee = Employee.objects.get(user=request.user)
        if task.allotted_employee != employee:
            messages.error(request, 'Access denied. Task not assigned to you.')
            return redirect('employee')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('dashboard')

    if request.method == 'POST':
        location_lat = request.POST.get('location_lat')
        location_lng = request.POST.get('location_lng')
        notes = request.POST.get('notes')
        selfie_data = request.POST.get('selfie')

        # Handle base64 image data
        selfie = None
        if selfie_data and selfie_data.startswith('data:image'):
            import base64
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage
            import uuid

            # Extract base64 data
            format, imgstr = selfie_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'selfie_{uuid.uuid4()}.{ext}')
            selfie = default_storage.save(f'selfies/{data.name}', data)

        submission = TaskSubmission.objects.create(
            task=task,
            submitted_by=employee,
            location_lat=location_lat,
            location_lng=location_lng,
            notes=notes,
            selfie=selfie
        )

        messages.success(request, 'Task submission successful!')
        return redirect('employee')

    return render(request, 'core/submit_task.html', {'task': task})

@login_required
def employee_tasks_view(request):
    """Employee tasks page"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Employee':
            messages.error(request, 'Access denied. Employee privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

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
                return redirect('employee')
        except (UserProfile.DoesNotExist, Employee.DoesNotExist):
            messages.error(request, 'Employee profile not found.')
            return redirect('employee')

    # Get employee's tasks
    tasks = Task.objects.filter(allotted_employee=employee).order_by('-date_assigned')

    context = {
        'employee': employee,
        'tasks': tasks,
        'user_role': 'Employee',
    }
    return render(request, 'core/employee_tasks.html', context)

@login_required
def employee_tracking_view(request):
    """View for tracking employee locations on a map"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    # Get department employees
    dept_employees = Employee.objects.filter(department=manager.department, status=True)

    # Get recent attendance logs with location data (last 24 hours)
    from django.utils import timezone
    from datetime import timedelta
    yesterday = timezone.now() - timedelta(days=1)

    recent_logs = AttendanceLog.objects.filter(
        employee__in=dept_employees,
        punch_time__gte=yesterday,
        geo_lat__isnull=False,
        geo_long__isnull=False
    ).select_related('employee').order_by('-punch_time')

    # Prepare location data for the map
    location_data = []
    for log in recent_logs:
        location_data.append({
            'employee_code': log.employee.employee_code,
            'employee_name': f"{log.employee.first_name} {log.employee.last_name}",
            'latitude': float(log.geo_lat),
            'longitude': float(log.geo_long),
            'punch_time': log.punch_time.strftime('%Y-%m-%d %H:%M:%S'),
            'punch_type': log.punch_type,
            'selfie_url': log.selfie_url or ''
        })

    context = {
        'manager': manager,
        'location_data': location_data,
        'dept_employees': dept_employees,
        'total_locations': len(location_data),
        'today': date.today(),
        'user_role': 'Manager',
    }

    return render(request, 'core/employee_tracking.html', context)

@login_required
def manager_employees_view(request):
    """Manager view for managing department employees"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    # Get department employees with detailed info
    dept_employees = Employee.objects.filter(
        department=manager.department
    ).select_related('department', 'designation', 'shift', 'user').order_by('first_name')

    # Calculate inactive count and active count
    inactive_count = dept_employees.filter(status=False).count()
    active_count = dept_employees.filter(status=True).count()

    # Get attendance statistics for current month
    today = date.today()
    start_of_month = today.replace(day=1)

    attendance_stats = {}
    for emp in dept_employees:
        monthly_attendance = AttendanceSummary.objects.filter(
            employee=emp,
            date__gte=start_of_month,
            date__lte=today
        ).aggregate(
            present_days=Count('summary_id', filter=Q(status='present')),
            absent_days=Count('summary_id', filter=Q(status='absent')),
            half_days=Count('summary_id', filter=Q(status='half_day')),
            total_hours=Sum('total_hours')
        )
        attendance_stats[emp.employee_id] = monthly_attendance

    context = {
        'manager': manager,
        'dept_employees': dept_employees,
        'attendance_stats': attendance_stats,
        'inactive_count': inactive_count,
        'active_count': active_count,
        'today': today,
        'user_role': 'Manager',
    }
    return render(request, 'core/manager_employees.html', context)

@login_required
def manager_tasks_view(request):
    """Manager view for managing department tasks"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    # Get department employees for task assignment
    dept_employees = Employee.objects.filter(department=manager.department, status=True)

    # Get all department tasks with submissions
    dept_tasks = Task.objects.filter(
        allotted_employee__in=dept_employees
    ).select_related('allotted_employee').prefetch_related('submissions').order_by('-date_assigned')

    # Task statistics
    total_tasks = dept_tasks.count()
    pending_tasks = dept_tasks.filter(status='pending').count()
    completed_tasks = dept_tasks.filter(status='completed').count()
    in_progress_tasks = dept_tasks.filter(status='in_progress').count()

    context = {
        'manager': manager,
        'dept_employees': dept_employees,
        'dept_tasks': dept_tasks,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'today': date.today(),
        'user_role': 'Manager',
    }
    return render(request, 'core/manager_tasks.html', context)

@login_required
def manager_leave_view(request):
    """Manager view for managing department leave applications"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    # Get department employees
    dept_employees = Employee.objects.filter(department=manager.department, status=True)

    # Get leave applications for department
    dept_leaves = LeaveApplication.objects.filter(
        employee__in=dept_employees
    ).select_related('employee', 'leave_type', 'approved_by').order_by('-applied_date')

    # Leave statistics
    total_leaves = dept_leaves.count()
    pending_leaves = dept_leaves.filter(status='pending').count()
    approved_leaves = dept_leaves.filter(status='approved').count()
    rejected_leaves = dept_leaves.filter(status='rejected').count()

    context = {
        'manager': manager,
        'dept_leaves': dept_leaves,
        'total_leaves': total_leaves,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'today': date.today(),
        'user_role': 'Manager',
    }
    return render(request, 'core/manager_leave.html', context)

@login_required
def manager_attendance_view(request):
    """Manager view for department attendance management"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    # Get department employees
    dept_employees = Employee.objects.filter(department=manager.department, status=True)

    # Get attendance data - default to today
    selected_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    try:
        attendance_date = date.fromisoformat(selected_date)
    except ValueError:
        attendance_date = date.today()

    # Get attendance summaries for selected date
    attendance_summaries = AttendanceSummary.objects.filter(
        employee__in=dept_employees,
        date=attendance_date
    ).select_related('employee')

    # Get attendance logs for selected date
    attendance_logs = AttendanceLog.objects.filter(
        employee__in=dept_employees,
        punch_time__date=attendance_date
    ).select_related('employee', 'device').order_by('punch_time')

    # Calculate statistics
    total_employees = dept_employees.count()
    present_count = attendance_summaries.filter(status='present').count()
    absent_count = attendance_summaries.filter(status='absent').count()
    on_leave_count = LeaveApplication.objects.filter(
        employee__in=dept_employees,
        start_date__lte=attendance_date,
        end_date__gte=attendance_date,
        status='approved'
    ).count()

    context = {
        'manager': manager,
        'dept_employees': dept_employees,
        'attendance_summaries': attendance_summaries,
        'attendance_logs': attendance_logs,
        'selected_date': attendance_date,
        'total_employees': total_employees,
        'present_count': present_count,
        'absent_count': absent_count,
        'on_leave_count': on_leave_count,
        'today': date.today(),
        'user_role': 'Manager',
    }
    return render(request, 'core/manager_attendance.html', context)

@login_required
def approve_leave(request, leave_id):
    """Approve a leave application"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            return JsonResponse({'success': False, 'error': 'Access denied'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User profile not found'})

    try:
        leave_app = LeaveApplication.objects.get(leave_id=leave_id)
        # Check if leave belongs to manager's department
        manager = Employee.objects.get(user=request.user)
        if leave_app.employee.department != manager.department:
            return JsonResponse({'success': False, 'error': 'Access denied'})

        leave_app.status = 'approved'
        leave_app.approved_by = request.user
        leave_app.approved_date = timezone.now()
        leave_app.save()

        return JsonResponse({'success': True, 'message': 'Leave approved successfully'})
    except LeaveApplication.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Leave application not found'})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Manager profile not found'})

@login_required
def reject_leave(request, leave_id):
    """Reject a leave application"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            return JsonResponse({'success': False, 'error': 'Access denied'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User profile not found'})

    try:
        leave_app = LeaveApplication.objects.get(leave_id=leave_id)
        # Check if leave belongs to manager's department
        manager = Employee.objects.get(user=request.user)
        if leave_app.employee.department != manager.department:
            return JsonResponse({'success': False, 'error': 'Access denied'})

        leave_app.status = 'rejected'
        leave_app.approved_by = request.user
        leave_app.approved_date = timezone.now()
        leave_app.save()

        return JsonResponse({'success': True, 'message': 'Leave rejected successfully'})
    except LeaveApplication.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Leave application not found'})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Manager profile not found'})

@login_required
def manager_add_employee_view(request):
    """Manager view for adding employees to their department"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        employee_id = request.POST.get('employee_id')
        mobile = request.POST.get('mobile')
        designation_id = request.POST.get('designation')
        shift_id = request.POST.get('shift')
        date_of_joining = request.POST.get('date_of_joining')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('manager_add_employee')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('manager_add_employee')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('manager_add_employee')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        # Get or create Employee role
        role, created = Role.objects.get_or_create(role_name='Employee')

        # Create user profile
        UserProfile.objects.create(
            user=user,
            role=role,
            employee_id=employee_id if employee_id else None,
            mobile=mobile,
            status=True
        )

        # Handle new department creation
        if department_id == 'new' and new_department:
            from master.models import Department
            department, created = Department.objects.get_or_create(
                department_name=new_department.strip(),
                defaults={'is_active': True}
            )
        else:
            department = manager.department

        # Handle new designation creation
        if designation_id == 'new' and new_designation:
            from master.models import Designation
            designation, created = Designation.objects.get_or_create(
                designation_name=new_designation.strip(),
                defaults={'is_active': True}
            )
        else:
            designation = None
            if designation_id:
                designation = Designation.objects.get(pk=designation_id)

        # Create Employee object
        from master.models import Designation, Shift
        from datetime import date

        shift = Shift.objects.get(pk=shift_id) if shift_id else None
        joining_date = date.fromisoformat(date_of_joining) if date_of_joining else date.today()

        employee_code = employee_id or f"EMP{user.id}"

        Employee.objects.create(
            user=user,
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile=mobile,
            department=department,
            manager=manager,
            designation=designation,
            shift=shift,
            date_of_joining=joining_date,
            status=True
        )

        messages.success(request, 'Employee created successfully with login credentials')
        return redirect('manager_employees')

    # Get data for dropdowns
    from master.models import Designation, Shift
    designations = Designation.objects.filter(is_active=True)
    shifts = Shift.objects.filter(is_active=True)

    context = {
        'user_role': 'Manager',
        'manager': manager,
        'designations': designations,
        'shifts': shifts,
    }
    return render(request, 'core/manager_add_employee.html', context)

@login_required
def manager_profile_view(request):
    """Manager profile page - view own attendance, leave, and payroll records"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    # Get manager's attendance summary (last 10 days)
    attendance = AttendanceSummary.objects.filter(employee=manager).order_by('-date')[:10]

    # Get manager's leave applications
    leaves = LeaveApplication.objects.filter(employee=manager).order_by('-applied_date')[:10]

    # Today's attendance status
    today = date.today()
    today_attendance = AttendanceSummary.objects.filter(employee=manager, date=today).first()

    # Attendance statistics for current month
    start_of_month = today.replace(day=1)
    attendance_stats = AttendanceSummary.objects.filter(
        employee=manager,
        date__gte=start_of_month,
        date__lte=today
    ).aggregate(
        present_days=Count('summary_id', filter=Q(status='present')),
        absent_days=Count('summary_id', filter=Q(status='absent')),
        half_days=Count('summary_id', filter=Q(status='half_day')),
        total_hours=Sum('total_hours')
    )

    # Get manager's tasks
    tasks = Task.objects.filter(allotted_employee=manager).order_by('-date_assigned')[:10]

    context = {
        'manager': manager,
        'user_role': 'Manager',
        'attendance': attendance,
        'leaves': leaves,
        'today_attendance': today_attendance,
        'attendance_stats': attendance_stats,
        'tasks': tasks,
        'today': today,
    }
    return render(request, 'core/manager_profile.html', context)

@login_required
def manager_own_attendance_view(request):
    """Manager view for own attendance records"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    # Get attendance data - default to current month
    selected_month = request.GET.get('month', date.today().strftime('%Y-%m'))
    try:
        year, month = map(int, selected_month.split('-'))
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
    except (ValueError, IndexError):
        start_date = date.today().replace(day=1)
        end_date = date.today()

    # Get attendance summaries for selected month
    attendance_records = AttendanceSummary.objects.filter(
        employee=manager,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('-date')

    # Calculate statistics
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = attendance_records.filter(status='absent').count()
    half_days = attendance_records.filter(status='half_day').count()
    total_hours = attendance_records.aggregate(Sum('total_hours'))['total_hours__sum'] or 0

    context = {
        'manager': manager,
        'user_role': 'Manager',
        'attendance_records': attendance_records,
        'selected_month': selected_month,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'half_days': half_days,
        'total_hours': total_hours,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'core/manager_own_attendance.html', context)

@login_required
def manager_own_leave_view(request):
    """Manager view for own leave records"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    # Get manager's leave applications
    leaves = LeaveApplication.objects.filter(employee=manager).order_by('-applied_date')

    # Leave statistics
    total_leaves = leaves.count()
    pending_leaves = leaves.filter(status='pending').count()
    approved_leaves = leaves.filter(status='approved').count()
    rejected_leaves = leaves.filter(status='rejected').count()

    context = {
        'manager': manager,
        'leaves': leaves,
        'user_role': 'Manager',
        'total_leaves': total_leaves,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
    }
    return render(request, 'core/manager_own_leave.html', context)

@login_required
def manager_own_payroll_view(request):
    """Manager view for own payroll records"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            messages.error(request, 'Access denied. Manager privileges required.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

    # Get manager linked to user
    try:
        manager = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Manager profile not found.')
        return redirect('dashboard')

    # Import payroll models
    from payroll.models import EmployeeSalary, PayrollRun, Payslip

    # Get manager's salary information
    try:
        employee_salary = EmployeeSalary.objects.get(employee=manager, is_active=True)
    except EmployeeSalary.DoesNotExist:
        employee_salary = None

    # Get manager's payslips
    payslips = Payslip.objects.filter(employee=manager).order_by('-payroll_run__period_end_date')

    # Get recent payroll runs that include this manager
    recent_payroll_runs = PayrollRun.objects.filter(
        payslip__employee=manager
    ).distinct().order_by('-period_end_date')[:12]

    context = {
        'manager': manager,
        'user_role': 'Manager',
        'employee_salary': employee_salary,
        'payslips': payslips,
        'recent_payroll_runs': recent_payroll_runs,
    }
    return render(request, 'core/manager_own_payroll.html', context)

@login_required
def create_task(request):
    """Create a new task for department employee"""
    try:
        user_profile = request.user.userprofile
        if user_profile.role.role_name != 'Manager':
            return JsonResponse({'success': False, 'error': 'Access denied'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User profile not found'})

    if request.method == 'POST':
        try:
            manager = Employee.objects.get(user=request.user)
            task_type = request.POST.get('task_type')
            allotted_employee_id = request.POST.get('allotted_employee')
            task_description = request.POST.get('task_description')
            visiting_company_name = request.POST.get('visiting_company_name')
            company_location = request.POST.get('company_location')
            due_date_str = request.POST.get('due_date')

            # Validate allotted employee is in manager's department
            allotted_employee = Employee.objects.get(employee_id=allotted_employee_id)
            if allotted_employee.department != manager.department:
                return JsonResponse({'success': False, 'error': 'Cannot assign tasks to employees outside your department'})

            due_date = None
            if due_date_str:
                due_date = date.fromisoformat(due_date_str)

            task = Task.objects.create(
                task_type=task_type,
                task_description=task_description,
                allotted_employee=allotted_employee,
                approved_by=request.user,
                due_date=due_date,
                visiting_company_name=visiting_company_name,
                company_location=company_location
            )

            return JsonResponse({'success': True, 'message': 'Task created successfully'})
        except Employee.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Employee not found'})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

