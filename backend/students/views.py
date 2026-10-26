from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import StudentProfile, StudentQualification
from accounts.serializers import StudentProfileSerializer, StudentQualificationSerializer


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.student_profile
            return Response(StudentProfileSerializer(profile).data)
        except StudentProfile.DoesNotExist:
            return Response(
                {"error": "Student profile not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        try:
            profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            profile = StudentProfile.objects.create(user=request.user)

        data = request.data
        if 'date_of_birth' in data:
            profile.date_of_birth = data['date_of_birth']
        if 'gender' in data:
            profile.gender = data['gender']
        if 'category' in data:
            profile.category = data['category']
        if 'domicile_state' in data:
            profile.domicile_state = data['domicile_state']
        if 'additional_certifications' in data:
            profile.additional_certifications = data['additional_certifications']
        profile.save()

        # Update qualifications if provided
        if 'qualifications' in data and isinstance(data['qualifications'], list):
            # Replace existing qualifications
            StudentQualification.objects.filter(student=profile).delete()
            for q in data['qualifications']:
                StudentQualification.objects.create(
                    student=profile,
                    level=q.get('level', 'Graduate'),
                    degree=q.get('degree', ''),
                    status=q.get('status', 'completed'),
                    passing_year=q.get('passing_year'),
                    percentage=q.get('percentage')
                )

        return Response(StudentProfileSerializer(profile).data)
