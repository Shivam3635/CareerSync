from django.core.management.base import BaseCommand
from jobs.services.job_watcher import (
    discover_candidate_recruitment_links,
    run_autonomous_discovery_and_ingestion
)


class Command(BaseCommand):
    help = "Discovers and auto-ingests recruitment notifications into the Admin Review Queue."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help="Maximum number of new recruitment notices to ingest into pending_review (default: 5)"
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Discover links and print them without saving to database"
        )
        parser.add_argument(
            '--gemini-key',
            type=str,
            default="",
            help="Optional Google Gemini API key for AI structuring"
        )

    def handle(self, *args, **options):
        limit = options.get('limit', 5)
        dry_run = options.get('dry_run', False)
        gemini_key = options.get('gemini_key', '')

        self.stdout.write(self.style.NOTICE(f"=== Starting Autonomous Recruitment Watcher (Limit: {limit}) ==="))

        if dry_run:
            self.stdout.write("Running in DRY-RUN mode. Discovering candidate links...")
            candidates = discover_candidate_recruitment_links(limit=limit)
            self.stdout.write(f"Discovered {len(candidates)} candidate recruitment link(s):")
            for idx, c in enumerate(candidates, start=1):
                self.stdout.write(f"  {idx}. [{c['source']}] {c['title']} -> {c['url']}")
            return

        self.stdout.write("Running autonomous discovery & ingestion...")
        report = run_autonomous_discovery_and_ingestion(
            limit=limit,
            custom_gemini_api_key=gemini_key
        )

        self.stdout.write(self.style.SUCCESS(
            f"\nIngestion Complete!"
            f"\n  - Discovered Candidates: {report['discovered_candidates']}"
            f"\n  - Successfully Staged Drafts: {report['ingested_count']}"
            f"\n  - Skipped (Duplicates/Filtered): {report['skipped_count']}"
            f"\n  - Errors encountered: {report['error_count']}"
        ))

        if report['ingested_jobs']:
            self.stdout.write("\nStaged Drafts Waiting in Admin Review Queue:")
            for j in report['ingested_jobs']:
                conflicts_str = f" [Conflicts: {len(j.get('conflicts', []))}]" if j.get('conflicts') else ""
                self.stdout.write(self.style.WARNING(
                    f"  * Job #{j['job_id']}: '{j['title']}' ({j.get('organization', 'N/A')}) - "
                    f"Confidence: {int(j.get('confidence', 0.8) * 100)}%{conflicts_str}"
                ))
            self.stdout.write(self.style.NOTICE(
                "\nAll drafts are stored in 'pending_review' with 'is_published=False'.\n"
                "Review and publish them in your Admin Dashboard at /admin."
            ))
