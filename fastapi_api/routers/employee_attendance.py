from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, date
import os
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from auth import get_current_user, get_user_role
from models import Employee, AttendanceLog, AttendanceSummary, Department, Designation
from schemas import AttendanceLogCreate, AttendanceLog, AttendanceSummary as AttendanceSummarySchema
# Helper function to get employee from user
def get_employee_from_user(user, db):
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return employee

router = APIRouter()

@router.post("/employee/attendance/mark")
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

@router.get("/employee/attendance/history")
def get_attendance_history(
    page: int = 1,
    limit: int = 50,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)
    offset = (page - 1) * limit

    query = db.query(AttendanceLog).filter(AttendanceLog.employee_id == employee.employee_id)
    
    if start_date:
        query = query.filter(func.date(AttendanceLog.punch_time) >= start_date)
    if end_date:
        query = query.filter(func.date(AttendanceLog.punch_time) <= end_date)

    attendance_logs = query.order_by(AttendanceLog.punch_time.desc()).offset(offset).limit(limit).all()
    
    return {
        "employee": {
            "employee_id": employee.employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}"
        },
        "attendance_logs": [
            {
                "attendance_id": log.attendance_id,
                "punch_type": log.punch_type,
                "punch_time": log.punch_time,
                "geo_lat": log.geo_lat,
                "geo_long": log.geo_long,
                "selfie_url": log.selfie_url,
                "status": log.status
            }
            for log in attendance_logs
        ]
    }

@router.get("/employee/attendance/summary")
def get_attendance_summary(
    page: int = 1,
    limit: int = 30,
    month: Optional[int] = Query(None, description="Month (1-12)"),
    year: Optional[int] = Query(None, description="Year"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = get_employee_from_user(current_user, db)
    offset = (page - 1) * limit

    # Default to current month if not specified
    if not month:
        month = datetime.utcnow().month
    if not year:
        year = datetime.utcnow().year

    summaries = db.query(AttendanceSummary).filter(
        and_(
            AttendanceSummary.employee_id == employee.employee_id,
            func.extract('month', AttendanceSummary.date) == month,
            func.extract('year', AttendanceSummary.date) == year
        )
    ).order_by(AttendanceSummary.date.desc()).offset(offset).limit(limit).all()
    
    # Calculate month statistics
    month_summaries = db.query(AttendanceSummary).filter(
        and_(
            AttendanceSummary.employee_id == employee.employee_id,
            func.extract('month', AttendanceSummary.date) == month,
            func.extract('year', AttendanceSummary.date) == year
        )
    ).all()
    
    total_days = len(month_summaries)
    present_days = len([s for s in month_summaries if s.status == 'present'])
    absent_days = len([s for s in month_summaries if s.status == 'absent'])
    half_days = len([s for s in month_summaries if s.status == 'half_day'])
    leave_days = len([s for s in month_summaries if s.status == 'leave'])
    
    return {
        "month": month,
        "year": year,
        "statistics": {
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "half_days": half_days,
            "leave_days": leave_days,
            "attendance_percentage": round((present_days + half_days * 0.5) / total_days * 100, 2) if total_days > 0 else 0
        },
        "summaries": summaries
    }

@router.get("/employee/attendance/today")
def get_today_attendance(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Get today's attendance status"""
    employee = get_employee_from_user(current_user, db)
    today = date.today()
    
    # Get today's attendance summary
    today_summary = db.query(AttendanceSummary).filter(
        and_(
            AttendanceSummary.employee_id == employee.employee_id,
            AttendanceSummary.date == today
        )
    ).first()
    
    # Get today's attendance logs
    today_logs = db.query(AttendanceLog).filter(
        and_(
            AttendanceLog.employee_id == employee.employee_id,
            func.date(AttendanceLog.punch_time) == today
        )
    ).order_by(AttendanceLog.punch_time).all()
    
    return {
        "date": today.isoformat(),
        "status": today_summary.status if today_summary else "not_marked",
        "summary": {
            "in_time": today_summary.in_time if today_summary else None,
            "out_time": today_summary.out_time if today_summary else None,
            "total_hours": today_summary.total_hours if today_summary else None,
            "late_by": today_summary.late_by if today_summary else 0
        },
        "logs": [
            {
                "punch_type": log.punch_type,
                "punch_time": log.punch_time,
                "selfie_url": log.selfie_url
            }
            for log in today_logs
        ]
    }

@router.get("/employee/attendance/stats")
def get_attendance_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance statistics for a date range"""
    employee = get_employee_from_user(current_user, db)
    
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date.replace(day=1)
    
    summaries = db.query(AttendanceSummary).filter(
        and_(
            AttendanceSummary.employee_id == employee.employee_id,
            AttendanceSummary.date >= start_date,
            AttendanceSummary.date <= end_date
        )
    ).all()
    
    # Calculate statistics
    total_days = len(summaries)
    present_days = len([s for s in summaries if s.status == 'present'])
    absent_days = len([s for s in summaries if s.status == 'absent'])
    half_days = len([s for s in summaries if s.status == 'half_day'])
    leave_days = len([s for s in summaries if s.status == 'leave'])
    
    # Calculate total working hours
    total_hours = sum([s.total_hours or 0 for s in summaries])
    avg_hours = total_hours / total_days if total_days > 0 else 0
    
    # Calculate late arrivals and early departures
    late_days = len([s for s in summaries if s.late_by > 0])
    early_days = len([s for s in summaries if s.early_out > 0])
    
    return {
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        },
        "statistics": {
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "half_days": half_days,
            "leave_days": leave_days,
            "working_days": present_days + half_days + leave_days,
            "attendance_percentage": round((present_days + half_days * 0.5) / total_days * 100, 2) if total_days > 0 else 0,
            "total_hours": round(total_hours, 2),
            "average_hours_per_day": round(avg_hours, 2),
            "late_arrivals": late_days,
            "early_departures": early_days
        }
    }