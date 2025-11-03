from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from auth import get_current_user
from models import Employee, AttendanceLog, AttendanceSummary
from schemas import AttendanceLogCreate, AttendanceLog, AttendanceSummary as AttendanceSummarySchema
# Helper function to get employee from user
def get_employee_from_user(user, db):
    from models import Employee
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return employee

router = APIRouter()

@router.post("/attendance/mark")
def mark_attendance(
    punch_type: str = Form(...),
    punch_time: Optional[str] = Form(None),
    geo_lat: Optional[float] = Form(None),
    geo_long: Optional[float] = Form(None),
    photo: Optional[UploadFile] = File(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)

    # Handle punch_time
    if punch_time:
        try:
            punch_datetime = datetime.fromisoformat(punch_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid punch_time format")
    else:
        punch_datetime = datetime.utcnow()

    # Handle photo upload
    selfie_url = None
    if photo:
        # Ensure media/selfies directory exists
        os.makedirs("media/selfies", exist_ok=True)
        file_extension = os.path.splitext(photo.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = f"media/selfies/{unique_filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(photo.file.read())
        selfie_url = f"/media/selfies/{unique_filename}"

    # Create attendance log
    attendance_log = AttendanceLog(
        employee_id=employee.employee_id,
        punch_type=punch_type.upper(),
        punch_time=punch_datetime,
        geo_lat=geo_lat,
        geo_long=geo_long,
        selfie_url=selfie_url,
        status="approved"
    )
    db.add(attendance_log)
    db.commit()
    db.refresh(attendance_log)

    return {"message": "Attendance marked successfully", "attendance_id": attendance_log.attendance_id}

@router.get("/attendance/history", response_model=List[AttendanceLog])
def get_attendance_history(
    page: int = 1,
    limit: int = 50,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)
    offset = (page - 1) * limit

    attendance_logs = (
        db.query(AttendanceLog)
        .filter(AttendanceLog.employee_id == employee.employee_id)
        .order_by(AttendanceLog.punch_time.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return attendance_logs

@router.get("/attendance/summary", response_model=List[AttendanceSummarySchema])
def get_attendance_summary(
    page: int = 1,
    limit: int = 30,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)
    offset = (page - 1) * limit

    summaries = (
        db.query(AttendanceSummary)
        .filter(AttendanceSummary.employee_id == employee.employee_id)
        .order_by(AttendanceSummary.date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return summaries