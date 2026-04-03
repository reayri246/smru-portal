from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django import forms
from .models import College, Branch, Year, Subject, LoginActivity, Notification, Event, Complaint, StudentProfile


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'college_type', 'created_at', 'branches_count']
    list_filter = ['college_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def branches_count(self, obj):
        return obj.branches.count()
    branches_count.short_description = 'Branches'


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'college', 'branch_type', 'years_count']
    list_filter = ['college', 'branch_type']
    search_fields = ['name', 'code']
    
    def years_count(self, obj):
        return obj.years.count()
    years_count.short_description = 'Years'


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'get_college', 'subjects_count']
    list_filter = ['branch__college__college_type', 'branch__branch_type', 'branch', 'name']
    search_fields = ['branch__name', 'branch__college__name', 'name']

    def get_college(self, obj):
        return obj.branch.college
    get_college.short_description = 'College'

    def subjects_count(self, obj):
        return obj.subjects.count()
    subjects_count.short_description = 'Subjects'


class SubjectAdminForm(forms.ModelForm):
    college = forms.ModelChoiceField(
        queryset=College.objects.all(),
        required=True,
        label="College"
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=True,
        label="Branch"
    )

    class Meta:
        model = Subject
        fields = ['college', 'branch', 'year', 'name', 'code', 'drive_folder_id', 'drive_link']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values if editing existing subject
        if self.instance and self.instance.pk:
            self.fields['college'].initial = self.instance.year.branch.college
            self.fields['branch'].initial = self.instance.year.branch

        # Filter branch based on college
        college = self.data.get('college') or self.initial.get('college')
        if isinstance(college, College):
            self.fields['branch'].queryset = college.branches.all()
        elif college:
            try:
                college_obj = College.objects.get(id=college)
                self.fields['branch'].queryset = college_obj.branches.all()
            except College.DoesNotExist:
                self.fields['branch'].queryset = Branch.objects.none()
        else:
            # For new subjects, show all branches
            self.fields['branch'].queryset = Branch.objects.all()

        # Filter year based on branch
        branch = self.data.get('branch') or self.initial.get('branch')
        if isinstance(branch, Branch):
            self.fields['year'].queryset = branch.years.all()
        elif branch:
            try:
                branch_obj = Branch.objects.get(id=branch)
                self.fields['year'].queryset = branch_obj.years.all()
            except Branch.DoesNotExist:
                self.fields['year'].queryset = Year.objects.none()
        else:
            # For new subjects, show all years
            self.fields['year'].queryset = Year.objects.all()


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    form = SubjectAdminForm
    list_display = ['name', 'code', 'year', 'get_college', 'has_drive_link']
    list_filter = ['year', 'year__branch__college', 'created_at']
    search_fields = ['name', 'code', 'year__branch__name', 'year__branch__college__name']
    readonly_fields = ['created_at']
    
    class Media:
        js = ('smru/admin/subject_form.js',)
    
    def get_college(self, obj):
        return obj.year.branch.college.name
    get_college.short_description = 'College'

    def has_drive_link(self, obj):
        if obj.drive_link:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_drive_link.short_description = 'Drive Link'


@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'timestamp', 'ip_address']
    list_filter = ['activity_type', ('timestamp', admin.DateFieldListFilter), 'user']
    date_hierarchy = 'timestamp'
    search_fields = ['user__username', 'user__email', 'ip_address', 'notes']
    readonly_fields = ['user', 'activity_type', 'timestamp', 'ip_address', 'user_agent', 'notes']


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
    list_display = ['id', 'name', 'roll', 'category', 'status_badge', 'submitted_at', 'has_response', 'complaint_preview']
    list_filter = ['status', 'category', 'submitted_at']
    search_fields = ['name', 'roll', 'email', 'complaint_text', 'response']
    readonly_fields = ['submitted_at', 'resolved_at', 'id']
    date_hierarchy = 'submitted_at'
    ordering = ['-submitted_at']
    
    fieldsets = (
        ('Complainant Information', {
            'fields': ('id', 'name', 'roll', 'email', 'phone'),
            'classes': ('collapse',)
        }),
        ('Complaint Details', {
            'fields': ('category', 'complaint_text', 'file'),
        }),
        ('Admin Response', {
            'fields': ('status', 'response'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_resolved', 'mark_closed', 'mark_in_progress']
    
    def status_badge(self, obj):
        status_colors = {
            'new': 'danger',
            'in_progress': 'warning', 
            'resolved': 'success',
            'closed': 'secondary'
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}" style="font-size: 0.8em;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def complaint_preview(self, obj):
        """Show a preview of the complaint text"""
        preview = obj.complaint_text[:50]
        if len(obj.complaint_text) > 50:
            preview += '...'
        return format_html('<span title="{}">{}</span>', obj.complaint_text, preview)
    complaint_preview.short_description = 'Complaint Preview'
    
    def has_response(self, obj):
        """Check if admin has responded"""
        if obj.response:
            return format_html('<span style="color: green; font-weight: bold;">✓</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗</span>')
    has_response.short_description = 'Response'
    
    def mark_resolved(self, request, queryset):
        count = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{count} complaint(s) marked as resolved.')
    mark_resolved.short_description = 'Mark selected as Resolved'
    
    def mark_closed(self, request, queryset):
        count = queryset.update(status='closed')
        self.message_user(request, f'{count} complaint(s) marked as Closed.')
    mark_closed.short_description = 'Mark selected as Closed'
    
    def mark_in_progress(self, request, queryset):
        count = queryset.update(status='in_progress')
        self.message_user(request, f'{count} complaint(s) marked as In Progress.')
    mark_in_progress.short_description = 'Mark selected as In Progress'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make complaint_text and response fields larger for better readability
        if 'complaint_text' in form.base_fields:
            form.base_fields['complaint_text'].widget.attrs.update({
                'rows': 8,
                'style': 'font-family: monospace; resize: vertical;'
            })
        if 'response' in form.base_fields:
            form.base_fields['response'].widget.attrs.update({
                'rows': 6,
                'style': 'resize: vertical;'
            })
        return form


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'roll_number', 'college', 'branch', 'year', 'can_view_all_complaints', 'can_manage_events', 'can_manage_notifications']
    list_filter = ['college', 'branch', 'year', 'can_view_all_complaints', 'can_manage_events', 'can_manage_notifications']
    search_fields = ['user__username', 'user__email', 'roll_number']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'roll_number', 'phone')
        }),
        ('Academic Information', {
            'fields': ('college', 'branch', 'year')
        }),
        ('Profile', {
            'fields': ('profile_picture', 'bio')
        }),
        ('Permissions', {
            'fields': ('can_view_all_complaints', 'can_manage_events', 'can_manage_notifications'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_username(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_username.short_description = 'Student Name'


# Customize admin site
admin.site.site_header = 'College Portal Administration'
admin.site.site_title = 'College Portal Admin'
admin.site.index_title = 'Welcome to College Portal Admin'