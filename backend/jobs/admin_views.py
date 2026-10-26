import os
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count
from django.utils import timezone
from .models import Job, JobEligibilityRule
from .serializers import JobSerializer
from .admin_serializers import AdminJobWriteSerializer, AdminStudentSerializer
from .permissions import IsAdminRole
from .services.notification_service import dispatch_job_notifications
from .services.url_extractor import extract_webpage_content, SSRFSecurityError, InvalidContentError
from .services.pdf_extractor import extract_pdf_content, PDFValidationError
from .services.ai_extractor import extract_and_structure_job
from students.models import StudentProfile
from notifications.models import Notification


def check_for_duplicate_job(title: str, org: str, advt_no: str = "", source_url: str = "") -> Job | None:
    """Detects potential duplicate recruitment postings in database."""
    query = Q()
    if advt_no and advt_no.strip():
        query |= (Q(advertisement_number__iexact=advt_no.strip()) & Q(organization__iexact=org.strip()))
    if source_url and source_url.strip():
        query |= Q(original_url=source_url.strip())
    if title and org:
        query |= (Q(title__iexact=title.strip()) & Q(organization__iexact=org.strip()))

    if query:
        return Job.objects.filter(query).first()
    return None


class AdminDashboardStatsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        today = timezone.now().date()
        total_jobs = Job.objects.count()
        published_jobs = Job.objects.filter(is_published=True).count()
        pending_review_jobs = Job.objects.filter(status='pending_review').count()
        draft_jobs = Job.objects.filter(status='draft').count()
        rejected_jobs = Job.objects.filter(status='rejected').count()
        active_jobs = Job.objects.filter(is_published=True, status='approved', application_deadline__gte=today).count()
        expired_jobs = Job.objects.filter(application_deadline__lt=today).count()
        
        total_students = StudentProfile.objects.count()
        total_notifications_sent = Notification.objects.filter(is_sent=True).count()

        category_breakdown = list(
            Job.objects.values('category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return Response({
            'total_jobs': total_jobs,
            'published_jobs': published_jobs,
            'pending_review_jobs': pending_review_jobs,
            'draft_jobs': draft_jobs,
            'rejected_jobs': rejected_jobs,
            'active_jobs': active_jobs,
            'expired_jobs': expired_jobs,
            'total_students': total_students,
            'total_notifications_sent': total_notifications_sent,
            'category_breakdown': category_breakdown,
        })


class AdminJobListCreateView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        queryset = Job.objects.all().select_related('rule')

        q = request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(organization__icontains=q) |
                Q(category__icontains=q) |
                Q(advertisement_number__icontains=q)
            )

        status_param = request.query_params.get('status', 'all').lower()
        today = timezone.now().date()
        if status_param == 'published':
            queryset = queryset.filter(is_published=True, status='approved')
        elif status_param == 'pending_review':
            queryset = queryset.filter(status='pending_review')
        elif status_param == 'draft':
            queryset = queryset.filter(status='draft')
        elif status_param == 'rejected':
            queryset = queryset.filter(status='rejected')
        elif status_param == 'expired':
            queryset = queryset.filter(application_deadline__lt=today)

        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdminJobWriteSerializer(data=request.data)
        if serializer.is_valid():
            job = serializer.save()
            notified_count = 0
            if job.is_published and job.status == 'approved':
                notified_count = dispatch_job_notifications(job)
            
            output_serializer = JobSerializer(job)
            return Response({
                'job': output_serializer.data,
                'notifications_sent': notified_count,
                'message': f"Job recruitment saved successfully with status '{job.get_status_display()}'."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminExtractUrlView(APIView):
    """
    Extracts recruitment job information from a provided URL (e.g. Sarkari Result).
    Enforces SSRF prevention, content validation, AI extraction, and creates a Pending Review draft.
    """
    permission_classes = [IsAdminRole]

    def post(self, request):
        url = request.data.get('url', '').strip()
        custom_key = request.data.get('gemini_api_key', '').strip()
        if not url:
            return Response({'error': 'Please provide a valid job notification URL.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            extracted_webpage = extract_webpage_content(url)
        except SSRFSecurityError as e:
            return Response({'error': f"Security validation failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidContentError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Failed to fetch or parse webpage: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Run AI Structuring & Normalization
        structured_data = extract_and_structure_job(
            source_text=f"PAGE TITLE: {extracted_webpage['page_title']}\n\nTABLES:\n{chr(10).join(extracted_webpage['tables'])}\n\nCONTENT:\n{extracted_webpage['cleaned_text']}",
            source_url=extracted_webpage['source_url'],
            detected_links=extracted_webpage['detected_links'],
            source_type='url',
            page_title=extracted_webpage['page_title'],
            key_values=extracted_webpage.get('key_values'),
            custom_gemini_api_key=custom_key
        )

        job_fields = structured_data['job_fields']
        rule_fields = structured_data['rule_fields']
        metadata = structured_data['metadata']

        # Duplicate check
        dup = check_for_duplicate_job(
            job_fields['title'],
            job_fields['organization'],
            job_fields['advertisement_number'],
            extracted_webpage['source_url']
        )
        if dup:
            metadata['warnings'].append(f"Potential duplicate notice: An existing job '{dup.title}' (ID #{dup.id}) has matching details.")

        # Save as pending_review draft
        job_fields['ai_extraction_metadata'] = metadata
        job_fields['ai_confidence_score'] = metadata['confidence_score']
        job_fields['status'] = 'pending_review'
        job_fields['is_published'] = False  # NEVER auto-publish AI drafts!

        # Combine for AdminJobWriteSerializer
        create_payload = {
            **job_fields,
            **rule_fields
        }

        serializer = AdminJobWriteSerializer(data=create_payload)
        if serializer.is_valid():
            draft_job = serializer.save()
            return Response({
                'job': JobSerializer(draft_job).data,
                'metadata': metadata,
                'message': "Draft created successfully from URL. Please review all fields before publishing."
            }, status=status.HTTP_201_CREATED)
        return Response({'error': 'Schema validation error on extracted draft', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AdminExtractPdfView(APIView):
    """
    Extracts recruitment job information from an uploaded government notification PDF.
    Validates file, extracts digital text / OCR fallback, runs AI structuring, and creates a Pending Review draft.
    """
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        pdf_file = request.FILES.get('pdf_file')
        custom_key = request.data.get('gemini_api_key', '').strip()
        if not pdf_file:
            return Response({'error': 'Please select a valid PDF file to upload.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pdf_result = extract_pdf_content(pdf_file)
        except PDFValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Failed to process PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Run AI Structuring & Normalization
        structured_data = extract_and_structure_job(
            source_text=pdf_result['extracted_text'],
            source_url="",
            detected_links={},
            source_type='pdf',
            uploaded_pdf_path=pdf_result['saved_relative_path'],
            custom_gemini_api_key=custom_key
        )

        job_fields = structured_data['job_fields']
        rule_fields = structured_data['rule_fields']
        metadata = structured_data['metadata']

        if pdf_result.get('ocr_warning'):
            metadata['warnings'].append(pdf_result['ocr_warning'])

        metadata['original_filename'] = pdf_result['original_filename']
        metadata['page_count'] = pdf_result['page_count']
        metadata['is_scanned'] = pdf_result['is_scanned']

        # Duplicate check
        dup = check_for_duplicate_job(
            job_fields['title'],
            job_fields['organization'],
            job_fields['advertisement_number'],
            ""
        )
        if dup:
            metadata['warnings'].append(f"Potential duplicate notice: An existing job '{dup.title}' (ID #{dup.id}) has matching details.")

        # Save as pending_review draft
        job_fields['ai_extraction_metadata'] = metadata
        job_fields['ai_confidence_score'] = metadata['confidence_score']
        job_fields['status'] = 'pending_review'
        job_fields['is_published'] = False  # NEVER auto-publish AI drafts!

        create_payload = {
            **job_fields,
            **rule_fields
        }

        serializer = AdminJobWriteSerializer(data=create_payload)
        if serializer.is_valid():
            draft_job = serializer.save()
            return Response({
                'job': JobSerializer(draft_job).data,
                'metadata': metadata,
                'message': "Draft created successfully from PDF. Please review all fields before publishing."
            }, status=status.HTTP_201_CREATED)
        return Response({'error': 'Schema validation error on extracted draft', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AdminAiStatusView(APIView):
    """Returns status of AI configuration and tests API key."""
    permission_classes = [IsAdminRole]

    def get(self, request):
        configured_key = os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', '')
        return Response({
            'gemini_configured': bool(configured_key.strip()),
            'default_model': 'gemini-3-flash-preview',
            'supported_models': ['gemini-3-flash-preview', 'gemini-3.5-flash', 'gemini-flash-latest'],
            'fallback_engine': 'High-Fidelity Heuristic Parser (Offline)'
        })

    def post(self, request):
        test_key = request.data.get('api_key', '').strip()
        if not test_key:
            return Response({'error': 'Please provide an API key to test.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ping Gemini with a tiny prompt
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={test_key}"
        try:
            resp = requests.post(
                url,
                json={"contents": [{"parts": [{"text": "Hello, respond with OK."}]}]},
                timeout=10
            )
            if resp.status_code == 200:
                return Response({
                    'valid': True,
                    'model': 'gemini-3.5-flash',
                    'message': 'Google Gemini API connected and verified successfully!'
                })
            else:
                return Response({
                    'valid': False,
                    'error': f"Gemini API rejected key with HTTP {resp.status_code}: {resp.text[:150]}"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'valid': False,
                'error': f"Connection to Gemini API failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)



class AdminJobApproveView(APIView):
    """
    Explicit admin approval endpoint.
    Transitions a pending_review or draft job to 'approved', sets is_published=True,
    and dispatches candidate notification alerts.
    """
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            job = Job.objects.select_related('rule').get(pk=pk)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validation check before approval
        if not job.title or not job.organization:
            return Response({'error': 'Cannot approve job without Title and Organization.'}, status=status.HTTP_400_BAD_REQUEST)
        if not job.application_deadline:
            return Response({'error': 'Cannot approve job without an Application Deadline.'}, status=status.HTTP_400_BAD_REQUEST)
        if job.min_age > job.max_age:
            return Response({'error': f'Cannot approve job with invalid age bounds ({job.min_age} > {job.max_age}).'}, status=status.HTTP_400_BAD_REQUEST)

        # Save optional review notes
        notes = request.data.get('review_notes')
        if notes:
            job.review_notes = notes

        job.status = 'approved'
        job.is_published = True
        job.save()

        # Dispatch candidate notifications
        notified_count = dispatch_job_notifications(job)

        return Response({
            'job': JobSerializer(job).data,
            'notifications_sent': notified_count,
            'message': f"Job '{job.title}' approved and published. Dispatched {notified_count} alert(s) to eligible aspirants."
        })


class AdminJobRejectView(APIView):
    """
    Rejects a job draft with optional rejection reason.
    """
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            job = Job.objects.select_related('rule').get(pk=pk)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

        notes = request.data.get('review_notes', '')
        if notes:
            job.review_notes = notes

        job.status = 'rejected'
        job.is_published = False
        job.save()

        return Response({
            'job': JobSerializer(job).data,
            'message': f"Job '{job.title}' marked as rejected."
        })


class AdminJobDetailView(APIView):
    permission_classes = [IsAdminRole]

    def get_object(self, pk):
        try:
            return Job.objects.select_related('rule').get(pk=pk)
        except Job.DoesNotExist:
            return None

    def get(self, request, pk):
        job = self.get_object(pk)
        if not job:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(JobSerializer(job).data)

    def put(self, request, pk):
        job = self.get_object(pk)
        if not job:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

        was_published = job.is_published and job.status == 'approved'
        serializer = AdminJobWriteSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            updated_job = serializer.save()
            
            notified_count = 0
            if not was_published and updated_job.is_published and updated_job.status == 'approved':
                notified_count = dispatch_job_notifications(updated_job)

            return Response({
                'job': JobSerializer(updated_job).data,
                'notifications_sent': notified_count,
                'message': 'Job notification updated successfully.'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        job = self.get_object(pk)
        if not job:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)
        job.delete()
        return Response({'message': 'Job recruitment notification deleted.'})


class AdminJobTogglePublishView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            job = Job.objects.select_related('rule').get(pk=pk)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

        job.is_published = not job.is_published
        if job.is_published and job.status != 'approved':
            job.status = 'approved'
        elif not job.is_published and job.status == 'approved':
            job.status = 'draft'

        job.save()

        notified_count = 0
        if job.is_published and job.status == 'approved':
            notified_count = dispatch_job_notifications(job)

        return Response({
            'is_published': job.is_published,
            'status': job.status,
            'notifications_sent': notified_count,
            'message': f"Job {'published' if job.is_published else 'unpublished'}. Dispatched {notified_count} alert(s)."
        })


class AdminStudentListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        students = StudentProfile.objects.select_related('user').prefetch_related('qualifications').order_by('-created_at')
        serializer = AdminStudentSerializer(students, many=True)
        return Response(serializer.data)
