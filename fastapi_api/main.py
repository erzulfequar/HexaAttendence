import os
import sys
import django
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer


##############################################
# 1) Correct Django Path Setup
##############################################

# FastAPI folder: fastapi_api/
# Django project folder: hexaattendanceportal/

# Add project ROOT directory to PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hexaattendanceportal.settings")

# Initialize Django
django.setup()


##############################################
# 2) Import Django-dependent modules
##############################################

from fastapi_api.database import get_db
from fastapi_api.auth import authenticate_user, create_access_token, verify_token
from fastapi_api.schemas import Token, UserLogin
from fastapi_api.routers import admin_auth


##############################################
# 3) Create FastAPI App
##############################################

app = FastAPI(title="Attendance Portal API", version="1.0.0")

# CORS for mobile apps or frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Include Routers
app.include_router(admin_auth.router)


##############################################
# 4) Local Run Support
##############################################
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
