from django.db import models
from students.models import StudentProfile
from jobs.models import Job


class Notification(models.Model):
    TYPE_CHOICES = (
        ('email', 'Email Alert'),
        ('system', 'In-App System Notification'),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='email')
    is_sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'job', 'notification_type'],
                name='unique_student_job_notification'
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} -> {self.student.user.email} for {self.job.title}"
