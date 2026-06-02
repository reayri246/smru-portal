"""
Django management command to process registration approval requests:
- Send reminders to assigned staff every 30 minutes after 1 hour
- Lock staff permissions after 4 hours of no response
- Delete requests and notify students after 12 hours of no response
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from smru.models import RegistrationApprovalRequest, RegistrationAuditLog, User
import logging

logger = logging.getLogger('smru')


class Command(BaseCommand):
    help = 'Process registration approval requests: send reminders, lock staff, delete old requests'

    def handle(self, *args, **options):
        self.stdout.write('Processing approval requests...')
        
        now = timezone.now()
        
        # Process requests that are still pending
        pending_requests = RegistrationApprovalRequest.objects.filter(
            status='pending',
            assigned_staff__isnull=False
        )

        for request in pending_requests:
            if not request.assigned_at:
                continue
                
            time_elapsed = now - request.assigned_at
            
            # After 12 hours: delete and notify student
            if time_elapsed >= timedelta(hours=12):
                self._delete_request(request, now)
            
            # After 4 hours: lock staff permissions if not already locked
            elif time_elapsed >= timedelta(hours=4) and not request.staff_permissions_locked:
                self._lock_staff_permissions(request, now)
            
            # After 1 hour: send reminders every 30 minutes
            elif time_elapsed >= timedelta(hours=1):
                self._send_reminder_if_needed(request, now)

        self.stdout.write(self.style.SUCCESS('Approval requests processed successfully'))

    def _send_reminder_if_needed(self, request, now):
        """Send reminder email to assigned staff if 30 minutes have passed since last reminder"""
        if request.first_reminder_sent_at is None:
            # First reminder after 1 hour
            self._send_staff_reminder(request, now, is_first=True)
            request.first_reminder_sent_at = now
            request.last_reminder_at = now
            request.reminder_count = 1
            request.save()
            self.stdout.write(f'  Sent first reminder for request {request.id} to {request.assigned_staff.email}')
        
        elif request.last_reminder_at and (now - request.last_reminder_at) >= timedelta(minutes=30):
            # Subsequent reminders every 30 minutes
            self._send_staff_reminder(request, now, is_first=False)
            request.last_reminder_at = now
            request.reminder_count += 1
            request.save()
            self.stdout.write(f'  Sent reminder #{request.reminder_count} for request {request.id} to {request.assigned_staff.email}')

    def _send_staff_reminder(self, request, now, is_first=False):
        """Send reminder email to assigned staff about pending request"""
        try:
            subject = f'[URGENT] Registration Request Pending - Student: {request.user.get_full_name()}'
            
            if is_first:
                time_remaining = timedelta(hours=4) - (now - request.assigned_at)
                message = f"""
Dear {request.assigned_staff.get_full_name()},

A registration request from student {request.user.get_full_name()} ({request.user.email}) 
for {request.college.name if request.college else 'Unknown College'} 
has been pending for 1 hour and awaits your approval or rejection.

Roll Number: {request.roll_number}
Email: {request.email}

ACTION REQUIRED:
Please log in to the admin panel and take action within the next 3 hours, or your 
account permissions will be locked.

Time until lock: {time_remaining}
Requested at: {request.assigned_at}

Admin Link: {self._get_admin_link(request)}

Please approve or reject this request to regain full admin access.

Best regards,
SMRU Portal Admin
                """
            else:
                time_remaining = timedelta(hours=4) - (now - request.assigned_at)
                message = f"""
Dear {request.assigned_staff.get_full_name()},

REMINDER #{request.reminder_count}: Registration request from {request.user.get_full_name()} ({request.user.email}) 
is still pending for {request.college.name if request.college else 'Unknown College'}.

This is reminder #{request.reminder_count}. 
If no action is taken, your account permissions will be locked.

Time remaining before lock: {time_remaining}

Admin Link: {self._get_admin_link(request)}

Please approve or reject this request immediately.

Best regards,
SMRU Portal Admin
                """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                [request.assigned_staff.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f'Error sending reminder email for request {request.id}: {str(e)}')

    def _lock_staff_permissions(self, request, now):
        """Lock staff permissions after 4 hours of no response"""
        try:
            request.staff_permissions_locked = True
            request.staff_locked_at = now
            request.save()
            
            # Send notification to staff that account is locked
            subject = '[ACTION REQUIRED] Your Admin Account Permissions Have Been Locked'
            message = f"""
Dear {request.assigned_staff.get_full_name()},

Your admin account permissions have been LOCKED due to inaction on a pending 
registration request from {request.user.get_full_name()}.

RESTRICTION:
You can only access the Registration Requests section to approve or reject pending requests.
Once you take action on pending requests, your full permissions will be restored.

STUDENT DETAILS:
Name: {request.user.get_full_name()}
Email: {request.user.email}
Roll Number: {request.roll_number}

To unlock your account:
1. Log in to the admin panel: {self._get_admin_url()}
2. Navigate to Login Requests (RegistrationApprovalRequest)
3. Find the request for {request.user.get_full_name()}
4. Approve or reject the request
5. Your permissions will be automatically restored

Locked at: {now}

If you need further assistance, please contact the system administrator.

Best regards,
SMRU Portal Admin
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                [request.assigned_staff.email],
                fail_silently=False,
            )
            
            logger.info(f'Locked staff permissions for {request.assigned_staff.email} due to request {request.id}')
            self.stdout.write(f'  Locked permissions for staff {request.assigned_staff.email} on request {request.id}')
            
        except Exception as e:
            logger.error(f'Error locking staff permissions for request {request.id}: {str(e)}')

    def _delete_request(self, request, now):
        """Delete request after 12 hours and notify student to re-register"""
        try:
            # Update status to deleted
            request.status = 'deleted'
            request.save()
            
            # Create audit log
            RegistrationAuditLog.objects.create(
                request=request,
                action='deleted_no_response',
                performed_by=None,
                details='Request deleted due to no staff response for 12 hours'
            )
            
            # Send email to student
            from smru.views import send_registration_reregister_email
            send_registration_reregister_email(request)
            
            logger.info(f'Deleted registration request {request.id} and notified student {request.user.email}')
            self.stdout.write(f'  Deleted request {request.id} and notified student {request.user.email}')
            
        except Exception as e:
            logger.error(f'Error deleting request {request.id}: {str(e)}')

    def _get_admin_link(self, request):
        """Get direct admin link for the request"""
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
        return f'{site_url}/admin/smru/registrationapprovalrequest/{request.id}/change/'
    
    def _get_admin_url(self):
        """Get the admin panel URL"""
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
        return f'{site_url}/admin/'

