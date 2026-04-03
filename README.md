# SMRU College Portal - Production Ready Website

A comprehensive Django-based college management portal that provides students with access to study materials, notifications, events, and complaint management.

## 📋 Features

### ✅ Core Features
- **User Authentication**: Secure login/signup system with email verification
- **Study Materials**: Access engineering and medical notes organized by college, branch, and year
- **Notifications**: Real-time notifications with priority levels
- **Events Management**: Track upcoming college events with registration
- **Complaint System**: Submit and track complaints with status updates
- **Student Profile**: Manage profile information and academic details
- **Admin Dashboard**: Comprehensive admin interface for content management

### 🔒 Security Features
- CSRF Protection
- XSS Prevention
- SQL Injection Prevention
- Secure password hashing
- SSL/TLS Support
- Environment-based configuration

### 📊 Admin Features
- Beautiful custom admin dashboard
- Bulk complaint management
- Event status tracking
- Notification management with expiry
- Student profile verification
- Logging and monitoring

## � Complaint Management System

### For Administrators

#### How to Access and Read Student Complaints

1. **Login to Admin Panel**
   - Navigate to `/admin/` in your browser
   - Login with your admin credentials

2. **Access Complaints Section**
   - In the admin dashboard, click on **"Complaints"** under the **"SMRU"** section
   - You'll see a list of all student complaints

3. **Reading Complaints**
   - **List View**: Shows complaint ID, student name, roll number, category, status, and preview
   - **Status Indicators**: 
     - 🔴 Red badge = New complaints
     - 🟡 Yellow badge = In Progress
     - 🟢 Green badge = Resolved
     - ⚪ Gray badge = Closed
   - **Response Indicator**: ✓ (green) if you've responded, ✗ (red) if not

4. **Viewing Full Complaint Details**
   - Click on a complaint ID or name to open the detailed view
   - **Complainant Info**: Student name, roll number, email, phone
   - **Complaint Details**: Category, full complaint text, attached files
   - **Admin Response**: Status and your response text

5. **Responding to Complaints**
   - Change the **Status** dropdown (New → In Progress → Resolved → Closed)
   - Write your **Response** in the text area
   - Save the complaint

6. **Bulk Actions**
   - Select multiple complaints using checkboxes
   - Use **Actions** dropdown to:
     - Mark as Resolved
     - Mark as Closed
     - Mark as In Progress

7. **Filtering and Searching**
   - **Filter by**: Status, Category, Submission Date
   - **Search by**: Name, Roll Number, Email, Complaint Text, Response
   - **Date Hierarchy**: Click on date headers to filter by time periods

#### Complaint Categories
- **Academic**: Issues with studies, grades, courses
- **Infrastructure**: Building, classroom, facility problems
- **Faculty**: Teacher-related concerns
- **Facilities**: Library, lab, equipment issues
- **Other**: Miscellaneous complaints

#### Permission Management
To allow other users to view all complaints:
1. Go to **Student Profiles** in admin
2. Edit a user's profile
3. Check **"Can view all complaints"** in the Permissions section
4. Save the profile

Authorized users will see **"All Complaints"** in their navigation menu.

## �🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or pipenv
- Virtual environment (recommended)

### Installation

1. **Clone the Repository**
```bash
git clone <repository-url>
cd college_portal
```

2. **Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup Environment Variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings
# Important: Change SECRET_KEY to a secure value
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

5. **Run Migrations**
```bash
python manage.py migrate
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

8. **Run Development Server**
```bash
python manage.py runserver
```

Visit http://localhost:8000 in your browser

## 📁 Project Structure

```
college_portal/
├── config/              # Project configuration
│   ├── settings.py      # Django settings (production-ready)
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI application
│   └── asgi.py          # ASGI application
├── smru/                # Main application
│   ├── models.py        # Database models
│   ├── views.py         # Views and logic
│   ├── urls.py          # App URL routing
│   ├── forms.py         # Django forms
│   ├── admin.py         # Admin customization
│   └── templates/       # HTML templates
├── static/              # CSS, JS, images
├── media/               # User uploads
├── logs/                # Application logs
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables (.env)

```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DATABASE_URL=sqlite:///db.sqlite3  # Or PostgreSQL for production

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

## 📚 Database Models

### Core Models
- **College**: College information with optional drive links
- **Branch**: Course branches within colleges
- **Year**: Academic years within branches
- **Subject**: Individual subjects with drive links
- **Notification**: Important announcements and updates
- **Event**: College events and activities
- **Complaint**: Student complaints and feedback
- **StudentProfile**: Extended student information

## 🌐 API Endpoints

All endpoints use the `/` prefix and are prefixed with `smru:` namespace.

### Authentication
- `GET /signup/` - Sign up page
- `GET /login/` - Login page
- `POST /login/` - Process login
- `GET /logout/` - Logout

### Main Pages
- `GET /` - Home page
- `GET /notifications/` - All notifications
- `GET /events/` - All events
- `GET /engineering/` - Engineering notes
- `GET /medical/` - Medical notes
- `GET /student-files/` - Student resources

### Complaints
- `GET /complaints/` - Submit complaint form
- `POST /complaints/` - Submit complaint
- `GET /my-complaints/` - View submitted complaints
- `GET /complaint/<id>/` - View complaint details

### User
- `GET /profile/` - View/edit profile (login required)

## 👨‍💼 Admin Panel

Access admin panel at `/admin/` with superuser credentials.

### Admin Features
- Complete model management
- Bulk actions for complaints
- Event status tracking
- Notification scheduling
- Advanced filtering and search
- Activity logging

## 🔐 Security Checklist

For production deployment:

- [ ] Change `SECRET_KEY` to a random, secure value
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Setup `HTTPS/SSL` certificates
- [ ] Configure `SECURE_SSL_REDIRECT = True`
- [ ] Setup email service for notifications
- [ ] Configure database (PostgreSQL recommended)
- [ ] Setup backup strategy
- [ ] Enable logging
- [ ] Configure CORS if needed
- [ ] Setup monitoring and alerts
- [ ] Regular security updates

## 📝 Admin Management Tasks

### Adding Colleges
1. Login to admin panel
2. Navigate to Colleges
3. Click "Add College"
4. Fill in details and save

### Managing Subjects
1. Add College → Branch → Year
2. Then add Subjects to Years
3. Add Google Drive folder IDs for file sharing

### Creating Notifications
1. Go to Notifications section
2. Create new notification
3. Set priority and expiry date
4. Add optional registration link

### Handling Complaints
1. Review complaints in admin
2. Change status (New → In Progress → Resolved)
3. Add response/notes
4. Mark as Closed

## 🚀 Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run application
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Production Checklist
- [ ] Setup reverse proxy (Nginx/Apache)
- [ ] Configure SSL certificates
- [ ] Setup PostgreSQL database
- [ ] Configure Redis for caching
- [ ] Setup logging and monitoring
- [ ] Configure backup automation
- [ ] Setup email service
- [ ] Enable CDN for static files
- [ ] Configure rate limiting
- [ ] Setup health checks

## 📊 Logging

Application logs are stored in `logs/django.log` with the following features:
- Rotating file handler (15MB max per file, 10 backup files)
- Console logging for development
- Error email notifications for production
- Structured logging format with timestamps

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run specific test
python manage.py test smru.tests.TestComplaint

# Generate coverage report
coverage run --source='.' manage.py test
coverage report
```

## 📱 Responsive Design

The application uses Bootstrap 5 for responsive design that works seamlessly on:
- Desktop (1920px+)
- Laptop (1024px - 1920px)
- Tablet (768px - 1024px)
- Mobile (320px - 768px)

## 🛠️ Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database Errors
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

### Media Files Not Uploading
- Check `MEDIA_ROOT` and `MEDIA_URL` settings
- Ensure `/media/` directory is writable
- Verify file upload permissions

## 📧 Email Configuration

For Gmail:
1. Enable 2-Step Verification
2. Create App Password
3. Use app password in `.env`
4. Set `EMAIL_HOST_USER` to your Gmail

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Django documentation
3. Contact development team

## 📄 License

This project is proprietary and confidential.

## 👥 Contributors

- College Portal Development Team

---

**Last Updated**: April 2026
**Version**: 1.0.0-production
#   s m r u  
 