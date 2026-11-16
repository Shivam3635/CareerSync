"""
Autonomous Job Watcher & Ingestion Service for CareerSync.
Primary Single Source of Truth (SSOT): https://sarkariresult.com.cm/

Discovers new recruitment notifications from sarkariresult.com.cm,
extracts both the Sarkari Result Verification URL (for Admin Audit)
and the Official Government Application Portal & PDF links (for Aspirants),
and stages them directly into the Admin Review Queue as 'pending_review' drafts.
"""

import logging
import re
import time
import threading
import urllib.parse
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from django.db.models import Q
from django.utils import timezone
from jobs.models import Job, SkippedRecruitment
from jobs.admin_serializers import AdminJobWriteSerializer
from jobs.services.url_extractor import extract_webpage_content, SSRFSecurityError, InvalidContentError
from jobs.services.ai_extractor import extract_and_structure_job

logger = logging.getLogger(__name__)

# Primary Single Source of Truth (SSOT)
SARKARI_RESULT_HOME = 'https://sarkariresult.com.cm/'
SARKARI_RESULT_LATEST_JOBS = 'https://sarkariresult.com.cm/latest-jobs/'

# Disqualifying keywords for non-recruitment links
DISQUALIFYING_KEYWORDS = [
    'admit card', 'hall ticket', 'call letter', 'answer key', 'exam date',
    'result', 'marksheet', 'cutoff marks', 'syllabus', 'counselling',
    'admission', 'scholarship', 'answer-key', 'exam-date', 'correction',
    'rejected list', 'allotment', 'marks', 'score card'
]

# Qualifying keywords that indicate an actual recruitment opening
RECRUITMENT_KEYWORDS = [
    'recruitment', 'apply online', 'online form', 'bharti', 'vacancy',
    'vacancies', 'posts', 'officer', 'constable', 'engineer', 'clerk',
    'assistant', 'cgl', 'chsl', 'ntpc', 'po recruitment', 'specialist',
    'inspector', 'sub inspector', 'professor', 'teacher', 'notification',
    'tgt', 'je online', 'ro / aro', 'apprentice'
]


def is_recruitment_link(title: str, url: str) -> bool:
    """
    Returns True if the link/title describes an active job recruitment,
    and False if it is an admit card, answer key, result, or irrelevant navigation page.
    """
    clean_url = url.strip().rstrip('/')
    clean_title = title.strip()

    # Skip generic navigation and category hubs
    for hub in [
        '/latest-jobs', '/admit-card', '/result', '/admission',
        '/syllabus', '/answer-key', '/contact', '/privacy-policy',
        '/disclaimer', '/about-us', '/latest-posts'
    ]:
        if clean_url.endswith(hub):
            return False

    # Skip very short or generic titles
    if len(clean_title) < 6:
        return False

    parsed = urllib.parse.urlparse(clean_url)
    path_lower = parsed.path.lower().rstrip('/')
    title_lower = clean_title.lower()

    # Path-based rejections for non-recruitment sections
    for bad_path in ['/admit-card', '/result', '/syllabus', '/answer-key', '/admission']:
        if path_lower.startswith(bad_path) or f"{bad_path}/" in path_lower:
            return False

    # Rejection checks (match 'result' only as standalone word in title, not in domain/slug)
    for kw in DISQUALIFYING_KEYWORDS:
        if kw == 'result':
            if re.search(r'\bresults?\b', title_lower):
                return False
        elif kw in title_lower or kw in path_lower:
            return False

    # Acceptance checks: title or URL path must mention a recruitment signal
    combined_signal = f"{title_lower} {path_lower}"
    for kw in RECRUITMENT_KEYWORDS:
        if kw in combined_signal:
            # Reject archaic recruitment notices with explicit old years (e.g. 2024 or earlier)
            if re.search(r'\b(19\d\d|20[0-1]\d|202[0-4])\b', clean_title):
                return False
            return True

    return False


def is_notice_already_ingested(url: str, title: str = "") -> bool:
    """
    Checks if a recruitment URL (verification or original) or title has already been ingested
    into active jobs or previously evaluated and skipped.
    Checks both stripped and trailing-slash normalized variants.

    SMART RE-CHECK CACHE:
    - If a notice was skipped because it's not live yet (upcoming / link activate soon),
      it has a `recheck_after` date.
    - If today >= recheck_after: Returns False to allow re-checking if the form is now LIVE!
    - If today < recheck_after: Returns True (auto-skips without HTTP or Gemini calls, saving tokens).
    - If recheck_after is None (e.g. expired): Returns True (permanently skipped).
    """
    clean_url = url.strip().rstrip('/')
    today = timezone.now().date()
    if clean_url:
        slash_url = clean_url + '/'

        # Check SkippedRecruitment
        skipped_entry = SkippedRecruitment.objects.filter(
            Q(url=clean_url) | Q(url=slash_url)
        ).first()
        if skipped_entry:
            if skipped_entry.recheck_after and today >= skipped_entry.recheck_after:
                # Re-check date reached! Allow re-check to see if form has opened
                return False
            # Still in skip period or permanently expired
            return True

        # Check existing live jobs in database
        if Job.objects.filter(
            Q(original_url=clean_url) | Q(original_url=slash_url) |
            Q(verification_url=clean_url) | Q(verification_url=slash_url)
        ).exists():
            return True

    if title and len(title.strip()) > 8:
        clean_title = title.strip()
        skipped_title = SkippedRecruitment.objects.filter(title__iexact=clean_title).first()
        if skipped_title:
            if skipped_title.recheck_after and today >= skipped_title.recheck_after:
                return False
            return True
        if Job.objects.filter(title__iexact=clean_title).exists():
            return True

    return False


def discover_candidate_recruitment_links(limit: int = 10) -> List[Dict[str, str]]:
    """
    Scrapes https://sarkariresult.com.cm/latest-jobs/ to discover fresh, uningested recruitment links.
    Returns list of candidate dicts: [{'title': str, 'url': str, 'source': str}].
    """
    discovered: List[Dict[str, str]] = []
    seen_urls = set()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    try:
        resp = requests.get(SARKARI_RESULT_LATEST_JOBS, headers=headers, timeout=15)
        if resp.status_code != 200:
            logger.warning(f"Watcher: Sarkari Result latest-jobs returned HTTP {resp.status_code}")
            return discovered

        soup = BeautifulSoup(resp.content, 'html.parser')
        # Target post article links
        anchor_tags = soup.select('article a, h2 a, h3 a, div.entry-content a, li a')

        for a in anchor_tags:
            if len(discovered) >= limit:
                break

            href = a.get('href', '').strip()
            link_text = a.get_text(strip=True)

            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue

            full_url = urllib.parse.urljoin(SARKARI_RESULT_HOME, href)

            if not full_url.startswith(('http://', 'https://')):
                continue

            # Must be a sarkariresult.com.cm job page
            if 'sarkariresult.com.cm' not in full_url:
                continue

            # Deduplicate within current run
            clean_url = full_url.rstrip('/')
            if clean_url in seen_urls:
                continue
            seen_urls.add(clean_url)

            # Check recruitment validity
            if not is_recruitment_link(link_text, clean_url):
                continue

            # Check if already ingested into database
            if is_notice_already_ingested(clean_url, link_text):
                continue

            discovered.append({
                'title': link_text,
                'url': clean_url + '/',
                'source': 'Sarkari Result Official (sarkariresult.com.cm)'
            })

    except Exception as e:
        logger.error(f"Watcher: Error discovering links from Sarkari Result: {e}")

    return discovered


def parse_sarkari_result_post_links(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extracts the official external links from Sarkari Result's 'Useful Important Links' table:
    - official_apply_url (e.g. upsc.gov.in, apply.upessc.org)
    - official_pdf_url (official notification PDF)
    - official_portal_url (official commission homepage)
    """
    links = {
        'official_apply_url': '',
        'official_pdf_url': '',
        'official_portal_url': '',
    }

    for tr in soup.find_all('tr'):
        row_text = tr.get_text(' ', strip=True).lower()
        a_tag = tr.find('a', href=True)
        if not a_tag:
            continue

        href = a_tag['href'].strip()
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue

        # Skip internal sarkariresult links or social channels
        if 'sarkariresult.com' in href or 'whatsapp.com' in href or 't.me' in href:
            continue

        # Match Official Apply Link (must be active, not a future activation placeholder)
        if not links['official_apply_url'] and any(k in row_text for k in ['apply online', 'online apply']):
            link_anchor_text = a_tag.get_text(' ', strip=True).lower()
            if any(term in link_anchor_text or term in row_text for term in ['activate soon', 'link activate', 'available soon', 'coming soon', 'not active']):
                continue
            links['official_apply_url'] = href

        # Match Official Notification PDF
        elif not links['official_pdf_url'] and (
            any(k in row_text for k in ['official notification', 'download notification', 'check notification'])
            or href.lower().endswith('.pdf')
        ):
            links['official_pdf_url'] = href

        # Match Official Commission Portal
        elif not links['official_portal_url'] and any(k in row_text for k in ['official website', 'commission website']):
            links['official_portal_url'] = href

    return links


def ingest_single_recruitment(
    url: str,
    detected_title: str = "",
    custom_gemini_api_key: str = ""
) -> Dict[str, Any]:
    """
    Extracts, structures, validates, and stages a single recruitment notice
    from https://sarkariresult.com.cm/ into the database as a 'pending_review' draft.
    Stores:
      - verification_url: https://sarkariresult.com.cm/<slug>/ (for Admin Audit)
      - original_url: Official Government Application URL (for Aspirants)
      - official_pdf_url: Official notification PDF (if available)
    """
    if is_notice_already_ingested(url, detected_title):
        return {
            'success': False,
            'skipped': True,
            'reason': 'Recruitment notice is already in the database.',
            'url': url
        }

    try:
        extracted_webpage = extract_webpage_content(url)
    except SSRFSecurityError as e:
        return {'success': False, 'skipped': False, 'error': f"Security guard blocked URL: {e}", 'url': url}
    except InvalidContentError as e:
        return {'success': False, 'skipped': True, 'reason': f"Content filtered: {e}", 'url': url}
    except Exception as e:
        return {'success': False, 'skipped': False, 'error': f"Failed to fetch content: {str(e)[:150]}", 'url': url}

    # Extract official external government links from page tables
    soup = BeautifulSoup(extracted_webpage.get('html_content', ''), 'html.parser')
    official_links = parse_sarkari_result_post_links(soup)

    detected = extracted_webpage.get('detected_links', {})
    official_apply = (
        official_links.get('official_apply_url')
        or detected.get('apply_url')
        or detected.get('apply_online_url')
        or ''
    )
    official_pdf = (
        official_links.get('official_pdf_url')
        or detected.get('notification_url')
        or detected.get('official_notification_pdf')
        or ''
    )

    # Format table-first context for optimal Gemini token processing
    tables_block = "\n\n".join(extracted_webpage.get('tables', []))
    content_summary = extracted_webpage.get('cleaned_text', '')[:7000]
    structured_source = (
        f"PAGE TITLE: {extracted_webpage['page_title']}\n\n"
        f"STRUCTURED TABLES:\n{tables_block}\n\n"
        f"NOTIFICATION SUMMARY:\n{content_summary}"
    )

    # Run AI Structuring & Normalization
    structured_data = extract_and_structure_job(
        source_text=structured_source,
        source_url=url,
        detected_links=extracted_webpage['detected_links'],
        source_type='url',
        page_title=extracted_webpage['page_title'] or detected_title,
        key_values=extracted_webpage.get('key_values'),
        custom_gemini_api_key=custom_gemini_api_key
    )

    job_fields = structured_data['job_fields']
    rule_fields = structured_data['rule_fields']
    metadata = structured_data['metadata']

    advt_no = job_fields.get('advertisement_number', '')
    org = job_fields.get('organization', '')
    title = job_fields.get('title', '')
    clean_url = url.strip().rstrip('/')

    # 1. AUTO-SKIP FILTER: Drop expired recruitment notices before staging
    deadline_val = job_fields.get('application_deadline')
    deadline_date = None
    if isinstance(deadline_val, (date, datetime)):
        deadline_date = deadline_val if isinstance(deadline_val, date) else deadline_val.date()
    elif isinstance(deadline_val, str) and deadline_val.strip():
        try:
            deadline_date = datetime.strptime(deadline_val.strip(), '%Y-%m-%d').date()
        except ValueError:
            deadline_date = None

    today = timezone.now().date()
    if deadline_date and deadline_date < today:
        logger.info(
            "Auto-Skip Filter: Recruitment notice '%s' skipped - deadline %s expired before today %s",
            title or detected_title, deadline_date, today
        )
        SkippedRecruitment.objects.update_or_create(
            url=clean_url,
            defaults={
                'title': title or detected_title or 'Untitled Notice',
                'reason': f"Deadline expired on {deadline_date}",
                'application_deadline': deadline_date,
            }
        )
        return {
            'success': False,
            'skipped': True,
            'reason': f"Recruitment application deadline has expired ({deadline_date}). Auto-skip filter applied.",
            'url': url,
            'title': title or detected_title,
            'deadline': str(deadline_date)
        }

    # 2. 100% LIVE RECRUITMENT FILTER
    # CareerSync accepts strictly 100% live recruitment openings where candidates can apply immediately:
    # - official_apply link must be present and external (not empty, not sarkariresult.com, not '#')
    # - application_start_date must be present and <= today
    # - application_deadline must be >= today (already verified above)
    # - AI extractor signals must not indicate upcoming / non-live status

    start_val = job_fields.get('application_start_date')
    start_date = None
    if isinstance(start_val, (date, datetime)):
        start_date = start_val if isinstance(start_val, date) else start_val.date()
    elif isinstance(start_val, str) and start_val.strip():
        try:
            start_date = datetime.strptime(start_val.strip(), '%Y-%m-%d').date()
        except ValueError:
            start_date = None

    ai_upcoming = bool(job_fields.get('is_upcoming', False))

    is_live = bool(
        official_apply
        and not ai_upcoming
        and start_date
        and start_date <= today
    )

    if not is_live:
        # Schedule smart re-check date
        # If start_date is announced in the future, schedule exactly for start_date
        # If start_date is unannounced ("Available Soon") or apply link is pending, re-check tomorrow
        recheck_date = start_date if (start_date and start_date > today) else (today + timedelta(days=1))

        reason_parts = []
        if not official_apply:
            reason_parts.append("Official apply link inactive/pending")
        if not start_date:
            reason_parts.append("Start date unannounced / Available Soon")
        elif start_date > today:
            reason_parts.append(f"Application starts on {start_date}")
        elif ai_upcoming:
            reason_parts.append("Marked upcoming in notice details")

        reason_str = f"Form not live yet ({', '.join(reason_parts)})"

        logger.info(
            "Auto-Skip Filter: Recruitment notice '%s' skipped - %s. Re-check scheduled for %s.",
            title or detected_title, reason_str, recheck_date
        )

        SkippedRecruitment.objects.update_or_create(
            url=clean_url,
            defaults={
                'title': title or detected_title or 'Untitled Notice',
                'reason': reason_str[:255],
                'application_deadline': deadline_date,
                'recheck_after': recheck_date,
            }
        )

        return {
            'success': False,
            'skipped': True,
            'reason': f"Recruitment is not live yet: {reason_str}. Scheduled for re-check on {recheck_date}.",
            'url': url,
            'title': title or detected_title,
            'recheck_after': str(recheck_date)
        }

    # Cross-check for existing live job
    dup_query = Q()
    if advt_no and advt_no.strip():
        dup_query |= (Q(advertisement_number__iexact=advt_no.strip()) & Q(organization__iexact=org.strip()))
    if title and org:
        dup_query |= (Q(title__iexact=title.strip()) & Q(organization__iexact=org.strip()))
    if clean_url:
        dup_query |= (Q(verification_url=clean_url) | Q(verification_url=clean_url + '/') | Q(original_url=clean_url) | Q(original_url=clean_url + '/'))

    existing_job = Job.objects.filter(dup_query).first() if dup_query else None
    if existing_job:
        return {
            'success': False,
            'skipped': True,
            'reason': f"Duplicate recruitment detected with matching Title/Org: '{title}' ({org})",
            'url': url
        }

    job_fields['is_upcoming'] = False
    metadata['is_upcoming'] = False

    # TWO-TIER LINK ARCHITECTURE:
    # 1. verification_url: Sarkari Result page for Admin Audit
    # 2. original_url: Official Commission Application URL for Aspirants
    # 3. official_pdf_url: Official notification PDF
    job_fields['verification_url'] = url
    job_fields['source_name'] = 'Sarkari Result'
    job_fields['source_type'] = 'url'

    if official_apply:
        job_fields['original_url'] = official_apply
    else:
        job_fields['original_url'] = url

    if official_pdf:
        job_fields['official_pdf_url'] = official_pdf

    # Stage strictly as pending_review draft (NEVER auto-published!)
    metadata['auto_ingested'] = True
    metadata['ssot_source'] = 'https://sarkariresult.com.cm/'
    metadata['verification_url'] = url
    metadata['official_apply_url'] = official_apply
    metadata['official_pdf_url'] = official_pdf
    metadata['original_source_title'] = detected_title

    job_fields['ai_extraction_metadata'] = metadata
    job_fields['ai_confidence_score'] = metadata.get('confidence_score', 0.90)
    job_fields['status'] = 'pending_review'
    job_fields['is_published'] = False

    create_payload = {
        **job_fields,
        **rule_fields
    }

    serializer = AdminJobWriteSerializer(data=create_payload)
    if serializer.is_valid():
        draft_job = serializer.save()
        # Clean up any previous SkippedRecruitment record for this URL now that it is successfully ingested as LIVE!
        SkippedRecruitment.objects.filter(Q(url=clean_url) | Q(url=clean_url + '/')).delete()
        return {
            'success': True,
            'skipped': False,
            'job_id': draft_job.id,
            'title': draft_job.title,
            'organization': draft_job.organization,
            'confidence': draft_job.ai_confidence_score,
            'verification_url': draft_job.verification_url,
            'original_url': draft_job.original_url,
            'official_pdf_url': draft_job.official_pdf_url,
            'conflicts': metadata.get('conflicts', []),
            'warnings': metadata.get('warnings', []),
            'url': url
        }

    return {
        'success': False,
        'skipped': False,
        'error': f"Schema validation failed: {serializer.errors}",
        'url': url
    }


def run_autonomous_discovery_and_ingestion(
    limit: int = 5,
    custom_gemini_api_key: str = ""
) -> Dict[str, Any]:
    """
    Executes a complete autonomous discovery run from https://sarkariresult.com.cm/:
    1. Re-verifies existing upcoming jobs to detect if their application link is now live.
    2. Discovers new candidate links from /latest-jobs/.
    3. Ingests, parses, and stages pending_review drafts with verification URLs.
    4. Returns summary counts and ingested jobs.
    """
    ingested_jobs = []
    skipped_count = 0
    error_count = 0

    today = timezone.now().date()
    # 1. Proactively re-check candidate recruitments whose scheduled re-check date has arrived
    due_to_recheck = SkippedRecruitment.objects.filter(
        recheck_after__isnull=False,
        recheck_after__lte=today
    ).order_by('skipped_at')[:3]

    for skipped in due_to_recheck:
        if len(ingested_jobs) >= limit:
            break
        logger.info("Autonomous Watcher: Re-checking scheduled notice '%s' for live form activation...", skipped.title or skipped.url)
        recheck_res = ingest_single_recruitment(
            url=skipped.url,
            detected_title=skipped.title,
            custom_gemini_api_key=custom_gemini_api_key
        )
        if recheck_res.get('success'):
            logger.info("Autonomous Watcher: Scheduled notice '%s' is now 100%% LIVE! Staged as draft #%s", skipped.title, recheck_res.get('job_id'))
            ingested_jobs.append(recheck_res)
            time.sleep(2)
        elif recheck_res.get('skipped'):
            skipped_count += 1

    candidate_links = discover_candidate_recruitment_links(limit=limit * 3)

    for item in candidate_links:
        if len(ingested_jobs) >= limit:
            break

        logger.info(f"Autonomous Watcher: Sequential processing of '{item['title']}'...")
        res = ingest_single_recruitment(
            url=item['url'],
            detected_title=item['title'],
            custom_gemini_api_key=custom_gemini_api_key
        )

        if res.get('success'):
            ingested_jobs.append(res)
            logger.info(f"Autonomous Watcher: Successfully staged draft #{res.get('job_id')} '{res.get('title')}'")
            # Polite pause between jobs to drain Google Gemini API rate limit buckets
            time.sleep(3)
        elif res.get('skipped'):
            skipped_count += 1
        else:
            error_count += 1

    return {
        'discovered_candidates': len(candidate_links),
        'ingested_count': len(ingested_jobs),
        'skipped_count': skipped_count,
        'error_count': error_count,
        'ingested_jobs': ingested_jobs,
    }


_watcher_thread_instance: Optional[threading.Thread] = None
_watcher_lock = threading.Lock()


def start_background_watcher_thread(interval_seconds: int = 300):
    """
    Spawns an autonomous background worker thread that monitors Sarkari Result periodically.
    Runs silently in the background of the live application so the Admin never has to manually click.
    Defaults to 300 seconds (5 minutes) to stay active within hosting keep-alive limits.
    """
    global _watcher_thread_instance

    with _watcher_lock:
        if _watcher_thread_instance is not None and _watcher_thread_instance.is_alive():
            return

        def _worker_loop():
            # Initial grace period on startup
            time.sleep(10)
            logger.info("Autonomous Background Job Watcher activated (interval: %ds).", interval_seconds)
            while True:
                try:
                    logger.info("Autonomous Background Watcher: Checking Sarkari Result for new recruitments...")
                    report = run_autonomous_discovery_and_ingestion(limit=5)
                    if report.get('ingested_count', 0) > 0:
                        logger.info(
                            "Autonomous Watcher: Staged %d new draft(s) into Admin Review Queue!",
                            report['ingested_count']
                        )
                except Exception as exc:
                    logger.error("Autonomous Watcher background cycle error: %s", exc)

                time.sleep(interval_seconds)

        _watcher_thread_instance = threading.Thread(
            target=_worker_loop,
            name="CareerSyncAutonomousJobWatcher",
            daemon=True
        )
        _watcher_thread_instance.start()
        logger.info("Autonomous Background Job Watcher thread registered.")
