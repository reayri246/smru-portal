# SMRU College Portal
- Name of the application: SMRU College Portal
- Developed by: Mohammad Rehan
- Technology stack used: Django 4.2.16, Python 3.8+, SQLite, HTML5, CSS3, JavaScript, Bootstrap

## Table of Contents
1. [Project Overview](#project-overview)
2. [Abstract](#abstract)
3. [Introduction](#introduction)
4. [Features](#features)
5. [Technology Stack](#technology-stack)
6. [System Architecture](#system-architecture)
7. [Database Design](#database-design)
8. [Modules Description](#modules-description)
9. [Security Implementation](#security-implementation)
10. [API Documentation](#api-documentation)
11. [Workflow of the Application](#workflow-of-the-application)
12. [Installation & Deployment](#installation--deployment)
13. [Testing](#testing)
14. [Bug Fixes and Stability](#bug-fixes-and-stability)
15. [Migration Guide](#migration-guide)
16. [Project Status](#project-status)
17. [File Structure](#file-structure)
18. [Notes](#notes)
19. [Enhanced Features & Environment Configuration](#enhanced-features--environment-configuration)
    - [New Features Implemented](#new-features-implemented)
    - [Why .env File is Critical](#why-env-file-is-critical)
    - [Environment Variables Configuration](#environment-variables-configuration)
    - [Feature Details](#feature-details)

---

## Project Overview

**SMRU College Portal** is a Django-based college management portal designed to connect students, faculty, and administrators through a unified web application. It provides study materials, notifications, event management, complaint submission, and profile handling with secure access and administrative oversight.

## Abstract

The SMRU College Portal is a comprehensive Django-based web application designed to serve as a centralized platform for college students and administrators. The system provides access to study materials, complaint management, notifications, events, and user profile management. The primary purpose is to digitize and streamline college administrative processes while providing students with easy access to academic resources. The main problem solved is the lack of a unified digital platform for student-administrator communication and resource sharing in educational institutions.

## Introduction

### Background of the Project
The project was developed to address the growing need for digital transformation in educational institutions. Traditional paper-based complaint systems and scattered study materials create inefficiencies and communication barriers between students and college administration. The SMRU College Portal aims to create a centralized, secure, and user-friendly platform that serves both students and administrators.

### Why This Project Was Developed
The project was developed to:

- Provide students with easy access to organized study materials
- Create an efficient complaint management system
- Enable real-time notifications and event management
- Establish secure user authentication and role-based access
- Reduce administrative overhead through automation

### Objectives of the System
- Provide secure user authentication with role-based access control
- Enable organized access to study materials by college, branch, and year
- Implement a comprehensive complaint management system
- Deliver real-time notifications and event management
- Ensure data security and privacy protection
- Provide responsive and user-friendly interface

## Features

### Core Features
- User authentication with login, signup, and password recovery
- Role-based access control for students and administrators
- Dashboard with notifications, events, and study material access
- Structured complaint submission and status tracking
- Student profile management with document upload support
- Custom admin panel for management of colleges, events, notifications, and complaints

### Additional Features
- Dynamic form filtering for colleges, branches, and complaint categories
- File upload and media handling for student documents and complaints
- Notification priority levels and expiry management
- Event registration and status tracking
- Rate limiting on login attempts
- Environment-based configuration for secure deployment

## Technology Stack

### Frontend
- HTML5 and CSS3
- Bootstrap 5 for responsive layout and components
- JavaScript for dynamic behavior and AJAX calls
- Django templates for server-rendered views

### Backend
- Django 4.2.16 web framework
- Python 3.7+ programming language
- Django ORM for database operations
- Django forms for validation and user input

### Database
- SQLite for development
- PostgreSQL support for production deployments
- Django ORM provides SQL injection protection and data abstraction

### APIs
- Internal AJAX endpoints for dynamic content
- Google Drive integration for study material links
- JSON response endpoints for frontend interactions

### Hosting / Deployment
- Gunicorn WSGI server for Python application hosting
- WhiteNoise for static file serving
- Nginx recommended as reverse proxy
- Environment-based configuration with python-decouple

### Security Tools
- Django security middleware and built-in protections
- CSRF token enforcement
- XSS prevention via template auto-escaping
- Rate limiting with Django cache
- Secure password hashing through Django auth
- HTTPS and security headers in production

## System Architecture

The application uses the Django Model-View-Template architecture.

### Interaction Flow
- User sends HTTP request to Django URL router
- Request passes through middleware for security, authentication, and session handling
- View functions process business logic, query models, and return templates or JSON
- Templates render HTML and client-side scripts
- Static assets are served through WhiteNoise or web server

### Example View Code
```python
@login_required(login_url='smru:login')
def manage_complaints(request):
    complaints = Complaint.objects.order_by('-submitted_at')
    return render(request, 'smru/manage_complaints.html', {'complaints': complaints})
```

```python
def get_colleges_by_type(request):
    college_type = request.GET.get('type')
    colleges = College.objects.filter(type=college_type).values('id', 'name')
    return JsonResponse({'colleges': list(colleges)})
```

### Request-Response Flow
1. Browser requests a page or endpoint
2. Django URL configuration routes the request
3. View validates input and queries the database
4. Data is rendered in a template
5. Response is returned to the browser

### Authentication Flow
- User submits credentials through login form
- Authentication validates credentials using Django auth
- Rate limiting checks prevent brute force attacks
- Successful login creates a session and redirects to dashboard
- Protected views require login decorators

### File Handling
- Uploaded files are stored in `media/`
- Media path configuration is defined in Django settings
- File fields in models manage student documents and complaint attachments
- Static assets are collected with `collectstatic` and served efficiently

## Database Design

### Main Tables and Relationships
- `UserRole`: One-to-one link to Django `User` for role assignment
- `StudentProfile`: Extended user information with academic details and documents
- `College`, `Branch`, `Year`, `Subject`: Hierarchical academic structure for study materials
- `Notification`: System messages with priority and expiry
- `Event`: College events with status and registration data
- `ComplaintCategory`, `ComplaintPerson`, `Complaint`: Complaint workflow and routing
- `LoginRequest`: Account approval workflow

### Important Fields
- `UserRole.role`, `UserRole.department`
- `StudentProfile.roll_number`, `college`, `branch`, `year`, `phone`
- `Notification.priority`, `expires_at`, `recipient_user`
- `Event.status`, `capacity`, `registered_count`
- `Complaint.status`, `response`, `is_confirmed_solved_by_student`, `is_confirmed_solved_by_admin`

### Example Model Code
```python
class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.CASCADE)
    person = models.ForeignKey(ComplaintPerson, on_delete=models.SET_NULL, null=True, blank=True)
    complaint_text = models.TextField()
    file = models.FileField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    response = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
```

```python
class Notification(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)
```

### ER-style Relationships
- Django User → `UserRole` (1:1)
- Django User → `StudentProfile` (1:1)
- College → Branch → Year → Subject (1:N chaining)
- ComplaintCategory → ComplaintPerson (1:N)
- Complaint → User, ComplaintCategory, ComplaintPerson (many-to-one)

## Modules Description

### Authentication Module
Handles signup, login, logout, password reset, and email verification. Includes rate limiting and session management.

```python
# smru/urls.py
path('signup/', views.signup, name='signup'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('forgot-password/', views.forgot_password, name='forgot_password'),
path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
```

```python
# smru/forms.py
class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')
```

```python
# smru/views.py
@login_required(login_url='smru:login')
def profile(request):
    # profile logic
    pass
```

### Admin Module
Provides interface for managing colleges, branches, years, subjects, notifications, events, complaints, and user roles.

```python
# smru/admin.py
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'status', 'submitted_at')
    list_filter = ('status', 'category')
```

### User Module
Manages student profiles, document uploads, study material browsing, and complaint submissions.

```python
# smru/models.py
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
```

```python
# smru/forms.py
class ComplaintForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    roll = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Complaint
        fields = ('category', 'person', 'complaint_text', 'file')
```

### Database Module
Uses Django ORM for models, migrations, and database operations. Supports SQLite for development and PostgreSQL for production.

```python
# smru/models.py
class College(models.Model):
    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=COLLEGE_TYPE_CHOICES, default='engineering')
```

### API Module
Contains AJAX endpoints required for dependent dropdowns and dynamic data loading.

```python
# smru/urls.py
path('api/colleges-by-type/', views.get_colleges_by_type, name='get_colleges_by_type'),
path('api/persons-by-category/', views.get_persons_by_category, name='get_persons_by_category'),
```

```python
# smru/views.py
def get_persons_by_category(request):
    category_id = request.GET.get('category_id')
    persons = ComplaintPerson.objects.filter(category_id=category_id, is_active=True)
    data = [{'id': p.id, 'name': p.name} for p in persons]
    return JsonResponse({'persons': data})
```

### Security Module
Enforces CSRF protection, input validation, rate limiting, secure cookie settings, and password hashing.

```python
# config/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

```python
# smru/views.py
LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_ATTEMPTS_TIMEOUT = 1800
```

### Reporting Module
Implements notification delivery, event tracking, complaint status reports, and administrative summaries.

## Security Implementation

### Authentication
- Django-built authentication
- Session-based login
- Password hashing with PBKDF2
- Password reset with token verification

### Authorization
- Role-based access control through `UserRole`
- Admin-only sections in Django admin
- View-level login requirements

### CSRF Protection
- `CsrfViewMiddleware` enabled in middleware
- CSRF tokens included in all forms

### SQL Injection Prevention
- Django ORM used for all database access
- No raw SQL in views or models

### XSS Prevention
- Django template auto-escaping
- Form validation before rendering user input

### Rate Limiting
- Login attempts limited to 5 failures per 15 minutes for non-staff users
- Login attempt counters reset on success
- Staff users are exempt from rate limiting

### Password Security
- Secure hashing through Django auth
- Random secret key from environment
- Recommended production values for secure cookies

```python
# config/settings.py
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())
```

### Environment Variables
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, and email database credentials stored in environment
- `python-decouple` used for configuration

```python
# config/settings.py
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
```
## API Documentation

### Authentication Endpoints
- `GET /signup/` — Registration page
- `GET /login/` — Login page
- `POST /login/` — Authenticate user
- `GET /logout/` — Logout user
- `GET /forgot-password/` — Forgot password form
- `POST /forgot-password/` — Send password reset token
- `GET /reset-password/<token>/` — Reset password form

### Main Pages
- `GET /` — Home page
- `GET /notifications/` — Notifications list
- `GET /staff-notifications/` — Staff notifications
- `GET /events/` — Events page
- `GET /engineering/` — Engineering study materials
- `GET /medical/` — Medical study materials
- `GET /student-files/` — Student files
- `GET /team/` — Team page
- `GET /privacy-policy/` — Privacy policy
- `GET /terms-of-service/` — Terms of service

### Complaints
- `GET /complaints/` — Complaint submission form
- `POST /complaints/` — Submit complaint
- `GET /my-complaints/` — View a user’s complaints
- `GET /complaint/<int:complaint_id>/` — Complaint details
- `GET /manage-complaints/` — Admin complaint management

### AJAX Endpoints
- `GET /api/colleges-by-type/` — Fetch colleges filtered by type
- `GET /api/persons-by-category/` — Fetch persons filtered by complaint category

## Workflow of the Application

1. User registers and creates profile information
2. Admin approves login requests if required
3. User logs in and accesses the dashboard
4. User browses study materials by college, branch, year, and subject
5. User submits complaints through the complaint module
6. Admin reviews and responds to complaints
7. Notifications and events inform users of updates
8. Users update profiles and monitor complaint statuses

## Installation & Deployment

### Local Installation
1. Clone the repository
   ```bash
git clone <repository-url>
cd college_portal
```
2. Create a virtual environment
   ```bash
python -m venv venv
venv\Scripts\activate
```
3. Install dependencies
   ```bash
pip install -r requirements.txt
```
4. Create `.env` from template
   ```bash
copy .env.example .env
```
5. Edit `.env` file with project-specific values
6. Run database migrations
   ```bash
python manage.py migrate
```
7. Create a superuser
   ```bash
python manage.py createsuperuser
```
8. Collect static files
   ```bash
python manage.py collectstatic --noinput
```
9. Start the development server
   ```bash
python manage.py runserver
```

### Deployment
1. Prepare production environment
   - Use PostgreSQL as the production database if available
   - Install Gunicorn and Nginx
   - Configure environment variables on the server
2. Configure the application for production
   - Set `DEBUG=False`
   - Set `ALLOWED_HOSTS` to your domain or IP addresses
   - Set `SECRET_KEY` in the environment
3. Configure the web server
   - Use Gunicorn to serve the Django WSGI app
   - Use Nginx as reverse proxy for static/media and SSL termination
4. Collect static files
   ```bash
python manage.py collectstatic --noinput
```
5. Apply database migrations
   ```bash
python manage.py migrate
```
6. Configure SSL/TLS certificates
   - Use Let's Encrypt or equivalent
7. Configure automated backups and monitoring

### Environment Configuration
Configure `.env` for local and production environments. Example values:

```env
DEBUG=False
SECRET_KEY=your-secure-secret
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
SITE_URL=https://yourdomain.com
```

#### Example `.env` setup for local development
```env
DEBUG=True
SECRET_KEY=local-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=1025
EMAIL_USE_TLS=False
```

#### Example `.env` setup for production
```env
DEBUG=False
SECRET_KEY=your-production-secret
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/college_portal
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
SITE_URL=https://yourdomain.com
```

### Notes
- Ensure `SECRET_KEY` is not committed to version control.
- Use a secure value for `EMAIL_HOST_PASSWORD` and store it as a secret.
- For production, set secure cookie flags and use HTTPS.

## Testing

### Unit Testing
- Django test framework used for model and view tests
- Focus on form validation, model integrity, and view behavior

### Integration Testing
- Test end-to-end user workflows such as signup, login, complaint submission, and profile updates
- Ensure page navigation and data persistence across requests

### Manual Testing
- Verify UI behavior on different pages
- Confirm file uploads work as expected
- Test role-based access control and admin features

### Security Testing
- Verify CSRF protection on forms
- Test login rate limiting behavior
- Check SQL injection resistance through ORM usage
- Confirm XSS protection via template escaping

### Error Handling
- Custom `404` and `500` error pages
- Form validation messages displayed to users
- Logging enabled for server-side errors

## Bug Fixes and Stability

### Notable Fixes
- Fixed static file configuration for production and development
- Resolved signup form field errors and invalid template filters
- Corrected namespaced login URLs for protected views
- Adjusted debug mode defaults for development

### Result
The portal is now stable and fully operational with all major pages working. The complaint system, event management, notifications, and user profile modules are functioning as intended.

## Migration Guide

### Working with Migrations
- Run `python manage.py makemigrations` after model changes
- Apply changes with `python manage.py migrate`
- Use `python manage.py showmigrations` to inspect migration state
- For a new field use `python manage.py makemigrations --name add_field`
- Review generated migration files before applying

### Common Tasks
- Add fields: modify `models.py`, then `makemigrations` and `migrate`
- Rename fields: use `RenameField` in migration or follow Django guidance
- Delete fields: remove from model and migrate
- Reset database in development by deleting `db.sqlite3` and rerunning migrations

## Project Status

The application is production-ready and includes:
- Secure authentication and role management
- Academic resource management
- Complaint tracking and resolution
- Event and notification systems
- Admin management support
- Deployment and security configuration

## File Structure

```
college_portal/
├── config/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── smru/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── templates/
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── static/
├── media/
├── logs/
├── manage.py
├── requirements.txt
├── .env.example
└── COMPLETE_DOCUMENTATION.md
```

## Notes

This file consolidates all previous Markdown-based documentation into a single master document. All old documentation `.md` files have been removed from the repository to maintain a single source of reference.
# SMRU College Portal - Enhanced Features & Environment Configuration Guide

## Table of Contents
1. [New Features Implemented](#new-features-implemented)
2. [Why .env File is Critical](#why-env-file-is-critical)
3. [Environment Variables Configuration](#environment-variables-configuration)
4. [Feature Details](#feature-details)

---

## New Features Implemented

### 1. **Admin Crash Alert System**
When the website crashes (unhandled exceptions), automatic email alerts are sent to the configured admin email address.

**What happens:**
- Exception traceback and error details are included in the email
- The complete SQLite database file is attached to the email (for backup/debugging)
- Admins are notified immediately of any critical failures
- Works even when `DEBUG=False` in production

**Configuration:**
```
ADMIN_EMAIL=smruportal.helpline2026@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=smruportal.helpline2026@gmail.com
EMAIL_HOST_PASSWORD=<your-app-password>
```

**How it works:**
- Middleware: `smru/middleware.py` - `AdminErrorAlertMiddleware`
- Catches all unhandled exceptions
- Sends alert email with crash reason and database backup

---

### 2. **Password Reset OTP Expiry (5 Minutes)**
OTP (One-Time Password) for password reset now expires after **5 minutes** instead of 24 hours.

**Security Benefits:**
- Reduced window for brute-force attacks
- Users must act quickly, improving security
- OTP validity clearly communicated in email

**Configuration:**
```python
# In smru/views.py, forgot_password function
expires_at=timezone.now() + timezone.timedelta(minutes=5)
```

**User Experience:**
- Email states: "This OTP expires in 5 minutes"
- Reset page shows: "Enter the 6-digit OTP sent to your email or WhatsApp. The OTP expires in 5 minutes."

---

### 3. **Email System Failure Alerts**
If email sending fails, the admin is automatically notified via email with:
- Details of what email failed to send
- The error message
- Database backup attached

**Scenario:**
- User initiates password reset
- Email system fails to send OTP
- Admin receives alert: "SMRU Email Sending Failure"
- Database is attached to preserve data
- System attempts to resend with database attachment

---

### 4. **Admin-Only Health Check Dashboard**
Access point: `/admin-health/`

**Visible only to:**
- Superusers (`is_superuser=True`)
- Staff members (`is_staff=True`)

**Displays:**
- Site status (ok/error)
- Current timestamp
- Database connectivity status
- Email configuration status
- Configured admin email addresses
- Public site URL

**Security:**
- No sensitive credentials exposed
- Only admins can view
- Returns 403 Forbidden for non-admin users

**URL:** `http://localhost:8000/admin-health/` or `https://yourdomain.com/admin-health/`

---

### 5. **Database Backup on Crashes**
When a critical error occurs:
- SQLite database file (`db.sqlite3`) is automatically attached to the crash alert email
- Admin receives a complete database backup
- Enables quick recovery and data preservation

**File attached as:** `database_backup.sqlite3`

---

## Why .env File is Critical

### **The .env File is the Heart of Your Application's Security & Configuration**

The `.env` file is a **hidden configuration file** that stores sensitive information and environment-specific settings. It's critical for these reasons:

### 1. **Security - Protects Sensitive Data**
```
SECRET_KEY=your-django-secret-key
EMAIL_HOST_PASSWORD=your-email-password
DATABASE_PASSWORD=your-database-password
ADMIN_EMAIL=admin@collegeportal.com
```

**Why it matters:**
- These credentials are **never hardcoded** in source code
- `.env` is listed in `.gitignore` so it's never committed to Git
- Even if someone clones your repo, they can't access passwords
- Each environment (development, staging, production) has its own `.env`

### 2. **Environment-Specific Configuration**
Different settings for different deployments:

**Development (.env local):**
```
DEBUG=True
SECURE_SSL_REDIRECT=False
DATABASE_URL=sqlite:///db.sqlite3
```

**Production (.env on server):**
```
DEBUG=False
SECURE_SSL_REDIRECT=True
DATABASE_URL=postgresql://user:pass@host/db
ADMIN_EMAIL=production-admin@company.com
```

### 3. **Email Configuration**
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=smruportal.helpline2026@gmail.com
EMAIL_HOST_PASSWORD=awzg pzvv ovjb wvqv
ADMIN_EMAIL=smruportal.helpline2026@gmail.com
```

**Without this:**
- No emails sent to users
- No password reset functionality
- No admin alerts on crashes
- System can't notify admins of failures

### 4. **Database Connection**
```
DATABASE_URL=postgresql://user:pass@host:port/dbname
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=smru_portal
DATABASE_USER=smur_user
DATABASE_PASSWORD=YNFe3RX178Uu5JotKqMxPIhEiu2a5Ghd
DATABASE_HOST=dpg-d8205450lvsc73fq9hl0-a.ohio-postgres.render.com
DATABASE_PORT=5432
```

**Why needed:**
- Credentials stored securely
- Can switch databases without code changes
- Easy to deploy to different cloud providers

### 5. **CSRF & Security Settings**
```
CSRF_COOKIE_SECURE=False          # Set to True in production
SESSION_COOKIE_SECURE=False       # Set to True in production
SECURE_SSL_REDIRECT=False         # Set to True in production
SECURE_HSTS_SECONDS=0             # Set to high value in production
```

**Purpose:**
- Prevents form hijacking attacks
- Ensures HTTPS enforcement
- Protects session cookies

### 6. **Dynamic Feature Toggles**
```
DEBUG=True                         # Show detailed errors in development
TWILIO_ACCOUNT_SID=your_sid       # Optional WhatsApp integration
TWILIO_AUTH_TOKEN=your_token      # Optional WhatsApp integration
USE_S3=True                        # Optional AWS S3 storage
```

**Benefit:**
- Enable/disable features without code changes
- No redeployment needed
- Control behavior per environment

---

## Environment Variables Configuration

### **Current .env File Settings**

```ini
# Django Core Settings
DEBUG=True
SECRET_KEY=g5gam)c7$11h*^#*^9f+)sbxit2zl!t_swk@o8m7hrj7-dw-1#
ALLOWED_HOSTS=127.0.0.1,localhost
SITE_URL=https://smru-portal.onrender.com

# Security Settings (set to True in production)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False

# CSRF Configuration
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://smru-portal.onrender.com

# Database Configuration
DATABASE_URL=postgresql://smur_user:YNFe3RX178Uu5JotKqMxPIhEiu2a5Ghd@dpg-d8205450lvsc73fq9hl0-a.ohio-postgres.render.com/smru_portal
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=smru_portal
DATABASE_USER=smur_user
DATABASE_PASSWORD=YNFe3RX178Uu5JotKqMxPIhEiu2a5Ghd
DATABASE_HOST=dpg-d8205450lvsc73fq9hl0-a.ohio-postgres.render.com
DATABASE_PORT=5432

# Email Configuration (CRITICAL FOR ALL FEATURES)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=smruportal.helpline2026@gmail.com
EMAIL_HOST_PASSWORD=awzg pzvv ovjb wvqv
DEFAULT_FROM_EMAIL=noreply@collegeportal.com
ADMIN_EMAIL=smruportal.helpline2026@gmail.com

# WhatsApp / Twilio Configuration (Optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+919642785735

# Logging
DJANGO_LOG_LEVEL=INFO
```

### **Changing .env for Different Environments**

**Before Deploying to Production:**
1. Set `DEBUG=False`
2. Set `SECURE_SSL_REDIRECT=True`
3. Set `SESSION_COOKIE_SECURE=True`
4. Set `CSRF_COOKIE_SECURE=True`
5. Update `ADMIN_EMAIL` to production admin
6. Use production database URL
7. Use production email credentials

---

## Feature Details

### **How Admin Gets Notified**

**Crash Flow:**
```
1. User accesses website
2. Unhandled exception occurs
3. AdminErrorAlertMiddleware catches it
4. Email constructed with:
   - Exception traceback
   - Request details (path, method, user)
   - Remote IP address
   - User agent
   - Database file attached
5. Email sent to ADMIN_EMAIL
6. Exception re-raised (shows 500 error to user)
```

**Email Example:**
```
Subject: [SMRU Portal] Unhandled Exception: /complaints/

A server error occurred at /complaints/
Method: GET
User: student_username
Remote addr: 192.168.1.100
Host: localhost:8000

Exception:
ValueError: invalid literal for int() with base 10: 'abc'

Traceback:
  File "django/core/handlers/exception.py", line 47, in inner
    response = get_response(request)
  File "...views.py", line 125, in complaints
    complaint_id = int(request.GET.get('id'))
ValueError: invalid literal for int() with base 10: 'abc'

[Attachment: database_backup.sqlite3]
```

### **Password Reset Flow with 5-Minute OTP**

```
1. User clicks "Forgot Password"
2. Enters username/email
3. OTP generated: 6-digit code
4. Expires in 5 minutes
5. Email sent with OTP
6. User must enter OTP within 5 minutes
7. After verification, user sets new password
8. Reset complete
```

### **Health Check Access**

**Admin accesses:**
```
http://localhost:8000/admin-health/
```

**Response:**
```
Admin Health Check
Site status: ok
Timestamp: 2026-05-16 09:39:38
Database status: ok
Email configuration: configured
Configured admin emails:
  â€¢ smruportal.helpline2026@gmail.com
Public site URL: https://smru-portal.onrender.com
```

---

## Important Notes

### âš ï¸ **Never Commit .env to Git**
```bash
# .gitignore already includes:
.env
.env.local
.env.*.local
```

### âš ï¸ **Keep .env Backup Safe**
- Store backup in secure location
- Use password manager for credentials
- Rotate passwords periodically

### âš ï¸ **Update .env After Code Changes**
When deploying new features, ensure:
- New environment variables are set
- Server is restarted (reads .env on startup)
- All credentials are valid

### âœ… **Test Email Configuration**
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test email', 'sender@example.com', ['admin@example.com'])
# Should return 1 if successful
```

### âœ… **Check Admin Email**
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.ADMIN_EMAIL)
# Should print: smruportal.helpline2026@gmail.com
```

---

## Summary

| Feature | Enabled | Configuration |
|---------|---------|---|
| Admin Crash Alerts | âœ… | `ADMIN_EMAIL`, email settings |
| OTP Expiry (5 min) | âœ… | Middleware configured |
| Email Failure Alerts | âœ… | Automatic |
| Health Check Dashboard | âœ… | `/admin-health/` URL |
| Database Backup on Crash | âœ… | Automatic attachment |

**The .env file is the foundation of this system.** All features depend on proper configuration in `.env`. Always update it carefully and keep it secure.
