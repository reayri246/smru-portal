# SMRU College Portal - Complete Documentation

## 📋 Table of Contents
1. [Application Overview](#application-overview)
2. [Technical Specifications](#technical-specifications)
3. [System Architecture](#system-architecture)
4. [Database Schema](#database-schema)
5. [Features & Functionality](#features--functionality)
6. [Installation & Setup](#installation--setup)
7. [Deployment Guide](#deployment-guide)
8. [API Documentation](#api-documentation)
9. [Security Features](#security-features)
10. [Performance Optimization](#performance-optimization)
11. [Troubleshooting](#troubleshooting)
12. [Maintenance Guide](#maintenance-guide)

---

## 🎓 Application Overview

### Project Description
The **SMRU College Portal** is a comprehensive web-based platform designed to serve students, faculty, and administrators of SMRU (Sri Muthukumaran Rajagopal Educational) institutions. The portal provides a centralized system for academic resources, complaint management, event coordination, and administrative oversight.

### Key Objectives
- **Digital Transformation**: Modernize college administration and student services
- **Resource Accessibility**: Provide easy access to study materials and academic resources
- **Efficient Communication**: Streamline notifications and announcements
- **Complaint Resolution**: Establish transparent complaint handling mechanisms
- **Event Management**: Coordinate and manage college events effectively

### Target Users
- **Students**: Access study materials, submit complaints, view notifications, register for events
- **Faculty**: Manage academic resources, oversee student activities
- **Administrators**: System management, complaint resolution, content management
- **HODs/Principals**: Department oversight and approval workflows

---

## 🔧 Technical Specifications

### Backend Framework
- **Framework**: Django 4.2.16
- **Python Version**: 3.7+
- **Architecture**: MVT (Model-View-Template) Pattern
- **Database**: SQLite 3 (Development) / PostgreSQL (Production)

### Frontend Technologies
- **HTML5**: Semantic markup and accessibility
- **CSS3**: Responsive design with custom styling
- **Bootstrap 5.3.2**: Component library and grid system
- **Font Awesome 6.4.0**: Icon library
- **JavaScript**: Interactive elements and form validation

### Key Dependencies
```
Django==4.2.16
Pillow==10.4.0
python-decouple==3.8
whitenoise==6.5.0
gunicorn==23.0.0
django-cors-headers==4.0.0
```

### Server Configuration
- **WSGI Server**: Gunicorn
- **Web Server**: Nginx
- **Static Files**: WhiteNoise
- **Process Management**: systemd

---

## 🏗️ System Architecture

### Application Structure
```
college_portal/
├── config/                    # Django Project Configuration
│   ├── settings.py           # Main settings file
│   ├── urls.py               # URL routing
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
│
├── smru/                      # Main Application Module
│   ├── models.py             # Database models (12 models)
│   ├── views.py              # Business logic (20+ views)
│   ├── forms.py              # Form classes (4 forms)
│   ├── urls.py               # App URL patterns
│   ├── admin.py              # Admin customization
│   ├── apps.py               # App configuration
│   ├── tests.py              # Unit tests
│   ├── migrations/           # Database migrations
│   └── templates/smru/       # HTML templates (15+ templates)
│
├── static/                   # Static assets
├── media/                    # User-uploaded files
├── logs/                     # Application logs
├── requirements.txt          # Python dependencies
└── manage.py                 # Django management script
```

### Database Architecture
- **Total Models**: 12 database models
- **Total Views**: 20+ view functions
- **Total Templates**: 15+ HTML templates
- **Total Forms**: 4 form classes

### Security Layers
1. **Application Level**: Django's built-in security features
2. **Database Level**: SQL injection prevention
3. **Network Level**: HTTPS enforcement
4. **File Level**: Secure file upload validation

---

## 🗄️ Database Schema

### Core Models

#### 1. UserRole Model
```python
class UserRole(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('hod', 'Head of Department'),
        ('chairman', 'Chairman'),
        ('principal', 'Principal'),
        ('director', 'Director'),
        ('faculty', 'Faculty'),
        ('security', 'Security'),
        ('anti_ragging_team', 'Anti Ragging Team'),
        ('she_team', 'SHE Team'),
        ('admin', 'Administrator'),
        ('other', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
```

#### 2. College Model
```python
class College(models.Model):
    COLLEGE_TYPE_CHOICES = (
        ('engineering', 'Engineering'),
        ('medical', 'Medical'),
    )
    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=COLLEGE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    drive_link = models.URLField(blank=True)
    image = models.ImageField(upload_to='college_images/')
```

#### 3. StudentProfile Model
```python
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=50, unique=True)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=15)
    id_card = models.ImageField(upload_to='student_id_cards/')
    live_photo = models.ImageField(upload_to='student_live_photos/')
    profile_picture = models.ImageField(upload_to='student_profiles/')
    is_approved = models.BooleanField(default=False)
```

#### 4. Notification Model
```python
class Notification(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)
```

#### 5. Event Model
```python
class Event(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    capacity = models.IntegerField(blank=True, null=True)
    registered_count = models.IntegerField(default=0)
```

#### 6. Complaint System Models
```python
class ComplaintCategory(models.Model):
    CATEGORY_TYPE_CHOICES = (
        ('listed_college', 'For Listed Colleges'),
        ('other_college', 'For Other Colleges'),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES)

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.CASCADE)
    complaint_text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response = models.TextField(blank=True)
    is_confirmed_solved_by_student = models.BooleanField(default=False)
    is_confirmed_solved_by_admin = models.BooleanField(default=False)
```

### Database Relationships
- **UserRole** → One-to-One with Django User
- **College** → Has many Branches
- **Branch** → Has many Years
- **Year** → Has many Subjects
- **StudentProfile** → One-to-One with User, Foreign Keys to College/Branch/Year
- **Complaint** → Foreign Key to User and ComplaintCategory

---

## ✨ Features & Functionality

### 1. Authentication System
- **User Registration**: Email validation and secure signup
- **Login/Logout**: Session-based authentication
- **Password Management**: Secure password hashing (PBKDF2)
- **Role-Based Access**: Different permissions for different user types
- **Profile Management**: User profile editing and photo upload

### 2. Dashboard & Home Page
- **Statistics Dashboard**: Real-time metrics display
- **Hero Section**: Professional gradient design with CTAs
- **Feature Grid**: Animated cards showcasing portal features
- **Notification Feed**: Priority-based notification display
- **Event Calendar**: Upcoming events with registration links
- **Quick Access**: Direct links to study materials

### 3. Study Materials Management
- **College Organization**: Engineering and Medical colleges
- **Branch & Year Structure**: Hierarchical organization
- **Google Drive Integration**: Direct links to subject materials
- **File Organization**: Systematic categorization
- **Access Control**: Role-based material access

### 4. Complaint Management System
- **Category-Based Complaints**: Different categories for different issues
- **File Attachments**: Support for complaint evidence uploads
- **Status Tracking**: Complete complaint lifecycle management
- **Response System**: Admin responses and student feedback
- **Resolution Confirmation**: Dual confirmation system
- **Timeline Tracking**: Complete audit trail

### 5. Event Management
- **Event Creation**: Admin event creation with details
- **Registration System**: Capacity management and registration tracking
- **Status Management**: Upcoming, ongoing, completed status
- **Image Support**: Event promotional images
- **Location & Time**: Complete event scheduling

### 6. Notification System
- **Priority Levels**: Low, Medium, High priority notifications
- **Expiry Management**: Automatic notification expiry
- **Rich Content**: Support for images and links
- **Real-time Display**: Live notification updates
- **Admin Controls**: Complete notification management

### 7. Admin Panel Features
- **Custom Admin Interface**: Enhanced Django admin
- **Bulk Operations**: Mass actions on records
- **Advanced Filtering**: Complex query filtering
- **Search Functionality**: Full-text search capabilities
- **Export Features**: Data export capabilities
- **Audit Logging**: Complete action tracking

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip package manager
- Git
- SQLite3 (for development)

### Local Development Setup

#### 1. Clone Repository
```bash
git clone <repository-url>
cd college_portal
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your settings
```

#### 5. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

#### 6. Load Sample Data (Optional)
```bash
python manage.py shell < create_sample_data.py
```

#### 7. Run Development Server
```bash
python manage.py runserver
```

### Production Deployment

#### Server Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- Nginx web server
- PostgreSQL database (recommended)
- SSL certificate (Let's Encrypt)

#### Deployment Steps
1. **Server Preparation**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-pip python3-venv postgresql nginx git
   ```

2. **Application Setup**
   ```bash
   sudo mkdir -p /var/www/college_portal
   cd /var/www/college_portal
   sudo git clone <repository-url> .
   sudo chown -R www-data:www-data /var/www/college_portal
   ```

3. **Environment Configuration**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Configure production settings in .env
   ```

4. **Database Setup**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE college_portal;
   CREATE USER portal_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE college_portal TO portal_user;
   \q
   ```

5. **Django Configuration**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

6. **Gunicorn Setup**
   ```bash
   sudo nano /etc/systemd/system/college_portal.service
   # Add Gunicorn service configuration
   sudo systemctl daemon-reload
   sudo systemctl enable college_portal
   sudo systemctl start college_portal
   ```

7. **Nginx Configuration**
   ```bash
   sudo nano /etc/nginx/sites-available/college_portal
   # Add Nginx configuration
   sudo ln -s /etc/nginx/sites-available/college_portal /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

8. **SSL Setup**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

---

## 🔒 Security Features

### Authentication & Authorization
- **Password Hashing**: PBKDF2 with SHA256
- **Session Security**: Secure session cookies
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Prevention**: HTML escaping and content security policy
- **SQL Injection Prevention**: Parameterized queries

### Data Protection
- **Encryption**: Sensitive data encryption at rest
- **File Upload Security**: File type and size validation
- **Input Sanitization**: All user inputs validated and sanitized
- **Rate Limiting**: Protection against brute force attacks

### Network Security
- **HTTPS Enforcement**: SSL/TLS encryption
- **Security Headers**: HSTS, CSP, X-Frame-Options
- **CORS Configuration**: Cross-origin resource sharing controls
- **Firewall Rules**: UFW configuration for server protection

### Access Control
- **Role-Based Access**: Different permissions per user role
- **Object-Level Permissions**: Fine-grained access control
- **Admin Restrictions**: Limited admin access
- **Audit Logging**: Complete user action tracking

---

## 📊 Performance Optimization

### Database Optimization
- **Indexing Strategy**: Optimized indexes on frequently queried fields
- **Query Optimization**: Use of select_related and prefetch_related
- **Connection Pooling**: Efficient database connection management
- **Caching Layer**: Redis integration for session and query caching

### Frontend Optimization
- **Static File Optimization**: Compressed and cached static assets
- **Image Optimization**: Automatic image compression with Pillow
- **Lazy Loading**: Progressive content loading
- **Minification**: CSS and JavaScript minification

### Server Optimization
- **Gunicorn Tuning**: Optimized worker processes
- **Nginx Configuration**: Efficient reverse proxy setup
- **Caching Headers**: Appropriate cache control headers
- **Compression**: Gzip compression enabled

### Monitoring & Metrics
- **Application Performance**: Response time monitoring
- **Database Performance**: Query performance tracking
- **System Resources**: CPU, memory, and disk monitoring
- **Error Tracking**: Comprehensive error logging and alerting

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
**Symptoms**: Application fails to start, database errors
**Solutions**:
```bash
# Check database connectivity
python manage.py dbshell

# Verify migrations
python manage.py showmigrations

# Reset database if needed
python manage.py reset_db
python manage.py migrate
```

#### 2. Static Files Not Loading
**Symptoms**: CSS/JS files not loading, broken styling
**Solutions**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check static file settings
python manage.py shell -c "from django.conf import settings; print(settings.STATIC_URL)"
```

#### 3. Permission Errors
**Symptoms**: File upload failures, permission denied errors
**Solutions**:
```bash
# Fix media directory permissions
sudo chown -R www-data:www-data /var/www/college_portal/media/
sudo chmod -R 755 /var/www/college_portal/media/

# Fix log directory permissions
sudo chown -R www-data:www-data /var/www/college_portal/logs/
sudo chmod -R 755 /var/www/college_portal/logs/
```

#### 4. 502 Bad Gateway
**Symptoms**: Nginx returns 502 error
**Solutions**:
```bash
# Check Gunicorn status
sudo systemctl status college_portal

# Check Gunicorn logs
sudo journalctl -u college_portal -n 50

# Restart Gunicorn
sudo systemctl restart college_portal
```

#### 5. Memory Issues
**Symptoms**: Application running slow, high memory usage
**Solutions**:
```bash
# Check system resources
htop
free -m

# Optimize Gunicorn workers
# Reduce worker count in systemd service file
sudo systemctl daemon-reload
sudo systemctl restart college_portal
```

### Debug Mode
Enable debug mode for detailed error information:
```python
# In settings.py
DEBUG = True
```

### Logging Configuration
Check application logs for detailed error information:
```bash
# Development
tail -f logs/django.log

# Production
sudo journalctl -u college_portal -f
```

---

## 🛠️ Maintenance Guide

### Regular Maintenance Tasks

#### 1. Database Maintenance
```bash
# Backup database
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Clean old sessions
python manage.py clearsessions

# Database optimization (PostgreSQL)
VACUUM ANALYZE;
```

#### 2. File System Maintenance
```bash
# Clean old log files
find logs/ -name "*.log" -mtime +30 -delete

# Clean temporary files
find /tmp -name "django_*" -mtime +1 -delete

# Check disk usage
df -h
du -sh /var/www/college_portal/
```

#### 3. Security Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip list --outdated
pip install -U -r requirements.txt

# Security audit
pip install safety
safety check
```

#### 4. Performance Monitoring
```bash
# Check application response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/

# Monitor database connections
python manage.py shell -c "from django.db import connection; print(len(connection.queries))"
```

### Backup Strategy

#### Automated Backups
```bash
# Create backup script
cat > /usr/local/bin/backup_college_portal.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/college_portal"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
python manage.py dumpdata --exclude=auth.permission --exclude=contenttypes > $BACKUP_DIR/data_$TIMESTAMP.json

# Media files backup
tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz media/

# Keep only last 7 days
find $BACKUP_DIR -name "*.json" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup_college_portal.sh
```

#### Cron Job Setup
```bash
# Add to crontab
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup_college_portal.sh
```

### Monitoring Setup

#### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop sysstat

# Check system status
systemctl status college_portal
systemctl status nginx
systemctl status postgresql
```

#### Application Monitoring
```bash
# Check application health
curl -f http://localhost:8000/health/

# Monitor error logs
tail -f logs/django.log | grep ERROR

# Check database connections
python manage.py shell -c "from django.db import connections; print(connections['default'].queries)"
```

---

## 📞 Support & Contact

### Development Team
- **Project Lead**: Development Team
- **Technical Support**: Available via repository issues
- **Documentation**: Comprehensive inline code documentation

### Emergency Contacts
- **System Administrator**: For production issues
- **Database Administrator**: For database-related problems
- **Security Team**: For security incidents

### Reporting Issues
1. Check existing issues in the repository
2. Provide detailed error logs
3. Include system information
4. Describe steps to reproduce

---

## 📈 Future Enhancements

### Planned Features
1. **Mobile Application**: Native iOS and Android apps
2. **API Development**: RESTful API for third-party integrations
3. **Advanced Analytics**: Detailed usage analytics and reporting
4. **Multi-language Support**: Internationalization (i18n)
5. **Real-time Notifications**: WebSocket-based live notifications
6. **Advanced Search**: Elasticsearch integration
7. **Workflow Automation**: Automated approval processes
8. **Integration APIs**: Google Classroom, Microsoft Teams integration

### Technology Upgrades
- **Django 5.0**: Latest Django LTS version
- **Python 3.11+**: Latest Python features
- **PostgreSQL 15+**: Advanced database features
- **Redis Caching**: High-performance caching layer
- **Docker Containerization**: Containerized deployment
- **Kubernetes Orchestration**: Scalable deployment

---

## 📋 Checklist

### Pre-deployment Checklist
- [ ] Environment variables configured
- [ ] Database created and migrated
- [ ] Static files collected
- [ ] Superuser account created
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Backup system in place
- [ ] Monitoring tools configured

### Security Checklist
- [ ] DEBUG = False in production
- [ ] SECRET_KEY properly set
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] File upload restrictions in place
- [ ] Password policies enforced

### Performance Checklist
- [ ] Database indexes optimized
- [ ] Static files compressed
- [ ] Caching configured
- [ ] CDN setup for static assets
- [ ] Database connection pooling
- [ ] Gunicorn workers optimized

---

**Document Version**: 1.0  
**Last Updated**: May 9, 2026  
**Application Version**: 1.0.0  
**Django Version**: 4.2.16  
**Python Version**: 3.7+  

---

*This documentation is comprehensive and covers all aspects of the SMRU College Portal application. For the latest updates, please refer to the project repository.*