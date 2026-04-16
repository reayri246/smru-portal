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
import logging
import secrets
import hashlib

from .models import (College, Notification, Event, Complaint, StudentProfile, 
                     Branch, Year, Subject, UserRole, LoginRequest, LoginActivity, 
                     ComplaintCategory, ComplaintPerson, PasswordResetRequest)
from .forms import (SignUpForm, LoginForm, ComplaintForm, StudentProfileForm,
                    ForgotPasswordForm, ResetPasswordForm)

logger = logging.getLogger('smru')

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
                hall_ticket = form.cleaned_data.get('hall_ticket_number', '')
                
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
                    roll_number=user.username,
                    hall_ticket_number=hall_ticket,
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
    
    return render(request, 'smru/signup.html', {'form': form})


def login_view(request):
    """User login view - check LoginRequest approval for students"""
    if request.user.is_authenticated:
        return redirect('smru:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Try to authenticate by username first, then by email
            user = authenticate(request, username=username_or_email, password=password)
            if user is None:
                try:
                    user = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user is not None:
                # Check if user is active
                if not user.is_active:
                    messages.error(request, 'Your account is deactivated. Please contact admin.')
                    return render(request, 'smru/login.html', {'form': form})
                
                try:
                    user_role = user.user_role if hasattr(user, 'user_role') else None
                    
                    try:
                        login_request = LoginRequest.objects.get(user=user)
                        if login_request.status == 'pending':
                            messages.warning(request, 'Your login request is pending admin approval. Please wait.')
                            return render(request, 'smru/login.html', {'form': form})
                        elif login_request.status == 'rejected':
                            messages.error(request, 'Your login request has been rejected. Please contact admin for details.')
                            return render(request, 'smru/login.html', {'form': form})
                    except LoginRequest.DoesNotExist:
                        login_request = None

                    # Check if student profile is approved
                    if hasattr(user, 'student_profile') and not user.student_profile.is_approved:
                        messages.error(request, 'Your profile is pending admin approval. Please wait for final approval.')
                        return render(request, 'smru/login.html', {'form': form})
                
                except (UserRole.DoesNotExist, LoginRequest.DoesNotExist, AttributeError) as e:
                    logger.error(f"Error checking user role/profile: {str(e)}")
                    messages.error(request, 'Your profile is incomplete. Please contact admin.')
                    return render(request, 'smru/login.html', {'form': form})
                
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
                messages.error(request, 'Invalid username/email or password.')
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
                # Generate secure token
                token = secrets.token_urlsafe(32)
                
                # Create password reset request
                reset_request = PasswordResetRequest.objects.create(
                    user=user,
                    token=token,
                    reset_method=reset_method,
                    expires_at=timezone.now() + timezone.timedelta(hours=24)
                )
                
                # TODO: Implement actual email/WhatsApp sending here
                # For now, just show success message
                logger.info(f"Password reset requested for user: {user.username}, method: {reset_method}")
                messages.success(request, f'A password reset link has been sent to your {reset_method}.')
                
                # In a real application, you would send here
                # - Email with link containing token
                # - WhatsApp message with link containing token
            
            return redirect('smru:login')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'smru/forgot_password.html', {'form': form})


def reset_password(request, token):
    """Reset password view - user enters new password with token"""
    try:
        reset_request = PasswordResetRequest.objects.get(token=token)
        
        # Check if token is expired
        if reset_request.is_expired or reset_request.status != 'pending':
            messages.error(request, 'Password reset link has expired. Please request a new one.')
            return redirect('smru:forgot_password')
        
    except PasswordResetRequest.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('smru:forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user = reset_request.user
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Mark reset request as completed
            reset_request.status = 'completed'
            reset_request.completed_at = timezone.now()
            reset_request.save()
            
            logger.info(f"Password reset completed for user: {user.username}")
            messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
            return redirect('smru:login')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'smru/reset_password.html', {'form': form, 'token': token})


# ======================== HOME & MAIN PAGES ========================

@login_required(login_url='smru:login')
def home(request):
    """Home page with colleges, notifications, and events"""
    try:
        colleges = College.objects.all()
        notifications = Notification.objects.filter(
            is_active=True
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


def notifications_view(request):
    """All notifications page with pagination"""
    try:
        notifications = Notification.objects.filter(
            is_active=True
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
        })
    except Exception as e:
        logger.error(f"Error in notifications view: {str(e)}")
        return render(request, 'smru/notifications.html', {'error': 'Could not load notifications'})


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


# ======================== STUDY MATERIALS ========================

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
                    branch = Branch.objects.get(id=branch_id)
                    years = branch.years.all()
                    
                    if year_id:
                        year = Year.objects.get(id=year_id)
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
                    branch = Branch.objects.get(id=branch_id)
                    years = branch.years.all()
                    
                    if year_id:
                        year = Year.objects.get(id=year_id)
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
        
        # Handle POST requests for marking as solved
        if request.method == 'POST':
            complaint_id = request.POST.get('complaint_id')
            action = request.POST.get('action')
            
            if complaint_id and action == 'mark_solved':
                try:
                    complaint = Complaint.objects.get(id=complaint_id, user=request.user)
                    complaint.is_confirmed_solved_by_student = True
                    complaint.save()
                    messages.success(request, 'Complaint marked as solved by you.')
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
        if user_role.role in ['hod', 'chairman', 'principal', 'director', 'faculty', 'security']:
            # Get complaints assigned to persons in categories relevant to this role
            complaints = Complaint.objects.filter(
                person__designation__icontains=user_role.get_role_display()
            ).order_by('-submitted_at')
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
            except AttributeError:
                messages.error(request, 'Your role is not configured.')
                return redirect('smru:home')
        
        return render(request, 'smru/complaint_detail.html', {'complaint': complaint})
    except Exception as e:
        logger.error(f"Error in complaint_detail view: {str(e)}")
        return redirect('smru:complaints')


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


# ======================== ERROR HANDLERS ========================

def error_404(request, exception):
    """404 error handler"""
    return render(request, 'smru/404.html', status=404)


def error_500(request):
    """500 error handler"""
    logger.error("500 error occurred")
    return render(request, 'smru/500.html', status=500)