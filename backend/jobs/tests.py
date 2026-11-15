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

    def test_job_watcher_filter_logic(self):
        from jobs.services.job_watcher import is_recruitment_link
        # Genuine recruitment notices
        self.assertTrue(is_recruitment_link("SSC CGL 2026 Apply Online Form", "https://example.com/ssc-cgl-online-form"))
        self.assertTrue(is_recruitment_link("UPSC Civil Services 2026 Notification", "https://example.com/upsc-cse-notification"))
        self.assertTrue(is_recruitment_link("RRB Technician Vacancy 2026", "https://example.com/rrb-technician-bharti"))

        # Non-recruitment notices (Must be rejected)
        self.assertFalse(is_recruitment_link("SSC CGL Tier 1 Admit Card 2026", "https://example.com/ssc-admit-card"))
        self.assertFalse(is_recruitment_link("UPSC CSE Prelims Result Declared", "https://example.com/upsc-prelims-result"))
        self.assertFalse(is_recruitment_link("IBPS PO Official Answer Key", "https://example.com/ibps-po-answer-key"))
        self.assertFalse(is_recruitment_link("Railway Exam Date Sheet & Schedule", "https://example.com/rrb-exam-date"))

    def test_job_watcher_deduplication(self):
        from jobs.services.job_watcher import is_notice_already_ingested
        # Create an existing job
        Job.objects.create(
            title="Combined Graduate Level Examination (SSC CGL) 2026",
            organization="Staff Selection Commission (SSC)",
            original_url="https://example.com/cgl2026",
            status="approved",
            is_published=True
        )
        # Existing job URL or Title should return True
        self.assertTrue(is_notice_already_ingested("https://example.com/cgl2026", "Some Title"))
        self.assertTrue(is_notice_already_ingested("https://example.com/other-url", "Combined Graduate Level Examination (SSC CGL) 2026"))
        # Brand new uningested job should return False
        self.assertFalse(is_notice_already_ingested("https://example.com/brand-new-job-2026", "Brand New Board Officer Recruitment 2026"))

    def test_admin_auto_discover_api_security(self):
        # Non-admin / student must be rejected
        self.client.force_authenticate(user=self.student)
        res = self.client.post('/api/admin/jobs/auto-discover/', {'limit': 2}, format='json')
        self.assertEqual(res.status_code, 403)

        # Admin is authorized
        self.client.force_authenticate(user=self.admin)
        res = self.client.post('/api/admin/jobs/auto-discover/', {'limit': 2}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertIn('report', res.data)
        self.assertIn('ingested_count', res.data)

    def test_parse_sarkari_result_post_links(self):
        from bs4 import BeautifulSoup
        from jobs.services.job_watcher import parse_sarkari_result_post_links

        html = """
        <html>
          <body>
            <h1>UPESSC Assistant Professor Recruitment 2026</h1>
            <table>
              <tr><th>Important Links</th><th>Links</th></tr>
              <tr>
                <td>Apply Online</td>
                <td><a href="https://apply.upessc.org/register">Click Here</a></td>
              </tr>
              <tr>
                <td>Check Official Notification</td>
                <td><a href="https://upessc.up.gov.in/notices/advt_51.pdf">Download PDF</a></td>
              </tr>
              <tr>
                <td>UPESSC Official Website</td>
                <td><a href="https://upessc.up.gov.in">Visit Website</a></td>
              </tr>
            </table>
          </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = parse_sarkari_result_post_links(soup)
        self.assertEqual(links['official_apply_url'], "https://apply.upessc.org/register")
        self.assertEqual(links['official_pdf_url'], "https://upessc.up.gov.in/notices/advt_51.pdf")
        self.assertEqual(links['official_portal_url'], "https://upessc.up.gov.in")

    def test_sarkari_result_two_tier_urls_in_admin_api(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            'title': 'UPESSC Assistant Professor Online Form 2026',
            'organization': 'Uttar Pradesh Higher Education Commission',
            'category': 'Teaching',
            'status': 'pending_review',
            'is_published': False,
            'source_name': 'Sarkari Result',
            'source_type': 'url',
            'verification_url': 'https://sarkariresult.com.cm/upessc-assistant-professor-recruitment-2026/',
            'original_url': 'https://apply.upessc.org/register',
            'official_pdf_url': 'https://upessc.up.gov.in/notices/advt_51.pdf',
            'application_deadline': '2026-05-15',
            'min_age': 21,
            'max_age': 40,
            'min_qualification_level': 'Post Graduate',
        }
        res = self.client.post('/api/admin/jobs/', payload, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('job', res.data)
        job_id = res.data['job']['id']
        job = Job.objects.get(id=job_id)
        self.assertEqual(job.verification_url, 'https://sarkariresult.com.cm/upessc-assistant-professor-recruitment-2026/')
        self.assertEqual(job.original_url, 'https://apply.upessc.org/register')
        self.assertEqual(job.official_pdf_url, 'https://upessc.up.gov.in/notices/advt_51.pdf')
        self.assertEqual(res.data['job']['verification_url'], 'https://sarkariresult.com.cm/upessc-assistant-professor-recruitment-2026/')
        self.assertEqual(res.data['job']['official_pdf_url'], 'https://upessc.up.gov.in/notices/advt_51.pdf')
        self.assertEqual(job.status, 'pending_review')
        self.assertFalse(job.is_published)

    @patch('jobs.services.ai_extractor.requests.post')
    def test_cascade_fallback_gemini_api(self, mock_post):
        from jobs.services.ai_extractor import call_gemini_api
        import requests

        # Case 1: Primary model (gemini-flash-lite-latest) succeeds
        mock_response_primary = MagicMock()
        mock_response_primary.status_code = 200
        mock_response_primary.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': '{"title": "Fast Job", "min_age": 21}'}]}}]
        }
        mock_post.return_value = mock_response_primary

        res, err = call_gemini_api("Some job text", custom_api_key="dummy_key", retries_per_model=0)
        self.assertIsNotNone(res)
        self.assertEqual(res['title'], 'Fast Job')
        self.assertEqual(res['model_used'], 'gemini-flash-lite-latest')
        self.assertIsNone(err)

        # Case 2: Primary model times out, fallback model (gemini-3-flash-preview) succeeds
        mock_response_backup = MagicMock()
        mock_response_backup.status_code = 200
        mock_response_backup.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': '{"title": "Backup Job", "min_age": 18}'}]}}]
        }
        mock_post.side_effect = [requests.exceptions.Timeout("Read timeout"), mock_response_backup]

        res, err = call_gemini_api("Some job text", custom_api_key="dummy_key", retries_per_model=0)
        self.assertIsNotNone(res)
        self.assertEqual(res['title'], 'Backup Job')
        self.assertEqual(res['model_used'], 'gemini-3-flash-preview')
        self.assertIsNone(err)

        # Case 3: All models fail -> graceful fallback to heuristic engine
        mock_post.side_effect = [
            requests.exceptions.Timeout("Timeout 1"),
            requests.exceptions.Timeout("Timeout 2"),
            requests.exceptions.Timeout("Timeout 3")
        ]
        res, err = call_gemini_api("Some job text", custom_api_key="dummy_key", retries_per_model=0)
        self.assertIsNone(res)
        self.assertIn("Loaded via heuristic engine", err)

    @patch('jobs.services.job_watcher.extract_webpage_content')
    @patch('jobs.services.job_watcher.extract_and_structure_job')
    def test_job_watcher_auto_skips_expired_deadline(self, mock_structure, mock_webpage):
        from jobs.services.job_watcher import ingest_single_recruitment
        from jobs.models import SkippedRecruitment

        mock_webpage.return_value = {
            'html_content': '<html><body>Test Content</body></html>',
            'cleaned_text': 'Recruitment for 2025 Assistant Professor',
            'page_title': 'UPPSC Assistant Professor 2025',
            'detected_links': {},
            'tables': [],
            'key_values': {},
            'source_url': 'https://sarkariresult.com.cm/uppsc-ap-2025/'
        }

        mock_structure.return_value = {
            'job_fields': {
                'title': 'UPPSC Assistant Professor 2025',
                'organization': 'UPPSC',
                'advertisement_number': '01/2025',
                'application_deadline': '2025-03-15',  # Expired
                'application_start_date': '2025-02-01',
                'age_cutoff_date': '2025-02-01',
                'min_age': 21,
                'max_age': 40,
                'category': 'Teaching'
            },
            'rule_fields': {
                'min_qualification_level': 'Post Graduate',
                'allowed_status': 'completed_only'
            },
            'metadata': {'confidence_score': 0.95}
        }

        test_url = 'https://sarkariresult.com.cm/uppsc-ap-2025/'
        res = ingest_single_recruitment(test_url, detected_title='UPPSC AP 2025')

        self.assertFalse(res['success'])
        self.assertTrue(res['skipped'])
        self.assertIn('expired', res['reason'].lower())
        # Verify saved in SkippedRecruitment
        self.assertTrue(SkippedRecruitment.objects.filter(url='https://sarkariresult.com.cm/uppsc-ap-2025').exists())
        # Verify NOT created in Job table
        self.assertFalse(Job.objects.filter(title='UPPSC Assistant Professor 2025').exists())

    def test_is_notice_already_ingested_recognizes_skipped_recruitment(self):
        from jobs.services.job_watcher import is_notice_already_ingested
        from jobs.models import SkippedRecruitment

        SkippedRecruitment.objects.create(
            url='https://sarkariresult.com.cm/old-expired-job',
            title='Old Expired Clerk 2024',
            reason='Expired deadline'
        )

        self.assertTrue(is_notice_already_ingested('https://sarkariresult.com.cm/old-expired-job'))
        self.assertTrue(is_notice_already_ingested('https://sarkariresult.com.cm/old-expired-job/'))
        self.assertTrue(is_notice_already_ingested('https://other.com', 'Old Expired Clerk 2024'))
        self.assertFalse(is_notice_already_ingested('https://sarkariresult.com.cm/brand-new-recruitment-2026/'))

    def test_job_watcher_rejects_archaic_years(self):
        from jobs.services.job_watcher import is_recruitment_link
        # 2024 or older recruitment titles must be rejected early
        self.assertFalse(is_recruitment_link("UPPSC Staff Nurse Recruitment 2024", "https://sarkariresult.com.cm/uppsc-2024/"))
        self.assertFalse(is_recruitment_link("SSC MTS Recruitment 2023", "https://sarkariresult.com.cm/ssc-2023/"))
        # 2026 recruitment titles must be accepted
        self.assertTrue(is_recruitment_link("UPPSC Staff Nurse Recruitment 2026", "https://sarkariresult.com.cm/uppsc-2026/"))

    @patch('jobs.admin_views.extract_webpage_content')
    @patch('jobs.admin_views.extract_and_structure_job')
    def test_admin_extract_url_rejects_expired_jobs(self, mock_structure, mock_webpage):
        mock_webpage.return_value = {
            'html_content': '<html><body>Old Post</body></html>',
            'cleaned_text': 'Text',
            'page_title': 'Old Exam 2024',
            'detected_links': {},
            'tables': [],
            'key_values': {},
            'source_url': 'https://sarkariresult.com.cm/old-job-2024/'
        }

        mock_structure.return_value = {
            'job_fields': {
                'title': 'Old Job 2024',
                'organization': 'Board',
                'advertisement_number': '02/2024',
                'application_deadline': '2024-05-10',  # Expired
                'application_start_date': '2024-04-01',
                'min_age': 18,
                'max_age': 30,
                'category': 'General'
            },
            'rule_fields': {'min_qualification_level': 'Graduate', 'allowed_status': 'completed_only'},
            'metadata': {'confidence_score': 0.90}
        }

        self.client.force_authenticate(user=self.admin)
        res = self.client.post('/api/admin/jobs/extract-url/', {'url': 'https://sarkariresult.com.cm/old-job-2024/'}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('expired', res.data['error'].lower())

    @patch('jobs.services.job_watcher.extract_webpage_content')
    @patch('jobs.services.job_watcher.extract_and_structure_job')
    def test_job_watcher_detects_and_stages_upcoming_job(self, mock_structure, mock_webpage):
        from jobs.services.job_watcher import ingest_single_recruitment
        from django.utils import timezone
        from datetime import timedelta

        future_start = (timezone.now() + timedelta(days=20)).date()
        future_deadline = (timezone.now() + timedelta(days=50)).date()

        mock_webpage.return_value = {
            'html_content': '<html><body><h1>UP Police Constable 2026</h1><p>Available Soon</p></body></html>',
            'cleaned_text': 'UP Police Constable 2026 Available Soon Link Activate Soon',
            'page_title': 'UP Police Constable 2026',
            'detected_links': {},
            'tables': [],
            'key_values': {'Application Begin': 'Available Soon'},
            'source_url': 'https://sarkariresult.com.cm/up-police-upcoming-2026/'
        }

        mock_structure.return_value = {
            'job_fields': {
                'title': 'UP Police 60,000 Constable 2026',
                'organization': 'UPPRPB',
                'advertisement_number': 'CONSTABLE/2026',
                'application_start_date': str(future_start),
                'application_deadline': str(future_deadline),
                'min_age': 18,
                'max_age': 25,
                'category': 'Police & Security',
                'is_upcoming': True,
            },
            'rule_fields': {
                'min_qualification_level': '12th',
                'allowed_status': 'completed_only'
            },
            'metadata': {'confidence_score': 0.92, 'is_upcoming': True}
        }

        test_url = 'https://sarkariresult.com.cm/up-police-upcoming-2026/'
        res = ingest_single_recruitment(test_url, detected_title='UP Police Constable 2026')

        self.assertTrue(res['success'])
        job = Job.objects.get(id=res['job_id'])
        self.assertTrue(job.is_upcoming)
        self.assertTrue(job.is_currently_upcoming)

    @patch('jobs.services.job_watcher.extract_webpage_content')
    @patch('jobs.services.job_watcher.extract_and_structure_job')
    def test_job_watcher_transitions_upcoming_job_to_live_in_future(self, mock_structure, mock_webpage):
        from jobs.services.job_watcher import ingest_single_recruitment
        from django.utils import timezone
        from datetime import timedelta

        test_url = 'https://sarkariresult.com.cm/rrb-alp-2026/'
        today = timezone.now().date()
        future_deadline = today + timedelta(days=30)

        # 1. First: Staged in database as UPCOMING (no live apply link yet)
        upcoming_job = Job.objects.create(
            title="Railway RRB ALP Recruitment 2026",
            organization="Railway Recruitment Board (RRB)",
            advertisement_number="CEN 01/2026",
            category="Railways",
            verification_url=test_url,
            original_url=test_url,  # points to summary page initially
            application_start_date=today,
            application_deadline=future_deadline,
            age_cutoff_date=today,
            is_upcoming=True,
            status='approved',
            is_published=True
        )
        JobEligibilityRule.objects.create(job=upcoming_job)
        self.assertTrue(upcoming_job.is_currently_upcoming)

        # 2. Later: Form goes LIVE! Sarkari Result updates page with official apply link
        mock_webpage.return_value = {
            'html_content': '<table><tr><td>Apply Online</td><td><a href="https://rrbapply.gov.in/alp">Click Here</a></td></tr></table>',
            'cleaned_text': 'Apply Online Link Active: https://rrbapply.gov.in/alp',
            'page_title': 'Railway RRB ALP 2026 Apply Online',
            'detected_links': {'apply_url': 'https://rrbapply.gov.in/alp'},
            'tables': [],
            'key_values': {},
            'source_url': test_url
        }

        mock_structure.return_value = {
            'job_fields': {
                'title': "Railway RRB ALP Recruitment 2026",
                'organization': "Railway Recruitment Board (RRB)",
                'advertisement_number': "CEN 01/2026",
                'application_start_date': str(today),
                'application_deadline': str(future_deadline),
                'min_age': 18,
                'max_age': 30,
                'category': 'Railways',
                'is_upcoming': False,
            },
            'rule_fields': {
                'min_qualification_level': '10th',
                'allowed_status': 'completed_only'
            },
            'metadata': {'confidence_score': 0.98, 'is_upcoming': False}
        }

        # 3. Autonomous watcher runs again when form goes live
        res = ingest_single_recruitment(test_url, detected_title='Railway RRB ALP 2026')

        self.assertTrue(res['success'])
        self.assertTrue(res.get('updated_live'))
        self.assertEqual(res['job_id'], upcoming_job.id)

        # 4. Verify existing job transitioned to LIVE in-place!
        upcoming_job.refresh_from_db()
        self.assertFalse(upcoming_job.is_upcoming)
        self.assertFalse(upcoming_job.is_currently_upcoming)
        self.assertEqual(upcoming_job.original_url, 'https://rrbapply.gov.in/alp')







