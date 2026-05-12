from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from smru.models import UserRole


class Command(BaseCommand):
    help = 'Manage user roles'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='Username of the user'
        )
        parser.add_argument(
            'role',
            type=str,
            choices=['student', 'hod', 'chairman', 'principal', 'director', 'faculty', 'security', 'anti_ragging_team', 'she_team', 'admin', 'other'],
            help='Role to assign'
        )
        parser.add_argument(
            '--department',
            type=str,
            help='Department (for HODs, faculty, etc.)',
            default=''
        )

    def handle(self, *args, **options):
        username = options['username']
        role = options['role']
        department = options['department']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')

        # Get or create UserRole
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            defaults={'role': role, 'department': department}
        )

        if not created:
            user_role.role = role
            user_role.department = department
            user_role.save()

        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(f'{action} role "{role}" for user "{username}"')
        )