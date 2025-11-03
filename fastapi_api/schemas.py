from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime, time

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class AdminSignup(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    mobile: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str  # 'admin', 'manager', 'employee'
    employee_code: Optional[str] = None
    mobile: Optional[str] = None

# Employee/Profile schemas
class EmployeeBase(BaseModel):
    employee_code: str
    first_name: str
    last_name: str
    email: str
    mobile: Optional[str] = None
    department_name: Optional[str] = None
    designation_name: Optional[str] = None

class EmployeeProfile(EmployeeBase):
    employee_id: int
    profile_picture: Optional[str] = None
    status: bool

# Attendance schemas
class AttendanceLogBase(BaseModel):
    punch_type: str  # 'IN' or 'OUT'
    punch_time: datetime
    geo_lat: Optional[float] = None
    geo_long: Optional[float] = None
    selfie_url: Optional[str] = None

class AttendanceLogCreate(AttendanceLogBase):
    pass

class AttendanceLog(AttendanceLogBase):
    attendance_id: int
    employee_id: int
    status: str

    class Config:
        from_attributes = True

class AttendanceSummaryBase(BaseModel):
    date: date
    in_time: Optional[time] = None
    out_time: Optional[time] = None
    total_hours: Optional[float] = None
    late_by: int
    early_out: int
    status: str

class AttendanceSummary(AttendanceSummaryBase):
    summary_id: int
    employee_id: int

    class Config:
        from_attributes = True

# Leave schemas
class LeaveTypeBase(BaseModel):
    type_name: str
    description: Optional[str] = None
    max_days: int

class LeaveType(LeaveTypeBase):
    type_id: int

    class Config:
        from_attributes = True

class LeaveApplicationBase(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    total_days: float
    reason: str

class LeaveApplicationCreate(LeaveApplicationBase):
    pass

class LeaveApplication(LeaveApplicationBase):
    leave_id: int
    employee_id: int
    status: str
    applied_date: datetime
    approved_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# Payroll schemas
class PayslipBase(BaseModel):
    basic_salary: float
    total_earnings: float
    total_deductions: float
    net_pay: float
    generated_date: datetime

class Payslip(PayslipBase):
    payslip_id: int
    employee_id: int

    class Config:
        from_attributes = True