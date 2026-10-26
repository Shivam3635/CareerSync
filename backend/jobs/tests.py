from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from students.models import StudentProfile, StudentQualification
from jobs.models import Job, JobEligibilityRule
from jobs.services.eligibility import calculate_age_at_cutoff, evaluate_student_for_job

User = get_user_model()


class EligibilityEngineTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='teststudent@example.com',
            password='testpassword123',
            full_name='Test Candidate'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            date_of_birth=date(1999, 6, 15),
            gender='male',
            category='OBC',
            domicile_state='Uttar Pradesh'
        )
        self.qual_10 = StudentQualification.objects.create(
            student=self.profile,
            level='10th',
            degree='High School',
            status='completed',
            passing_year=2015
        )
        self.qual_12 = StudentQualification.objects.create(
            student=self.profile,
            level='12th',
            degree='Intermediate',
            status='completed',
            passing_year=2017
        )
        self.qual_grad = StudentQualification.objects.create(
            student=self.profile,
            level='Graduate',
            degree='B.Sc',
            status='completed',
            passing_year=2020
        )

        # Base active job
        today = timezone.now().date()
        self.job = Job.objects.create(
            title='Sample Staff Exam 2026',
            organization='Test Commission',
            category='Civil Services',
            application_start_date=today - timedelta(days=5),
            application_deadline=today + timedelta(days=25),
            age_cutoff_date=date(today.year, 8, 1),
            min_age=21,
            max_age=30,
            original_url='https://example.com/notification',
            is_published=True
        )
        self.rule = JobEligibilityRule.objects.create(
            job=self.job,
            min_qualification_level='Graduate',
            allowed_status='completed_only',
            age_relaxations={'OBC': 3, 'SC': 5, 'ST': 5, 'EWS': 0, 'GEN': 0},
            domicile_requirement='All India'
        )

    def test_leap_year_and_exact_age_calculation(self):
        # Born on Feb 29, 2000 (leap year)
        born = date(2000, 2, 29)
        # On Feb 28, 2024 -> 23 full years
        self.assertEqual(calculate_age_at_cutoff(born, date(2024, 2, 28)), 23)
        # On Feb 29, 2024 -> 24 full years
        self.assertEqual(calculate_age_at_cutoff(born, date(2024, 2, 29)), 24)
        # On Mar 1, 2024 -> 24 full years
        self.assertEqual(calculate_age_at_cutoff(born, date(2024, 3, 1)), 24)

    def test_eligible_candidate_with_category_relaxation(self):
        # On cutoff (today.year, 8, 1), candidate born 1999-06-15 is ~27 years old
        # Min: 21, Max: 30 + 3 (OBC) = 33 -> Candidate is ELIGIBLE
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'eligible')
        self.assertTrue(len(result['reasons']) >= 2)
        self.assertEqual(len(result['failed_criteria']), 0)

    def test_above_age_limit_even_with_relaxation(self):
        # Set DOB to 1985 (age 41)
        self.profile.date_of_birth = date(1985, 1, 1)
        self.profile.save()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'not_eligible')
        self.assertTrue(any('Above age limit' in f for f in result['failed_criteria']))

    def test_under_age_limit(self):
        # Set DOB to 2010 (age 16, min age 21)
        self.profile.date_of_birth = date(2010, 1, 1)
        self.profile.save()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'not_eligible')
        self.assertTrue(any('Age requirement not met' in f for f in result['failed_criteria']))

    def test_qualification_mismatch(self):
        # Require Post Graduate, but candidate only has Graduate
        self.rule.min_qualification_level = 'Post Graduate'
        self.rule.save()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'not_eligible')
        self.assertTrue(any('Qualification mismatch' in f for f in result['failed_criteria']))

    def test_appearing_status_not_allowed(self):
        # Change Graduate status to appearing when rule requires completed_only
        self.qual_grad.status = 'appearing'
        self.qual_grad.save()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'not_eligible')
        self.assertTrue(any('Requires completed' in f for f in result['failed_criteria']))

    def test_appearing_status_allowed(self):
        # Allow appearing candidates
        self.rule.allowed_status = 'appearing_allowed'
        self.rule.save()
        self.qual_grad.status = 'appearing'
        self.qual_grad.save()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'eligible')

    def test_missing_profile_info_yields_review_required(self):
        # Remove qualifications
        StudentQualification.objects.filter(student=self.profile).delete()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'review_required')
        self.assertTrue(len(result['warnings']) > 0)

    def test_expired_job_yields_not_eligible(self):
        # Job whose application deadline has passed
        self.job.application_deadline = timezone.now().date() - timedelta(days=2)
        self.job.save()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'not_eligible')
        self.assertTrue(result['details']['is_expired'])

    def test_completed_lower_qual_when_higher_is_appearing(self):
        # Candidate has 12th (completed) and Graduate (appearing)
        self.qual_grad.status = 'appearing'
        self.qual_grad.save()
        # Job requires 12th (completed_only)
        self.rule.min_qualification_level = '12th'
        self.rule.allowed_status = 'completed_only'
        self.rule.save()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'eligible')
        self.assertTrue(any("hold '12th' (completed)" in r for r in result['reasons']))

    def test_additional_certification_requirement_not_met_yields_not_eligible(self):
        # Job requires 10th + 2-year ITI
        self.rule.min_qualification_level = '10th'
        self.rule.additional_certification_requirement = '2 year ITI by NCVT / SCVT, 3 years Diploma, or NSQF Skill Certificate'
        self.rule.save()
        # Candidate has 10th and 12th, but no ITI in additional_certifications
        self.profile.additional_certifications = ''
        self.profile.save()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'not_eligible')
        self.assertTrue(any('Certification requirement not met' in f for f in result['failed_criteria']))

    def test_additional_certification_requirement_met_yields_eligible(self):
        # Job requires 10th + 2-year ITI
        self.rule.min_qualification_level = '10th'
        self.rule.additional_certification_requirement = '2 year ITI by NCVT / SCVT, 3 years Diploma, or NSQF Skill Certificate'
        self.rule.save()
        # Candidate records ITI
        self.profile.additional_certifications = '2-year ITI Fitter trade by NCVT'
        self.profile.save()
        result = evaluate_student_for_job(self.profile, self.job)
        self.assertEqual(result['status'], 'eligible')
        self.assertTrue(any('Additional certification confirmed' in r for r in result['reasons']))


class AdminAPITestCase(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            email='admin_test@example.com',
            password='adminpassword123',
            full_name='Test Admin',
            role='admin',
            is_staff=True
        )
        self.student_user = User.objects.create_user(
            email='student_test@example.com',
            password='studentpassword123',
            full_name='Student Candidate',
            role='student'
        )

    def test_student_cannot_access_admin_api(self):
        self.client.force_authenticate(user=self.student_user)
        res = self.client.get('/api/admin/stats/')
        self.assertEqual(res.status_code, 403)

    def test_admin_can_access_stats(self):
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get('/api/admin/stats/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('total_jobs', res.data)

    def test_admin_create_job_and_toggle_publish(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            'title': 'New Test Commission Exam 2026',
            'organization': 'Staff Bureau',
            'category': 'Banking',
            'application_start_date': '2026-10-01',
            'application_deadline': '2026-12-01',
            'age_cutoff_date': '2026-08-01',
            'min_age': 20,
            'max_age': 28,
            'original_url': 'https://example.com/job',
            'source_name': 'Official Portal',
            'description': 'Recruitment for testing.',
            'is_published': False,
            'min_qualification_level': 'Graduate',
            'allowed_status': 'completed_only',
            'domicile_requirement': 'All India',
        }
        res = self.client.post('/api/admin/jobs/', payload, format='json')
        self.assertEqual(res.status_code, 201)
        job_id = res.data['job']['id']
        self.assertFalse(res.data['job']['is_published'])

        # Toggle publish
        toggle_res = self.client.post(f'/api/admin/jobs/{job_id}/toggle-publish/')
        self.assertEqual(toggle_res.status_code, 200)
        self.assertTrue(toggle_res.data['is_published'])


from unittest.mock import patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from jobs.services.url_extractor import validate_safe_url, SSRFSecurityError, detect_page_type
from jobs.services.pdf_extractor import validate_pdf_file, PDFValidationError
from jobs.services.ai_extractor import extract_and_structure_job, normalize_date_string


class AIAssistedJobPostingTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin_tester@careersync.demo',
            password='adminpass123',
            full_name='Super Admin',
            role='admin',
            is_staff=True
        )
        self.student = User.objects.create_user(
            email='student_tester@careersync.demo',
            password='studentpass123',
            full_name='Applicant Candidate',
            role='student'
        )
        self.profile = StudentProfile.objects.create(
            user=self.student,
            date_of_birth=date(1998, 5, 20),
            gender='female',
            category='GEN',
            domicile_state='Delhi'
        )
        StudentQualification.objects.create(
            student=self.profile,
            level='Graduate',
            degree='B.A.',
            status='completed',
            passing_year=2020
        )

    # 1. SSRF Guard Tests
    def test_ssrf_blocks_localhost_and_loopback(self):
        with self.assertRaises(SSRFSecurityError):
            validate_safe_url("http://localhost/admin")
        with self.assertRaises(SSRFSecurityError):
            validate_safe_url("http://127.0.0.1:8000/api/admin/")

    def test_ssrf_blocks_cloud_metadata(self):
        with self.assertRaises(SSRFSecurityError):
            validate_safe_url("http://169.254.169.254/latest/meta-data/")

    def test_ssrf_blocks_private_networks(self):
        with self.assertRaises(SSRFSecurityError):
            validate_safe_url("http://10.0.0.1/internal-secret")
        with self.assertRaises(SSRFSecurityError):
            validate_safe_url("http://192.168.1.1/router")

    def test_ssrf_blocks_bad_schemes(self):
        with self.assertRaises(SSRFSecurityError):
            validate_safe_url("file:///etc/passwd")
        with self.assertRaises(SSRFSecurityError):
            validate_safe_url("ftp://ftp.example.com/file.txt")

    # 2. Content Type & Non-Recruitment Detection Tests
    def test_page_type_detection_rejects_admit_cards(self):
        page_type = detect_page_type(
            "SSC CGL Admit Card 2026 Download Hall Ticket",
            "Staff Selection Commission has released the Admit Card and exam city slip for CGL Exam."
        )
        self.assertEqual(page_type, 'admit_card')

    def test_page_type_detection_identifies_recruitment(self):
        page_type = detect_page_type(
            "UPSC Civil Services Recruitment 2026 Online Application Form",
            "Union Public Service Commission invites online applications for 1056 vacancies."
        )
        self.assertEqual(page_type, 'recruitment')

    # 3. PDF Extraction & Validation Tests
    def test_pdf_validation_rejects_non_pdf_file(self):
        bad_file = SimpleUploadedFile("malicious.exe", b"MZexecutable...", content_type="application/octet-stream")
        with self.assertRaises(PDFValidationError):
            validate_pdf_file(bad_file)

    def test_pdf_validation_rejects_corrupted_header(self):
        corrupted = SimpleUploadedFile("fake.pdf", b"NOT_A_PDF_FILE", content_type="application/pdf")
        with self.assertRaises(PDFValidationError):
            validate_pdf_file(corrupted)

    # 4. AI Normalization & Conflict Detection Tests
    def test_ai_extractor_detects_age_conflict(self):
        raw_text = """
        Recruitment Notification 2026
        Age Limit: Minimum Age: 35 Years, Maximum Age: 28 Years
        Apply Online last date: 30/11/2026
        """
        extracted = extract_and_structure_job(raw_text, source_url="https://sarkariresult.com/demo")
        metadata = extracted['metadata']
        self.assertTrue(len(metadata['conflicts']) > 0)
        self.assertTrue(any('Mismatched age' in c for c in metadata['conflicts']))

    def test_ai_extractor_normalizes_dates(self):
        self.assertEqual(normalize_date_string("25/12/2026"), "2026-12-25")
        self.assertEqual(normalize_date_string("15-08-2026"), "2026-08-15")
        self.assertEqual(normalize_date_string("2026-05-10"), "2026-05-10")

    # 5. Authorization & Permissions
    def test_student_cannot_access_extract_endpoint(self):
        self.client.force_authenticate(user=self.student)
        res = self.client.post('/api/admin/jobs/extract-url/', {'url': 'https://example.com/job'}, format='json')
        self.assertEqual(res.status_code, 403)

    # 6. End-to-End Extraction, Pending Review, and Approval Workflow
    @patch('jobs.services.url_extractor.fetch_url_safely')
    def test_url_extraction_creates_pending_review_draft(self, mock_fetch):
        mock_html = """
        <html>
        <head><title>UPSC Combined Administrative Services 2026 Online Form</title></head>
        <body>
            <h1>Union Public Service Commission (UPSC)</h1>
            <p>Advt No: 05/2026-CSP</p>
            <p>Application Begin: 10/11/2026</p>
            <p>Last Date for Apply: 30/12/2026</p>
            <p>Age Limit as on: 01/08/2026</p>
            <p>Minimum Age: 21 Years</p>
            <p>Maximum Age: 32 Years</p>
            <p>Total Vacancy: 1250 Posts</p>
            <p>Eligibility: Bachelor Degree in Any Stream from Recognized University.</p>
            <a href="https://upsc.gov.in/notice.pdf">Download Notification</a>
            <a href="https://upsconline.nic.in/apply">Apply Online</a>
        </body>
        </html>
        """
        mock_fetch.return_value = ("https://sarkariresult.com/upsc-2026", mock_html)

        self.client.force_authenticate(user=self.admin)
        res = self.client.post('/api/admin/jobs/extract-url/', {'url': 'https://sarkariresult.com/upsc-2026'}, format='json')
        self.assertEqual(res.status_code, 201)
        job_data = res.data['job']

        # Rule check: MUST be pending_review and NOT published!
        self.assertEqual(job_data['status'], 'pending_review')
        self.assertFalse(job_data['is_published'])
        self.assertEqual(job_data['min_age'], 21)
        self.assertEqual(job_data['max_age'], 32)
        self.assertEqual(job_data['total_vacancies'], 1250)

        # UNAPPROVED JOB MUST NOT BE VISIBLE TO ASPIRANTS
        self.client.force_authenticate(user=self.student)
        public_res = self.client.get('/api/jobs/')
        self.assertFalse(any(j['id'] == job_data['id'] for j in public_res.data))

        matches_res = self.client.get('/api/jobs/matches/')
        self.assertFalse(any(j['id'] == job_data['id'] for j in matches_res.data['jobs']))

        # ADMIN APPROVAL WORKFLOW
        self.client.force_authenticate(user=self.admin)
        approve_res = self.client.post(f"/api/admin/jobs/{job_data['id']}/approve/", {'review_notes': 'Verified against gazette.'}, format='json')
        self.assertEqual(approve_res.status_code, 200)
        self.assertEqual(approve_res.data['job']['status'], 'approved')
        self.assertTrue(approve_res.data['job']['is_published'])

        # NOW APPROVED JOB IS VISIBLE TO ELIGIBLE CANDIDATE
        self.client.force_authenticate(user=self.student)
        public_after = self.client.get('/api/jobs/')
        self.assertTrue(any(j['id'] == job_data['id'] for j in public_after.data))

    def test_reject_job_draft(self):
        # Create a pending review draft
        job = Job.objects.create(
            title="Incomplete Job Draft",
            organization="State Board",
            status="pending_review",
            is_published=False,
            min_age=18,
            max_age=30,
            application_start_date=date(2026, 1, 1),
            application_deadline=date(2026, 2, 1),
            age_cutoff_date=date(2026, 1, 1)
        )
        JobEligibilityRule.objects.create(job=job)

        self.client.force_authenticate(user=self.admin)
        reject_res = self.client.post(f'/api/admin/jobs/{job.id}/reject/', {'review_notes': 'Duplicate notice'}, format='json')
        self.assertEqual(reject_res.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.status, 'rejected')
        self.assertFalse(job.is_published)


