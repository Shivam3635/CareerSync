from rest_framework import serializers
from .models import Job, JobEligibilityRule


class JobEligibilityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobEligibilityRule
        fields = [
            'id',
            'min_qualification_level',
            'allowed_status',
            'additional_certification_requirement',
            'age_relaxations',
            'domicile_requirement',
            'min_percentage',
            'conditions_summary'
        ]


class JobSerializer(serializers.ModelSerializer):
    rule = JobEligibilityRuleSerializer(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'organization',
            'advertisement_number',
            'recruitment_year',
            'category',
            'application_start_date',
            'application_deadline',
            'age_cutoff_date',
            'min_age',
            'max_age',
            'total_vacancies',
            'application_fee_details',
            'vacancy_details',
            'selection_process',
            'original_url',
            'source_name',
            'source_type',
            'uploaded_pdf',
            'description',
            'status',
            'is_published',
            'is_expired',
            'ai_extraction_metadata',
            'ai_confidence_score',
            'review_notes',
            'created_at',
            'updated_at',
            'rule'
        ]
