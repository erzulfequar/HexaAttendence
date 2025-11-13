import os
import sys
import django
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from django.core.asgi import get_asgi_application

###############################################################
# 1) Setup Django
###############################################################

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hexaattendanceportal.settings")
django.setup()


###############################################################
# 2) Import FASTAPI Routers (AFTER django.setup())
###############################################################

from fastapi_api.routers import admin_auth


###############################################################
# 3) Create FASTAPI App
###############################################################

app = FastAPI(title="Attendance Portal API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


###############################################################
# 4) Include FastAPI Routers
###############################################################

app.include_router(admin_auth.router)


###############################################################
# 5) Mount Django App inside FastAPI
###############################################################

django_app = get_asgi_application()
app.mount("/", django_app)   # <-- सबसे जरूरी step


###############################################################
# 6) Local run support
###############################################################

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_api.main:app",
                host="0.0.0.0",
                port=8002,
                reload=True)
