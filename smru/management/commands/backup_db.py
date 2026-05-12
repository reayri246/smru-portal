from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
import os
import datetime
import gzip
import shutil

class Command(BaseCommand):
    help = 'Create a backup of the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Output directory for backup files',
            default='backups'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress the backup file with gzip',
        )

    def handle(self, *args, **options):
        output_dir = options['output']
        compress = options['compress']

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        db_engine = settings.DATABASES['default']['ENGINE']

        if 'sqlite3' in db_engine:
            # SQLite backup
            db_path = settings.DATABASES['default']['NAME']
            backup_filename = f'db_backup_{timestamp}.sqlite3'
            backup_path = os.path.join(output_dir, backup_filename)

            try:
                shutil.copy2(db_path, backup_path)
                self.stdout.write(
                    self.style.SUCCESS(f'SQLite database backed up to {backup_path}')
                )

                if compress:
                    compressed_path = backup_path + '.gz'
                    with open(backup_path, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(backup_path)
                    backup_path = compressed_path
                    self.stdout.write(
                        self.style.SUCCESS(f'Backup compressed to {backup_path}')
                    )

            except Exception as e:
                raise CommandError(f'Backup failed: {str(e)}')

        elif 'postgresql' in db_engine:
            # PostgreSQL backup using pg_dump
            import subprocess

            db_name = settings.DATABASES['default']['NAME']
            db_user = settings.DATABASES['default']['USER']
            db_host = settings.DATABASES['default'].get('HOST', 'localhost')
            db_port = settings.DATABASES['default'].get('PORT', '5432')

            backup_filename = f'db_backup_{timestamp}.sql'
            backup_path = os.path.join(output_dir, backup_filename)

            cmd = [
                'pg_dump',
                '-h', db_host,
                '-p', db_port,
                '-U', db_user,
                '-d', db_name,
                '-f', backup_path
            ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                self.stdout.write(
                    self.style.SUCCESS(f'PostgreSQL database backed up to {backup_path}')
                )

                if compress:
                    compressed_path = backup_path + '.gz'
                    with open(backup_path, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(backup_path)
                    backup_path = compressed_path
                    self.stdout.write(
                        self.style.SUCCESS(f'Backup compressed to {backup_path}')
                    )

            except subprocess.CalledProcessError as e:
                raise CommandError(f'pg_dump failed: {e.stderr}')

        else:
            raise CommandError(f'Unsupported database engine: {db_engine}')

        self.stdout.write(
            self.style.SUCCESS(f'Database backup completed successfully: {backup_path}')
        )