from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# User Roles
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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True)  # For HODs, faculty, etc.
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'User Roles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


# College & Branch & Year & Subject for notes
class College(models.Model):
    COLLEGE_TYPE_CHOICES = (
        ('engineering', 'Engineering'),
        ('medical', 'Medical'),
    )
    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=COLLEGE_TYPE_CHOICES, default='engineering')
    description = models.TextField(blank=True, null=True)
    drive_link = models.URLField(blank=True, null=True)  # Optional general folder
    image = models.ImageField(upload_to='college_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Colleges'

    def __str__(self):
        return self.name

class Branch(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ['college', 'name']
        ordering = ['college', 'name']

    def __str__(self):
        return f"{self.college.name} - {self.name}"

class Year(models.Model):
    YEAR_CHOICES = (
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='years')
    name = models.CharField(max_length=50, choices=YEAR_CHOICES)

    class Meta:
        unique_together = ['branch', 'name']
        ordering = ['branch', 'name']

    def __str__(self):
        return f"{self.branch.name} - {self.name}"

class Subject(models.Model):
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    drive_folder_id = models.CharField(max_length=100)  # Google Drive Folder ID
    drive_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['year', 'name']
        ordering = ['year', 'name']
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return f"{self.year} - {self.name}"


# Student Profile
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=50, unique=True)
    hall_ticket_number = models.CharField(max_length=50, blank=True)
    college_name = models.CharField(max_length=200, blank=True)  # Store as string during signup
    branch_name = models.CharField(max_length=200, blank=True)  # Store as string during signup
    year_name = models.CharField(max_length=50, blank=True)  # Store as string during signup
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)  # Link to actual college later
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)  # Link to actual branch later
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True, blank=True)  # Link to actual year later
    phone = models.CharField(max_length=15, blank=True)
    id_card = models.ImageField(upload_to='student_id_cards/', blank=True, null=True)
    pan_card = models.ImageField(upload_to='student_pan_cards/', blank=True, null=True)
    live_photo = models.ImageField(upload_to='student_live_photos/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    is_from_listed_college = models.BooleanField(default=True)  # Track if from listed college
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number}"


# Notifications
class Notification(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)  # optional registration link
    image = models.ImageField(upload_to='notifications/', blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


# Events
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
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    registration_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    capacity = models.IntegerField(blank=True, null=True)  # max participants
    registered_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        verbose_name_plural = 'Events'
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name


# Complaint Categories
class ComplaintCategory(models.Model):
    CATEGORY_TYPE_CHOICES = (
        ('listed_college', 'For Listed Colleges'),
        ('other_college', 'For Other Colleges'),
    )
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CATEGORY_TYPE_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Complaint Categories'
        ordering = ['type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


# Complaint Persons (for sending complaints to specific people)
class ComplaintPerson(models.Model):
    category = models.ForeignKey(ComplaintCategory, on_delete=models.CASCADE, related_name='persons')
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Complaint Persons'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.designation}"


# Complaints
class Complaint(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.CASCADE)
    person = models.ForeignKey(ComplaintPerson, on_delete=models.SET_NULL, null=True, blank=True)
    complaint_text = models.TextField()
    file = models.FileField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    response = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)  # Optional feedback from student
    is_confirmed_solved_by_student = models.BooleanField(default=False)  # Student confirms it's solved
    is_confirmed_solved_by_admin = models.BooleanField(default=False)  # Admin/HOD confirms it's solved
    cleared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cleared_complaints')
    submitted_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = 'Complaints'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-submitted_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.category.name}"

    @property
    def is_fully_resolved(self):
        return self.is_confirmed_solved_by_student and self.is_confirmed_solved_by_admin


# Login Requests
class LoginRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_requests')

    class Meta:
        verbose_name_plural = 'Login Requests'
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.status}"


# Login Activities
class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Login Activities'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


# Teams
class Team(models.Model):
    TEAM_TYPE_CHOICES = (
        ('anti_ragging', 'Anti Ragging Team'),
        ('she', 'SHE Team'),
        ('event_managing', 'Event Managing Team'),
        ('discipline', 'Discipline Team'),
    )
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TEAM_TYPE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Teams'
        ordering = ['type']

    def __str__(self):
        return self.name


# Team Members
class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Team Members'
        ordering = ['team', 'name']

    def __str__(self):
        return f"{self.name} - {self.team.name}"


# Password Reset Requests
class PasswordResetRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    reset_method = models.CharField(max_length=20, choices=[('email', 'Email'), ('whatsapp', 'WhatsApp')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField()  # Token expires after 24 hours
    
    class Meta:
        verbose_name_plural = 'Password Reset Requests'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

