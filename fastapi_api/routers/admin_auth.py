from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from datetime import datetime
import sys
import os

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hexaattendanceportal.settings')
import django
django.setup()

from django.db import models
from django.contrib.auth.models import User

# 🔥 Correct Import (IMPORTANT)
from fastapi_api.auth import authenticate_user, create_access_token, verify_token, require_admin_role

from core.models import UserProfile, Role
from master.models import Employee
from fastapi_api.schemas import UserLogin, Token, AdminSignup, UserCreate

router = APIRouter()
security = HTTPBearer()


def get_current_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user from JWT"""
    token = credentials.credentials
    user = verify_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    if not require_admin_role(user.id):
        raise HTTPException(status_code=403, detail="Admin access required")

    return user


# 🔵 API 1: Admin Login
@router.post("/api/admin/login", response_model=Token)
def admin_login(user_credentials: UserLogin):

    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not require_admin_role(user.id):
        raise HTTPException(status_code=403, detail="Admin access required")

    access_token = create_access_token(subject=user.username)

    return {"access_token": access_token, "token_type": "bearer"}


# 🔵 API 2: Signup new admin
@router.post("/api/admin/signup")
def admin_signup(admin_data: AdminSignup):

    if User.objects.filter(username=admin_data.username).exists():
        raise HTTPException(400, "Username already exists")

    if User.objects.filter(email=admin_data.email).exists():
        raise HTTPException(400, "Email already exists")

    # Correct role creation
    admin_role, created = Role.objects.get_or_create(
        role_name="Admin",
        defaults={"description": "System Administrator"}
    )

    user = User.objects.create_user(
        username=admin_data.username,
        email=admin_data.email,
        first_name=admin_data.first_name,
        last_name=admin_data.last_name,
        password=admin_data.password,
        is_active=True
    )

    UserProfile.objects.create(
        user=user,
        role=admin_role,
        mobile=admin_data.mobile,
        status=True
    )

    return {
        "message": "Admin created successfully",
        "user_id": user.id,
        "username": user.username,
        "role": "Admin"
    }


# 🔵 API 3: Add User (Admin Only)
@router.post("/api/admin/add-user")
def add_user(user_data: UserCreate, current_admin=Depends(get_current_admin_user)):

    if User.objects.filter(username=user_data.username).exists():
        raise HTTPException(400, "Username already exists")

    if User.objects.filter(email=user_data.email).exists():
        raise HTTPException(400, "Email already exists")

    # Validate role
    valid_roles = ["Admin", "Manager", "Employee"]
    if user_data.role.capitalize() not in valid_roles:
        raise HTTPException(400, "Invalid role")

    role, created = Role.objects.get_or_create(
        role_name=user_data.role.capitalize(),
        defaults={"description": f"{user_data.role} role"}
    )

    user = User.objects.create_user(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=user_data.password
    )

    UserProfile.objects.create(
        user=user,
        role=role,
        mobile=user_data.mobile,
        status=True
    )

    if user_data.role.lower() == "employee":
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

    return {"message": f"{user_data.role} created", "user_id": user.id}


# 🔵 Verify Token
@router.get("/api/admin/verify-auth")
def verify_auth(current_admin=Depends(get_current_admin_user)):
    return {
        "authenticated": True,
        "user_id": current_admin.id,
        "username": current_admin.username,
        "role": "Admin"
    }


# 🔵 List All Users
@router.get("/api/admin/users")
def list_users(current_admin=Depends(get_current_admin_user)):
    users = User.objects.all(
