from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from students.models import StudentProfile, StudentQualification
from jobs.models import Job, JobEligibilityRule
from notifications.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds CareerSync with demo accounts (Student & Admin) and realistic sample job opportunities.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Flushing existing test data..."))
        
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

        # Clear existing qualifications and re-add
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

        # 3. Create Sample Job Notifications
        Job.objects.all().delete()
        
        today = timezone.now().date()
        
        sample_jobs = [
            {
                'title': 'Civil Services Examination (CSE) 2026',
                'organization': 'Union Public Service Commission (UPSC)',
                'category': 'Civil Services',
                'application_start_date': today - timedelta(days=15),
                'application_deadline': today + timedelta(days=35),
                'age_cutoff_date': date(today.year, 8, 1),
                'min_age': 21,
                'max_age': 32,
                'original_url': 'https://upsc.gov.in/examinations/civil-services-preliminary-examination',
                'source_name': 'Official UPSC Portal',
                'description': 'Recruitment to the Indian Administrative Service (IAS), Indian Foreign Service (IFS), Indian Police Service (IPS) and other Central Group A and Group B services.',
                'rule': {
                    'min_qualification_level': 'Graduate',
                    'allowed_status': 'appearing_allowed',
                    'age_relaxations': {'OBC': 3, 'SC': 5, 'ST': 5, 'EWS': 0, 'GEN': 0},
                    'domicile_requirement': 'All India',
                    'conditions_summary': 'Degree of any recognized University or equivalent qualification.'
                }
            },
            {
                'title': 'Combined Graduate Level Examination (SSC CGL) 2026',
                'organization': 'Staff Selection Commission (SSC)',
                'category': 'Civil Services',
                'application_start_date': today - timedelta(days=10),
                'application_deadline': today + timedelta(days=40),
                'age_cutoff_date': date(today.year, 8, 1),
                'min_age': 18,
                'max_age': 30,
                'original_url': 'https://ssc.gov.in/portal/cgl-examination',
                'source_name': 'SSC Official Portal',
                'description': 'Recruitment for Group B and Group C Non-Technical posts in various Ministries, Departments, and Attached Offices of the Government of India.',
                'rule': {
                    'min_qualification_level': 'Graduate',
                    'allowed_status': 'completed_only',
                    'age_relaxations': {'OBC': 3, 'SC': 5, 'ST': 5, 'EWS': 0, 'GEN': 0},
                    'domicile_requirement': 'All India',
                    'conditions_summary': 'Bachelor Degree from a recognized University or Institute.'
                }
            },
            {
                'title': 'Probationary Officers / Management Trainees (CRP PO/MT XIV)',
                'organization': 'Institute of Banking Personnel Selection (IBPS)',
                'category': 'Banking',
                'application_start_date': today - timedelta(days=5),
                'application_deadline': today + timedelta(days=25),
                'age_cutoff_date': date(today.year, 8, 1),
                'min_age': 20,
                'max_age': 30,
                'original_url': 'https://www.ibps.in/index.php/crp-po-mt/',
                'source_name': 'IBPS Official Portal',
                'description': 'Recruitment of Probationary Officers in 11 Public Sector Participating Banks across India.',
                'rule': {
                    'min_qualification_level': 'Graduate',
                    'allowed_status': 'completed_only',
                    'age_relaxations': {'OBC': 3, 'SC': 5, 'ST': 5, 'EWS': 0, 'GEN': 0},
                    'domicile_requirement': 'All India',
                    'conditions_summary': 'A Degree (Graduation) in any discipline from a University recognized by the Govt. Of India.'
                }
            },
            {
                'title': 'Non-Technical Popular Categories (RRB NTPC) 2026',
                'organization': 'Railway Recruitment Control Board (RRB)',
                'category': 'Railways',
                'application_start_date': today - timedelta(days=20),
                'application_deadline': today + timedelta(days=30),
                'age_cutoff_date': date(today.year, 7, 1),
                'min_age': 18,
                'max_age': 33,
                'original_url': 'https://indianrailways.gov.in/rrb-recruitment',
                'source_name': 'Ministry of Railways Portal',
                'description': 'Recruitment for Station Master, Goods Guard, Senior Clerk cum Typist, Commercial Apprentice, and Traffic Assistant.',
                'rule': {
                    'min_qualification_level': '12th',
                    'allowed_status': 'completed_only',
                    'age_relaxations': {'OBC': 3, 'SC': 5, 'ST': 5, 'EWS': 0, 'GEN': 0},
                    'domicile_requirement': 'All India',
                    'conditions_summary': '12th Class or equivalent from recognized Board.'
                }
            },
            {
                'title': 'Scientist / Engineer ‘SC’ Recruitment (Computer Science / IT)',
                'organization': 'Indian Space Research Organisation (ISRO)',
                'category': 'Engineering & Tech',
                'application_start_date': today - timedelta(days=3),
                'application_deadline': today + timedelta(days=45),
                'age_cutoff_date': date(today.year, 9, 1),
                'min_age': 18,
                'max_age': 28,
                'original_url': 'https://www.isro.gov.in/careers',
                'source_name': 'ISRO Centralised Recruitment Board',
                'description': 'Recruitment of Scientist/Engineer \'SC\' in Level 10 of Pay Matrix at various ISRO/DOS Centres.',
                'rule': {
                    'min_qualification_level': 'Graduate',
                    'allowed_status': 'completed_only',
                    'age_relaxations': {'OBC': 3, 'SC': 5, 'ST': 5, 'EWS': 0, 'GEN': 0},
                    'domicile_requirement': 'All India',
                    'conditions_summary': 'BE/B.Tech or equivalent in Computer Science with minimum 65% marks or CGPA 6.84/10.'
                }
            },
            {
                'title': 'Assistant Professor & Lecturer Recruitment (Higher Education)',
                'organization': 'Uttar Pradesh Public Service Commission (UPPSC)',
                'category': 'Teaching',
                'application_start_date': today - timedelta(days=12),
                'application_deadline': today + timedelta(days=20),
                'age_cutoff_date': date(today.year, 7, 1),
                'min_age': 21,
                'max_age': 40,
                'original_url': 'https://uppsc.up.gov.in/faculty-recruitment',
                'source_name': 'UPPSC Portal',
                'description': 'Recruitment of Assistant Professors for Government Degree Colleges across the State.',
                'rule': {
                    'min_qualification_level': 'Post Graduate',
                    'allowed_status': 'completed_only',
                    'age_relaxations': {'OBC': 3, 'SC': 5, 'ST': 5, 'EWS': 0, 'GEN': 0},
                    'domicile_requirement': 'Uttar Pradesh',
                    'conditions_summary': 'Master\'s Degree with 55% marks and qualifying UGC-NET/SLET.'
                }
            },
            {
                'title': 'National Defence Academy (NDA) Examination',
                'organization': 'Union Public Service Commission (UPSC)',
                'category': 'Defense',
                'application_start_date': today - timedelta(days=8),
                'application_deadline': today + timedelta(days=18),
                'age_cutoff_date': date(today.year, 7, 1),
                'min_age': 16,
                'max_age': 19,
                'original_url': 'https://upsc.gov.in/examinations/nda-na',
                'source_name': 'UPSC Portal',
                'description': 'Admission to the Army, Navy and Air Force wings of the NDA for the 154th Course.',
                'rule': {
                    'min_qualification_level': '12th',
                    'allowed_status': 'appearing_allowed',
                    'age_relaxations': {'OBC': 0, 'SC': 0, 'ST': 0, 'EWS': 0, 'GEN': 0},
                    'domicile_requirement': 'All India',
                    'conditions_summary': 'Strict unrelaxed age cutoff: must be between 16.5 and 19.5 years.'
                }
            },
            {
                'title': 'Sub-Inspector of Police (Haryana Police Recruitment)',
                'organization': 'Haryana Staff Selection Commission (HSSC)',
                'category': 'Police & Security',
                'application_start_date': today - timedelta(days=14),
                'application_deadline': today + timedelta(days=14),
                'age_cutoff_date': date(today.year, 8, 1),
                'min_age': 21,
                'max_age': 27,
                'original_url': 'https://hssc.gov.in/si-recruitment',
                'source_name': 'HSSC Portal',
                'description': 'Recruitment of 400 Sub-Inspectors in Haryana Police Department.',
                'rule': {
                    'min_qualification_level': 'Graduate',
                    'allowed_status': 'completed_only',
                    'age_relaxations': {'OBC': 3, 'SC': 5, 'ST': 5, 'EWS': 0, 'GEN': 0},
                    'domicile_requirement': 'Haryana',
                    'conditions_summary': 'Graduate from a recognized university with Haryana domicile certificate.'
                }
            }
        ]

        for item in sample_jobs:
            rule_data = item.pop('rule')
            job = Job.objects.create(**item, is_published=True)
            JobEligibilityRule.objects.create(job=job, **rule_data)
            self.stdout.write(f"  + Seeded Job: {job.title} ({job.organization})")

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(sample_jobs)} sample jobs with eligibility rules."))
