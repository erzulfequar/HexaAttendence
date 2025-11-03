import os
import django
from datetime import date, time, datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hexaattendanceportal.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Sum
from core.models import Role, UserProfile, ActivityLog
from master.models import Department, Designation, Shift, Employee, Device, Holiday
from attendance.models import AttendanceLog, AttendanceSummary
from leave.models import LeaveType, LeaveApplication
from settings.models import CompanyProfile, AttendanceRule, WorkWeek
from payroll.models import SalaryComponent, EmployeeSalary, SalaryComponentValue, PayrollPeriod, PayrollRun, Payslip, PayslipDetail

def create_roles():
    roles = [
        {'role_name': 'Admin', 'description': 'System Administrator'},
        {'role_name': 'Manager', 'description': 'Department Manager'},
        {'role_name': 'Employee', 'description': 'Regular Employee'},
        {'role_name': 'HR', 'description': 'Human Resources'},
    ]
    for role_data in roles:
        Role.objects.get_or_create(**role_data)

def create_departments():
    departments = [
        {'department_name': 'IT', 'is_active': True},
        {'department_name': 'HR', 'is_active': True},
        {'department_name': 'Finance', 'is_active': True},
        {'department_name': 'Operations', 'is_active': True},
        {'department_name': 'Marketing', 'is_active': True},
    ]
    for dept_data in departments:
        Department.objects.get_or_create(**dept_data)

def create_designations():
    designations = [
        {'designation_name': 'Software Engineer', 'description': 'Develops software applications', 'is_active': True},
        {'designation_name': 'Senior Software Engineer', 'description': 'Leads software development', 'is_active': True},
        {'designation_name': 'HR Manager', 'description': 'Manages human resources', 'is_active': True},
        {'designation_name': 'Accountant', 'description': 'Handles financial records', 'is_active': True},
        {'designation_name': 'Operations Manager', 'description': 'Manages operations', 'is_active': True},
        {'designation_name': 'Marketing Specialist', 'description': 'Handles marketing activities', 'is_active': True},
    ]
    for desig_data in designations:
        Designation.objects.get_or_create(**desig_data)

def create_shifts():
    shifts = [
        {'shift_name': 'Morning', 'start_time': time(9, 0), 'end_time': time(17, 0), 'grace_in': 15, 'grace_out': 15, 'is_active': True},
        {'shift_name': 'Evening', 'start_time': time(14, 0), 'end_time': time(22, 0), 'grace_in': 10, 'grace_out': 10, 'is_active': True},
        {'shift_name': 'Night', 'start_time': time(22, 0), 'end_time': time(6, 0), 'grace_in': 20, 'grace_out': 20, 'is_active': True},
    ]
    for shift_data in shifts:
        Shift.objects.get_or_create(**shift_data)

def create_employees():
    departments = list(Department.objects.all())
    designations = list(Designation.objects.all())
    shifts = list(Shift.objects.all())

    employees_data = [
        {'employee_code': 'EMP001', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@company.com', 'mobile': '1234567890', 'date_of_joining': date(2023, 1, 15), 'status': True},
        {'employee_code': 'EMP002', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane.smith@company.com', 'mobile': '1234567891', 'date_of_joining': date(2023, 2, 20), 'status': True},
        {'employee_code': 'EMP003', 'first_name': 'Bob', 'last_name': 'Johnson', 'email': 'bob.johnson@company.com', 'mobile': '1234567892', 'date_of_joining': date(2023, 3, 10), 'status': True},
        {'employee_code': 'EMP004', 'first_name': 'Alice', 'last_name': 'Williams', 'email': 'alice.williams@company.com', 'mobile': '1234567893', 'date_of_joining': date(2023, 4, 5), 'status': True},
        {'employee_code': 'EMP005', 'first_name': 'Charlie', 'last_name': 'Brown', 'email': 'charlie.brown@company.com', 'mobile': '1234567894', 'date_of_joining': date(2023, 5, 12), 'status': True},
        {'employee_code': 'EMP006', 'first_name': 'Diana', 'last_name': 'Davis', 'email': 'diana.davis@company.com', 'mobile': '1234567895', 'date_of_joining': date(2023, 6, 18), 'status': True},
        {'employee_code': 'EMP007', 'first_name': 'Eve', 'last_name': 'Miller', 'email': 'eve.miller@company.com', 'mobile': '1234567896', 'date_of_joining': date(2023, 7, 25), 'status': True},
        {'employee_code': 'EMP008', 'first_name': 'Frank', 'last_name': 'Wilson', 'email': 'frank.wilson@company.com', 'mobile': '1234567897', 'date_of_joining': date(2023, 8, 30), 'status': True},
        {'employee_code': 'EMP009', 'first_name': 'Grace', 'last_name': 'Moore', 'email': 'grace.moore@company.com', 'mobile': '1234567898', 'date_of_joining': date(2023, 9, 14), 'status': True},
        {'employee_code': 'EMP010', 'first_name': 'Henry', 'last_name': 'Taylor', 'email': 'henry.taylor@company.com', 'mobile': '1234567899', 'date_of_joining': date(2023, 10, 22), 'status': True},
    ]

    for emp_data in employees_data:
        emp_data['department'] = random.choice(departments)
        emp_data['designation'] = random.choice(designations)
        emp_data['shift'] = random.choice(shifts)
        Employee.objects.get_or_create(employee_code=emp_data['employee_code'], defaults=emp_data)

def create_devices():
    devices = [
        {'device_name': 'Main Entrance Biometric', 'serial_number': 'BIO001', 'ip_address': '192.168.1.100', 'mac_address': '00:11:22:33:44:55', 'status': 'online', 'last_seen': datetime.now(), 'location': 'Main Entrance'},
        {'device_name': 'Back Entrance RFID', 'serial_number': 'RFID001', 'ip_address': '192.168.1.101', 'mac_address': '00:11:22:33:44:56', 'status': 'online', 'last_seen': datetime.now(), 'location': 'Back Entrance'},
        {'device_name': 'Office Floor 1', 'serial_number': 'BIO002', 'ip_address': '192.168.1.102', 'mac_address': '00:11:22:33:44:57', 'status': 'offline', 'last_seen': datetime.now() - timedelta(hours=2), 'location': 'Floor 1'},
        {'device_name': 'Cafeteria', 'serial_number': 'RFID002', 'ip_address': '192.168.1.103', 'mac_address': '00:11:22:33:44:58', 'status': 'online', 'last_seen': datetime.now(), 'location': 'Cafeteria'},
    ]
    for device_data in devices:
        Device.objects.get_or_create(serial_number=device_data['serial_number'], defaults=device_data)

def create_holidays():
    holidays = [
        {'holiday_date': date(2025, 1, 1), 'description': 'New Year\'s Day'},
        {'holiday_date': date(2025, 1, 26), 'description': 'Republic Day'},
        {'holiday_date': date(2025, 5, 1), 'description': 'Labour Day'},
        {'holiday_date': date(2025, 8, 15), 'description': 'Independence Day'},
        {'holiday_date': date(2025, 10, 2), 'description': 'Gandhi Jayanti'},
        {'holiday_date': date(2025, 12, 25), 'description': 'Christmas'},
    ]
    for holiday_data in holidays:
        Holiday.objects.get_or_create(**holiday_data)

def create_users_and_profiles():
    roles = list(Role.objects.all())

    users_data = [
        {'username': 'admin', 'email': 'admin@company.com', 'first_name': 'Admin', 'last_name': 'User', 'is_staff': True, 'is_superuser': False},
        {'username': 'manager1', 'email': 'manager1@company.com', 'first_name': 'Manager', 'last_name': 'One', 'is_staff': True},
        {'username': 'hr1', 'email': 'hr1@company.com', 'first_name': 'HR', 'last_name': 'One', 'is_staff': True},
    ]

    for user_data in users_data:
        user, created = User.objects.get_or_create(username=user_data['username'], defaults=user_data)
        if created:
            user.set_password('password123')
            user.save()

        # Assign specific roles based on username
        if user_data['username'] == 'admin':
            role = Role.objects.get(role_name='Admin')
        elif user_data['username'] == 'manager1':
            role = Role.objects.get(role_name='Manager')
        elif user_data['username'] == 'hr1':
            role = Role.objects.get(role_name='HR')
        else:
            role = random.choice(roles)

        employee_id = 'ADM001' if user_data['username'] == 'admin' else ('MGR001' if user_data['username'] == 'manager1' else 'HR001')
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': role,
                'employee_id': employee_id,
                'mobile': user_data.get('mobile', ''),
                'status': True
            }
        )

def create_leave_types():
    leave_types = [
        {'type_name': 'Annual Leave', 'description': 'Regular annual leave', 'max_days': 30},
        {'type_name': 'Sick Leave', 'description': 'Medical leave', 'max_days': 15},
        {'type_name': 'Casual Leave', 'description': 'Short term leave', 'max_days': 12},
        {'type_name': 'Maternity Leave', 'description': 'Maternity leave for female employees', 'max_days': 180},
        {'type_name': 'Paternity Leave', 'description': 'Paternity leave for male employees', 'max_days': 15},
    ]
    for leave_data in leave_types:
        LeaveType.objects.get_or_create(**leave_data)

def create_leave_applications():
    employees = list(Employee.objects.all())
    leave_types = list(LeaveType.objects.all())
    users = list(User.objects.filter(is_staff=True))

    for _ in range(20):
        employee = random.choice(employees)
        leave_type = random.choice(leave_types)
        start_date = date.today() - timedelta(days=random.randint(1, 60))
        end_date = start_date + timedelta(days=random.randint(1, leave_type.max_days))
        total_days = (end_date - start_date).days + 1

        LeaveApplication.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            defaults={
                'end_date': end_date,
                'total_days': total_days,
                'reason': f'Personal {leave_type.type_name.lower()}',
                'status': random.choice(['pending', 'approved', 'rejected']),
                'approved_by': random.choice(users) if random.random() > 0.5 else None,
                'approved_date': datetime.now() if random.random() > 0.5 else None,
            }
        )

def create_attendance_logs():
    employees = list(Employee.objects.all())
    devices = list(Device.objects.all())

    for employee in employees:
        shift = employee.shift
        if not shift:
            continue

        # Generate attendance for the last 30 days
        for days_back in range(30):
            attendance_date = date.today() - timedelta(days=days_back)

            # Skip weekends and holidays
            if attendance_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue
            if Holiday.objects.filter(holiday_date=attendance_date).exists():
                continue

            # Randomly decide if employee is present (80% chance)
            if random.random() < 0.8:
                # Check-in
                check_in_time = datetime.combine(attendance_date, shift.start_time) + timedelta(minutes=random.randint(-30, 30))
                AttendanceLog.objects.get_or_create(
                    employee=employee,
                    punch_type='IN',
                    punch_time=check_in_time,
                    defaults={
                        'device': random.choice(devices),
                        'geo_lat': 28.6139 + random.uniform(-0.01, 0.01),  # Delhi coordinates with small variation
                        'geo_long': 77.2090 + random.uniform(-0.01, 0.01),
                        'selfie_url': '',
                        'status': 'approved'
                    }
                )

                # Check-out (if present)
                if random.random() < 0.9:  # 90% chance of check-out
                    check_out_time = datetime.combine(attendance_date, shift.end_time) + timedelta(minutes=random.randint(-30, 30))
                    AttendanceLog.objects.get_or_create(
                        employee=employee,
                        punch_type='OUT',
                        punch_time=check_out_time,
                        defaults={
                            'device': random.choice(devices),
                            'geo_lat': 28.6139 + random.uniform(-0.01, 0.01),
                            'geo_long': 77.2090 + random.uniform(-0.01, 0.01),
                            'selfie_url': '',
                            'status': 'approved'
                        }
                    )

def create_attendance_summaries():
    employees = list(Employee.objects.all())

    for employee in employees:
        for days_back in range(30):
            attendance_date = date.today() - timedelta(days=days_back)

            # Get attendance logs for this date
            logs = AttendanceLog.objects.filter(
                employee=employee,
                punch_time__date=attendance_date
            ).order_by('punch_time')

            if logs.exists():
                in_log = logs.filter(punch_type='IN').first()
                out_log = logs.filter(punch_type='OUT').last()

                in_time = in_log.punch_time.time() if in_log else None
                out_time = out_log.punch_time.time() if out_log else None

                total_hours = None
                if in_time and out_time:
                    duration = datetime.combine(attendance_date, out_time) - datetime.combine(attendance_date, in_time)
                    total_hours = round(duration.total_seconds() / 3600, 2)

                late_by = 0
                if in_time and employee.shift:
                    expected_in = employee.shift.start_time
                    if in_time > expected_in:
                        late_minutes = (datetime.combine(attendance_date, in_time) - datetime.combine(attendance_date, expected_in)).total_seconds() / 60
                        late_by = int(late_minutes)

                early_out = 0
                if out_time and employee.shift:
                    expected_out = employee.shift.end_time
                    if out_time < expected_out:
                        early_minutes = (datetime.combine(attendance_date, expected_out) - datetime.combine(attendance_date, out_time)).total_seconds() / 60
                        early_out = int(early_minutes)

                status = 'present'
                if not in_time:
                    status = 'absent'
                elif total_hours and total_hours < 4:
                    status = 'half_day'

                AttendanceSummary.objects.get_or_create(
                    employee=employee,
                    date=attendance_date,
                    defaults={
                        'in_time': in_time,
                        'out_time': out_time,
                        'total_hours': total_hours,
                        'late_by': late_by,
                        'early_out': early_out,
                        'status': status
                    }
                )

def create_company_profile():
    CompanyProfile.objects.get_or_create(
        name='HexaHash Technologies',
        defaults={
            'address': '123 Tech Street, Silicon Valley, CA 94043',
            'contact_email': 'info@hexahash.com',
            'logo_url': 'https://example.com/logo.png'
        }
    )

def create_attendance_rules():
    AttendanceRule.objects.get_or_create(
        rule_name='Standard Rule',
        defaults={
            'grace_minutes': 15,
            'rounding_policy': 'nearest_15'
        }
    )

def create_work_week():
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for day in days:
        is_working = day not in ['saturday', 'sunday']
        WorkWeek.objects.get_or_create(
            day=day,
            defaults={'is_working_day': is_working}
        )

def create_activity_logs():
    users = list(User.objects.all())
    actions = ['Login', 'Logout', 'Created Employee', 'Updated Profile', 'Generated Report']

    for _ in range(50):
        user = random.choice(users)
        action = random.choice(actions)
        timestamp = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        ActivityLog.objects.get_or_create(
            user=user,
            action=action,
            timestamp=timestamp,
            defaults={'ip_address': f'192.168.1.{random.randint(1, 255)}'}
        )

def create_payroll_data():
    # Create salary components
    salary_components = [
        {'component_name': 'Basic Salary', 'component_type': 'earning', 'description': 'Base salary component', 'is_taxable': True, 'is_active': True},
        {'component_name': 'HRA', 'component_type': 'earning', 'description': 'House Rent Allowance', 'is_taxable': True, 'is_active': True},
        {'component_name': 'Conveyance Allowance', 'component_type': 'earning', 'description': 'Transport allowance', 'is_taxable': True, 'is_active': True},
        {'component_name': 'Medical Allowance', 'component_type': 'earning', 'description': 'Medical expenses allowance', 'is_taxable': True, 'is_active': True},
        {'component_name': 'LTA', 'component_type': 'earning', 'description': 'Leave Travel Allowance', 'is_taxable': True, 'is_active': True},
        {'component_name': 'Professional Tax', 'component_type': 'deduction', 'description': 'State professional tax', 'is_taxable': False, 'is_active': True},
        {'component_name': 'Provident Fund', 'component_type': 'deduction', 'description': 'Employee PF contribution', 'is_taxable': False, 'is_active': True},
        {'component_name': 'Income Tax', 'component_type': 'deduction', 'description': 'TDS deduction', 'is_taxable': False, 'is_active': True},
    ]

    for comp_data in salary_components:
        SalaryComponent.objects.get_or_create(component_name=comp_data['component_name'], defaults=comp_data)

    # Create employee salaries
    employees = list(Employee.objects.all())
    components = list(SalaryComponent.objects.all())

    for employee in employees:
        basic_salary = random.choice([30000, 35000, 40000, 45000, 50000, 55000, 60000])
        emp_salary, created = EmployeeSalary.objects.get_or_create(
            employee=employee,
            defaults={
                'basic_salary': basic_salary,
                'effective_date': date(2024, 1, 1),
                'is_active': True
            }
        )

        if created:
            # Add salary components
            for component in components:
                if component.component_name == 'Basic Salary':
                    amount = basic_salary
                elif component.component_name == 'HRA':
                    amount = basic_salary * 0.4  # 40% of basic
                elif component.component_name == 'Conveyance Allowance':
                    amount = 19200  # Standard conveyance allowance
                elif component.component_name == 'Medical Allowance':
                    amount = 50000  # Standard medical allowance
                elif component.component_name == 'LTA':
                    amount = basic_salary * 0.0833  # 1 month basic
                elif component.component_name == 'Professional Tax':
                    amount = 2352  # Annual PT for salary > 21,000
                elif component.component_name == 'Provident Fund':
                    amount = basic_salary * 0.12  # 12% of basic
                elif component.component_name == 'Income Tax':
                    amount = basic_salary * 0.1  # Approximate 10% TDS
                else:
                    amount = 0

                SalaryComponentValue.objects.get_or_create(
                    employee_salary=emp_salary,
                    component=component,
                    defaults={
                        'amount': amount,
                        'is_percentage': False
                    }
                )

    # Create payroll periods
    payroll_periods = [
        {'period_name': 'September 2024', 'start_date': date(2024, 9, 1), 'end_date': date(2024, 9, 30), 'is_closed': True},
        {'period_name': 'October 2024', 'start_date': date(2024, 10, 1), 'end_date': date(2024, 10, 31), 'is_closed': True},
        {'period_name': 'November 2024', 'start_date': date(2024, 11, 1), 'end_date': date(2024, 11, 30), 'is_closed': True},
        {'period_name': 'December 2024', 'start_date': date(2024, 12, 1), 'end_date': date(2024, 12, 31), 'is_closed': True},
        {'period_name': 'January 2025', 'start_date': date(2025, 1, 1), 'end_date': date(2025, 1, 31), 'is_closed': False},
    ]

    for period_data in payroll_periods:
        PayrollPeriod.objects.get_or_create(period_name=period_data['period_name'], defaults=period_data)

    # Create payroll runs and payslips
    periods = list(PayrollPeriod.objects.all())
    users = list(User.objects.filter(is_staff=True))

    for period in periods:
        if period.is_closed:
            processed_by = None
            if users:
                user_profile = UserProfile.objects.filter(user=random.choice(users)).first()
                processed_by = user_profile

            payroll_run, created = PayrollRun.objects.get_or_create(
                period=period,
                defaults={
                    'run_date': datetime.now(),
                    'status': 'completed',
                    'total_employees': len(employees),
                    'total_gross_pay': 0,
                    'total_deductions': 0,
                    'total_net_pay': 0,
                    'processed_by': processed_by
                }
            )

            if created:
                total_gross = 0
                total_deductions = 0
                total_net = 0

                for employee in employees:
                    emp_salary = EmployeeSalary.objects.filter(employee=employee, is_active=True).first()
                    if emp_salary:
                        # Calculate totals
                        earnings = SalaryComponentValue.objects.filter(
                            employee_salary=emp_salary,
                            component__component_type='earning'
                        ).aggregate(total=Sum('amount'))['total'] or 0

                        deductions = SalaryComponentValue.objects.filter(
                            employee_salary=emp_salary,
                            component__component_type='deduction'
                        ).aggregate(total=Sum('amount'))['total'] or 0

                        net_pay = earnings - deductions

                        # Create payslip
                        payslip = Payslip.objects.create(
                            payroll_run=payroll_run,
                            employee=employee,
                            basic_salary=emp_salary.basic_salary,
                            total_earnings=earnings,
                            total_deductions=deductions,
                            net_pay=net_pay,
                            generated_date=datetime.now()
                        )

                        # Create payslip details
                        component_values = SalaryComponentValue.objects.filter(employee_salary=emp_salary)
                        for comp_value in component_values:
                            PayslipDetail.objects.create(
                                payslip=payslip,
                                component=comp_value.component,
                                amount=comp_value.amount
                            )

                        total_gross += earnings
                        total_deductions += deductions
                        total_net += net_pay

                # Update payroll run totals
                payroll_run.total_gross_pay = total_gross
                payroll_run.total_deductions = total_deductions
                payroll_run.total_net_pay = total_net
                payroll_run.save()

if __name__ == '__main__':
    print("Creating dummy data...")

    create_roles()
    print("Roles created")

    create_departments()
    print("Departments created")

    create_designations()
    print("Designations created")

    create_shifts()
    print("Shifts created")

    create_employees()
    print("Employees created")

    create_devices()
    print("Devices created")

    create_holidays()
    print("Holidays created")

    create_users_and_profiles()
    print("Users and profiles created")

    create_leave_types()
    print("Leave types created")

    create_leave_applications()
    print("Leave applications created")

    create_attendance_logs()
    print("Attendance logs created")

    create_attendance_summaries()
    print("Attendance summaries created")

    create_company_profile()
    print("Company profile created")

    create_attendance_rules()
    print("Attendance rules created")

    create_work_week()
    print("Work week created")

    create_activity_logs()
    print("Activity logs created")

    create_payroll_data()
    print("Payroll data created")

    print("All dummy data created successfully!")