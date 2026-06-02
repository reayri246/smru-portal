from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from smru.models import RegistrationApprovalRequest, ReminderLog, RegistrationAuditLog, StaffLockLog, UserAccountLock
from django.contrib.auth.models import User
import datetime


class Command(BaseCommand):
    help = 'Process registration reminders and lock staff if they ignore requests'

    def handle(self, *args, **options):
        now = timezone.now()
        one_hour_ago = now - datetime.timedelta(hours=1)
        thirty_minutes = datetime.timedelta(minutes=30)

        pending = RegistrationApprovalRequest.objects.filter(status='pending')
        for req in pending:
            # if created > 1 hour and no reminders yet -> send first reminder
            if req.created_at <= one_hour_ago and not req.last_reminder_at:
                if req.assigned_staff and req.assigned_staff.email:
                    subject = f"Reminder: Registration request for {req.user.get_full_name()}"
                    message = f"Please review registration request ID {req.id} submitted at {req.created_at}."
                    try:
                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [req.assigned_staff.email])
                    except Exception:
                        pass
                    ReminderLog.objects.create(request=req, to_staff=req.assigned_staff, message=message)
                    req.last_reminder_at = now
                    req.save()
                    RegistrationAuditLog.objects.create(request=req, action='reminder_sent', performed_by=None, details=f'Reminder sent to {req.assigned_staff}')

            # subsequent reminders every 30 minutes
            if req.last_reminder_at and (now - req.last_reminder_at) >= thirty_minutes:
                if req.assigned_staff and req.assigned_staff.email:
                    subject = f"Follow-up: Registration request for {req.user.get_full_name()}"
                    message = f"Follow-up: please act on registration request ID {req.id}."
                    try:
                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [req.assigned_staff.email])
                    except Exception:
                        pass
                    ReminderLog.objects.create(request=req, to_staff=req.assigned_staff, message=message)
                    req.last_reminder_at = now
                    req.save()
                    RegistrationAuditLog.objects.create(request=req, action='reminder_sent', performed_by=None, details=f'Follow-up reminder sent to {req.assigned_staff}')

            # If there are 3 or more reminders for this request, lock the staff account
            reminders_count = ReminderLog.objects.filter(request=req).count()
            if reminders_count >= 3 and req.assigned_staff:
                staff = req.assigned_staff
                # lock account
                try:
                    account_lock, created = UserAccountLock.objects.get_or_create(user=staff)
                    if not account_lock.is_account_locked():
                        account_lock.lock_account('Ignored registration requests', duration_minutes=60*24)  # lock for 24 hours
                    StaffLockLog.objects.create(staff=staff, reason='Ignored registration requests')
                    RegistrationAuditLog.objects.create(request=req, action='account_locked', performed_by=None, details=f'Staff {staff.username} locked')
                except Exception:
                    pass
