from django.urls import path
from . import views

app_name = 'smru'

urlpatterns = [
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Home and main pages
    path('', views.home, name='home'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('events/', views.events_view, name='events'),
    
    # Study materials
    path('engineering/', views.engineering_notes, name='engineering'),
    path('medical/', views.medical_notes, name='medical'),
    path('student-files/', views.student_files, name='student_files'),
    
    # Complaints
    path('complaints/', views.complaints, name='complaints'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('all-complaints/', views.all_complaints, name='all_complaints'),
    path('complaint/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    
    # User profile
    path('profile/', views.profile, name='profile'),
]