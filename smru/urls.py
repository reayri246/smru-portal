from django.urls import path
from . import views
from . import dashboard_views

app_name = 'smru'

urlpatterns = [
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('request-unlock/', views.request_unlock, name='request_unlock'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    # Home and main pages
    path('', views.home, name='home'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('staff-notifications/', views.staff_notifications_view, name='staff_notifications'),
    path('admin-health/', views.admin_health, name='admin_health'),
    path('events/', views.events_view, name='events'),
    
    # Study materials
    path('notes/', views.notes, name='notes'),
    path('engineering/', views.engineering_notes, name='engineering'),
    path('medical/', views.medical_notes, name='medical'),
    path('student-files/', views.student_files, name='student_files'),
    path('team/', views.team, name='team'),
    path('about/', views.about, name='about'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    
    # AJAX endpoints
    path('api/colleges-by-type/', views.get_colleges_by_type, name='get_colleges_by_type'),
    path('api/branches-by-college/', views.get_branches_by_college, name='get_branches_by_college'),
    path('api/persons-by-category/', views.get_persons_by_category, name='get_persons_by_category'),
    path('manage-complaints/', views.manage_complaints, name='manage_complaints'),
    path('complaints/', views.complaints, name='complaints'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('complaint/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    
    # User profile
    path('profile/', views.profile, name='profile'),
    # Dashboards removed: routes deleted per request
    path('api/unlock-staff/<int:lock_log_id>/', dashboard_views.unlock_staff_account, name='unlock_staff_account'),
    path('api/approve-registration/<int:registration_id>/', dashboard_views.approve_registration, name='approve_registration'),
    path('api/reject-registration/<int:registration_id>/', dashboard_views.reject_registration, name='reject_registration'),
    # manage-staff-permissions and add_study_material routes removed
    # role dashboard removed
]