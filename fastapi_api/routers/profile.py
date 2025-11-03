from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from auth import get_current_user
from models import Employee, Department, Designation
from schemas import EmployeeProfile
# Helper function to get employee from user
def get_employee_from_user(user, db):
    from models import Employee
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return employee

router = APIRouter()

@router.get("/profile", response_model=EmployeeProfile)
def get_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)

    # Get department and designation names
    department_name = None
    designation_name = None

    if employee.department_id:
        department = db.query(Department).filter(Department.department_id == employee.department_id).first()
        department_name = department.department_name if department else None

    if employee.designation_id:
        designation = db.query(Designation).filter(Designation.designation_id == employee.designation_id).first()
        designation_name = designation.designation_name if designation else None

    profile = EmployeeProfile(
        employee_id=employee.employee_id,
        employee_code=employee.employee_code,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        mobile=employee.mobile,
        department_name=department_name,
        designation_name=designation_name,
        profile_picture=employee.profile_picture,
        status=employee.status
    )
    return profile