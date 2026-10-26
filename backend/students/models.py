from django.db import models
from django.conf import settings


class StudentProfile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    CATEGORY_CHOICES = (
        ('GEN', 'General (UR)'),
        ('OBC', 'Other Backward Classes (OBC)'),
        ('SC', 'Scheduled Castes (SC)'),
        ('ST', 'Scheduled Tribes (ST)'),
        ('EWS', 'Economically Weaker Section (EWS)'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='GEN')
    domicile_state = models.CharField(max_length=100, default='All India')
    
    # Additional certifications / specialized diplomas
    additional_certifications = models.TextField(
        blank=True,
        default='',
        help_text="Specialized diplomas / certifications e.g. Polytechnic Diploma in Engineering, CCC Computer Course, ITI, B.Ed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.category} ({self.domicile_state})"

    @property
    def highest_qualification(self):
        """Returns the highest qualification recorded for this student."""
        hierarchy = {
            'Doctorate': 5,
            'Post Graduate': 4,
            'Graduate': 3,
            '12th': 2,
            '10th': 1,
        }
        quals = list(self.qualifications.all())
        if not quals:
            return None
        return max(quals, key=lambda q: hierarchy.get(q.level, 0))


class StudentQualification(models.Model):
    LEVEL_CHOICES = (
        ('10th', '10th Standard / Matriculation'),
        ('12th', '12th Standard / Intermediate'),
        ('Graduate', 'Bachelor / Graduate Degree'),
        ('Post Graduate', 'Master / Post Graduate Degree'),
        ('Doctorate', 'Doctorate / Ph.D.'),
    )

    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('appearing', 'Final Year / Appearing'),
    )

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='qualifications'
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    degree = models.CharField(max_length=200, blank=True, help_text="e.g. B.Tech CS, B.Sc Physics, BA History")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='completed')
    passing_year = models.PositiveIntegerField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.email} - {self.level} ({self.status})"
