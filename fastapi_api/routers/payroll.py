from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from auth import get_current_user
from models import Payslip
from schemas import Payslip as PayslipSchema
# Helper function to get employee from user
def get_employee_from_user(user, db):
    from models import Employee
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return employee

router = APIRouter()

@router.get("/payroll/payslips", response_model=List[PayslipSchema])
def get_payslips(
    page: int = 1,
    limit: int = 12,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)
    offset = (page - 1) * limit

    payslips = (
        db.query(Payslip)
        .filter(Payslip.employee_id == employee.employee_id)
        .order_by(Payslip.generated_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return payslips