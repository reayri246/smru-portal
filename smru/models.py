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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True)  # For HODs, faculty, etc.
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'User Roles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"


# Backwards-compatible single-role accessor for templates and legacy code
from django.contrib.auth.models import User as DjangoUser

def _get_primary_user_role(self):
    try:
        # prefer active roles and return first one
        return self.user_roles.filter(is_active=True).first() or self.user_roles.first()
    except Exception:
        return None


DjangoUser.add_to_class('user_role', property(_get_primary_user_role))


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        ('5', '5th Year'),
        ('6', '6th Year'),
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
    syllabus_year = models.CharField(
        max_length=50,
        blank=True,
        help_text='Set the syllabus year for this subject notes, e.g. 2023-24.'
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, blank=True)
    drive_folder_id = models.CharField(max_length=100)  # Google Drive Folder ID
    drive_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['year', 'name', 'syllabus_year']
        ordering = ['year', 'name']
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return f"{self.year} - {self.name}"


# Student Profile
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=50, unique=True)
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
    TARGET_CHOICES = (
        ('listed_colleges', 'Listed Colleges'),
        ('non_listed_colleges', 'Non Listed Colleges'),
        ('both_colleges', 'Listed and Non Listed Colleges'),
        ('specific_college', 'Specific College'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)  # optional registration link
    image = models.ImageField(upload_to='notifications/', blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    target = models.CharField(max_length=30, choices=TARGET_CHOICES, default='listed_colleges')
    college = models.ForeignKey('College', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    recipient_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    recipient_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_public']),
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
    TARGET_CHOICES = (
        ('listed_colleges', 'Listed Colleges'),
        ('non_listed_colleges', 'Non Listed Colleges'),
        ('both_colleges', 'Listed and Non Listed Colleges'),
        ('specific_college', 'Specific College'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    registration_link = models.URLField(blank=True, null=True)
    target = models.CharField(max_length=30, choices=TARGET_CHOICES, default='listed_colleges')
    college = models.ForeignKey('College', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
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
        ('both', 'For Both Listed and Other Colleges'),
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='complaint_person')
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
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_verified = models.BooleanField(default=False)
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


# User Account Lock for rate limiting
class UserAccountLock(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_locked = models.BooleanField(default=False)
    # When True, this account bypasses lock checks (used by admins/system accounts)
    unlimited_access = models.BooleanField(default=False)
    lock_reason = models.CharField(max_length=100, blank=True)
    locked_at = models.DateTimeField(blank=True, null=True)
    unlock_at = models.DateTimeField(blank=True, null=True)
    daily_login_count = models.PositiveIntegerField(default=0)
    last_login_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'User Account Locks'

    def __str__(self):
        return f"{self.user.username} - {'Locked' if self.is_locked else 'Unlocked'}"

    def is_account_locked(self):
        """Check if account is currently locked"""
        if not self.is_locked:
            return False
        if self.unlock_at and timezone.now() > self.unlock_at:
            self.is_locked = False
            self.save()
            return False
        return True

    def lock_account(self, reason, duration_minutes=60):
        """Lock the account for specified duration"""
        self.is_locked = True
        self.lock_reason = reason
        self.locked_at = timezone.now()
        self.unlock_at = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save()

    def increment_daily_login(self):
        """Increment daily login count, reset if new day"""
        today = timezone.now().date()
        if self.last_login_date != today:
            self.daily_login_count = 1
            self.last_login_date = today
        else:
            self.daily_login_count += 1
        self.save()

    def can_login_today(self, max_logins=5):
        """Check if user can login today based on daily limit"""
        today = timezone.now().date()
        if self.last_login_date != today:
            return True
        return self.daily_login_count < max_logins


# Unlock requests (user requests admin to unlock their account)
class UnlockRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent to admin'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unlock_requests')
    token = models.CharField(max_length=100, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_unlocks')
    assigned_at = models.DateTimeField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"UnlockRequest {self.user.username} - {self.status}"


# Signup verification model (Excel/listed-student feature removed)
class SignupVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signup_verifications')
    token = models.CharField(max_length=100, unique=True)
    otp = models.CharField(max_length=6)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SignupVerification {self.user.username} - {'verified' if self.verified else 'pending'}"


# =================== Registration Approval & Audit Models ===================
class RegistrationApprovalRequest(models.Model):
    SOURCE_CHOICES = (
        ('listed', 'Listed College'),
        ('non_listed', 'Non Listed College'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deleted', 'Deleted (No Response)'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registration_requests')
    student_profile = models.ForeignKey('StudentProfile', on_delete=models.CASCADE, null=True, blank=True, related_name='registration_requests')
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True, blank=True)
    roll_number = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='listed')
    id_proof = models.FileField(upload_to='registration_proofs/', blank=True, null=True)
    pan_card = models.FileField(upload_to='registration_proofs/', blank=True, null=True)
    live_selfie = models.ImageField(upload_to='registration_selfies/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    assigned_at = models.DateTimeField(blank=True, null=True)
    
    # Workflow timeline tracking for approval reminders
    first_reminder_sent_at = models.DateTimeField(blank=True, null=True)
    last_reminder_at = models.DateTimeField(blank=True, null=True)
    reminder_count = models.IntegerField(default=0)
    staff_locked_at = models.DateTimeField(blank=True, null=True)
    staff_permissions_locked = models.BooleanField(default=False)
    
    verification_passed = models.BooleanField(default=False)
    verification_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"RegistrationRequest {self.user.username} - {self.status}"
    
    def is_pending_response(self):
        """Check if request is still waiting for staff response"""
        return self.status == 'pending' and self.assigned_staff is not None


# Excel import models (admin upload + listed students)

class ExcelImportHistory(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='excel_imports')
    file = models.FileField(upload_to='excel_imports/', blank=True, default='')
    file_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    imported_count = models.IntegerField(default=0)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='excel_imports')
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_excel_imports')
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"ExcelImport {self.file_name or (self.file.name if self.file else '')} - {self.uploaded_at}"


class ListedStudent(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='listed_students')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    branch_name = models.CharField(max_length=200, blank=True)
    roll_number = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='listed_students_assigned')
    import_history = models.ForeignKey(ExcelImportHistory, on_delete=models.SET_NULL, null=True, blank=True, related_name='imported_students')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.roll_number} - {self.first_name} {self.last_name} ({self.email})"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ExcelImportHistory)
def process_excel_import(sender, instance, created, **kwargs):
    import logging
    logger = logging.getLogger('smru')
    
    if instance.processed:
        return
    
    try:
        # Delay import until file is saved to storage
        if not instance.file:
            logger.warning(f'ExcelImportHistory {instance.id}: No file attached')
            return
        
        # Try to import openpyxl
        try:
            import openpyxl
        except ImportError:
            logger.error(f'ExcelImportHistory {instance.id}: openpyxl not installed')
            return

        logger.info(f'Processing Excel import {instance.id}: {instance.file.name}')
        
        # Open workbook
        try:
            wb = openpyxl.load_workbook(instance.file.path)
        except Exception as e:
            logger.error(f'ExcelImportHistory {instance.id}: Cannot open file {instance.file.path}: {str(e)}')
            instance.processed = True
            instance.imported_count = 0
            instance.save()
            return
            
        sheet = wb.active
        imported = 0
        total_rows = 0
        
        for row in sheet.iter_rows(min_row=2, values_only=True):
            total_rows += 1
            # Expect columns: roll_number, first_name, last_name, email
            roll = (row[0] or '').strip() if row and row[0] else ''
            first = (row[1] or '').strip() if row and len(row) > 1 and row[1] else ''
            last = (row[2] or '').strip() if row and len(row) > 2 and row[2] else ''
            email = (row[3] or '').strip() if row and len(row) > 3 and row[3] else ''

            if not (roll or email):
                logger.debug(f'ExcelImportHistory {instance.id}: Skipping row {total_rows} (no roll or email)')
                continue

            try:
                obj, created_row = ListedStudent.objects.update_or_create(
                    college=instance.branch.college if instance.branch else None,
                    roll_number=roll,
                    defaults={
                        'first_name': first,
                        'last_name': last,
                        'email': email,
                        'branch': instance.branch,
                        'branch_name': instance.branch.name if instance.branch else '',
                        'assigned_staff': instance.assigned_staff,
                        'import_history': instance,
                    }
                )
                imported += 1
                logger.debug(f'ExcelImportHistory {instance.id}: Imported student {roll} - {email}')
            except Exception as e:
                logger.error(f'ExcelImportHistory {instance.id}: Error importing row {total_rows}: {str(e)}')
                continue

        instance.imported_count = imported
        instance.processed = True
        if not instance.file_name:
            instance.file_name = instance.file.name
        instance.save()
        
        logger.info(f'ExcelImportHistory {instance.id}: Successfully imported {imported} students out of {total_rows} rows')
        
    except Exception as e:
        import traceback
        logger = logging.getLogger('smru')
        logger.error(f'ExcelImportHistory {instance.id}: Unexpected error: {str(e)}')
        logger.error(traceback.format_exc())
        instance.processed = True
        instance.imported_count = 0
        instance.save()


class RegistrationAuditLog(models.Model):
    request = models.ForeignKey(RegistrationApprovalRequest, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=100)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_audits')
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on {self.request.id} at {self.timestamp}"


class ReminderLog(models.Model):
    request = models.ForeignKey(RegistrationApprovalRequest, on_delete=models.CASCADE, related_name='reminder_logs')
    to_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminders_received')
    sent_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Reminder for {self.request.id} at {self.sent_at}"


class StaffLockLog(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lock_logs')
    locked_at = models.DateTimeField(auto_now_add=True)
    unlocked_at = models.DateTimeField(blank=True, null=True)
    reason = models.CharField(max_length=200, blank=True)
    locked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='locks_performed')

    class Meta:
        ordering = ['-locked_at']

    def __str__(self):
        return f"Lock {self.staff.username} at {self.locked_at}"


class StaffPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_permissions')
    permission = models.CharField(max_length=100)

    class Meta:
        unique_together = ['user', 'permission']

    def __str__(self):
        return f"{self.user.username} - {self.permission}"


# Study material model for admin uploads
class StudyMaterial(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='study_materials/')
    college = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_materials')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_materials')
    year = models.ForeignKey(Year, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_materials')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_study_materials')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

