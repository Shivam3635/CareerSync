from django.apps import AppConfig
from django.db.models.signals import post_migrate

def ensure_jobs_populated(sender, **kwargs):
    from jobs.models import Job
    try:
        if Job.objects.filter(is_published=True).count() == 0:
            from django.core.management import call_command
            call_command('populate_latest_jobs')
    except Exception:
        pass


class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'

    def ready(self):
        post_migrate.connect(ensure_jobs_populated, sender=self)
