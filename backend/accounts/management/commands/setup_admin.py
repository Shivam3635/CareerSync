from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = "Create or update administrative account with explicit credentials"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='singhshivamop36@gmail.com',
            help='Admin email address'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Admin@CareerSync2026',
            help='Admin password'
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']

        user, created = User.objects.get_or_create(
            email=email,
            defaults={'role': 'admin', 'is_staff': True, 'is_superuser': True}
        )

        user.role = 'admin'
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "Created new" if created else "Updated existing"
        self.stdout.write(self.style.SUCCESS(
            f"Successfully {action} admin account: {email}"
        ))

        # Also ensure backup admin@careersync.in is provisioned
        backup_email = 'admin@careersync.in'
        b_user, b_created = User.objects.get_or_create(
            email=backup_email,
            defaults={'role': 'admin', 'is_staff': True, 'is_superuser': True}
        )
        b_user.role = 'admin'
        b_user.is_staff = True
        b_user.is_superuser = True
        b_user.set_password(password)
        b_user.save()
        self.stdout.write(self.style.SUCCESS(
            f"Successfully synced admin account: {backup_email}"
        ))
