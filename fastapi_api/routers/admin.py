from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from auth import get_current_user, get_user_role
from models import (
    User, UserProfile, Role, Employee, Department, Designation,
    AttendanceLog, AttendanceSummary, LeaveApplication, LeaveType,
    Payslip, Department, Designation
)
from schemas import EmployeeProfile, LeaveType

router = APIRouter()

def require_admin(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Dependency to require admin role"""
    user_role = get_user_role(db, current_user.id)
    if user_role != 'Admin' and user_role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# === USER MANAGEMENT ENDPOINTS ===

@router.get("/admin/users")
def get_all_users(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = Query(None, description="Search by username or email"),
    role_filter: Optional[str] = Query(None, description="Filter by role"),
    status_filter: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users with optional filtering"""
    query = db.query(User).join(UserProfile, isouter=True).join(Role, isouter=True)
    
    if search:
        query = query.filter(
            User.username.contains(search) |
            User.email.contains(search)
        )
    
    if role_filter:
        query = query.filter(Role.role_name.contains(role_filter))
    
    if status_filter:
        if status_filter.lower() == 'active':
            query = query.filter(User.is_active == True)
        elif status_filter.lower() == 'inactive':
            query = query.filter(User.is_active == False)
    
    total = query.count()
    offset = (page - 1) * limit
    
    users = query.offset(offset).limit(limit).all()
    
    user_list = []
    for user in users:
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        role_name = user_profile.role.role_name if user_profile and user_profile.role else None
        
        # Get employee info if exists
        employee_info = None
        if user_profile and user_profile.employee_id:
            employee = db.query(Employee).filter(Employee.employee_id == user_profile.employee_id).first()
            if employee:
                employee_info = {
                    "employee_id": employee.employee_id,
                    "employee_code": employee.employee_code,
                    "first_name": employee.first_name,
                    "last_name": employee.last_name
                }
        
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": role_name,
            "is_active": user.is_active,
            "date_joined": user.date_joined,
            "employee_info": employee_info
        })
    
    return {
        "users": user_list,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.post("/admin/users")
def create_user(
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    role_id: Optional[int] = None,
    employee_code: Optional[str] = None,
    mobile: Optional[str] = None,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Create user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
        date_joined=datetime.utcnow()
    )
    # Note: In production, you'd need to handle password hashing properly
    # For now, we'll just set a placeholder
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        role_id=role_id,
        employee_id=employee_code,
        mobile=mobile,
        status=True
    )
    db.add(profile)
    db.commit()
    
    return {"message": "User created successfully", "user_id": user.id}

@router.put("/admin/users/{user_id}")
def update_user(
    user_id: int,
    email: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    role_id: Optional[int] = None,
    mobile: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields
    if email:
        user.email = email
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if is_active is not None:
        user.is_active = is_active
    
    db.commit()
    
    # Update profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        if role_id:
            profile.role_id = role_id
        if mobile:
            profile.mobile = mobile
    
    db.commit()
    
    return {"message": "User updated successfully"}

@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user (soft delete by deactivating)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting the current admin user
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}

# === EMPLOYEE MANAGEMENT ENDPOINTS ===

@router.get("/admin/employees")
def get_all_employees(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = Query(None),
    department_filter: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all employees with filtering"""
    query = db.query(Employee).join(Department, isouter=True).join(Designation, isouter=True)
    
    if search:
        query = query.filter(
            Employee.first_name.contains(search) |
            Employee.last_name.contains(search) |
            Employee.employee_code.contains(search) |
            Employee.email.contains(search)
        )
    
    if department_filter:
        query = query.filter(Employee.department_id == department_filter)
    
    if status_filter:
        if status_filter.lower() == 'active':
            query = query.filter(Employee.status == True)
        elif status_filter.lower() == 'inactive':
            query = query.filter(Employee.status == False)
    
    total = query.count()
    offset = (page - 1) * limit
    
    employees = query.offset(offset).limit(limit).all()
    
    employee_list = []
    for emp in employees:
        manager_name = None
        if emp.manager_id:
            manager = db.query(Employee).filter(Employee.employee_id == emp.manager_id).first()
            if manager:
                manager_name = f"{manager.first_name} {manager.last_name}"
        
        employee_list.append({
            "employee_id": emp.employee_id,
            "employee_code": emp.employee_code,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "mobile": emp.mobile,
            "department_name": emp.department.department_name if emp.department else None,
            "designation_name": emp.designation.designation_name if emp.designation else None,
            "manager_name": manager_name,
            "date_of_joining": emp.date_of_joining,
            "status": emp.status
        })
    
    return {
        "employees": employee_list,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/admin/departments")
def get_departments(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    """Get all departments"""
    departments = db.query(Department).all()
    return [
        {
            "department_id": dept.department_id,
            "department_name": dept.department_name,
            "is_active": dept.is_active
        }
        for dept in departments
    ]

@router.get("/admin/designations")
def get_designations(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    """Get all designations"""
    designations = db.query(Designation).all()
    return [
        {
            "designation_id": desig.designation_id,
            "designation_name": desig.designation_name,
            "description": desig.description,
            "is_active": desig.is_active
        }
        for desig in designations
    ]

@router.get("/admin/roles")
def get_roles(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    """Get all roles"""
    roles = db.query(Role).all()
    return [
        {
            "role_id": role.role_id,
            "role_name": role.role_name,
            "description": role.description
        }
        for role in roles
    ]

# === ATTENDANCE MANAGEMENT ENDPOINTS ===

@router.get("/admin/attendance/overview")
def get_company_attendance_overview(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    department_filter: Optional[int] = Query(None),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get company-wide attendance overview"""
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    query = db.query(Employee).join(Department, isouter=True)
    
    if department_filter:
        query = query.filter(Employee.department_id == department_filter)
    
    employees = query.all()
    
    attendance_data = []
    
    for emp in employees:
        # Get attendance summary for this period
        summaries = db.query(AttendanceSummary).filter(
            and_(
                AttendanceSummary.employee_id == emp.employee_id,
                AttendanceSummary.date >= start_date,
                AttendanceSummary.date <= end_date
            )
        ).all()
        
        # Calculate statistics
        total_days = len(summaries)
        present_days = len([s for s in summaries if s.status == 'present'])
        absent_days = len([s for s in summaries if s.status == 'absent'])
        half_days = len([s for s in summaries if s.status == 'half_day'])
        
        attendance_data.append({
            "employee_id": emp.employee_id,
            "employee_name": f"{emp.first_name} {emp.last_name}",
            "employee_code": emp.employee_code,
            "department_name": emp.department.department_name if emp.department else None,
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "half_days": half_days,
            "attendance_percentage": round((present_days + half_days * 0.5) / total_days * 100, 2) if total_days > 0 else 0
        })
    
    return attendance_data

@router.get("/admin/attendance/logs")
def get_attendance_logs(
    page: int = 1,
    limit: int = 100,
    employee_filter: Optional[int] = Query(None),
    date_filter: Optional[date] = Query(None),
    status_filter: Optional[str] = Query(None),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get attendance logs with filtering"""
    query = db.query(AttendanceLog).join(Employee)
    
    if employee_filter:
        query = query.filter(AttendanceLog.employee_id == employee_filter)
    
    if date_filter:
        query = query.filter(func.date(AttendanceLog.punch_time) == date_filter)
    
    if status_filter:
        query = query.filter(AttendanceLog.status == status_filter)
    
    total = query.count()
    offset = (page - 1) * limit
    
    logs = query.order_by(AttendanceLog.punch_time.desc()).offset(offset).limit(limit).all()
    
    log_list = []
    for log in logs:
        log_list.append({
            "attendance_id": log.attendance_id,
            "employee_name": f"{log.employee.first_name} {log.employee.last_name}",
            "employee_code": log.employee.employee_code,
            "punch_type": log.punch_type,
            "punch_time": log.punch_time,
            "geo_lat": log.geo_lat,
            "geo_long": log.geo_long,
            "status": log.status
        })
    
    return {
        "logs": log_list,
        "total": total,
        "page": page,
        "limit": limit
    }

# === LEAVE MANAGEMENT ENDPOINTS ===

@router.get("/admin/leaves/overview")
def get_leave_overview(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status_filter: Optional[str] = Query(None),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get company-wide leave overview"""
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    query = db.query(LeaveApplication).join(Employee).join(LeaveType)
    
    if status_filter:
        query = query.filter(LeaveApplication.status == status_filter)
    
    # Filter by date range
    query = query.filter(
        and_(
            LeaveApplication.start_date >= start_date,
            LeaveApplication.end_date <= end_date
        )
    )
    
    leave_applications = query.all()
    
    # Calculate statistics
    total_applications = len(leave_applications)
    approved_leaves = len([l for l in leave_applications if l.status == 'approved'])
    pending_leaves = len([l for l in leave_applications if l.status == 'pending'])
    rejected_leaves = len([l for l in leave_applications if l.status == 'rejected'])
    
    # Get leave by type
    leave_by_type = {}
    for leave in leave_applications:
        leave_type_name = leave.leave_type.type_name
        if leave_type_name not in leave_by_type:
            leave_by_type[leave_type_name] = 0
        leave_by_type[leave_type_name] += 1
    
    return {
        "total_applications": total_applications,
        "approved": approved_leaves,
        "pending": pending_leaves,
        "rejected": rejected_leaves,
        "by_leave_type": leave_by_type,
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

@router.get("/admin/leaves/applications")
def get_leave_applications(
    page: int = 1,
    limit: int = 50,
    status_filter: Optional[str] = Query(None),
    employee_filter: Optional[int] = Query(None),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all leave applications with filtering"""
    query = db.query(LeaveApplication).join(Employee).join(LeaveType)
    
    if status_filter:
        query = query.filter(LeaveApplication.status == status_filter)
    
    if employee_filter:
        query = query.filter(LeaveApplication.employee_id == employee_filter)
    
    total = query.count()
    offset = (page - 1) * limit
    
    applications = query.order_by(LeaveApplication.applied_date.desc()).offset(offset).limit(limit).all()
    
    application_list = []
    for app in applications:
        # Get approver info
        approver_name = None
        if app.approved_by_id:
            approver = db.query(User).filter(User.id == app.approved_by_id).first()
            if approver:
                approver_name = f"{approver.first_name} {approver.last_name}"
        
        application_list.append({
            "leave_id": app.leave_id,
            "employee_name": f"{app.employee.first_name} {app.employee.last_name}",
            "employee_code": app.employee.employee_code,
            "leave_type": app.leave_type.type_name,
            "start_date": app.start_date,
            "end_date": app.end_date,
            "total_days": app.total_days,
            "reason": app.reason,
            "status": app.status,
            "applied_date": app.applied_date,
            "approved_date": app.approved_date,
            "approved_by": approver_name
        })
    
    return {
        "applications": application_list,
        "total": total,
        "page": page,
        "limit": limit
    }

# === PAYROLL ENDPOINTS ===

@router.get("/admin/payroll/overview")
def get_payroll_overview(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get payroll overview"""
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # Get all payslips in the date range
    payslips = db.query(Payslip).filter(
        and_(
            Payslip.generated_date >= start_date,
            Payslip.generated_date <= end_date
        )
    ).all()
    
    total_employees = len(set(p.payroll_id for p in payslips))  # Unique employees
    total_gross = sum(p.total_earnings for p in payslips)
    total_deductions = sum(p.total_deductions for p in payslips)
    total_net = sum(p.net_pay for p in payslips)
    
    return {
        "total_employees": total_employees,
        "total_gross": total_gross,
        "total_deductions": total_deductions,
        "total_net": total_net,
        "payslips_count": len(payslips),
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        }
    }

# === SYSTEM STATISTICS ENDPOINTS ===

@router.get("/admin/dashboard")
def get_admin_dashboard(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    """Get admin dashboard statistics"""
    # User statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Employee statistics
    total_employees = db.query(Employee).count()
    active_employees = db.query(Employee).filter(Employee.status == True).count()
    
    # Department statistics
    total_departments = db.query(Department).filter(Department.is_active == True).count()
    
    # Today's attendance statistics
    today = date.today()
    today_attendance = db.query(AttendanceSummary).filter(AttendanceSummary.date == today).all()
    
    present_today = len([a for a in today_attendance if a.status == 'present'])
    absent_today = len([a for a in today_attendance if a.status == 'absent'])
    
    # Pending leaves
    pending_leaves = db.query(LeaveApplication).filter(LeaveApplication.status == 'pending').count()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "employees": {
            "total": total_employees,
            "active": active_employees,
            "inactive": total_employees - active_employees
        },
        "departments": total_departments,
        "today_attendance": {
            "present": present_today,
            "absent": absent_today,
            "total_marked": len(today_attendance)
        },
        "pending_leaves": pending_leaves,
        "date": today.isoformat()
    }