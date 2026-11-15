from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobs'

    def ready(self):
        # Launch autonomous background watcher thread in server process
        import os
        import sys
        running_tests = 'test' in sys.argv
        running_migrate = any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'collectstatic', 'shell', 'createsuperuser'])
        
        argv_str = ' '.join(sys.argv).lower()
        is_dev_server = os.environ.get('RUN_MAIN') == 'true' or ('runserver' in argv_str and '--noreload' in argv_str)
        is_prod_server = (
            any(srv in argv_str for srv in ['gunicorn', 'uvicorn', 'waitress', 'daphne']) or 
            os.environ.get('RENDER') == 'true' or 
            bool(os.environ.get('PORT'))
        )
        is_server_process = (is_dev_server or is_prod_server)

        if is_server_process and not (running_tests or running_migrate):
            try:
                from jobs.services.job_watcher import start_background_watcher_thread
                start_background_watcher_thread(interval_seconds=1800)
            except Exception:
                pass
