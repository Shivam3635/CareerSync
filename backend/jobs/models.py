from django.db import models
from django.utils import timezone


class Job(models.Model):
    CATEGORY_CHOICES = (
        ('Civil Services', 'Civil Services & Administration'),
        ('Banking', 'Banking & Finance'),
        ('Railways', 'Railways'),
        ('Defense', 'Defense & Paramilitary'),
        ('Engineering & Tech', 'Engineering & Technology'),
        ('Teaching', 'Teaching & Academia'),
        ('Police & Security', 'Police & State Security'),
        ('General', 'General Recruitment'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved / Published'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    )

    SOURCE_TYPE_CHOICES = (
        ('manual', 'Manual Entry'),
        ('url', 'URL Extraction'),
        ('pdf', 'PDF Extraction'),
    )

    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    advertisement_number = models.CharField(max_length=150, blank=True, help_text="Official Advt / Notification No.")
    recruitment_year = models.PositiveIntegerField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='General')
    
    application_start_date = models.DateField(null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    age_cutoff_date = models.DateField(null=True, blank=True, help_text="Official recruitment cutoff date for calculating candidate age")
    
    min_age = models.PositiveIntegerField(default=18)
    max_age = models.PositiveIntegerField(default=32)

    total_vacancies = models.PositiveIntegerField(null=True, blank=True)
    application_fee_details = models.JSONField(default=dict, blank=True, help_text="Category-wise fee e.g. {'General': 500, 'SC/ST': 0}")
    vacancy_details = models.JSONField(default=list, blank=True, help_text="Post-wise or category-wise vacancy breakdown")
    selection_process = models.TextField(blank=True, help_text="Selection stages: Prelims, Mains, Interview, etc.")
    
    original_url = models.URLField(max_length=500, blank=True, help_text="Official recruitment advertisement or notification URL")
    source_name = models.CharField(max_length=150, default="Official Portal")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES, default='manual')
    uploaded_pdf = models.FileField(upload_to='notifications_pdfs/', null=True, blank=True)

    description = models.TextField(blank=True)
    
    # Workflow status
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='approved')
    is_published = models.BooleanField(default=True)
    
    # AI Extraction and Review Metadata
    ai_extraction_metadata = models.JSONField(default=dict, blank=True, help_text="Metadata: warnings, conflicts, extracted links, confidence")
    ai_confidence_score = models.FloatField(null=True, blank=True)
    review_notes = models.TextField(blank=True, help_text="Admin review notes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.organization} [{self.get_status_display()}]"

    @property
    def is_expired(self):
        if not self.application_deadline:
            return False
        return timezone.now().date() > self.application_deadline


def default_age_relaxations():
    return {
        'OBC': 3,
        'SC': 5,
        'ST': 5,
        'EWS': 0,
        'GEN': 0
    }


class JobEligibilityRule(models.Model):
    LEVEL_CHOICES = (
        ('10th', '10th Standard / Matriculation'),
        ('12th', '12th Standard / Intermediate'),
        ('Graduate', 'Bachelor / Graduate Degree'),
        ('Post Graduate', 'Master / Post Graduate Degree'),
        ('Doctorate', 'Doctorate / Ph.D.'),
    )

    STATUS_RULE_CHOICES = (
        ('completed_only', 'Completed Degree Only'),
        ('appearing_allowed', 'Final Year / Appearing Candidates Allowed'),
    )

    job = models.OneToOneField(
        Job,
        on_delete=models.CASCADE,
        related_name='rule'
    )
    min_qualification_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Graduate')
    allowed_status = models.CharField(max_length=20, choices=STATUS_RULE_CHOICES, default='completed_only')
    
    # Additional certification/diploma requirement (e.g. Polytechnic Diploma, ITI, CCC, B.Ed, Typing/Steno)
    additional_certification_requirement = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="e.g. Polytechnic Diploma in Engineering, ITI Trade Certificate, CCC Computer Course, B.Ed, Typing"
    )

    # Category based age relaxation in years: e.g. {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0}
    age_relaxations = models.JSONField(default=default_age_relaxations, blank=True)
    
    # State domicile restriction: 'All India' or specific state (e.g. 'Uttar Pradesh')
    domicile_requirement = models.CharField(max_length=100, default='All India')
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    conditions_summary = models.TextField(blank=True, help_text="Human readable summary of eligibility conditions")

    def __str__(self):
        return f"Rules for {self.job.title} (Min: {self.min_qualification_level}, Status: {self.allowed_status})"
