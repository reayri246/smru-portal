import logging
import traceback
from django.conf import settings
from django.core.mail import EmailMessage
from .views import get_admin_recipients

logger = logging.getLogger('smru')


class AdminErrorAlertMiddleware:
    """Middleware that notifies admins by email whenever an unhandled exception occurs."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            if not settings.DEBUG:
                subject = f"[SMRU Portal] Unhandled Exception: {request.path}"
                message = (
                    f"A server error occurred at {request.path}\n"
                    f"Method: {request.method}\n"
                    f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}\n"
                    f"Remote addr: {request.META.get('REMOTE_ADDR', 'unknown')}\n"
                    f"Host: {request.get_host()}\n\n"
                    f"Exception:\n{repr(exc)}\n\n"
                    f"Traceback:\n{traceback.format_exc()}"
                )
                recipients = get_admin_recipients()
                if recipients:
                    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER
                    email = EmailMessage(subject, message, from_email, recipients)
                    try:
                        db_path = settings.DATABASES['default'].get('NAME', '')
                        if db_path and hasattr(settings, 'DATABASES') and db_path and db_path.endswith(('sqlite3', '.db')):
                            try:
                                with open(db_path, 'rb') as db_file:
                                    email.attach('database_backup.sqlite3', db_file.read(), 'application/octet-stream')
                                    logger.info('Attached database file to admin crash alert.')
                            except Exception as attach_error:
                                logger.error(f'Failed to attach database file to admin crash alert: {attach_error}')
                        email.send(fail_silently=False)
                        logger.info('Admin crash alert email sent successfully.')
                    except Exception as mail_error:
                        logger.error(f'Failed to send admin crash alert email: {mail_error}')
            raise
