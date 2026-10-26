"""
Service for dispatching notifications to eligible students when a job is published.
"""

import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from students.models import StudentProfile
from jobs.models import Job
from notifications.models import Notification
from jobs.services.eligibility import evaluate_student_for_job

logger = logging.getLogger(__name__)


def dispatch_job_notifications(job: Job) -> int:
    """
    Evaluates all active student profiles against a newly published job
    and sends email alerts to eligible candidates. Prevents duplicate notifications.
    Returns count of sent notifications.
    """
    if not job.is_published or job.is_expired:
        logger.info(f"Skipping notifications for job {job.id} (published={job.is_published}, expired={job.is_expired})")
        return 0

    students = StudentProfile.objects.select_related('user').prefetch_related('qualifications').all()
    notifications_sent = 0

    for student in students:
        eval_result = evaluate_student_for_job(student, job)
        if eval_result['status'] == 'eligible':
            # Check or create notification record
            notification, created = Notification.objects.get_or_create(
                student=student,
                job=job,
                notification_type='email',
                defaults={
                    'is_sent': False
                }
            )

            if not notification.is_sent:
                subject = f"[CareerSync] New Eligible Opportunity: {job.title}"
                message = (
                    f"Hello {student.user.full_name or 'Aspirant'},\n\n"
                    f"Good news! A new government recruitment opportunity matches your profile:\n\n"
                    f"Role: {job.title}\n"
                    f"Organization: {job.organization}\n"
                    f"Application Deadline: {job.application_deadline.strftime('%d %B %Y')}\n\n"
                    f"Why you match:\n" + "\n".join(f"- {r}" for r in eval_result['reasons']) + "\n\n"
                    f"View official notification:\n{job.original_url}\n\n"
                    f"— CareerSync Notification Engine"
                )

                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[student.user.email],
                        fail_silently=False
                    )
                    notification.is_sent = True
                    notification.sent_at = timezone.now()
                    notification.save(update_fields=['is_sent', 'sent_at'])
                    notifications_sent += 1
                except Exception as e:
                    logger.error(f"Failed to send email to {student.user.email}: {e}")

    return notifications_sent
