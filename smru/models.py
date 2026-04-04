from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# College & Branch & Year & Subject for notes
class College(models.Model):
    name = models.CharField(max_length=200, unique=True)
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


# Complaints
class Complaint(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    CATEGORY_CHOICES = (
        ('academic', 'Academic'),
        ('infrastructure', 'Infrastructure'),
        ('faculty', 'Faculty'),
        ('facilities', 'Facilities'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=200)
    roll = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    complaint_text = models.TextField()
    file = models.FileField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    response = models.TextField(blank=True, null=True)
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
        return f"{self.name} - {self.roll}"


# Student Profile
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=50, unique=True)
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number}"

