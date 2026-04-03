# Project Architecture & Structure Flow

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│                    (Web Browser / Mobile)                       │
└────────────────────────┬──────────────────────────────────────┘
                         │ HTTP/HTTPS
┌────────────────────────┴──────────────────────────────────────┐
│                     Nginx (Reverse Proxy)                     │
│                    - SSL/TLS Termination                      │
│                    - Static File Serving                      │
│                    - Load Balancing                           │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────┴──────────────────────────────────────┐
│                   Gunicorn WSGI Server                        │
│              (4 Workers for Concurrency)                      │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────┴──────────────────────────────────────┐
│                  Django Application                           │
│   ┌──────────────────────────────────────────────────────┐   │
│   │    URL Routing & Middleware                         │   │
│   │    • CSRF Protection                                │   │
│   │    • Session Management                            │   │
│   │    • Authentication                                │   │
│   └──────────────────────────────────────────────────────┘   │
│   ┌──────────────────────────────────────────────────────┐   │
│   │    Views Layer                                       │   │
│   │    • Authentication (Login/Signup)                  │   │
│   │    • Study Materials (Engineering/Medical)          │   │
│   │    • Notifications & Events                         │   │
│   │    • Complaints Management                          │   │
│   │    • Profile Management                             │   │
│   └──────────────────────────────────────────────────────┘   │
│   ┌──────────────────────────────────────────────────────┐   │
│   │    Models & Business Logic                          │   │
│   │    • Database ORM                                   │   │
│   │    • Relationships & Constraints                    │   │
│   │    • Validation & Processing                        │   │
│   └──────────────────────────────────────────────────────┘   │
└────────────────────────┬──────────────────────────────────────┘
            │            │            │
            ▼            ▼            ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ PostgreSQL   │ │ Redis    │ │ File Storage │
    │ (Database)   │ │ (Cache)  │ │ (Media/Logs) │
    └──────────────┘ └──────────┘ └──────────────┘
```

## Data Flow Architecture

```
USER REQUEST
    │
    ▼
NGINX (Static Files Check)
    │
    ├─ YES ──► RETURN STATIC FILE
    │
    NO
    │
    ▼
GUNICORN/DJANGO
    │
    ▼
MIDDLEWARE CHAIN
    ├─ Security
    ├─ Session
    ├─ CSRF
    └─ Authentication
    │
    ▼
URL ROUTER (smru/urls.py)
    │
    ▼
VIEW FUNCTION/CLASS
    │
    ├─ Check Authentication
    ├─ Validate Input
    ├─ Query Database
    ├─ Process Data
    └─ Render Template
    │
    ▼
TEMPLATE ENGINE
    │
    ├─ HTML Generation
    ├─ CSS/JavaScript
    └─ Static Assets
    │
    ▼
HTML RESPONSE
    │
    ▼
BROWSER RENDERING
```

## Database Schema

```
┌─────────────────────────────────────────────┐
│              College                        │
├─────────────────────────────────────────────┤
│ • id (PK)                                   │
│ • name                                      │
│ • description                               │
│ • drive_link                                │
│ • image                                     │
│ • created_at, updated_at                    │
└────────────┬────────────────────────────────┘
             │
             │ 1-N
             ▼
┌─────────────────────────────────────────────┐
│              Branch                         │
├─────────────────────────────────────────────┤
│ • id (PK)                                   │
│ • college_id (FK)                           │
│ • name                                      │
│ • code                                      │
└────────────┬────────────────────────────────┘
             │
             │ 1-N
             ▼
┌─────────────────────────────────────────────┐
│              Year                           │
├─────────────────────────────────────────────┤
│ • id (PK)                                   │
│ • branch_id (FK)                            │
│ • name (1st/2nd/3rd/4th)                    │
└────────────┬────────────────────────────────┘
             │
             │ 1-N
             ▼
┌─────────────────────────────────────────────┐
│             Subject                         │
├─────────────────────────────────────────────┤
│ • id (PK)                                   │
│ • year_id (FK)                              │
│ • name                                      │
│ • code                                      │
│ • drive_folder_id                           │
│ • drive_link                                │
│ • created_at                                │
└─────────────────────────────────────────────┘
```

## User Management Structure

```
┌──────────────────────────────────────┐
│         Django User Model            │
├──────────────────────────────────────┤
│ • username                           │
│ • email                              │
│ • password (hashed)                  │
│ • first_name, last_name              │
│ • is_active, is_staff, is_superuser  │
│ • date_joined                        │
└──────────┬───────────────────────────┘
           │
           │ 1-1
           ▼
┌──────────────────────────────────────┐
│    StudentProfile (Extended)         │
├──────────────────────────────────────┤
│ • user (FK)                          │
│ • roll_number (unique)               │
│ • college (FK)                       │
│ • branch (FK)                        │
│ • year (FK)                          │
│ • phone                              │
│ • profile_picture                    │
│ • bio                                │
│ • created_at, updated_at             │
└──────────────────────────────────────┘
```

## Application Workflow

### 1. User Registration Flow
```
Sign Up Form (signup.html)
    ↓
SignUpForm Validation
    ↓
Create User with hashed password
    ↓
Redirect to Login
    ↓
Login Page (login.html)
```

### 2. Study Materials Access Flow
```
User selects "Engineering" or "Medical"
    ↓
Choose College
    ↓
Choose Branch (Filtered by College)
    ↓
Choose Year (Filtered by Branch)
    ↓
View Subjects (Filtered by Year)
    ↓
Click subject → Google Drive Link (Opens)
```

### 3. Complaint Submission Flow
```
Complaint Form (complaints.html)
    ↓
Fill Details (Name, Roll, Email, Category, Text, File)
    ↓
File Upload Validation
    ↓
Save to Database
    ↓
Redirect to Confirmation
    ↓
Admin Reviews Complaint
    ↓
Update Status (New → In Progress → Resolved)
    ↓
Add Response → User Notification
```

### 4. Admin Dashboard Flow
```
Admin Panel (/admin)
    ↓
├─ Colleges Management
│  ├─ View/Add/Edit/Delete Colleges
│  └─ Manage Branches → Years → Subjects
│
├─ Notifications Management
│  ├─ Create Notifications (Priority, Expiry)
│  └─ View Status/Analytics
│
├─ Events Management
│  ├─ Create Events
│  ├─ Set Status (Upcoming, Ongoing, Completed)
│  └─ Track Registrations
│
├─ Complaints Management
│  ├─ View All Complaints
│  ├─ Bulk Update Status
│  └─ Add Responses
│
└─ User Management
   ├─ View/Edit Users
   ├─ View Student Profiles
   └─ Manage Permissions
```

## File Organization

```
college_portal/
│
├── config/                          # Project Configuration
│   ├── settings.py                  # Django Settings (Production)
│   ├── urls.py                      # URL Configuration
│   └── wsgi.py, asgi.py             # WSGI/ASGI
│
├── smru/                            # Main Application
│   ├── models.py                    # Database Models
│   ├── views.py                     # Application Logic
│   ├── urls.py                      # App URLs
│   ├── forms.py                     # Django Forms
│   ├── admin.py                     # Admin Customization
│   │
│   ├── migrations/                  # Database Migrations
│   │   ├── 0001_initial.py
│   │   └── ...
│   │
│   └── templates/smru/              # HTML Templates
│       ├── base.html               # Base Template
│       ├── home.html               # Home Page
│       ├── login.html              # Login
│       ├── signup.html             # Sign Up
│       ├── notifications.html      # Notifications
│       ├── events.html             # Events
│       ├── engineering.html        # Engineering Notes
│       ├── medical.html            # Medical Notes
│       ├── student_files.html      # Student Files
│       ├── complaints.html         # Complaints
│       ├── my_complaints.html      # My Complaints
│       ├── complaint_detail.html   # Complaint Details
│       ├── profile.html            # User Profile
│       ├── 404.html               # 404 Error
│       └── 500.html               # 500 Error
│
├── static/                          # Static Files
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/                           # User Uploads
│   ├── complaints/
│   ├── college_images/
│   ├── events/
│   ├── notifications/
│   └── student_profiles/
│
├── logs/                            # Application Logs
│   └── django.log
│
├── requirements.txt                 # Python Dependencies
├── .env.example                     # Environment Template
├── .gitignore                       # Git Ignore
├── README.md                        # Documentation
├── DEPLOYMENT.md                    # Deployment Guide
└── manage.py                        # Django CLI
```

## Security Architecture

```
┌─────────────────────────────────────────────┐
│         External Request                    │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│    HTTPS/SSL Termination (Nginx)            │
│  • Enforced HTTPS Redirect                  │
│  • Security Headers (HSTS, X-Frame-Options) │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│    CSRF Token Verification                  │
│  • All POST requests validated              │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│    Authentication Middleware                │
│  • Session Validation                       │
│  • User Identification                      │
│  • Permission Checks                        │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│    XSS Prevention                           │
│  • Template Auto-escaping                   │
│  • Content Security Policy                  │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│    SQL Injection Prevention                 │
│  • Django ORM Parameterized Queries         │
│  • No Raw SQL                               │
└────────────┬────────────────────────────────┘
             │
             ▼
✓ SAFE REQUEST PROCESSING
```

## Performance Optimizations

```
┌────────────────────────────────────────────┐
│  Browser Caching                           │
│  • Static files cached for 30 days          │
│  • Media files cached for 7 days            │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  Database Optimization                     │
│  • Indexed Fields (date, status, college)  │
│  • Connection Pooling (Production)         │
│  • Query Optimization (select_related)     │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  Application Caching                       │
│  • Session Caching (Redis/Database)        │
│  • Query Result Caching                    │
│  • Template Fragment Caching                │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│  Response Compression                      │
│  • Gzip Compression (Nginx)                │
│  • Minified CSS/JavaScript                 │
└────────────────────────────────────────────┘
```

---

**This architecture ensures scalability, security, and performance for a production college portal.**
