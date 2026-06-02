from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.admin.sites import AdminSite
import django.contrib.admin.sites as admin_sites
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group, User
from django.core.cache import cache
import logging
import secrets

logger = logging.getLogger('smru')

from .models import (
    College, Branch, Year, Subject, Notification, Event, Complaint, StudentProfile,
    UserRole, ComplaintCategory, ComplaintPerson, LoginRequest, LoginActivity, 
    Team, TeamMember, PasswordResetRequest, UserAccountLock,
    ExcelImportHistory, ListedStudent, SignupVerification,
    RegistrationApprovalRequest, RegistrationAuditLog
)
# local views import for admin custom urls
from . import views as smru_views
# Excel-related models removed


class YearSelect(forms.Select):
    def __init__(self, attrs=None, year_college_map=None):
        self.year_college_map = year_college_map or {}
        super().__init__(attrs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value is not None:
            value_str = str(value)
            if value_str.isdigit():
                college_id = self.year_college_map.get(int(value_str))
                if college_id is not None:
                    option['attrs']['data-college-id'] = str(college_id)
        return option


class SecureAdminSite(AdminSite):
    """Custom admin site with enhanced security"""
    index_template = 'smru/admin_index.html'
    site_header = "SMRU PORTAL ADMINISTRATOR"
    site_title = "SMRU Admin Portal"
    index_title = "Welcome to SMRU Admin Portal"
    STAFF_ROLES = [
        'admin',
        'hod',
        'chairman',
        'principal',
        'director',
        'faculty',
        'security',
        'anti_ragging_team',
        'she_team',
    ]

    def has_permission(self, request):
        """Override to add custom permission checks"""
        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        user_role = getattr(request.user, 'user_role', None)
        if not user_role:
            return False
        return getattr(user_role, 'is_active', False) and getattr(user_role, 'role', '') in self.STAFF_ROLES

    def get_urls(self):
        return super().get_urls()

    def index(self, request, extra_context=None):
        return super().index(request, extra_context=extra_context)


# Create secure admin site
admin_site = SecureAdminSite(name='secure_admin')
admin.site = admin_site  # Replace default admin site
admin_sites.site = admin_site  # Also replace Django's default admin site object used by decorators

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'created_at', 'branches_count']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    # actions = ['upload_students_action']
    
    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = 'Branches'

    # Upload students action removed


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'college', 'years_count']
    list_filter = ['college']
    search_fields = ['name', 'code']
    # actions = ['upload_students_for_branch']
    
    def years_count(self, obj):
        return obj.years.count()
    years_count.short_description = 'Years'

    # Upload students for branch action removed


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'subjects_count']
    list_filter = ['branch', 'name']
    
    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = 'Subjects'


class SubjectAdminForm(forms.ModelForm):
    college = forms.ModelChoiceField(
        queryset=College.objects.all(),
        required=False,
        label='College',
        help_text='Select the college that owns this subject.'
    )

    class Meta:
        model = Subject
        fields = ['college', 'name', 'code', 'year', 'syllabus_year', 'drive_folder_id', 'drive_link']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.year:
            self.fields['college'].initial = self.instance.year.branch.college

        year_college_map = {year.pk: year.branch.college_id for year in Year.objects.all()}
        self.fields['year'].widget = YearSelect(year_college_map=year_college_map)

        selected_college = self.data.get('college') or self.initial.get('college')
        selected_year = self.data.get('year') or self.initial.get('year')
        if selected_college:
            try:
                college = College.objects.get(pk=selected_college)
                queryset = Year.objects.filter(branch__college=college)
                if selected_year:
                    try:
                        selected_year_obj = Year.objects.get(pk=selected_year)
                        queryset = queryset | Year.objects.filter(pk=selected_year_obj.pk)
                    except (Year.DoesNotExist, ValueError, TypeError):
                        pass
                self.fields['year'].queryset = queryset.distinct()
            except (College.DoesNotExist, ValueError, TypeError):
                self.fields['year'].queryset = Year.objects.none()
        else:
            self.fields['year'].queryset = Year.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        college = cleaned_data.get('college')
        year = cleaned_data.get('year')
        if college and year and year.branch.college != college:
            raise forms.ValidationError('Selected subject year must belong to the chosen college.')
        return cleaned_data


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    form = SubjectAdminForm
    list_display = ['name', 'code', 'year', 'syllabus_year', 'has_drive_link']
    list_filter = ['year', 'syllabus_year', 'created_at']
    search_fields = ['name', 'code', 'syllabus_year']
    readonly_fields = ['created_at']
    fieldsets = (
        (None, {
            'fields': ('college', 'name', 'code', 'year', 'syllabus_year', 'drive_folder_id', 'drive_link')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    class Media:
        js = ('smru/js/admin_subject_year_filter.js',)

    def has_drive_link(self, obj):
        if obj.drive_link:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_drive_link.short_description = 'Drive Link'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'target', 'college', 'is_active', 'is_public', 'recipient_user', 'recipient_email', 'status_badge', 'created_at']
    list_filter = ['is_active', 'is_public', 'priority', 'target', 'college', 'created_at']
    search_fields = ['title', 'description', 'recipient_email', 'recipient_user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'description', 'image')
        }),
        ('Settings', {
            'fields': ('link', 'priority', 'is_active', 'is_public', 'recipient_user', 'recipient_email', 'target', 'college', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_expired:
            color = 'red'
            status = 'Expired'
        elif obj.is_active:
            color = 'green'
            status = 'Active'
        else:
            color = 'orange'
            status = 'Inactive'
        return format_html(f'<span style="color: {color}; font-weight: bold;">{status}</span>')
    status_badge.short_description = 'Status'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'status', 'location', 'registered_count']
    list_filter = ['status', 'date', 'target', 'college']
    search_fields = ['name', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at', 'registered_count']
    fieldsets = (
        ('Event Details', {
            'fields': ('name', 'description', 'image')
        }),
        ('Date & Time', {
            'fields': ('date', 'time')
        }),
        ('Location & Registration', {
            'fields': ('location', 'registration_link', 'capacity', 'registered_count')
        }),
        ('Targeting', {
            'fields': ('target', 'college')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Excel admin removed


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category', 'person', 'status', 'is_fully_resolved', 'file_uploaded', 'submitted_at']
    list_filter = ['status', 'category', 'submitted_at', 'is_confirmed_solved_by_student', 'is_confirmed_solved_by_admin']
    search_fields = ['user__username', 'user__email', 'complaint_text']
    readonly_fields = ['submitted_at', 'resolved_at', 'id', 'complaint_detail_display', 'file_detail_display']
    fieldsets = (
        ('Complainant Info', {
            'fields': ('id', 'user', 'complaint_detail_display')
        }),
        ('Complaint', {
            'fields': ('category', 'person', 'complaint_text', 'file_detail_display')
        }),
        ('Response', {
            'fields': ('status', 'response', 'feedback', 'is_confirmed_solved_by_student', 'is_confirmed_solved_by_admin', 'cleared_by')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_resolved', 'mark_closed', 'mark_admin_solved']
    
    def file_uploaded(self, obj):
        """Show if file is uploaded with a clickable link"""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" style="color: green; text-decoration: none;">✓ Download</a>',
                obj.file.url
            )
        return format_html('<span style="color: red;">✗ No file</span>')
    file_uploaded.short_description = 'Attachment'
    
    def file_detail_display(self, obj):
        """Display detailed file information with preview"""
        if not obj.file:
            return "No file uploaded"
        
        import os
        file_size = obj.file.size
        file_name = os.path.basename(obj.file.name)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Convert bytes to human readable format
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"
        
        # Check if file is an image
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        is_image = file_ext in image_extensions
        
        html = f"""
        <div style="background: #f9f9f9; padding: 15px; border: 1px solid #ddd; border-radius: 5px; font-size: 13px;">
            <h4>📎 Attached Document</h4>
            <table style="width: 100%; margin-top: 10px;">
                <tr>
                    <td style="padding: 5px;"><strong>File Name:</strong></td>
                    <td style="padding: 5px;"><code>{file_name}</code></td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>File Size:</strong></td>
                    <td style="padding: 5px;">{size_str}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>File Type:</strong></td>
                    <td style="padding: 5px;">{file_ext or "Unknown"}</td>
                </tr>
                <tr>
                    <td style="padding: 5px;"><strong>Download:</strong></td>
                    <td style="padding: 5px;"><a href="{obj.file.url}" target="_blank" style="color: #0066cc; text-decoration: underline;">Click here to download →</a></td>
                </tr>
            </table>
        """
        
        # If it's an image, show preview
        if is_image:
            html += f"""
            <h4 style="margin-top: 15px;">📷 File Preview</h4>
            <div style="margin-top: 10px;">
                <img src="{obj.file.url}" style="max-width: 400px; max-height: 300px; border: 2px solid #0066cc; padding: 10px; background: white;">
            </div>
            """
        
        html += "</div>"
        return format_html(html)
    file_detail_display.short_description = 'Uploaded Document Details'
    
    def complaint_detail_display(self, obj):
        """Display complaint details in a formatted way"""
        html = f"""
        <div style="background: #e8f4f8; padding: 10px; border-left: 4px solid #0066cc; border-radius: 3px; font-size: 13px;">
            <strong>📝 Complaint Text:</strong><br>
            <div style="margin-top: 8px; padding: 10px; background: white; border-radius: 3px; border: 1px solid #ccc; line-height: 1.6;">
                {obj.complaint_text}
            </div>
        </div>
        """
        return format_html(html)
    complaint_detail_display.short_description = 'Complaint Details'
    
    def is_fully_resolved(self, obj):
        return obj.is_fully_resolved
    is_fully_resolved.boolean = True
    is_fully_resolved.short_description = 'Fully Resolved'
    
    def mark_resolved(self, request, queryset):
        count = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{count} complaint(s) marked as resolved.')
    mark_resolved.short_description = 'Mark selected as Resolved'
    
    def mark_closed(self, request, queryset):
        count = queryset.update(status='closed')
        self.message_user(request, f'{count} complaint(s) marked as Closed.')
    mark_closed.short_description = 'Mark selected as Closed'
    
    def mark_admin_solved(self, request, queryset):
        for complaint in queryset:
            complaint.is_confirmed_solved_by_admin = True
            complaint.cleared_by = request.user
            if not complaint.resolved_at:
                complaint.resolved_at = timezone.now()
            complaint.save()
        self.message_user(request, f'{queryset.count()} complaint(s) marked as solved by admin.')
    mark_admin_solved.short_description = 'Mark as Solved by Admin'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['user__username', 'user__email', 'department']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(ComplaintPerson)
class ComplaintPersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation', 'category', 'email', 'phone', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'designation', 'email']


@admin.register(LoginRequest)
class LoginRequestAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'status', 'requested_at', 'approved_at', 'approved_by']
    list_filter = ['status', 'requested_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['requested_at', 'approved_at', 'user_details_display']
    actions = ['approve_requests', 'reject_requests']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_details_display')
        }),
        ('Application Status', {
            'fields': ('status', 'requested_at', 'approved_at', 'approved_by')
        }),
    )
    
    def user_display(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.username})"
    user_display.short_description = 'Student'
    
    def user_details_display(self, obj):
        """Display comprehensive student details including ID proofs"""
        if not hasattr(obj.user, 'student_profile'):
            return "No student profile found"
        
        profile = obj.user.student_profile
        html = f"""
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; font-size: 14px;">
            <h3>Student Details</h3>
            <table style="width: 100%; margin-top: 10px;">
                <tr><td><strong>Full Name:</strong></td><td>{obj.user.get_full_name()}</td></tr>
                <tr><td><strong>Email:</strong></td><td>{obj.user.email}</td></tr>
                <tr><td><strong>Roll Number:</strong></td><td>{profile.roll_number}</td></tr>
                <tr><td><strong>Phone:</strong></td><td>{profile.phone}</td></tr>
                <tr><td><strong>College:</strong></td><td>{profile.college_name}</td></tr>
                <tr><td><strong>Branch:</strong></td><td>{profile.branch_name}</td></tr>
                <tr><td><strong>Year:</strong></td><td>{profile.year_name}</td></tr>
                <tr><td><strong>From Listed College:</strong></td><td>{"Yes" if profile.is_from_listed_college else "No"}</td></tr>
            </table>
            <h4 style="margin-top: 20px;">ID Proofs</h4>
        """
        
        if profile.id_card:
            html += f'<div style="margin: 10px 0;"><strong>College ID Card:</strong><br><img src="{profile.id_card.url}" style="max-width: 200px; max-height: 200px; border: 1px solid #ccc; padding: 5px;"></div>'
        
        if profile.pan_card:
            html += f'<div style="margin: 10px 0;"><strong>PAN Card:</strong><br><img src="{profile.pan_card.url}" style="max-width: 200px; max-height: 200px; border: 1px solid #ccc; padding: 5px;"></div>'
        
        if profile.live_photo:
            html += f'<div style="margin: 10px 0;"><strong>Live Photo for Verification:</strong><br><img src="{profile.live_photo.url}" style="max-width: 200px; max-height: 200px; border: 1px solid #ccc; padding: 5px;"></div>'
        
        html += '</div>'
        return format_html(html)
    user_details_display.short_description = 'Student Application Details'
    
    def approve_requests(self, request, queryset):
        for login_request in queryset.filter(status='pending'):
            login_request.status = 'approved'
            login_request.approved_at = timezone.now()
            login_request.approved_by = request.user
            login_request.save()
            
            # Approve student profile if exists
            try:
                if hasattr(login_request.user, 'student_profile'):
                    login_request.user.student_profile.is_approved = True
                    login_request.user.student_profile.save()
            except:
                pass
        
        self.message_user(request, f'{queryset.filter(status="pending").count()} login requests approved.')
    approve_requests.short_description = 'Approve selected login requests'
    
    def reject_requests(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{count} login requests rejected.')
    reject_requests.short_description = 'Reject selected login requests'



@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'logout_time', 'ip_address']
    list_filter = ['login_time', 'logout_time']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['login_time', 'logout_time', 'ip_address', 'user_agent']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(UserAccountLock)
class UserAccountLockAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_locked', 'lock_reason', 'locked_at', 'unlock_at', 'daily_login_count', 'last_login_date']
    list_filter = ['is_locked', 'locked_at', 'last_login_date']
    search_fields = ['user__username', 'lock_reason']
    readonly_fields = ['locked_at']
    actions = ['unlock_accounts']
    
    def unlock_accounts(self, request, queryset):
        count = 0
        for account_lock in queryset.select_related('user'):
            # Update DB record
            account_lock.is_locked = False
            account_lock.lock_reason = ''
            account_lock.locked_at = None
            account_lock.unlock_at = None
            account_lock.daily_login_count = 0
            account_lock.last_login_date = None
            account_lock.save()
            
            # Clear all possible rate-limit cache keys for this user
            username = account_lock.user.username.strip().lower()
            email = account_lock.user.email.strip().lower()
            
            cache_keys_to_clear = [
                f'login_attempts_user:{username}',
                f'login_attempts_input:{username}',
                f'login_attempts_input:{email}',
            ]
            for cache_key in cache_keys_to_clear:
                cache.delete(cache_key)
                logger.info(f"Cleared cache key: {cache_key}")
            
            count += 1
            logger.info(f"Unlocked account: {account_lock.user.username}")
        
        self.message_user(request, f'{count} accounts unlocked and cache cleared.')
    unlock_accounts.short_description = 'Unlock selected accounts'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation', 'team', 'email', 'phone', 'is_active']
    list_filter = ['team', 'is_active']
    search_fields = ['name', 'designation', 'email']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'roll_number', 'college_name', 'branch_name', 'year_name', 'is_approved_badge']
    list_filter = ['is_approved', 'college_name', 'branch_name', 'year_name', 'is_from_listed_college']
    search_fields = ['user__username', 'user__email', 'roll_number', 'college_name', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'id_proofs_display']
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'roll_number', 'phone', 'bio')
        }),
        ('College Details', {
            'fields': ('college', 'college_name', 'branch', 'branch_name', 'year', 'year_name', 'is_from_listed_college')
        }),
        ('ID Proofs & Photos', {
            'fields': ('id_card', 'pan_card', 'live_photo', 'id_proofs_display'),
            'description': 'Review submitted identity proofs for verification'
        }),
        ('Profile Picture', {
            'fields': ('profile_picture',)
        }),
        ('Approval Status', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['approve_students', 'reject_students']
    
    def get_username(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.username})"
    get_username.short_description = 'Student'
    
    def is_approved_badge(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: green; font-weight: bold;">✓ Approved</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Pending</span>')
    is_approved_badge.short_description = 'Status'
    
    def id_proofs_display(self, obj):
        """Display all ID proofs for admin review"""
        html = '<div style="background: #f9f9f9; padding: 15px; border-radius: 5px;">'
        
        if obj.id_card:
            html += f'''
            <div style="margin: 15px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
                <h4>College ID Card</h4>
                <img src="{obj.id_card.url}" style="max-width: 300px; max-height: 300px; border: 1px solid #999; padding: 5px; margin-top: 10px;">
            </div>
            '''
        
        if obj.pan_card:
            html += f'''
            <div style="margin: 15px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
                <h4>PAN Card</h4>
                <img src="{obj.pan_card.url}" style="max-width: 300px; max-height: 300px; border: 1px solid #999; padding: 5px; margin-top: 10px;">
            </div>
            '''
        
        if obj.live_photo:
            html += f'''
            <div style="margin: 15px 0; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
                <h4>Live Photo for Verification</h4>
                <img src="{obj.live_photo.url}" style="max-width: 300px; max-height: 300px; border: 1px solid #999; padding: 5px; margin-top: 10px;">
            </div>
            '''
        
        if not obj.id_card and not obj.pan_card and not obj.live_photo:
            html += '<p style="color: #999; font-style: italic;">No ID proofs uploaded</p>'
        
        html += '</div>'
        return format_html(html)
    id_proofs_display.short_description = 'ID Proofs Review'
    
    def approve_students(self, request, queryset):
        count = 0
        for profile in queryset:
            profile.is_approved = True
            profile.save()
            login_request, created = LoginRequest.objects.get_or_create(user=profile.user)
            login_request.status = 'approved'
            login_request.approved_at = timezone.now()
            login_request.approved_by = request.user
            login_request.save()
            count += 1
        self.message_user(request, f'{count} student(s) approved and login requests synced.')
    approve_students.short_description = 'Approve selected students'

    def reject_students(self, request, queryset):
        count = 0
        for profile in queryset:
            profile.is_approved = False
            profile.save()
            login_request, created = LoginRequest.objects.get_or_create(user=profile.user)
            login_request.status = 'rejected'
            login_request.save()
            count += 1
        self.message_user(request, f'{count} student(s) rejected and login requests synced.')
    reject_students.short_description = 'Reject selected students'



@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'reset_method', 'status', 'requested_at', 'expires_at', 'is_expired_badge']
    list_filter = ['status', 'reset_method', 'requested_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'requested_at', 'completed_at', 'expires_at']
    
    def is_expired_badge(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red; font-weight: bold;">✗ Expired</span>')
        elif obj.status == 'completed':
            return format_html('<span style="color: green; font-weight: bold;">✓ Completed</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">⧖ Pending</span>')
    is_expired_badge.short_description = 'Status'


@admin.register(ExcelImportHistory)
class ExcelImportHistoryAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'uploaded_by', 'uploaded_at', 'imported_count', 'branch', 'assigned_staff', 'processed', 'file_link']
    list_filter = ['uploaded_at', 'branch', 'assigned_staff', 'processed']
    search_fields = ['file_name', 'uploaded_by__username']
    readonly_fields = ['uploaded_at', 'file_name']
    actions = ['reprocess_excel_files']

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)
        return '-'
    file_link.short_description = 'File'
    
    def reprocess_excel_files(self, request, queryset):
        """Re-process selected Excel files to import students"""
        count = 0
        for excel_import in queryset:
            try:
                # Reset processed flag to trigger re-processing
                excel_import.processed = False
                excel_import.imported_count = 0
                excel_import.save()
                
                # The post_save signal will process the file
                count += 1
                logger.info(f'Re-queued Excel import {excel_import.id} for processing')
            except Exception as e:
                logger.error(f'Error re-processing Excel import {excel_import.id}: {str(e)}')
        
        self.message_user(request, f'{count} Excel file(s) re-queued for processing. Check logs for details.')
    reprocess_excel_files.short_description = 'Re-process selected Excel files'


@admin.register(ListedStudent)
class ListedStudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'first_name', 'last_name', 'email', 'college', 'branch', 'assigned_staff', 'import_history']
    list_filter = ['college', 'branch', 'assigned_staff']
    search_fields = ['roll_number', 'first_name', 'last_name', 'email']
    readonly_fields = ['created_at']


@admin.register(SignupVerification)
class SignupVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'verified', 'created_at', 'expires_at']
    readonly_fields = ['token', 'otp']
    
    def save_model(self, request, obj, form, change):
        """Generate token and otp automatically if not provided"""
        if not obj.token or obj.token.strip() == '':
            # Generate unique token
            while True:
                obj.token = secrets.token_urlsafe(32)
                # Check if token already exists
                if not SignupVerification.objects.filter(token=obj.token).exclude(pk=obj.pk).exists():
                    break
        
        if not obj.otp or obj.otp.strip() == '':
            # Generate 6-digit OTP
            obj.otp = str(secrets.randbelow(900000) + 100000)
        
        super().save_model(request, obj, form, change)


@admin.register(RegistrationApprovalRequest)
class RegistrationApprovalRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'student_name', 'username', 'college', 'branch', 'status', 
        'assigned_staff', 'created_at', 'lock_status_badge', 'time_since_assignment'
    ]
    list_filter = ['status', 'college', 'branch', 'source', 'staff_permissions_locked', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'roll_number']
    readonly_fields = ['created_at', 'updated_at', 'assigned_at', 'first_reminder_sent_at', 'last_reminder_at']
    fieldsets = (
        ('Student Information', {
            'fields': ('user', 'student_profile', 'roll_number', 'email')
        }),
        ('Registration Details', {
            'fields': ('college', 'branch', 'year', 'source', 'status')
        }),
        ('Documents', {
            'fields': ('id_proof', 'pan_card', 'live_selfie')
        }),
        ('Approval Process', {
            'fields': ('assigned_staff', 'assigned_at', 'verification_passed', 'verification_details')
        }),
        ('Workflow Timeline', {
            'fields': (
                'first_reminder_sent_at', 'last_reminder_at', 'reminder_count', 
                'staff_locked_at', 'staff_permissions_locked'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['approve_requests', 'reject_requests', 'unlock_staff_permissions']
    
    def student_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    student_name.short_description = 'Student Name'
    
    def username(self, obj):
        return obj.user.username
    username.short_description = 'Username'
    
    def lock_status_badge(self, obj):
        """Display lock status as a colored badge"""
        if obj.staff_permissions_locked:
            return format_html(
                '<span style="background-color: #ff6b6b; color: white; padding: 3px 8px; border-radius: 3px;">'
                'LOCKED</span>'
            )
        return format_html(
            '<span style="background-color: #51cf66; color: white; padding: 3px 8px; border-radius: 3px;">'
            'ACTIVE</span>'
        )
    lock_status_badge.short_description = 'Staff Status'
    
    def time_since_assignment(self, obj):
        """Display time elapsed since assignment"""
        if not obj.assigned_at:
            return 'Not assigned'
        elapsed = timezone.now() - obj.assigned_at
        hours = elapsed.total_seconds() / 3600
        return f'{hours:.1f}h'
    time_since_assignment.short_description = 'Time Since Assign'
    
    def approve_requests(self, request, queryset):
        """Admin action to approve selected requests"""
        count = 0
        for registration_request in queryset.filter(status='pending'):
            registration_request.status = 'approved'
            registration_request.save()
            
            # Send approval email to student
            try:
                from .views import send_registration_approved_email
                send_registration_approved_email(registration_request)
            except Exception as e:
                logger.error(f'Error sending approval email: {str(e)}')
            
            # Create audit log
            RegistrationAuditLog.objects.create(
                request=registration_request,
                action='approved',
                performed_by=request.user,
                details='Approved by admin'
            )
            
            # Unlock staff permissions if locked
            if registration_request.staff_permissions_locked:
                registration_request.staff_permissions_locked = False
                registration_request.staff_locked_at = None
                registration_request.save()
            
            count += 1
        
        self.message_user(request, f'{count} request(s) approved successfully.')
    approve_requests.short_description = 'Approve selected requests'
    
    def reject_requests(self, request, queryset):
        """Admin action to reject selected requests"""
        count = 0
        for registration_request in queryset.filter(status='pending'):
            registration_request.status = 'rejected'
            registration_request.save()
            
            # Send rejection email to student
            try:
                from .views import send_registration_rejected_email
                send_registration_rejected_email(
                    registration_request, 
                    reason='Your registration was rejected by the verification staff.'
                )
            except Exception as e:
                logger.error(f'Error sending rejection email: {str(e)}')
            
            # Create audit log
            RegistrationAuditLog.objects.create(
                request=registration_request,
                action='rejected',
                performed_by=request.user,
                details='Rejected by admin'
            )
            
            # Unlock staff permissions if locked
            if registration_request.staff_permissions_locked:
                registration_request.staff_permissions_locked = False
                registration_request.staff_locked_at = None
                registration_request.save()
            
            count += 1
        
        self.message_user(request, f'{count} request(s) rejected successfully.')
    reject_requests.short_description = 'Reject selected requests'
    
    def unlock_staff_permissions(self, request, queryset):
        """Admin action to manually unlock staff permissions"""
        count = 0
        for registration_request in queryset.filter(staff_permissions_locked=True):
            registration_request.staff_permissions_locked = False
            registration_request.staff_locked_at = None
            registration_request.save()
            
            # Create audit log
            RegistrationAuditLog.objects.create(
                request=registration_request,
                action='staff_unlocked',
                performed_by=request.user,
                details='Staff permissions manually unlocked by admin'
            )
            
            # Send email to staff that they've been unlocked
            try:
                staff_user = registration_request.assigned_staff
                if staff_user and staff_user.email:
                    subject = 'Your Admin Account Permissions Have Been Restored'
                    message = f"""
Dear {staff_user.get_full_name()},

Your admin account permissions have been restored by an administrator.

You can now access the full admin panel again.

If you have any questions, please contact the system administrator.

Best regards,
SMRU Portal Admin Team
                    """
                    from django.core.mail import send_mail
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                        [staff_user.email],
                        fail_silently=False,
                    )
            except Exception as e:
                logger.error(f'Error sending unlock email: {str(e)}')
            
            count += 1
        
        self.message_user(request, f'{count} staff member(s) unlocked successfully.')
    unlock_staff_permissions.short_description = 'Unlock staff permissions'