import os
import sys
import django
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from django.core.asgi import get_asgi_application
from django.core.management import call_command


################################################################
# 1) Setup Django
################################################################

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hexaattendanceportal.settings")
django.setup()


################################################################
# 2) Auto-run Django migrations on startup (FREE Render fix)
################################################################

def run_migrations():
    try:
        print("🔄 Applying Django migrations...")
        call_command("migrate", interactive=False)
        print("✔ Django migrations complete")
    except Exception as e:
        print("❌ Migration Error:", e)


################################################################
# 3) Import FASTAPI Routers (AFTER django.setup())
################################################################

from fastapi_api.routers import admin_auth


################################################################
# 4) Create FASTAPI App
################################################################

app = FastAPI(title="Attendance Portal API", version="1.0.0")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


################################################################
# 5) Run Django migrations when FastAPI starts
################################################################
@app.on_event("startup")
def startup_event():
    run_migrations()


################################################################
# 6) Include FastAPI Routers
################################################################

app.include_router(admin_auth.router)


################################################################
# 7) Mount Django inside FastAPI (UI + Admin Panel)
################################################################

django_app = get_asgi_application()
app.mount("/", django_app)   # ← सबसे important step


################################################################
# 8) Local Run Support
################################################################

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_api.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
