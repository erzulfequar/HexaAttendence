from sqlalchemy import create_engine
from models import Base
import os

# Use the same database file as the Django project
DATABASE_URL = "sqlite:///db.sqlite3"

def create_tables():
    """Create all database tables"""
    engine = create_engine(DATABASE_URL)
    print("Creating database tables...")
    
    # Import all models to ensure they're registered with Base
    from models import User, Role, UserProfile, Employee, Department, Designation
    from models import AttendanceLog, AttendanceSummary, LeaveType, LeaveApplication, Payslip
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()