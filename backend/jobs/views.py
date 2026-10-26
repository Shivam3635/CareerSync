from django.db.models import Q, Count
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from .models import Job, JobEligibilityRule
from .serializers import JobSerializer
from .services.eligibility import evaluate_student_for_job
from students.models import StudentProfile


class JobListPublicView(APIView):
    """
    Public listings of all active published recruitment notifications.
    Supports search query (?q=), category (?category=), and qualification (?qualification=).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Job.objects.filter(is_published=True, status='approved').select_related('rule')
        
        q = request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(organization__icontains=q) |
                Q(category__icontains=q) |
                Q(description__icontains=q)
            )

        category = request.query_params.get('category', '').strip()
        if category and category != 'all':
            queryset = queryset.filter(category__iexact=category)

        qualification = request.query_params.get('qualification', '').strip()
        if qualification and qualification != 'all':
            queryset = queryset.filter(rule__min_qualification_level=qualification)

        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)


class JobMatchesView(APIView):
    """
    Personalized eligibility discovery endpoint.
    Matches all published jobs against the currently logged-in student's profile.
    Supports:
      - ?status=eligible | review_required | not_eligible | all (defaults to 'eligible')
      - ?q=<search term>
      - ?category=<recruitment category>
      - ?qualification=<minimum qualification>
    """
    permission_classes = [AllowAny]

    def get(self, request):
        student_profile = None
        if request.user.is_authenticated:
            student_profile = getattr(request.user, 'student_profile', None)

        queryset = Job.objects.filter(is_published=True, status='approved').select_related('rule')

        # Text search
        q = request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(organization__icontains=q) |
                Q(category__icontains=q) |
                Q(description__icontains=q)
            )

        # Category filter
        category = request.query_params.get('category', '').strip()
        if category and category != 'all':
            queryset = queryset.filter(category__iexact=category)

        # Qualification filter
        qualification = request.query_params.get('qualification', '').strip()
        if qualification and qualification != 'all':
            queryset = queryset.filter(rule__min_qualification_level=qualification)

        # Status filter (default is 'eligible' as required by product spec)
        status_filter = request.query_params.get('status', 'eligible').lower()

        # Evaluate eligibility for each job
        matched_results = []
        eligible_count = 0
        review_count = 0
        not_eligible_count = 0
        total_active_jobs = 0

        for job in queryset:
            total_active_jobs += 1
            eval_result = evaluate_student_for_job(student_profile, job)
            job_status = eval_result['status']

            if job_status == 'eligible':
                eligible_count += 1
            elif job_status == 'review_required':
                review_count += 1
            elif job_status == 'not_eligible':
                not_eligible_count += 1

            job_data = JobSerializer(job).data
            item = {
                **job_data,
                'eligibility': eval_result
            }

            # Filter logic
            if status_filter == 'all':
                matched_results.append(item)
            elif status_filter == job_status:
                matched_results.append(item)

        return Response({
            'summary': {
                'total_jobs': total_active_jobs,
                'eligible_count': eligible_count,
                'review_required_count': review_count,
                'not_eligible_count': not_eligible_count,
                'selected_filter': status_filter,
            },
            'has_profile': student_profile is not None,
            'student_category': student_profile.category if student_profile else None,
            'student_domicile': student_profile.domicile_state if student_profile else None,
            'jobs': matched_results
        })


class JobCategoriesView(APIView):
    """
    Returns list of distinct job categories with count of published opportunities.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        categories = (
            Job.objects.filter(is_published=True, status='approved')
            .values('category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return Response(list(categories))
