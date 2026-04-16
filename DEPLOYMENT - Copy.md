# Production Deployment Guide

## Server Setup

### System Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- Nginx web server
- PostgreSQL database
- Supervisor for process management

### Step 1: Server Environment Setup

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql nginx supervisor git
```

### Step 2: Database Setup

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE college_portal;
CREATE USER college_user WITH PASSWORD 'strong_password_here';
ALTER ROLE college_user SET client_encoding TO 'utf8';
ALTER ROLE college_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE college_user SET default_transaction_deferrable TO on;
ALTER ROLE college_user SET default_transaction_level TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE college_portal TO college_user;
\q
```

### Step 3: Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/college_portal
cd /var/www/college_portal

# Clone repository
sudo git clone <repository-url> .
sudo chown -R $USER:$USER /var/www/college_portal

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Edit with production values
```

### Step 4: Django Configuration

```bash
# Create necessary directories
mkdir -p logs staticfiles media

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 5: Gunicorn Configuration

```bash
# Create Gunicorn socket file
sudo nano /etc/systemd/system/college_portal.socket
```

Add:
```
[Unit]
Description=College Portal WSGI Socket

[Socket]
ListenStream=/run/college_portal.sock

[Install]
WantedBy=sockets.target
```

```bash
# Create Gunicorn service file
sudo nano /etc/systemd/system/college_portal.service
```

Add:
```
[Unit]
Description=College Portal WSGI Service
Requires=college_portal.socket
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/college_portal
Environment="PATH=/var/www/college_portal/venv/bin"
ExecStart=/var/www/college_portal/venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/run/college_portal.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable college_portal.socket college_portal.service
sudo systemctl start college_portal.socket college_portal.service
```

### Step 6: Nginx Configuration

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/college_portal
```

Add:
```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your_domain.com www.your_domain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your_domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your_domain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/college_portal_access.log;
    error_log /var/log/nginx/college_portal_error.log;

    # Client upload limit
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /var/www/college_portal/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/college_portal/media/;
        expires 7d;
    }

    # Application
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/college_portal.sock;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/college_portal /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 7: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d your_domain.com -d www.your_domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Step 8: Firewall Configuration

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## Monitoring and Maintenance

### System Monitoring
```bash
# Check application status
sudo systemctl status college_portal.service

# View application logs
tail -f /var/www/college_portal/logs/django.log

# View Nginx logs
tail -f /var/log/nginx/college_portal_*.log

# Monitor system resources
htop
df -h  # Disk usage
free -m  # Memory usage
```

### Database Backup

```bash
# Create backup script
sudo nano /usr/local/bin/backup_college_portal.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/college_portal"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U college_user college_portal | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz /var/www/college_portal/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete
```

```bash
# Make executable and add to cron
chmod +x /usr/local/bin/backup_college_portal.sh
sudo crontab -e

# Add line: 0 2 * * * /usr/local/bin/backup_college_portal.sh
```

### Updates and Patches

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Update Python packages
cd /var/www/college_portal
source venv/bin/activate
pip install -U pip
pip install -U -r requirements.txt

# Run Django migrations
python manage.py migrate

# Restart application
sudo systemctl restart college_portal.service
```

## Performance Optimization

### Caching
- Enable Redis for session caching
- Cache notification queries
- Use CloudFront CDN for static files

### Database Optimization
- Add indexes to frequently queried fields
- Use connection pooling (pgBouncer)
- Regular VACUUM and ANALYZE

### Code Optimization
- Enable gzip compression in Nginx
- Minify CSS/JavaScript
- Use database query optimization

## Monitoring with Tools

### Application Performance Monitoring (APM)
- Setup New Relic or DataDog
- Monitor response times
- Track error rates

### Uptime Monitoring
- Setup Pingdom or UptimeRobot
- Monitor main endpoints
- Setup alerts

### Log Aggregation
- Use ELK Stack (Elasticsearch, Logstash, Kibana)
- Centralize application logs
- Setup log-based alerts

## Security Hardening

### Additional Security Measures
1. **Web Application Firewall (WAF)**
   - Setup ModSecurity
   - Enable DDoS protection

2. **Regular Audits**
   - Code security scanning
   - Dependency vulnerability checks
   - Penetration testing

3. **Access Control**
   - Implement IP whitelisting for admin
   - 2FA for superuser accounts
   - SSH key-based authentication only

## Troubleshooting Production Issues

### Application won't start
```bash
# Check service status
sudo systemctl status college_portal.service

# View service logs
sudo journalctl -u college_portal.service -n 50 --no-pager
```

### 502 Bad Gateway
- Check if Gunicorn is running
- Verify socket permissions
- Check Nginx error logs

### High memory usage
- Check for query N+1 problems
- Review cache configuration
- Increase server resources

---

**For questions or issues, contact the development team.**
