from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hexaattendanceportal.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.db import connection

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def authenticate_user(username: str, password: str):
    """Authenticate user using Django's authentication system"""
    try:
        user = User.objects.get(username=username, is_active=True)
        # Use Django's built-in password verification
        if check_password(password, user.password):
            return user
        return False
    except User.DoesNotExist:
        return False

def verify_token(token: str):
    """Verify JWT token and return Django user"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        # Get Django user by username
        try:
            user = User.objects.get(username=username, is_active=True)
            return user
        except User.DoesNotExist:
            return None
    except jwt.PyJWTError:
        return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_role(user_id: int):
    """Get user role from Django UserProfile"""
    from core.models import UserProfile, Role
    
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        if user_profile.role:
            return user_profile.role.role_name
        return None
    except UserProfile.DoesNotExist:
        return None

def require_admin_role(user_id: int):
    """Check if user has admin role"""
    role = get_user_role(user_id)
    return role and role.lower() in ['admin', 'administrator']

def get_employee_from_user_id(user_id: int):
    """Get employee from Django user_id"""
    from master.models import Employee
    
    try:
        employee = Employee.objects.get(user_id=user_id)
        return employee
    except Employee.DoesNotExist:
        return None

def get_current_user_from_employee(employee_id: int):
    """Get Django user from employee"""
    from master.models import Employee
    
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        if employee.user_id:
            user = User.objects.get(id=employee.user_id)
            return user
        return None
    except (Employee.DoesNotExist, User.DoesNotExist):
        return None