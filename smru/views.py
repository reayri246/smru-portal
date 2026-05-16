from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from urllib.parse import quote_plus
import logging
import secrets
import hashlib
import time
import os
import traceback
import requests

from .models import (College, Notification, Event, Complaint, StudentProfile, 
                     Branch, Year, Subject, UserRole, LoginRequest, LoginActivity, 
                     ComplaintCategory, ComplaintPerson, PasswordResetRequest, UserAccountLock)
from .forms import (SignUpForm, LoginForm, ComplaintForm, StudentProfileForm,
                    ForgotPasswordForm, ResetPasswordForm, OtpVerificationForm)

logger = logging.getLogger('smru')

# ======================== URL BUILDER HELPER ========================

def build_public_url(path):
    """Build a public URL using SITE_URL setting for email links."""
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    if path.startswith('/'):
        return f"{site_url}{path}"
    return f"{site_url}/{path}"


# Rate limiting constants
LOGIN_ATTEMPTS_LIMIT = 5  # Maximum login attempts
LOGIN_ATTEMPTS_TIMEOUT = 1800  # 30 minutes in seconds
LOGIN_ATTEMPTS_CACHE_KEY_PREFIX = 'login_attempts_'

# ======================== RATE LIMITING HELPERS ========================

def get_client_ip(request):
    """Get the client IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def is_rate_limited(identifier):
    """Check if the identifier is rate limited."""
    cache_key = f"{LOGIN_ATTEMPTS_CACHE_KEY_PREFIX}{identifier}"
    attempts = cache.get(cache_key, 0)
    return attempts >= LOGIN_ATTEMPTS_LIMIT

def increment_login_attempts(identifier):
    """Increment login attempts for the identifier."""
    cache_key = f"{LOGIN_ATTEMPTS_CACHE_KEY_PREFIX}{identifier}"
    attempts = cache.get(cache_key, 0) + 1
    cache.set(cache_key, attempts, LOGIN_ATTEMPTS_TIMEOUT)

def reset_login_attempts(identifier):
    """Reset login attempts for the identifier (on successful login)."""
    cache_key = f"{LOGIN_ATTEMPTS_CACHE_KEY_PREFIX}{identifier}"
    cache.delete(cache_key)

def get_remaining_attempts(identifier):
    """Get remaining login attempts for the identifier."""
    cache_key = f"{LOGIN_ATTEMPTS_CACHE_KEY_PREFIX}{identifier}"
    attempts = cache.get(cache_key, 0)
    return max(0, LOGIN_ATTEMPTS_LIMIT - attempts)

def get_login_identifier(username_or_email, user=None):
    """Return a stable identifier for login throttling."""
    if user:
        return f"user:{user.username.strip().lower()}"
    if username_or_email:
        return f"input:{username_or_email.strip().lower()}"
    return 'user:unknown'

# ======================== NOTIFICATION HELPERS ========================

def send_email_notification(subject, message, recipient_email):
    """Send an email notification if an email address is available."""
    if not recipient_email:
        return False
    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    try:
        send_mail(
            subject,
            message,
            from_email,
            [recipient_email],
            fail_silently=False,
        )
        logger.info(f"Complaint notification email sent to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending complaint email to {recipient_email}: {str(e)}")
        send_admin_alert(
            subject='SMRU Email Sending Failure',
            message=(
                f'Failed to send an email notification to {recipient_email}.\n\n'
                f'Error: {str(e)}\n\n'
                'Please investigate the email subsystem for failures.'
            ),
            attach_db=True,
        )
        return False


def get_admin_recipients():
    """Return a list of configured admin email recipients."""
    recipients = []
    admin_list = getattr(settings, 'ADMINS', []) or []
    for _, email in admin_list:
        if email:
            recipients.append(email)
    admin_email = getattr(settings, 'ADMIN_EMAIL', '')
    if admin_email and admin_email not in recipients:
        recipients.append(admin_email)
    return recipients


def send_admin_alert(subject, message, attach_db=False):
    """Send an alert email to configured admins, optionally attaching the SQLite database."""
    recipients = get_admin_recipients()
    if not recipients:
        logger.warning('No admin email configured to receive alerts.')
        return False

    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
    email = EmailMessage(subject, message, from_email, recipients)

    if attach_db:
        try:
            db_path = settings.DATABASES['default'].get('NAME', '')
            if db_path and os.path.exists(db_path):
                with open(db_path, 'rb') as db_file:
                    email.attach(os.path.basename(db_path), db_file.read(), 'application/octet-stream')
                    logger.info(f'Attached database file {db_path} to admin alert email.')
        except Exception as attach_error:
            logger.error(f'Unable to attach database file to admin alert email: {str(attach_error)}')

    try:
        email.send(fail_silently=False)
        logger.info('Admin alert email sent successfully.')
        return True
    except Exception as alert_error:
        logger.error(f'Error sending admin alert email: {str(alert_error)}')
        if not attach_db:
            return send_admin_alert(subject, message, attach_db=True)
        return False


def send_whatsapp_message(phone_number, message):
    """Send or prepare a WhatsApp notification for the recipient."""
    if not phone_number:
        return None

    formatted_number = phone_number.strip().replace('+', '').replace(' ', '')
    encoded_message = quote_plus(message)
    whatsapp_url = f"https://wa.me/{formatted_number}?text={encoded_message}"

    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    whatsapp_from = getattr(settings, 'TWILIO_WHATSAPP_FROM', '')

    if account_sid and auth_token and whatsapp_from:
        try:
            api_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            payload = {
                'From': whatsapp_from,
                'To': f'whatsapp:+{formatted_number}',
                'Body': message,
            }
            response = requests.post(api_url, data=payload, auth=(account_sid, auth_token), timeout=15)
            response.raise_for_status()
            logger.info(f"WhatsApp notification sent to {phone_number} via Twilio")
            return whatsapp_url
        except Exception as exc:
            logger.error(f"Error sending WhatsApp notification to {phone_number}: {str(exc)}")
            logger.info(f"Fallback to WhatsApp link: {whatsapp_url}")
            return whatsapp_url

    logger.info(f"WhatsApp notification prepared for {phone_number}: {whatsapp_url}")
    return whatsapp_url


def create_system_notification(title, description, link=None, priority='high', is_public=True, recipient_user=None, recipient_email=None):
    """Create an in-app notification record."""
    Notification.objects.create(
        title=title,
        description=description,
        link=link,
        priority=priority,
        is_active=True,
        is_public=is_public,
        recipient_user=recipient_user,
        recipient_email=recipient_email,
    )

# ======================== AUTHENTICATION VIEWS ========================

def signup(request):
    """User sign up view - handles all registration with login request flow"""
    if request.user.is_authenticated:
        return redirect('smru:home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Create UserRole
            role = form.cleaned_data['role']
            department = form.cleaned_data.get('department', '')
            UserRole.objects.create(user=user, role=role, department=department)

            # Create LoginRequest for every new user; login requires admin approval
            LoginRequest.objects.create(user=user, status='pending')

            # Create StudentProfile if student
            if role == 'student':
                college_obj = form.cleaned_data.get('college')
                other_college_name = form.cleaned_data.get('other_college_name', '')
                roll_number = form.cleaned_data.get('roll_number', '')
                
                # Handle "Other" college case
                if college_obj == 'other':
                    college_name = other_college_name
                    college_obj = None
                    is_from_listed = False
                else:
                    college_name = college_obj.name if college_obj else ''
                    is_from_listed = college_obj is not None
                
                StudentProfile.objects.create(
                    user=user,
                    roll_number=roll_number,
                    college_name=college_name,
                    college=college_obj,
                    branch_name=form.cleaned_data.get('branch', ''),
                    year_name=form.cleaned_data.get('year', ''),
                    phone=form.cleaned_data.get('phone', ''),
                    id_card=form.cleaned_data.get('id_card'),
                    pan_card=form.cleaned_data.get('pan_card'),
                    live_photo=form.cleaned_data.get('live_photo'),
                    is_from_listed_college=is_from_listed,
                    is_approved=False  # Needs admin approval
                )
                
                logger.info(f"New student registered: {user.username}, from {'listed' if is_from_listed else 'unlisted'} college")
            else:
                logger.info(f"New {role} user registered: {user.username}")

            messages.success(request, '''Account created successfully! Your login request has been sent to admin for approval. 
                                 You will receive a notification once your request is approved.''')
            return redirect('smru:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()
    
    # Get filtered colleges if college type is selected
    college_type = request.POST.get('student_college_type') if request.method == 'POST' else ''
    filtered_colleges = []
    if college_type and college_type != 'other':
        filtered_colleges = College.objects.filter(type=college_type)
    
    return render(request, 'smru/signup.html', {
        'form': form,
        'filtered_colleges': filtered_colleges,
        'selected_college_type': college_type
    })


def login_view(request):
    """User login view - enforce global per-account lockout after repeated login attempts."""
    if request.user.is_authenticated:
        return redirect('smru:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Determine user identity for global lockout tracking
            user_to_check = None
            try:
                user_to_check = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                try:
                    user_to_check = User.objects.get(email=username_or_email)
                except User.DoesNotExist:
                    user_to_check = None

            login_identifier = get_login_identifier(username_or_email, user=user_to_check)
            if is_rate_limited(login_identifier):
                remaining_time = LOGIN_ATTEMPTS_TIMEOUT // 60  # Convert to minutes
                messages.error(request, f'Too many login attempts. This account is locked for {remaining_time} minutes.')
                return render(request, 'smru/login.html', {'form': form})
            
            # Check account lock status
            if user_to_check:
                account_lock, created = UserAccountLock.objects.get_or_create(user=user_to_check)
                if account_lock.is_account_locked():
                    remaining_time = int((account_lock.unlock_at - timezone.now()).total_seconds() // 60)
                    messages.error(request, f'Account is temporarily locked due to excessive login attempts. Try again in {remaining_time} minutes.')
                    return render(request, 'smru/login.html', {'form': form})
                
                # Check daily login limit
                if not account_lock.can_login_today():
                    account_lock.lock_account('Exceeded daily login limit', 60)  # Lock for 1 hour
                    messages.error(request, 'You have exceeded the maximum number of logins allowed per day. Account locked for 1 hour.')
                    return render(request, 'smru/login.html', {'form': form})
            
            # Try to authenticate by username first, then by email
            user = authenticate(request, username=username_or_email, password=password)
            if user is None and user_to_check is not None:
                user = authenticate(request, username=user_to_check.username, password=password)

            if user is not None:
                # Check if user is active
                if not user.is_active:
                    increment_login_attempts(login_identifier)
                    remaining_attempts = get_remaining_attempts(login_identifier)
                    messages.error(request, 'Your account is deactivated. Please contact admin.')
                    return render(request, 'smru/login.html', {'form': form})
                
                try:
                    user_role = user.user_role if hasattr(user, 'user_role') else None
                    
                    try:
                        login_request = LoginRequest.objects.get(user=user)
                        if login_request.status == 'pending':
                            increment_login_attempts(login_identifier)
                            messages.warning(request, 'Your login request is pending admin approval. Please wait.')
                            return render(request, 'smru/login.html', {'form': form})
                        elif login_request.status == 'rejected':
                            increment_login_attempts(login_identifier)
                            messages.error(request, 'Your login request has been rejected. Please contact admin for details.')
                            return render(request, 'smru/login.html', {'form': form})
                        elif login_request.status == 'approved':
                            if hasattr(user, 'student_profile') and not user.student_profile.is_approved:
                                user.student_profile.is_approved = True
                                user.student_profile.save()
                    except LoginRequest.DoesNotExist:
                        login_request = None

                    if not login_request and hasattr(user, 'student_profile') and user_role.role == 'student' and not user.student_profile.is_approved:
                        increment_login_attempts(login_identifier)
                        messages.error(request, 'Your profile is pending admin approval. Please wait for final approval.')
                        return render(request, 'smru/login.html', {'form': form})
                
                except (UserRole.DoesNotExist, LoginRequest.DoesNotExist, AttributeError) as e:
                    logger.error(f"Error checking user role/profile: {str(e)}")
                    messages.error(request, 'Your profile is incomplete. Please contact admin.')
                    return render(request, 'smru/login.html', {'form': form})
                
                # Reset login attempts now that the account is fully allowed to login
                reset_login_attempts(login_identifier)

                # Increment daily login count
                if user_to_check:
                    account_lock, created = UserAccountLock.objects.get_or_create(user=user_to_check)
                    account_lock.increment_daily_login()

                # User can login
                login(request, user)
                
                # Record login activity
                LoginActivity.objects.create(
                    user=user,
                    login_time=timezone.now(),
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Session expiry: browser close by default
                if request.POST.get('remember_me') == 'on':
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # expire at browser close

                logger.info(f"User logged in: {user.username}")
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')

                next_url = request.GET.get('next', 'smru:home')
                return redirect(next_url)
            else:
                # Increment login attempts for failed login or blocked account
                increment_login_attempts(login_identifier)
                remaining_attempts = get_remaining_attempts(login_identifier)
                if remaining_attempts > 0:
                    messages.error(request, f'Invalid username/email or password. {remaining_attempts} attempts remaining.')
                else:
                    messages.error(request, f'Invalid username/email or password. Account temporarily locked for {LOGIN_ATTEMPTS_TIMEOUT // 60} minutes due to multiple attempts.')
    else:
        form = LoginForm()
    
    return render(request, 'smru/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    # Record logout activity
    if request.user.is_authenticated:
        try:
            # Get the latest login activity without logout time
            login_activity = LoginActivity.objects.filter(
                user=request.user, 
                logout_time__isnull=True
            ).order_by('-login_time').first()
            if login_activity:
                login_activity.logout_time = timezone.now()
                login_activity.save()
        except Exception as e:
            logger.error(f"Error recording logout activity: {str(e)}")
    
    logger.info(f"User logged out: {request.user.username}")
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('smru:home')


def forgot_password(request):
    """Forgot password view - user initiates password reset"""
    if request.user.is_authenticated:
        return redirect('smru:home')
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            reset_method = form.cleaned_data['reset_method']
            
            # Find user by username or email
            user = None
            try:
                user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
            except User.DoesNotExist:
                # Don't reveal whether user exists
                messages.info(request, 'If an account exists with that username/email, a reset link will be sent.')
                return redirect('smru:forgot_password')
            
            if user:
                # Generate secure token and OTP
                token = secrets.token_urlsafe(32)
                otp = f"{secrets.randbelow(900000) + 100000}"
                reset_request = PasswordResetRequest.objects.create(
                    user=user,
                    token=token,
                    otp=otp,
                    reset_method=reset_method,
                    expires_at=timezone.now() + timezone.timedelta(minutes=5)
                )

                reset_url = build_public_url(reverse('smru:reset_password', args=[token]))
                subject = 'SMRU College Portal Password Reset OTP'
                message_body = (
                    f"Hello {user.get_full_name() or user.username},\n\n"
                    "A password reset request was received for your account. "
                    f"Use the following OTP to verify the reset request:\n\nOTP: {otp}\n\n"
                    f"Then open the reset page: {reset_url}\n\n"
                    "This OTP expires in 5 minutes. If you did not request a password reset, please ignore this message.\n\n"
                    "Thank you,\nSMRU College Portal Team"
                )

                if reset_method == 'email':
                    if not user.email:
                        logger.warning(f"Password reset requested by user {user.username} but no email is available")
                        messages.error(request, 'No email address is available for this account.')
                        return redirect('smru:forgot_password')

                    if send_email_notification(subject, message_body, user.email):
                        logger.info(f"Password reset OTP sent to email {user.email} for user {user.username}")
                        messages.success(request, 'An OTP has been sent to your email. Enter the OTP on the reset page.')
                        return redirect('smru:reset_password', token=token)
                    logger.error(f"Failed to send password reset OTP email to {user.email} for user {user.username}")
                    messages.error(request, 'Unable to send password reset OTP email at this time. Please try again later.')
                    return redirect('smru:forgot_password')

                phone_number = ''
                if hasattr(user, 'student_profile') and user.student_profile.phone:
                    phone_number = user.student_profile.phone
                if not phone_number:
                    logger.warning(f"Password reset requested by user {user.username} but no WhatsApp number is available")
                    messages.error(request, 'No WhatsApp number is available for this account.')
                    return redirect('smru:forgot_password')

                whatsapp_link = send_whatsapp_message(phone_number, message_body)
                if whatsapp_link:
                    logger.info(f"Password reset OTP WhatsApp link prepared for {phone_number} user {user.username}")
                    return redirect(whatsapp_link)

                logger.error(f"Failed to prepare WhatsApp reset OTP for {phone_number} user {user.username}")
                messages.error(request, 'Unable to send WhatsApp OTP at this time. Please try again later.')
                return redirect('smru:forgot_password')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'smru/forgot_password.html', {'form': form})


def reset_password(request, token):
    """Reset password view - user enters OTP and then a new password"""
    try:
        reset_request = PasswordResetRequest.objects.get(token=token)
        
        if reset_request.is_expired or reset_request.status != 'pending':
            messages.error(request, 'Password reset request has expired. Please request a new one.')
            return redirect('smru:forgot_password')
    except PasswordResetRequest.DoesNotExist:
        messages.error(request, 'Invalid password reset request.')
        return redirect('smru:forgot_password')

    if request.method == 'POST':
        if not reset_request.otp_verified:
            otp_form = OtpVerificationForm(request.POST)
            password_form = None
            if otp_form.is_valid():
                entered_otp = otp_form.cleaned_data['otp'].strip()
                if entered_otp == reset_request.otp:
                    reset_request.otp_verified = True
                    reset_request.save()
                    messages.success(request, 'OTP verified. Please enter your new password.')
                    return redirect('smru:reset_password', token=token)
                otp_form.add_error('otp', 'OTP did not match. Please try again.')
        else:
            otp_form = None
            password_form = ResetPasswordForm(request.POST)
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password']
                user = reset_request.user
                user.set_password(new_password)
                user.save()

                reset_request.status = 'completed'
                reset_request.completed_at = timezone.now()
                reset_request.save()

                logger.info(f"Password reset completed for user: {user.username}")
                messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
                return redirect('smru:login')
    else:
        otp_form = None if reset_request.otp_verified else OtpVerificationForm()
        password_form = ResetPasswordForm() if reset_request.otp_verified else None

    return render(request, 'smru/reset_password.html', {
        'otp_form': otp_form,
        'form': password_form,
        'token': token,
        'otp_verified': reset_request.otp_verified,
    })


# ======================== HOME & MAIN PAGES ========================

@login_required(login_url='smru:login')
def home(request):
    """Home page with colleges, notifications, and events"""
    try:
        colleges = College.objects.all()
        notifications = Notification.objects.filter(
            is_active=True,
            is_public=True,
        ).exclude(
            expires_at__lt=timezone.now()
        ).order_by('-created_at')[:5]
        
        events = Event.objects.filter(
            date__gte=timezone.now().date()
        ).order_by('date')[:5]
        
        logger.info(f"Home page accessed by {request.user.username if request.user.is_authenticated else 'Anonymous'}")
        
        return render(request, 'smru/home.html', {
            'colleges': colleges,
            'notifications': notifications,
            'events': events,
            'total_colleges': colleges.count(),
            'total_events': Event.objects.count(),
            'total_complaints': Complaint.objects.count(),
        })
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        messages.error(request, 'An error occurred while loading the home page.')
        return render(request, 'smru/home.html', {})


@login_required(login_url='smru:login')
def admin_health(request):
    """Admin-only health view showing basic service status."""
    if not request.user.is_staff and not request.user.is_superuser:
        return HttpResponseForbidden('Access denied.')

    health = {
        'site_status': 'ok',
        'timestamp': timezone.now(),
        'database_status': 'unknown',
        'email_status': 'configured' if getattr(settings, 'EMAIL_HOST', '') else 'not configured',
        'admin_emails': get_admin_recipients(),
    }

    try:
        from django.db import connections
        with connections['default'].cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        health['database_status'] = 'ok'
    except Exception as e:
        health['database_status'] = f'error: {str(e)}'
        logger.error(f'Health check database error: {str(e)}')

    return render(request, 'smru/admin_health.html', {
        'health': health,
        'site_url': getattr(settings, 'SITE_URL', ''),
    })


def notifications_view(request):
    """All notifications page with pagination"""
    try:
        notifications = Notification.objects.filter(
            is_active=True,
            is_public=True,
        ).exclude(
            expires_at__lt=timezone.now()
        ).order_by('-created_at')
        
        # Pagination
        paginator = Paginator(notifications, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'smru/notifications.html', {
            'notifications': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        })
    except Exception as e:
        logger.error(f"Error in notifications view: {str(e)}")
        return render(request, 'smru/notifications.html', {'error': 'Could not load notifications'})


@login_required(login_url='smru:login')
def staff_notifications_view(request):
    """Staff-only notifications assigned to the logged-in user."""
    staff_roles = ['hod', 'chairman', 'principal', 'director', 'faculty', 'security', 'admin']
    if not (hasattr(request.user, 'user_role') and request.user.user_role.role in staff_roles):
        messages.warning(request, 'You do not have access to assigned notifications.')
        return redirect('smru:home')

    try:
        notifications = Notification.objects.filter(
            is_active=True,
            is_public=False,
        ).exclude(
            expires_at__lt=timezone.now()
        ).filter(
            Q(recipient_user=request.user) | Q(recipient_email__iexact=request.user.email)
        ).order_by('-created_at')
        
        paginator = Paginator(notifications, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'smru/staff_notifications.html', {
            'notifications': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        })
    except Exception as e:
        logger.error(f"Error in staff notifications view: {str(e)}")
        return render(request, 'smru/staff_notifications.html', {'error': 'Could not load staff notifications'})


def events_view(request):
    """All events page with filters"""
    try:
        events = Event.objects.all().order_by('-date')
        
        # Filter by status
        status = request.GET.get('status')
        if status:
            events = events.filter(status=status)
        
        # Pagination
        paginator = Paginator(events, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'smru/events.html', {
            'events': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'current_status': status,
        })
    except Exception as e:
        logger.error(f"Error in events view: {str(e)}")
        return render(request, 'smru/events.html', {'error': 'Could not load events'})


def notes(request):
    """Unified notes page - College type and college selection"""
    try:
        college_type = request.GET.get('type', 'engineering')  # Default to engineering
        colleges_list = College.objects.filter(type=college_type)
        college_id = request.GET.get('college')
        branch_id = request.GET.get('branch')
        year_id = request.GET.get('year')
        
        branches = []
        years = []
        subjects = []
        
        if college_id:
            try:
                college = College.objects.get(id=college_id, type=college_type)
                branches = college.branches.all()
                
                if branch_id:
                    branch = branches.get(id=branch_id)
                    years = branch.years.all()
                    
                    if year_id:
                        year = years.get(id=year_id)
                        subjects = year.subjects.all()
            except (College.DoesNotExist, Branch.DoesNotExist, Year.DoesNotExist):
                messages.error(request, 'Invalid selection.')
        
        return render(request, 'smru/notes.html', {
            'college_types': [('engineering', 'Engineering'), ('medical', 'Medical')],
            'colleges': colleges_list,
            'branches': branches,
            'years': years,
            'subjects': subjects,
            'selected_type': college_type,
            'selected_college': college_id,
            'selected_branch': branch_id,
            'selected_year': year_id,
        })
    except Exception as e:
        logger.error(f"Error in notes view: {str(e)}")
        return render(request, 'smru/notes.html', {'error': 'Error loading materials'})

def engineering_notes(request):
    """Engineering notes - Branch and subject selection"""
    try:
        colleges_list = College.objects.filter(type='engineering')
        college_id = request.GET.get('college')
        branch_id = request.GET.get('branch')
        year_id = request.GET.get('year')
        
        branches = []
        years = []
        subjects = []
        
        if college_id:
            try:
                college = College.objects.get(id=college_id, type='engineering')
                branches = college.branches.all()
                
                if branch_id:
                    branch = branches.get(id=branch_id)
                    years = branch.years.all()
                    
                    if year_id:
                        year = years.get(id=year_id)
                        subjects = year.subjects.all()
            except (College.DoesNotExist, Branch.DoesNotExist, Year.DoesNotExist):
                messages.error(request, 'Invalid selection.')
        
        return render(request, 'smru/engineering.html', {
            'colleges': colleges_list,
            'branches': branches,
            'years': years,
            'subjects': subjects,
            'selected_college': college_id,
            'selected_branch': branch_id,
            'selected_year': year_id,
        })
    except Exception as e:
        logger.error(f"Error in engineering_notes view: {str(e)}")
        return render(request, 'smru/engineering.html', {'error': 'Error loading materials'})
    """Engineering notes - Branch and subject selection"""
    try:
        colleges_list = College.objects.filter(type='engineering')
        college_id = request.GET.get('college')
        branch_id = request.GET.get('branch')
        year_id = request.GET.get('year')
        
        branches = []
        years = []
        subjects = []
        
        if college_id:
            try:
                college = College.objects.get(id=college_id, type='engineering')
                branches = college.branches.all()
                
                if branch_id:
                    branch = branches.get(id=branch_id)
                    years = branch.years.all()
                    
                    if year_id:
                        year = years.get(id=year_id)
                        subjects = year.subjects.all()
            except (College.DoesNotExist, Branch.DoesNotExist, Year.DoesNotExist):
                messages.error(request, 'Invalid selection.')
        
        return render(request, 'smru/engineering.html', {
            'colleges': colleges_list,
            'branches': branches,
            'years': years,
            'subjects': subjects,
            'selected_college': college_id,
            'selected_branch': branch_id,
            'selected_year': year_id,
        })
    except Exception as e:
        logger.error(f"Error in engineering_notes view: {str(e)}")
        return render(request, 'smru/engineering.html', {'error': 'Error loading materials'})


def medical_notes(request):
    """Medical notes - Branch and subject selection"""
    try:
        colleges_list = College.objects.filter(type='medical')
        college_id = request.GET.get('college')
        branch_id = request.GET.get('branch')
        year_id = request.GET.get('year')
        
        branches = []
        years = []
        subjects = []
        
        if college_id:
            try:
                college = College.objects.get(id=college_id, type='medical')
                branches = college.branches.all()
                
                if branch_id:
                    branch = branches.get(id=branch_id)
                    years = branch.years.all()
                    
                    if year_id:
                        year = years.get(id=year_id)
                        subjects = year.subjects.all()
            except (College.DoesNotExist, Branch.DoesNotExist, Year.DoesNotExist):
                messages.error(request, 'Invalid selection.')
        
        return render(request, 'smru/medical.html', {
            'colleges': colleges_list,
            'branches': branches,
            'years': years,
            'subjects': subjects,
            'selected_college': college_id,
            'selected_branch': branch_id,
            'selected_year': year_id,
        })
    except Exception as e:
        logger.error(f"Error in medical_notes view: {str(e)}")
        return render(request, 'smru/medical.html', {'error': 'Error loading materials'})


def student_files(request):
    """Student files and resources"""
    try:
        colleges_list = College.objects.all()
        college_id = request.GET.get('college')
        
        subjects = []
        if college_id:
            try:
                college = College.objects.get(id=college_id)
                # Get all subjects for this college
                subjects = Subject.objects.filter(year__branch__college=college)
            except College.DoesNotExist:
                messages.error(request, 'College not found.')
        
        return render(request, 'smru/student_files.html', {
            'colleges': colleges_list,
            'subjects': subjects,
            'selected_college': college_id,
        })
    except Exception as e:
        logger.error(f"Error in student_files view: {str(e)}")
        return render(request, 'smru/student_files.html', {'error': 'Error loading files'})


def team(request):
    """Team page showing portal contributors."""
    team_members = [
        {'name': 'Mohammed Rehan', 'roll_number': '24D01A66T6', 'role': 'Backend Developer'},
        {'name': 'Mohammed Aftab', 'roll_number': '24D01A66T7', 'role': 'Backend Developer'},
        {'name': 'Mohammed Junaid Hussain', 'roll_number': '24D01A66T8', 'role': 'Backend Developer'},
        {'name': 'P.Manasa', 'roll_number': '24D01A66U2', 'role': 'Frontend Developer'},
        {'name': 'P.Pranathi Reddy', 'roll_number': '24D01A66U3', 'role': 'Frontend Developer'},
    
    ]
    return render(request, 'smru/team.html', {
        'team_members': team_members,
    })




def privacy_policy(request):
    """Privacy policy informational page."""
    return render(request, 'smru/privacy_policy.html')


def terms_of_service(request):
    """Terms of service informational page."""
    return render(request, 'smru/terms_of_service.html')


# ======================== COMPLAINTS ========================

@require_http_methods(["GET", "POST"])
def complaints(request):
    """Complaints submission page"""
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            logger.info(f"New complaint created: ID={complaint.id}, User={request.user.username}")

            # Notify the selected complaint person
            try:
                student_name = request.user.get_full_name() or request.user.username
                complaint_url = build_public_url(reverse('smru:complaint_detail', args=[complaint.id]))
                complaint_link_text = complaint_url

                if complaint.person:
                    person = complaint.person
                    subject = f"New complaint assigned: #{complaint.id}"
                    message_body = (
                        f"A new complaint has been submitted and assigned to you.\n\n"
                        f"Complaint ID: {complaint.id}\n"
                        f"Category: {complaint.category.name}\n"
                        f"Student: {student_name} ({request.user.email})\n"
                        f"Complaint Details:\n{complaint.complaint_text}\n\n"
                    )
                    if complaint.file:
                        file_url = build_public_url(complaint.file.url)
                        message_body += f"Attachment: {file_url}\n\n"
                    message_body += f"View complaint: {complaint_link_text}\n"

                    send_email_notification(subject, message_body, person.email)
                    whatsapp_link = send_whatsapp_message(person.whatsapp_number, message_body)

                    notification_description = (
                        f"A new complaint #{complaint.id} was submitted by {student_name} and assigned to {person.name}. "
                        f"Email sent to {person.email if person.email else 'N/A'}. "
                        f"WhatsApp message {'prepared' if whatsapp_link else 'not sent'}."
                    )
                else:
                    whatsapp_link = None
                    notification_description = (
                        f"A new complaint #{complaint.id} was submitted by {student_name}, "
                        f"but no assigned complaint person was selected. "
                        f"Email and WhatsApp notifications were not sent."
                    )

                if complaint.file:
                    notification_description += " Attachment was included."

                recipient_user = User.objects.filter(email=person.email).first() if complaint.person and complaint.person.email else None
                create_system_notification(
                    title=(f"New complaint assigned to {complaint.person.name}" if complaint.person else f"New complaint #{complaint.id} submitted"),
                    description=notification_description,
                    link=complaint_link_text,
                    priority='high',
                    is_public=False,
                    recipient_user=recipient_user,
                    recipient_email=complaint.person.email if complaint.person and complaint.person.email else None,
                )
            except Exception as exc:
                logger.error(f"Error while sending complaint notifications: {str(exc)}")

            messages.success(request, 'Your complaint has been submitted successfully! Reference ID: {}'.format(complaint.id))
            return redirect('smru:complaints')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = ComplaintForm(user=request.user)
    
    return render(request, 'smru/complaints.html', {'form': form})


@login_required(login_url='smru:login')
def my_complaints(request):
    """View user's submitted complaints"""
    try:
        # Get complaints by user
        user_complaints = Complaint.objects.filter(
            user=request.user
        ).order_by('-submitted_at')
        
        # Handle POST requests for student confirmation of solved complaints
        if request.method == 'POST':
            complaint_id = request.POST.get('complaint_id')
            action = request.POST.get('action')
            
            if complaint_id and action == 'mark_solved':
                try:
                    complaint = Complaint.objects.get(id=complaint_id, user=request.user)
                    if complaint.status in ['resolved', 'closed']:
                        complaint.is_confirmed_solved_by_student = True
                        complaint.save()
                        messages.success(request, 'Thank you. You have confirmed this complaint is solved and you are satisfied with the resolution.')
                    else:
                        messages.error(request, 'You can confirm this complaint only after it is resolved or closed.')
                except Complaint.DoesNotExist:
                    messages.error(request, 'Complaint not found.')
            
            return redirect('smru:my_complaints')
        
        # Pagination
        paginator = Paginator(user_complaints, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'smru/my_complaints.html', {
            'complaints': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
        })
    except Exception as e:
        logger.error(f"Error in my_complaints view: {str(e)}")
        return render(request, 'smru/my_complaints.html', {'error': 'Could not load complaints'})


@login_required(login_url='smru:login')
def manage_complaints(request):
    """Manage complaints based on user role"""
    try:
        user_role = request.user.user_role
    except AttributeError:
        messages.error(request, 'Your role is not configured. Please contact admin.')
        return redirect('smru:home')
    
    try:
        # Filter complaints based on role
        if user_role.role in ['hod', 'chairman', 'principal', 'director', 'faculty', 'security', 'anti_ragging_team', 'she_team']:
            # Get complaints assigned to this user through ComplaintPerson or by matching email if user is not linked.
            complaints = Complaint.objects.none()
            complaint_person = None

            if hasattr(request.user, 'complaint_person'):
                complaint_person = request.user.complaint_person

            if complaint_person:
                complaints = Complaint.objects.filter(person=complaint_person).order_by('-submitted_at')
            elif request.user.email:
                complaints = Complaint.objects.filter(person__email=request.user.email).order_by('-submitted_at')
            else:
                complaints = Complaint.objects.none()
        elif user_role.role == 'admin':
            complaints = Complaint.objects.all().order_by('-submitted_at')
        else:
            # Other roles don't have complaint management access
            messages.error(request, 'You do not have permission to manage complaints.')
            return redirect('smru:home')
        
        # Handle POST requests for actions
        if request.method == 'POST':
            complaint_id = request.POST.get('complaint_id')
            action = request.POST.get('action')
            
            if complaint_id:
                try:
                    complaint = Complaint.objects.get(id=complaint_id)
                    
                    if action == 'mark_solved':
                        complaint.is_confirmed_solved_by_admin = True
                        complaint.cleared_by = request.user
                        if not complaint.resolved_at:
                            complaint.resolved_at = timezone.now()
                        complaint.save()
                        messages.success(request, 'Complaint marked as solved.')
                    
                    elif action == 'update_status':
                        new_status = request.POST.get('status')
                        if new_status in dict(Complaint.STATUS_CHOICES):
                            complaint.status = new_status
                            complaint.save()
                            messages.success(request, f'Complaint status updated to {complaint.get_status_display()}.')
                    
                    elif action == 'add_response':
                        response = request.POST.get('response')
                        if response:
                            complaint.response = response
                            complaint.save()
                            messages.success(request, 'Response added to complaint.')
                
                except Complaint.DoesNotExist:
                    messages.error(request, 'Complaint not found.')
            
            return redirect('smru:manage_complaints')
        
        # Pagination
        paginator = Paginator(complaints, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'smru/manage_complaints.html', {
            'complaints': page_obj,
            'paginator': paginator,
            'page_obj': page_obj,
            'user_role': user_role,
        })
    except UserRole.DoesNotExist:
        messages.error(request, 'Your role is not configured. Please contact admin.')
        return redirect('smru:home')
    except Exception as e:
        logger.error(f"Error in manage_complaints view: {str(e)}")
        return render(request, 'smru/manage_complaints.html', {'error': 'Could not load complaints'})


@login_required(login_url='smru:login')
def complaint_detail(request, complaint_id):
    """View single complaint status"""
    try:
        complaint = get_object_or_404(Complaint, id=complaint_id)

        # Check if user has permission to view this complaint
        if request.user != complaint.user and not request.user.is_staff:
            try:
                user_role = request.user.user_role
                if user_role.role not in ['hod', 'chairman', 'principal', 'director', 'faculty', 'security', 'admin']:
                    messages.error(request, 'You do not have permission to view this complaint.')
                    return redirect('smru:home')
            except:
                messages.error(request, 'Your role is not configured.')
                return redirect('smru:home')

        if request.method == 'POST' and request.user == complaint.user:
            action = request.POST.get('action')
            if action == 'mark_solved':
                if complaint.status in ['resolved', 'closed']:
                    if request.POST.get('confirm_solved') == '1':
                        if not complaint.is_confirmed_solved_by_student:
                            complaint.is_confirmed_solved_by_student = True
                            complaint.save()
                            messages.success(request, 'You have confirmed the complaint as solved.')
                        else:
                            messages.info(request, 'This complaint was already confirmed as solved by you.')
                    else:
                        messages.error(request, 'Please check the confirmation box before submitting.')
                else:
                    messages.error(request, 'Only resolved or closed complaints can be confirmed as solved.')
                return redirect('smru:complaint_detail', complaint_id=complaint.id)

        return render(request, 'smru/complaint_detail.html', {'complaint': complaint})
    except Exception as e:
        logger.error(f"Error in complaint_detail view: {str(e)}")
        messages.error(request, 'An error occurred while loading the complaint.')
        return redirect('smru:my_complaints')


# ======================== USER PROFILE ========================

@login_required(login_url='smru:login')
def profile(request):
    """User profile page"""
    try:
        student_profile, created = StudentProfile.objects.get_or_create(
            user=request.user,
            defaults={
                'roll_number': request.user.username,
            }
        )
        
        if request.method == 'POST':
            form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
            if form.is_valid():
                form.save()
                logger.info(f"User profile updated: {request.user.username}")
                messages.success(request, 'Profile updated successfully!')
                return redirect('smru:profile')
        else:
            form = StudentProfileForm(instance=student_profile)
        
        return render(request, 'smru/profile.html', {
            'form': form,
            'student_profile': student_profile,
        })
    except Exception as e:
        logger.error(f"Error in profile view: {str(e)}")
        messages.error(request, 'An error occurred.')
        return redirect('smru:home')


# ======================== AJAX VIEWS ========================

@require_http_methods(["GET"])
def get_colleges_by_type(request):
    """AJAX endpoint to get colleges filtered by type"""
    college_type = request.GET.get('type', '')
    
    if not college_type:
        return JsonResponse({'error': 'College type is required'}, status=400)
    
    try:
        colleges = College.objects.filter(type=college_type).values('id', 'name')
        college_data = list(colleges)
        # Always include "Other" option
        college_data.append({'id': 'other', 'name': 'Other'})
        return JsonResponse({'colleges': college_data})
    except Exception as e:
        logger.error(f"Error fetching colleges by type: {str(e)}")
        return JsonResponse({'error': 'Failed to load colleges'}, status=500)


def get_persons_by_category(request):
    """AJAX endpoint to get complaint persons filtered by category"""
    category_id = request.GET.get('category_id', '')
    
    if not category_id:
        return JsonResponse({'error': 'Category ID is required'}, status=400)
    
    try:
        persons = ComplaintPerson.objects.filter(
            category_id=category_id,
            is_active=True
        ).values('id', 'name', 'designation', 'email')
        persons_data = list(persons)
        return JsonResponse({'persons': persons_data})
    except Exception as e:
        logger.error(f"Error fetching persons by category: {str(e)}")
        return JsonResponse({'error': 'Failed to load persons'}, status=500)

def error_404(request, exception):
    """404 error handler"""
    return render(request, 'smru/404.html', status=404)


def error_500(request):
    """500 error handler"""
    logger.error("500 error occurred")
    return render(request, 'smru/500.html', status=500)