from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from smru.models import LoginRequest, StudentProfile


class Command(BaseCommand):
    help = 'Create missing LoginRequest objects for users with unapproved student profiles'

    def handle(self, *args, **options):
        created_count = 0
        for user in User.objects.all():
            if not LoginRequest.objects.filter(user=user).exists():
                # Check if user has unapproved student profile
                if StudentProfile.objects.filter(user=user, is_approved=False).exists():
                    LoginRequest.objects.create(user=user, status='pending')
                    self.stdout.write(
                        self.style.SUCCESS(f'Created LoginRequest for: {user.username}')
                    )
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Total LoginRequests created: {created_count}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total LoginRequests now: {LoginRequest.objects.count()}')
        )