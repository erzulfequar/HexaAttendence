# Unified Django + FastAPI Setup Instructions

## Project Structure
```
attendance_project/
├── manage.py
├── hexaattendanceportal/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py   👈 (edited - unified server)
│   └── ...
├── fastapi_api/
│   ├── main.py   👈 (FastAPI code here)
│   └── routers/
│       └── ...
├── requirements.txt   👈 (updated)
└── Procfile          👈 (created)
```

## Local Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Start Unified Server
```bash
uvicorn hexaattendanceportal.asgi:application --reload
```

### 4. Access Points

**Django Admin** → http://127.0.0.1:8000/admin
**Django Web App** → http://127.0.0.1:8000/
**FastAPI Health Check** → http://127.0.0.1:8000/api/health
**FastAPI Documentation** → http://127.0.0.1:8000/api/docs
**FastAPI Alternative Docs** → http://127.0.0.1:8000/redoc

## Deployment (Render/Railway/Heroku)

### For Render:
1. Connect your repository
2. Add environment variable: `PORT=10000`
3. Procfile is already configured: `web: uvicorn hexaattendanceportal.asgi:application --host 0.0.0.0 --port $PORT`

### For Railway:
1. Deploy from GitHub
2. Procfile auto-detected
3. Environment variables configured automatically

## Key Features ✅

- ✅ **One Server**: Django and FastAPI running on same uvicorn instance
- ✅ **One Port**: Both frameworks accessible on port 8000 (or deployment port)
- ✅ **Unified Authentication**: FastAPI can access Django user sessions
- ✅ **Cross-Framework Communication**: Django models accessible from FastAPI
- ✅ **Deployment Ready**: Works on Render, Railway, Heroku

## FastAPI Routes (Available at /api/*)
- `GET /api/health` - Health check
- `POST /api/admin/register` - Admin registration
- `POST /api/admin/login` - Admin login
- Additional routes available in `fastapi_api/routers/`

## Django Admin Access
- URL: `/admin`
- Use Django's built-in admin interface for user management
- All existing Django models and admin functionality preserved

## Troubleshooting

### Common Issues:
1. **Port already in use**: Kill existing processes on port 8000
2. **Module import errors**: Ensure virtual environment is activated
3. **Database errors**: Run migrations with `python manage.py migrate`

### Check Server Status:
- Visit `/api/health` to verify FastAPI is running
- Visit `/admin` to verify Django is running
- Check terminal for any import or connection errors