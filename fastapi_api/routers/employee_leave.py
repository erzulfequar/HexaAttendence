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
from models import Employee, LeaveApplication, LeaveType, User
from schemas import LeaveApplicationCreate, LeaveApplication, LeaveType as LeaveTypeSchema

router = APIRouter()

def get_employee_from_user(user, db):
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return employee

@router.post("/employee/leave/apply")
def apply_leave(
    leave: LeaveApplicationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)

    # Validate leave type exists
    leave_type = db.query(LeaveType).filter(LeaveType.type_id == leave.leave_type_id).first()
    if not leave_type:
        raise HTTPException(status_code=404, detail="Leave type not found")

    # Check if leave dates are valid
    if leave.start_date > leave.end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    # Check for overlapping leave applications
    overlapping_leave = db.query(LeaveApplication).filter(
        and_(
            LeaveApplication.employee_id == employee.employee_id,
            LeaveApplication.status.in_(['pending', 'approved']),
            or_(
                and_(
                    LeaveApplication.start_date <= leave.start_date,
                    LeaveApplication.end_date >= leave.start_date
                ),
                and_(
                    LeaveApplication.start_date <= leave.end_date,
                    LeaveApplication.end_date >= leave.end_date
                ),
                and_(
                    LeaveApplication.start_date >= leave.start_date,
                    LeaveApplication.end_date <= leave.end_date
                )
            )
        )
    ).first()

    if overlapping_leave:
        raise HTTPException(status_code=400, detail="You already have a leave application for the same dates")

    # Create leave application
    leave_application = LeaveApplication(
        employee_id=employee.employee_id,
        leave_type_id=leave.leave_type_id,
        start_date=leave.start_date,
        end_date=leave.end_date,
        total_days=leave.total_days,
        reason=leave.reason,
        status="pending"
    )
    db.add(leave_application)
    db.commit()
    db.refresh(leave_application)

    return {"message": "Leave application submitted successfully", "leave_id": leave_application.leave_id}

@router.get("/employee/leave/status")
def get_leave_status(
    page: int = 1,
    limit: int = 20,
    status_filter: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)
    offset = (page - 1) * limit

    query = db.query(LeaveApplication).filter(LeaveApplication.employee_id == employee.employee_id)
    
    if status_filter:
        query = query.filter(LeaveApplication.status == status_filter)

    leave_applications = query.order_by(LeaveApplication.applied_date.desc()).offset(offset).limit(limit).all()
    
    leave_list = []
    for leave in leave_applications:
        # Get leave type name
        leave_type = db.query(LeaveType).filter(LeaveType.type_id == leave.leave_type_id).first()
        leave_type_name = leave_type.type_name if leave_type else None
        
        # Get approver info
        approver_name = None
        if leave.approved_by_id:
            approver = db.query(User).filter(User.id == leave.approved_by_id).first()
            if approver:
                approver_name = f"{approver.first_name} {approver.last_name}"
        
        leave_list.append({
            "leave_id": leave.leave_id,
            "leave_type": leave_type_name,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "total_days": leave.total_days,
            "reason": leave.reason,
            "status": leave.status,
            "applied_date": leave.applied_date,
            "approved_date": leave.approved_date,
            "approved_by": approver_name
        })
    
    return {
        "leaves": leave_list,
        "page": page,
        "limit": limit,
        "total": len(leave_list)
    }

@router.get("/employee/leave/types")
def get_leave_types(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    leave_types = db.query(LeaveType).filter(LeaveType.is_active == True).all()
    return [
        {
            "type_id": lt.type_id,
            "type_name": lt.type_name,
            "description": lt.description,
            "max_days": lt.max_days
        }
        for lt in leave_types
    ]

@router.get("/employee/leave/balance")
def get_leave_balance(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current leave balance"""
    employee = get_employee_from_user(current_user, db)
    current_year = datetime.utcnow().year
    
    # Get all approved leaves for current year
    approved_leaves = db.query(LeaveApplication).filter(
        and_(
            LeaveApplication.employee_id == employee.employee_id,
            LeaveApplication.status == 'approved',
            func.extract('year', LeaveApplication.start_date) == current_year
        )
    ).all()
    
    # Group by leave type
    leave_balance = {}
    
    # Get all leave types
    leave_types = db.query(LeaveType).all()
    
    for leave_type in leave_types:
        # Calculate used days for this leave type
        used_days = sum([
            leave.total_days for leave in approved_leaves 
            if leave.leave_type_id == leave_type.type_id
        ])
        
        leave_balance[leave_type.type_name] = {
            "type_id": leave_type.type_id,
            "max_days": leave_type.max_days,
            "used_days": used_days,
            "remaining_days": leave_type.max_days - used_days
        }
    
    return {
        "year": current_year,
        "leave_balance": leave_balance
    }

@router.get("/employee/leave/calendar")
def get_leave_calendar(
    month: Optional[int] = Query(None, description="Month (1-12)"),
    year: Optional[int] = Query(None, description="Year"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leave calendar for a specific month"""
    employee = get_employee_from_user(current_user, db)
    
    # Default to current month if not specified
    if not month:
        month = datetime.utcnow().month
    if not year:
        year = datetime.utcnow().year
    
    # Get leaves for the specified month
    leaves = db.query(LeaveApplication).filter(
        and_(
            LeaveApplication.employee_id == employee.employee_id,
            func.extract('month', LeaveApplication.start_date) == month,
            func.extract('year', LeaveApplication.start_date) == year
        )
    ).all()
    
    calendar_data = []
    
    for leave in leaves:
        # Get leave type name
        leave_type = db.query(LeaveType).filter(LeaveType.type_id == leave.leave_type_id).first()
        leave_type_name = leave_type.type_name if leave_type else None
        
        # Create calendar entries for each day in the leave period
        current_date = leave.start_date
        while current_date <= leave.end_date:
            calendar_data.append({
                "date": current_date.isoformat(),
                "leave_type": leave_type_name,
                "status": leave.status,
                "total_days": leave.total_days
            })
            # Move to next day
            if isinstance(current_date, datetime):
                current_date = current_date + timedelta(days=1)
            else:
                from datetime import timedelta
                current_date = current_date + timedelta(days=1)
    
    return {
        "month": month,
        "year": year,
        "calendar": calendar_data
    }