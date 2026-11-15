from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from students.models import StudentProfile, StudentQualification

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds CareerSync with demo accounts (Student & Admin) without altering live job notices.'

    def handle(self, *args, **options):
        # 1. Create or update Admin Demo User
        admin_email = "admin@careersync.demo"
        admin_user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'username': admin_email,
                'full_name': 'Admin Officer',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password("admin123")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.role = 'admin'
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f"Admin demo ready: {admin_email} / admin123"))

        # 2. Create or update Student Demo User
        student_email = "student@careersync.demo"
        student_user, created = User.objects.get_or_create(
            email=student_email,
            defaults={
                'username': student_email,
                'full_name': 'Aarav Sharma',
                'role': 'student',
            }
        )
        student_user.set_password("password123")
        student_user.role = 'student'
        student_user.save()

        # Student Profile
        profile, _ = StudentProfile.objects.update_or_create(
            user=student_user,
            defaults={
                'date_of_birth': date(1999, 6, 15),
                'gender': 'male',
                'category': 'OBC',
                'domicile_state': 'Uttar Pradesh',
            }
        )

        # Clear existing qualifications and re-add for student demo
        StudentQualification.objects.filter(student=profile).delete()
        StudentQualification.objects.create(
            student=profile,
            level='10th',
            degree='CBSE Secondary School',
            status='completed',
            passing_year=2015,
            percentage=88.50
        )
        StudentQualification.objects.create(
            student=profile,
            level='12th',
            degree='Senior Secondary (PCM)',
            status='completed',
            passing_year=2017,
            percentage=85.00
        )
        StudentQualification.objects.create(
            student=profile,
            level='Graduate',
            degree='B.Tech in Computer Science',
            status='completed',
            passing_year=2021,
            percentage=78.20
        )
        self.stdout.write(self.style.SUCCESS(f"Student demo ready: {student_email} / password123 (DOB: 15-Jun-1999, OBC, Graduate)"))
        self.stdout.write(self.style.SUCCESS("Demo accounts initialized successfully without touching live job listings."))
