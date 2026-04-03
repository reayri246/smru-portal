@echo off
REM College Portal Quick Setup Script for Windows
REM This script automates the initial setup of the College Portal project

setlocal enabledelayedexpansion

echo ============================================
echo   SMRU College Portal - Quick Setup
echo ============================================
echo.

REM Check Python installation
echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python not found. Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo [*] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [+] Virtual environment created
) else (
    echo [+] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
echo [+] Virtual environment activated
echo.

REM Update pip
echo [*] Updating pip...
python -m pip install --upgrade pip >nul 2>&1
echo [+] Pip updated
echo.

REM Install requirements
echo [*] Installing Python dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    echo [+] Dependencies installed
) else (
    echo [!] requirements.txt not found
    pause
    exit /b 1
)
echo.

REM Create .env file if it doesn't exist
echo [*] Setting up environment variables...
if not exist ".env" (
    copy .env.example .env
    echo [+] Created .env file from template
    echo [!] Please edit .env and add your configuration
) else (
    echo [+] .env file already exists
)
echo.

REM Generate SECRET_KEY
echo [*] Generating SECRET_KEY...
for /f "delims=" %%i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"') do set SECRET_KEY=%%i
echo [+] Generated SECRET_KEY (add to .env)
echo SECRET_KEY=%SECRET_KEY%
echo.

REM Create necessary directories
echo [*] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "media" mkdir media
if not exist "media\complaints" mkdir media\complaints
if not exist "media\college_images" mkdir media\college_images
if not exist "media\events" mkdir media\events
if not exist "media\notifications" mkdir media\notifications
if not exist "media\student_profiles" mkdir media\student_profiles
if not exist "staticfiles" mkdir staticfiles
echo [+] Directories created
echo.

REM Run migrations
echo [*] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo [!] Migration failed
    pause
    exit /b 1
)
echo [+] Migrations applied successfully
echo.

REM Collect static files
echo [*] Collecting static files...
python manage.py collectstatic --noinput >nul 2>&1
echo [+] Static files collected
echo.

REM Create superuser
echo [*] Creating superuser account...
echo Run the following command to create a superuser:
echo python manage.py createsuperuser
echo.

REM Summary
echo ============================================
echo [+] Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your settings
echo 2. Create superuser: python manage.py createsuperuser
echo 3. Run development server: python manage.py runserver
echo 4. Access admin panel: http://localhost:8000/admin
echo.
echo Documentation:
echo - README.md - Project overview and setup
echo - DEPLOYMENT.md - Production deployment guide
echo - ARCHITECTURE.md - System architecture
echo.
echo Happy coding!
echo.
pause
