#!/bin/bash

# College Portal Quick Setup Script
# This script automates the initial setup of the College Portal project

echo "==========================================="
echo "  SMRU College Portal - Quick Setup"
echo "==========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python installation
echo -e "${YELLOW}[*] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}[✓] Found $PYTHON_VERSION${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}[*] Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}[✓] Virtual environment created${NC}"
else
    echo -e "${GREEN}[✓] Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}[*] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}[✓] Virtual environment activated${NC}"
echo ""

# Update pip
echo -e "${YELLOW}[*] Updating pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}[✓] Pip updated${NC}"
echo ""

# Install requirements
echo -e "${YELLOW}[*] Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}[✓] Dependencies installed${NC}"
else
    echo -e "${RED}[!] requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Create .env file if it doesn't exist
echo -e "${YELLOW}[*] Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}[✓] Created .env file from template${NC}"
    echo -e "${YELLOW}[!] Please edit .env and add your configuration${NC}"
else
    echo -e "${GREEN}[✓] .env file already exists${NC}"
fi
echo ""

# Generate SECRET_KEY
echo -e "${YELLOW}[*] Generating SECRET_KEY...${NC}"
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
echo -e "${GREEN}[✓] Generated SECRET_KEY (add to .env)${NC}"
echo "SECRET_KEY=$SECRET_KEY"
echo ""

# Create necessary directories
echo -e "${YELLOW}[*] Creating necessary directories...${NC}"
mkdir -p logs media/complaints media/college_images media/events media/notifications media/student_profiles
mkdir -p staticfiles
echo -e "${GREEN}[✓] Directories created${NC}"
echo ""

# Run migrations
echo -e "${YELLOW}[*] Running database migrations...${NC}"
python manage.py migrate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] Migrations applied successfully${NC}"
else
    echo -e "${RED}[!] Migration failed${NC}"
    exit 1
fi
echo ""

# Collect static files
echo -e "${YELLOW}[*] Collecting static files...${NC}"
python manage.py collectstatic --noinput > /dev/null 2>&1
echo -e "${GREEN}[✓] Static files collected${NC}"
echo ""

# Create superuser
echo -e "${YELLOW}[*] Creating superuser account...${NC}"
echo "Run the following command to create a superuser:"
echo -e "${GREEN}python manage.py createsuperuser${NC}"
echo ""

# Summary
echo "==========================================="
echo -e "${GREEN}[✓] Setup Complete!${NC}"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your settings"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Run development server: python manage.py runserver"
echo "4. Access admin panel: http://localhost:8000/admin"
echo ""
echo "Documentation:"
echo "- README.md - Project overview and setup"
echo "- DEPLOYMENT.md - Production deployment guide"
echo "- ARCHITECTURE.md - System architecture"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
