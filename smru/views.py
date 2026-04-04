from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
import logging

from .models import College, Notification, Event, Complaint, StudentProfile, Branch, Year, Subject
from .forms import SignUpForm, LoginForm, ComplaintForm, StudentProfileForm

logger = logging.getLogger('smru')

# ======================== AUTHENTICATION VIEWS ========================

def signup(request):
    """User sign up view"""
    if request.user.is_authenticated:
        return redirect('smru:home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"New user registered: {user.username}")
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('smru:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()
    
    return render(request, 'smru/signup.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('smru:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
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
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'smru/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logger.info(f"User logged out: {request.user.username}")
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('smru:home')


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
        colleges_list = College.objects.all()
        college_id = request.GET.get('college')
        branch_id = request.GET.get('branch')
        year_id = request.GET.get('year')
        
        branches = []
        years = []
        subjects = []
        
        if college_id:
            try:
                college = College.objects.get(id=college_id)
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
        colleges_list = College.objects.all()
        college_id = request.GET.get('college')
        branch_id = request.GET.get('branch')
        year_id = request.GET.get('year')
        
        branches = []
        years = []
        subjects = []
        
        if college_id:
            try:
                college = College.objects.get(id=college_id)
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
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save()
            logger.info(f"New complaint created: ID={complaint.id}, Roll={complaint.roll}")
            messages.success(request, 'Your complaint has been submitted successfully! Reference ID: {}'.format(complaint.id))
            return redirect('smru:complaints')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = ComplaintForm()
    
    return render(request, 'smru/complaints.html', {'form': form})


@login_required(login_url='smru:login')
def my_complaints(request):
    """View user's submitted complaints"""
    try:
        # Get complaints by email
        user_complaints = Complaint.objects.filter(
            email=request.user.email
        ).order_by('-submitted_at')
        
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


def complaint_detail(request, complaint_id):
    """View single complaint status"""
    try:
        complaint = get_object_or_404(Complaint, id=complaint_id)
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