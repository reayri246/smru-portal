from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    College, Branch, Year, Subject, Notification, Event, Complaint, StudentProfile,
    UserRole, ComplaintCategory, ComplaintPerson, LoginRequest, LoginActivity, 
    Team, TeamMember, PasswordResetRequest
)


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'created_at', 'branches_count']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = 'Branches'


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'college', 'years_count']
    list_filter = ['college']
    search_fields = ['name', 'code']
    
    def years_count(self, obj):
        return obj.years.count()
    years_count.short_description = 'Years'


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'subjects_count']
    list_filter = ['branch', 'name']
    
    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = 'Subjects'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'year', 'has_drive_link']
    list_filter = ['year', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at']
    
    def has_drive_link(self, obj):
        if obj.drive_link:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_drive_link.short_description = 'Drive Link'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'is_active', 'status_badge', 'created_at']
    list_filter = ['is_active', 'priority', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'description', 'image')
        }),
        ('Settings', {
            'fields': ('link', 'priority', 'is_active', 'expires_at')
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
    list_filter = ['status', 'date']
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
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category', 'person', 'status', 'is_fully_resolved', 'submitted_at']
    list_filter = ['status', 'category', 'submitted_at', 'is_confirmed_solved_by_student', 'is_confirmed_solved_by_admin']
    search_fields = ['user__username', 'user__email', 'complaint_text']
    readonly_fields = ['submitted_at', 'resolved_at', 'id']
    fieldsets = (
        ('Complainant Info', {
            'fields': ('id', 'user')
        }),
        ('Complaint', {
            'fields': ('category', 'person', 'complaint_text', 'file')
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
                <tr><td><strong>Hall Ticket:</strong></td><td>{profile.hall_ticket_number}</td></tr>
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
            'fields': ('user', 'roll_number', 'hall_ticket_number', 'phone', 'bio')
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
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} student(s) approved.')
    approve_students.short_description = 'Approve selected students'
    
    def reject_students(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} student(s) rejected.')
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