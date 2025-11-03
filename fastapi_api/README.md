# FastAPI Attendance Portal API

This FastAPI application provides RESTful APIs for the Android attendance management app, integrating with the existing Django backend.

## Features

- **Authentication**: JWT-based login for secure access
- **Attendance Management**: Mark attendance with selfie upload, view history and summaries
- **Leave Management**: Apply for leave, view leave status and types
- **Profile Management**: Get employee profile information
- **Payroll**: View payslips (read-only)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the API server:
   ```bash
   cd fastapi_api
   python main.py
   ```

   The server will start on `http://localhost:8001`

## API Endpoints

### Authentication
- `POST /api/token` - Login and get JWT token

### Attendance
- `POST /api/attendance/mark` - Mark attendance (with optional selfie)
- `GET /api/attendance/history` - Get attendance history
- `GET /api/attendance/summary` - Get attendance summaries

### Leave
- `POST /api/leave/apply` - Apply for leave
- `GET /api/leave/status` - Get leave applications status
- `GET /api/leave/types` - Get available leave types

### Profile
- `GET /api/profile` - Get employee profile

### Payroll
- `GET /api/payroll/payslips` - Get payslips

## Database

The API uses the same SQLite database as the Django application (`db.sqlite3`). All data written by the Android app via this API will be immediately available in the Django web interface.

## File Uploads

Selfies and other files are stored in the `media/` directory, compatible with Django's media handling.

## Security

- JWT tokens required for all endpoints except login
- CORS enabled for Android app integration
- Input validation using Pydantic models

## Testing

Visit `http://localhost:8001/docs` for interactive API documentation and testing.