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
    Employee, UserProfile, AttendanceLog, AttendanceSummary, 
    LeaveApplication, LeaveType, User, Department, Designation
)
from schemas import EmployeeProfile, AttendanceLog, LeaveApplication, LeaveType

router = APIRouter()

def get_manager_employee(current_user, db):
    """Get the employee record for the current manager user"""
    # Get employee record for this manager
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found for manager")
    return employee

def is_manager(current_user, db):
    """Check if current user is a manager"""
    user_role = get_user_role(db, current_user.id)
    return user_role in ['Manager', 'manager']

def require_manager(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Dependency to require manager role"""
    if not is_manager(current_user, db):
        raise HTTPException(status_code=403, detail="Manager access required")
    return current_user

# === EMPLOYEE MANAGEMENT ENDPOINTS ===

@router.get("/manager/employees")
def get_manager_employees(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = Query(None, description="Search by name or employee code"),
    current_user=Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get all employees under this manager"""
    manager_employee = get_manager_employee(current_user, db)
    
    query = db.query(Employee).filter(Employee.manager_id == manager_employee.employee_id)
    
    if search:
        query = query.filter(
            Employee.first_name.contains(search) |
            Employee.last_name.contains(search) |
            Employee.employee_code.contains(search) |
            Employee.email.contains(search)
        )
    
    total = query.count()
    offset = (page - 1) * limit
    
    employees = query.offset(offset).limit(limit).all()
    
    # Get department and designation names
    employee_list = []
    for emp in employees:
        dept_name = None
        desig_name = None
        
        if emp.department_id:
            dept = db.query(Department).filter(Department.department_id == emp.department_id).first()
            dept_name = dept.department_name if dept else None
            
        if emp.designation_id:
            desig = db.query(Designation).filter(Designation.designation_id == emp.designation_id).first()
            desig_name = desig.designation_name if desig else None
        
        employee_list.append({
            "employee_id": emp.employee_id,
            "employee_code": emp.employee_code,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "mobile": emp.mobile,
            "department_name": dept_name,
            "designation_name": desig_name,
            "status": emp.status
        })
    
    return {
        "employees": employee_list,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/manager/employees/{employee_id}")
def get_employee_details(
    employee_id: int,
    current_user=Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific employee under this manager"""
    manager_employee = get_manager_employee(current_user, db)
    
    # Verify employee is under this manager
    employee = db.query(Employee).filter(
        and_(
            Employee.employee_id == employee_id,
            Employee.manager_id == manager_employee.employee_id
        )
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found or not under your management")
    
    # Get department and designation names
    dept_name = None
    desig_name = None
    
    if employee.department_id:
        dept = db.query(Department).filter(Department.department_id == employee.department_id).first()
        dept_name = dept.department_name if dept else None
        
    if employee.designation_id:
        desig = db.query(Designation).filter(Designation.designation_id == employee.designation_id).first()
        desig_name = desig.designation_name if desig else None
    
    return {
        "employee_id": employee.employee_id,
        "employee_code": employee.employee_code,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "email": employee.email,
        "mobile": employee.mobile,
        "department_name": dept_name,
        "designation_name": desig_name,
        "date_of_joining": employee.date_of_joining,
        "status": employee.status
    }

# === ATTENDANCE MANAGEMENT ENDPOINTS ===

@router.get("/manager/attendance/overview")
def get_team_attendance_overview(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user=Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get attendance overview for all team members"""
    manager_employee = get_manager_employee(current_user, db)
    
    # Default to current month if dates not provided
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # Get employees under this manager
    employees = db.query(Employee).filter(Employee.manager_id == manager_employee.employee_id).all()
    
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
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "half_days": half_days,
            "attendance_percentage": round((present_days + half_days * 0.5) / total_days * 100, 2) if total_days > 0 else 0
        })
    
    return attendance_data

@router.get("/manager/attendance/{employee_id}")
def get_employee_attendance_details(
    employee_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user=Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get detailed attendance records for a specific employee"""
    manager_employee = get_manager_employee(current_user, db)
    
    # Verify employee is under this manager
    employee = db.query(Employee).filter(
        and_(
            Employee.employee_id == employee_id,
            Employee.manager_id == manager_employee.employee_id
        )
    ).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found or not under your management")
    
    # Default to current month
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    attendance_logs = db.query(AttendanceLog).filter(
        and_(
            AttendanceLog.employee_id == employee_id,
            func.date(AttendanceLog.punch_time) >= start_date,
            func.date(AttendanceLog.punch_time) <= end_date
        )
    ).order_by(AttendanceLog.punch_time.desc()).all()
    
    return {
        "employee": {
            "employee_id": employee.employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "employee_code": employee.employee_code
        },
        "attendance_logs": [
            {
                "attendance_id": log.attendance_id,
                "punch_type": log.punch_type,
                "punch_time": log.punch_time,
                "geo_lat": log.geo_lat,
                "geo_long": log.geo_long,
                "status": log.status
            }
            for log in attendance_logs
        ]
    }

# === LEAVE MANAGEMENT ENDPOINTS ===

@router.get("/manager/leaves/pending")
def get_pending_leave_applications(
    page: int = 1,
    limit: int = 20,
    current_user=Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get pending leave applications for manager approval"""
    manager_employee = get_manager_employee(current_user, db)
    
    # Get pending leaves for employees under this manager
    pending_leaves = db.query(LeaveApplication).join(Employee).filter(
        and_(
            Employee.manager_id == manager_employee.employee_id,
            LeaveApplication.status == 'pending'
        )
    ).order_by(LeaveApplication.applied_date.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    leave_list = []
    for leave in pending_leaves:
        # Get leave type name
        leave_type = db.query(LeaveType).filter(LeaveType.type_id == leave.leave_type_id).first()
        leave_type_name = leave_type.type_name if leave_type else None
        
        leave_list.append({
            "leave_id": leave.leave_id,
            "employee_id": leave.employee_id,
            "employee_name": f"{leave.employee.first_name} {leave.employee.last_name}",
            "employee_code": leave.employee.employee_code,
            "leave_type": leave_type_name,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "total_days": leave.total_days,
            "reason": leave.reason,
            "applied_date": leave.applied_date
        })
    
    return leave_list

@router.post("/manager/leaves/{leave_id}/approve")
def approve_leave_application(
    leave_id: int,
    current_user=Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Approve a leave application"""
    manager_employee = get_manager_employee(current_user, db)
    
    # Get the leave application and verify it belongs to an employee under this manager
    leave = db.query(LeaveApplication).join(Employee).filter(
        and_(
            LeaveApplication.leave_id == leave_id,
            Employee.manager_id == manager_employee.employee_id,
            LeaveApplication.status == 'pending'
        )
    ).first()
    
    if not leave:
        raise HTTPException(status_code=404, detail="Leave application not found or not under your management")
    
    # Approve the leave
    leave.status = 'approved'
    leave.approved_by_id = current_user.id
    leave.approved_date = datetime.utcnow()
    
    db.commit()
    db.refresh(leave)
    
    return {"message": "Leave application approved successfully"}

@router.post("/manager/leaves/{leave_id}/reject")
def reject_leave_application(
    leave_id: int,
    rejection_reason: Optional[str] = None,
    current_user=Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Reject a leave application"""
    manager_employee = get_manager_employee(current_user, db)
    
    # Get the leave application and verify it belongs to an employee under this manager
    leave = db.query(LeaveApplication).join(Employee).filter(
        and_(
            LeaveApplication.leave_id == leave_id,
            Employee.manager_id == manager_employee.employee_id,
            LeaveApplication.status == 'pending'
        )
    ).first()
    
    if not leave:
        raise HTTPException(status_code=404, detail="Leave application not found or not under your management")
    
    # Reject the leave
    leave.status = 'rejected'
    leave.approved_by_id = current_user.id
    leave.approved_date = datetime.utcnow()
    
    db.commit()
    db.refresh(leave)
    
    return {"message": "Leave application rejected successfully"}

# === DASHBOARD ENDPOINTS ===

@router.get("/manager/dashboard")
def get_manager_dashboard(
    current_user=Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Get manager dashboard data"""
    manager_employee = get_manager_employee(current_user, db)
    
    # Get team size
    team_size = db.query(Employee).filter(Employee.manager_id == manager_employee.employee_id).count()
    
    # Get pending leave applications count
    pending_leaves_count = db.query(LeaveApplication).join(Employee).filter(
        and_(
            Employee.manager_id == manager_employee.employee_id,
            LeaveApplication.status == 'pending'
        )
    ).count()
    
    # Get today's attendance statistics
    today = date.today()
    
    # Get all team members
    team_employees = db.query(Employee).filter(Employee.manager_id == manager_employee.employee_id).all()
    employee_ids = [emp.employee_id for emp in team_employees]
    
    if employee_ids:
        # Get today's attendance summary
        today_attendance = db.query(AttendanceSummary).filter(
            and_(
                AttendanceSummary.employee_id.in_(employee_ids),
                AttendanceSummary.date == today
            )
        ).all()
        
        present_today = len([a for a in today_attendance if a.status == 'present'])
        absent_today = len([a for a in today_attendance if a.status == 'absent'])
        half_day_today = len([a for a in today_attendance if a.status == 'half_day'])
    else:
        present_today = absent_today = half_day_today = 0
    
    return {
        "team_size": team_size,
        "pending_leave_requests": pending_leaves_count,
        "today": {
            "present": present_today,
            "absent": absent_today,
            "half_day": half_day_today,
            "total_team": team_size
        },
        "date": today.isoformat()
    }