from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Float, Boolean, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# Core models
class User(Base):
    __tablename__ = "auth_user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)  # Store hashed password
    is_active = Column(Boolean, default=True)
    date_joined = Column(DateTime, default=datetime.utcnow)

class Role(Base):
    __tablename__ = "core_role"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True)
    description = Column(Text)

class UserProfile(Base):
    __tablename__ = "core_userprofile"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("auth_user.id"))
    role_id = Column(Integer, ForeignKey("core_role.role_id"), nullable=True)
    employee_id = Column(String, unique=True, nullable=True)
    mobile = Column(String, nullable=True)
    status = Column(Boolean, default=True)

# Master models
class Department(Base):
    __tablename__ = "master_department"
    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String, unique=True)
    is_active = Column(Boolean, default=True)

class Designation(Base):
    __tablename__ = "master_designation"
    designation_id = Column(Integer, primary_key=True, index=True)
    designation_name = Column(String, unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

class Employee(Base):
    __tablename__ = "master_employee"
    employee_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("auth_user.id"), nullable=True)
    employee_code = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    mobile = Column(String, nullable=True)
    department_id = Column(Integer, ForeignKey("master_department.department_id"), nullable=True)
    designation_id = Column(Integer, ForeignKey("master_designation.designation_id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("master_employee.employee_id"), nullable=True)
    date_of_joining = Column(Date)
    status = Column(Boolean, default=True)
    profile_picture = Column(String, nullable=True)

# Attendance models
class AttendanceLog(Base):
    __tablename__ = "attendance_attendancelog"
    attendance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("master_employee.employee_id"))
    punch_type = Column(String)  # 'IN' or 'OUT'
    punch_time = Column(DateTime)
    geo_lat = Column(Float, nullable=True)
    geo_long = Column(Float, nullable=True)
    selfie_url = Column(String, nullable=True)
    status = Column(String, default='approved')

class AttendanceSummary(Base):
    __tablename__ = "attendance_attendancesummary"
    summary_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("master_employee.employee_id"))
    date = Column(Date)
    in_time = Column(Time, nullable=True)
    out_time = Column(Time, nullable=True)
    total_hours = Column(Float, nullable=True)
    late_by = Column(Integer, default=0)
    early_out = Column(Integer, default=0)
    status = Column(String, default='present')

# Leave models
class LeaveType(Base):
    __tablename__ = "leave_leavetype"
    type_id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String, unique=True)
    description = Column(Text)
    max_days = Column(Integer, default=30)

class LeaveApplication(Base):
    __tablename__ = "leave_leaveapplication"
    leave_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("master_employee.employee_id"))
    leave_type_id = Column(Integer, ForeignKey("leave_leavetype.type_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    total_days = Column(Float)
    reason = Column(Text)
    status = Column(String, default='pending')
    approved_by_id = Column(Integer, ForeignKey("auth_user.id"), nullable=True)
    applied_date = Column(DateTime, default=datetime.utcnow)
    approved_date = Column(DateTime, nullable=True)

# Payroll models (simplified for API)
class Payslip(Base):
    __tablename__ = "payroll_payslip"
    payslip_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("master_employee.employee_id"))
    basic_salary = Column(Float)
    total_earnings = Column(Float)
    total_deductions = Column(Float)
    net_pay = Column(Float)
    generated_date = Column(DateTime, default=datetime.utcnow)