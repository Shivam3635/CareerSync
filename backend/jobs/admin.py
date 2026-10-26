from django.contrib import admin
from .models import Job, JobEligibilityRule
from .services.notification_service import dispatch_job_notifications


class JobEligibilityRuleInline(admin.StackedInline):
    model = JobEligibilityRule
    can_delete = False
    verbose_name_plural = 'Eligibility Criteria & Rules'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'organization',
        'category',
        'application_deadline',
        'age_cutoff_date',
        'min_age',
        'max_age',
        'is_published',
        'is_expired'
    )
    list_filter = ('is_published', 'category', 'application_deadline')
    search_fields = ('title', 'organization', 'description')
    inlines = [JobEligibilityRuleInline]
    actions = ['publish_and_notify', 'unpublish_jobs']

    def publish_and_notify(self, request, queryset):
        for job in queryset:
            job.is_published = True
            job.save()
            sent = dispatch_job_notifications(job)
            self.message_user(request, f"Published '{job.title}' and dispatched {sent} notifications.")
    publish_and_notify.short_description = "Publish selected jobs and notify eligible students"

    def unpublish_jobs(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"Unpublished {count} jobs.")
    unpublish_jobs.short_description = "Unpublish selected jobs"


@admin.register(JobEligibilityRule)
class JobEligibilityRuleAdmin(admin.ModelAdmin):
    list_display = ('job', 'min_qualification_level', 'allowed_status', 'domicile_requirement')
    list_filter = ('min_qualification_level', 'allowed_status', 'domicile_requirement')
