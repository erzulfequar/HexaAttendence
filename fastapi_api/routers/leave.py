from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from auth import get_current_user
from models import LeaveApplication, LeaveType
from schemas import LeaveApplicationCreate, LeaveApplication, LeaveType as LeaveTypeSchema
# Helper function to get employee from user
def get_employee_from_user(user, db):
    from models import Employee
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return employee

router = APIRouter()

@router.post("/leave/apply")
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

@router.get("/leave/status", response_model=List[LeaveApplication])
def get_leave_status(
    page: int = 1,
    limit: int = 20,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)
    offset = (page - 1) * limit

    leave_applications = (
        db.query(LeaveApplication)
        .filter(LeaveApplication.employee_id == employee.employee_id)
        .order_by(LeaveApplication.applied_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return leave_applications

@router.get("/leave/types", response_model=List[LeaveTypeSchema])
def get_leave_types(db: Session = Depends(get_db)):
    leave_types = db.query(LeaveType).filter(LeaveType.is_active == True).all()
    return leave_types