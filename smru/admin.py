from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import College, Branch, Year, Subject, Notification, Event, Complaint, StudentProfile


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'branches_count']
    list_filter = ['created_at']
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
    list_display = ['id', 'name', 'roll', 'category', 'status', 'submitted_at']
    list_filter = ['status', 'category', 'submitted_at']
    search_fields = ['name', 'roll', 'email', 'complaint_text']
    readonly_fields = ['submitted_at', 'resolved_at', 'id']
    fieldsets = (
        ('Complainant Info', {
            'fields': ('id', 'name', 'roll', 'email', 'phone')
        }),
        ('Complaint', {
            'fields': ('category', 'complaint_text', 'file')
        }),
        ('Response', {
            'fields': ('status', 'response')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_resolved', 'mark_closed']
    
    def mark_resolved(self, request, queryset):
        count = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{count} complaint(s) marked as resolved.')
    mark_resolved.short_description = 'Mark selected as Resolved'
    
    def mark_closed(self, request, queryset):
        count = queryset.update(status='closed')
        self.message_user(request, f'{count} complaint(s) marked as Closed.')
    mark_closed.short_description = 'Mark selected as Closed'


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'roll_number', 'college', 'branch', 'year']
    list_filter = ['college', 'branch', 'year']
    search_fields = ['user__username', 'user__email', 'roll_number']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_username(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_username.short_description = 'Student Name'


# Customize admin site
admin.site.site_header = 'College Portal Administration'
admin.site.site_title = 'College Portal Admin'
admin.site.index_title = 'Welcome to College Portal Admin'