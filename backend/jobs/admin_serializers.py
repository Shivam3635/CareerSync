from rest_framework import serializers
from .models import Job, JobEligibilityRule
from .serializers import JobSerializer, JobEligibilityRuleSerializer
from students.models import StudentProfile
from accounts.serializers import StudentProfileSerializer


class AdminJobWriteSerializer(serializers.ModelSerializer):
    # Rule fields
    min_qualification_level = serializers.ChoiceField(
        choices=JobEligibilityRule.LEVEL_CHOICES,
        default='Graduate'
    )
    allowed_status = serializers.ChoiceField(
        choices=JobEligibilityRule.STATUS_RULE_CHOICES,
        default='completed_only'
    )
    additional_certification_requirement = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')
    age_relaxations = serializers.JSONField(required=False, default=dict)
    domicile_requirement = serializers.CharField(max_length=100, default='All India')
    min_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    conditions_summary = serializers.CharField(required=False, allow_blank=True, default='')
    uploaded_pdf = serializers.CharField(required=False, allow_null=True, allow_blank=True)

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
            'ai_extraction_metadata',
            'ai_confidence_score',
            'review_notes',
            'min_qualification_level',
            'allowed_status',
            'additional_certification_requirement',
            'age_relaxations',
            'domicile_requirement',
            'min_percentage',
            'conditions_summary',
        ]

    def create(self, validated_data):
        rule_fields = {
            'min_qualification_level': validated_data.pop('min_qualification_level', 'Graduate'),
            'allowed_status': validated_data.pop('allowed_status', 'completed_only'),
            'additional_certification_requirement': validated_data.pop('additional_certification_requirement', ''),
            'age_relaxations': validated_data.pop('age_relaxations', {'OBC': 3, 'SC': 5, 'ST': 5, 'EWS': 0, 'GEN': 0}),
            'domicile_requirement': validated_data.pop('domicile_requirement', 'All India'),
            'min_percentage': validated_data.pop('min_percentage', None),
            'conditions_summary': validated_data.pop('conditions_summary', ''),
        }

        # If status was not explicitly passed, align with is_published
        if 'status' not in validated_data:
            validated_data['status'] = 'approved' if validated_data.get('is_published', True) else 'draft'

        job = Job.objects.create(**validated_data)
        JobEligibilityRule.objects.create(job=job, **rule_fields)
        return job

    def update(self, instance, validated_data):
        rule_data = {
            'min_qualification_level': validated_data.pop('min_qualification_level', None),
            'allowed_status': validated_data.pop('allowed_status', None),
            'additional_certification_requirement': validated_data.pop('additional_certification_requirement', None),
            'age_relaxations': validated_data.pop('age_relaxations', None),
            'domicile_requirement': validated_data.pop('domicile_requirement', None),
            'min_percentage': validated_data.pop('min_percentage', None),
            'conditions_summary': validated_data.pop('conditions_summary', None),
        }

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        rule = getattr(instance, 'rule', None)
        if not rule:
            rule = JobEligibilityRule.objects.create(job=instance)

        for attr, value in rule_data.items():
            if value is not None:
                setattr(rule, attr, value)
        rule.save()

        return instance


class AdminStudentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    full_name = serializers.CharField(source='user.full_name')
    qualifications = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'email',
            'full_name',
            'date_of_birth',
            'gender',
            'category',
            'domicile_state',
            'created_at',
            'qualifications',
        ]

    def get_qualifications(self, obj):
        return [
            {
                'level': q.level,
                'degree': q.degree,
                'status': q.status,
            }
            for q in obj.qualifications.all()
        ]
