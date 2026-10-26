from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from jobs.management.commands.seed_data import Command as SeedCommand

User = get_user_model()


class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Seed initial demo data
        SeedCommand().handle()

    def test_student_demo_login(self):
        response = self.client.post('/api/auth/demo-login/', {'account_type': 'student'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'student@careersync.demo')
        self.assertEqual(response.data['role'], 'student')
        self.assertIsNotNone(response.data.get('student_profile'))

    def test_admin_demo_login(self):
        response = self.client.post('/api/auth/demo-login/', {'account_type': 'admin'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@careersync.demo')
        self.assertEqual(response.data['role'], 'admin')

    def test_student_registration(self):
        payload = {
            'email': 'newaspirant@example.com',
            'password': 'safePassword123',
            'full_name': 'Priya Patel',
            'date_of_birth': '2001-08-20',
            'gender': 'female',
            'category': 'GEN',
            'domicile_state': 'Gujarat',
            'highest_qualification': 'Graduate',
            'qualification_status': 'completed',
            'degree': 'B.Sc Chemistry'
        }
        response = self.client.post('/api/auth/register/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'newaspirant@example.com')
        self.assertEqual(response.data['student_profile']['category'], 'GEN')
        self.assertEqual(response.data['student_profile']['domicile_state'], 'Gujarat')

    def test_job_matches_authenticated(self):
        # Login demo student
        self.client.post('/api/auth/demo-login/', {'account_type': 'student'}, format='json')
        response = self.client.get('/api/jobs/matches/?status=eligible')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_profile'])
        self.assertTrue(response.data['summary']['eligible_count'] > 0)
        # All jobs in the list should be marked eligible
        for job in response.data['jobs']:
            self.assertEqual(job['eligibility']['status'], 'eligible')
