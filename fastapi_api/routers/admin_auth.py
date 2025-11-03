from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from datetime import datetime
import sys
import os

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hexaattendanceportal.settings')
import django
django.setup()

from django.db import models
from auth import authenticate_user, create_access_token, verify_token, require_admin_role
from django.contrib.auth.models import User
from core.models import UserProfile, Role
from master.models import Employee
from schemas import UserLogin, Token, AdminSignup, UserCreate

router = APIRouter()
security = HTTPBearer()

def get_current_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current admin user from JWT token"""
    token = credentials.credentials
    user = verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user has admin role
    if not require_admin_role(user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user

# API 1: Admin Login
@router.post("/api/admin/login", response_model=Token)
def admin_login(
    user_credentials: UserLogin
):
    """Admin login endpoint using Django authentication and JWT token generation"""
    
    # Authenticate user with Django's authentication
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user has admin role
    if not require_admin_role(user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}

# API 2: Admin Signup (Create new admin user using Django User model)
@router.post("/api/admin/signup")
def admin_signup(
    admin_data: AdminSignup
):
    """Create a new admin user using Django's User model"""
    
    # Check if username or email already exists
    existing_user = User.objects.filter(
        models.Q(username=admin_data.username) | models.Q(email=admin_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Get or create Admin role
    admin_role, created = Role.objects.get_or_create(
        role_name__iexact='admin',
        defaults={'role_name': 'Admin', 'description': 'System Administrator'}
    )
    
    # Create Django user
    user = User.objects.create_user(
        username=admin_data.username,
        email=admin_data.email,
        first_name=admin_data.first_name,
        last_name=admin_data.last_name,
        password=admin_data.password,
        is_active=True
    )
    
    # Create user profile
    UserProfile.objects.create(
        user=user,
        role=admin_role,
        mobile=admin_data.mobile,
        status=True
    )
    
    return {
        "message": "Admin user created successfully",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": "Admin"
    }

# API 3: Add User (Admin only)
@router.post("/api/admin/add-user")
def add_user(
    user_data: UserCreate,
    current_admin = Depends(get_current_admin_user)
):
    """Create a new user with specified role (Admin only) using Django User model"""
    
    # Check if username or email already exists
    existing_user = User.objects.filter(
        models.Q(username=user_data.username) | models.Q(email=user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Validate role
    valid_roles = ['admin', 'manager', 'employee']
    if user_data.role.lower() not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    # Get or create role
    role_name = user_data.role.capitalize()
    role, created = Role.objects.get_or_create(
        role_name__iexact=role_name,
        defaults={
            'role_name': role_name,
            'description': f'{role_name} role'
        }
    )
    
    # Create Django user
    user = User.objects.create_user(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=user_data.password,
        is_active=True
    )
    
    # Create user profile
    UserProfile.objects.create(
        user=user,
        role=role,
        employee_id=user_data.employee_code,
        mobile=user_data.mobile,
        status=True
    )
    
    # Create employee record if role is employee
    if user_data.role.lower() == 'employee' and user_data.employee_code:
        Employee.objects.create(
            employee_code=user_data.employee_code,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            mobile=user_data.mobile,
            user=user,
            date_of_joining=datetime.now().date(),
            status=True
        )
    
    return {
        "message": f"{user_data.role.capitalize()} user created successfully",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user_data.role.capitalize()
    }

# Additional helper endpoints
@router.get("/api/admin/verify-auth")
def verify_admin_auth(
    current_admin = Depends(get_current_admin_user)
):
    """Verify admin authentication"""
    return {
        "authenticated": True,
        "user_id": current_admin.id,
        "username": current_admin.username,
        "email": current_admin.email,
        "role": "Admin"
    }

@router.get("/api/admin/users")
def list_users(
    current_admin = Depends(get_current_admin_user)
):
    """List all users (Admin only)"""
    users = User.objects.all().select_related('userprofile__role')
    user_list = []
    
    for user in users:
        profile = getattr(user, 'userprofile', None)
        role_name = profile.role.role_name if profile and profile.role else None
        
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": role_name,
            "is_active": user.is_active,
            "date_joined": user.date_joined
        })
    
    return {"users": user_list}