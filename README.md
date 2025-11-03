# HexaAttendance Portal

A comprehensive Django-based Attendance & Workforce Management System designed for admin portals similar to etimeoffice.com.

## Features

- **Secure Authentication**: Role-based login system (Admin, Manager, Employee)
- **Dashboard**: Real-time attendance statistics with charts and summaries
- **Master Data Management**: CRUD operations for Departments, Designations, Employees, Shifts, Devices, Holidays
- **Attendance Tracking**: Live attendance view, logs, selfie approvals, correction requests
- **Leave Management**: Application, approval, and tracking system
- **Reports**: Daily/Monthly reports with export functionality
- **Settings**: Company profile, attendance rules, work week configuration
- **Admin Panel**: Full Django admin interface for data management

## Tech Stack

- **Backend**: Django 5.2.4
- **Frontend**: HTML, CSS, Bootstrap 5
- **Database**: Microsoft SQL Server (configurable)
- **Charts**: Chart.js for data visualization

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hexaattendanceportal
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**:
   - Update `hexaattendanceportal/settings.py` with your SQL Server credentials
   - Or use SQLite for development (already configured)

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data** (optional):
   ```bash
   python manage.py shell < sample_data.py
   ```

8. **Run the server**:
   ```bash
   python manage.py runserver
   ```

9. **Access the application**:
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Default Credentials

- **Username**: admin
- **Password**: (set during superuser creation)

## Project Structure

```
hexaattendanceportal/
├── core/                 # Authentication and dashboard
├── master/               # Master data management
├── attendance/           # Attendance tracking
├── leave/                # Leave management
├── reports/              # Reporting system
├── settings/             # System settings
├── hexaattendanceportal/ # Project settings
├── static/               # Static files
├── media/                # Media files
└── templates/            # HTML templates
```

## Database Configuration

### For SQL Server:
Update `DATABASES` in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'attendance_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
    }
}
```

### For SQLite (Development):
Already configured in `settings.py`.

## API Endpoints (Future Integration)

- `/api/login/` - User authentication
- `/api/attendance/punch/` - Record attendance punch
- `/api/attendance/logs/` - Get attendance logs
- `/api/employee/{id}/` - Employee details
- `/api/leave/apply/` - Apply for leave

## Features Overview

### Dashboard
- Total employees count
- Today's attendance summary (Present/Absent/On Leave)
- Department-wise attendance charts
- Monthly attendance trends
- Recent attendance logs

### Master Module
- Department management
- Designation management
- Employee records
- Shift configuration
- Device registration
- Holiday calendar

### Attendance Module
- Live attendance monitoring
- Punch logs (IN/OUT)
- Selfie verification system
- Attendance corrections
- Manual approvals

### Leave Module
- Leave type configuration
- Leave applications
- Approval workflow
- Leave balance tracking

### Reports Module
- Daily attendance reports
- Monthly summaries
- Late/Early reports
- Device status reports
- Export to Excel/CSV

### Settings Module
- Company profile management
- Attendance rules configuration
- Work week settings
- Notification preferences

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team.