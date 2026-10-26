from django.urls import path
from .admin_views import (
    AdminDashboardStatsView,
    AdminJobListCreateView,
    AdminJobDetailView,
    AdminJobTogglePublishView,
    AdminStudentListView,
    AdminExtractUrlView,
    AdminExtractPdfView,
    AdminJobApproveView,
    AdminJobRejectView,
    AdminAiStatusView,
)

urlpatterns = [
    path('stats/', AdminDashboardStatsView.as_view(), name='admin_stats'),
    path('ai-status/', AdminAiStatusView.as_view(), name='admin_ai_status'),
    path('jobs/', AdminJobListCreateView.as_view(), name='admin_jobs_list_create'),
    path('jobs/extract-url/', AdminExtractUrlView.as_view(), name='admin_extract_url'),
    path('jobs/extract-pdf/', AdminExtractPdfView.as_view(), name='admin_extract_pdf'),
    path('jobs/<int:pk>/', AdminJobDetailView.as_view(), name='admin_job_detail'),
    path('jobs/<int:pk>/approve/', AdminJobApproveView.as_view(), name='admin_job_approve'),
    path('jobs/<int:pk>/reject/', AdminJobRejectView.as_view(), name='admin_job_reject'),
    path('jobs/<int:pk>/toggle-publish/', AdminJobTogglePublishView.as_view(), name='admin_job_toggle_publish'),
    path('students/', AdminStudentListView.as_view(), name='admin_students'),
]
