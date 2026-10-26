import ipaddress
import re
import socket
import urllib.parse
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup


MAX_REDIRECTS = 5
REQUEST_TIMEOUT_SECONDS = 15
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB


class SSRFSecurityError(ValueError):
    """Raised when a URL attempts to target internal/private network infrastructure."""
    pass


class InvalidContentError(ValueError):
    """Raised when page is not a valid recruitment notification."""
    pass


def validate_safe_url(url: str) -> urllib.parse.ParseResult:
    """
    Validates URL scheme and resolves target IP to guarantee no SSRF access
    to localhost, private RFC-1918 networks, link-local addresses, or cloud metadata.
    """
    if not url or not isinstance(url, str):
        raise SSRFSecurityError("URL must be a non-empty string.")

    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme.lower() not in ('http', 'https'):
        raise SSRFSecurityError(f"Unsupported URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFSecurityError("URL must contain a valid hostname.")

    lower_host = hostname.lower()
    if lower_host in ('localhost', 'localhost.localdomain', 'metadata.google.internal', 'instance-data'):
        raise SSRFSecurityError(f"Access to internal host '{hostname}' is blocked.")

    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise SSRFSecurityError(f"Could not resolve host '{hostname}': {str(e)}")

    if not addr_info:
        raise SSRFSecurityError(f"DNS resolution returned no addresses for '{hostname}'.")

    for entry in addr_info:
        ip_str = entry[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            raise SSRFSecurityError(f"Invalid IP address resolved: {ip_str}")

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or str(ip) in ('169.254.169.254', '0.0.0.0', '::1', '::')
        ):
            raise SSRFSecurityError(f"Access to private/internal IP address '{ip}' is strictly forbidden.")

    return parsed


def fetch_url_safely(url: str) -> tuple[str, str]:
    """
    Fetches web content following redirects safely with re-validation of each hop.
    Returns (final_url, html_content).
    """
    current_url = url.strip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }

    session = requests.Session()
    redirect_count = 0

    while True:
        validate_safe_url(current_url)

        try:
            resp = session.get(
                current_url,
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
                allow_redirects=False,
                stream=True,
                verify=True
            )
        except requests.exceptions.SSLError:
            # Fallback for Indian state government portals with missing intermediate certs
            try:
                resp = session.get(
                    current_url,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    allow_redirects=False,
                    stream=True,
                    verify=False
                )
            except Exception as e:
                raise ValueError(f"SSL/TLS failure on '{current_url}': {str(e)}")
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL '{current_url}': {str(e)}")

        # Handle Redirects safely
        if resp.is_redirect or resp.status_code in (301, 302, 303, 307, 308):
            redirect_count += 1
            if redirect_count > MAX_REDIRECTS:
                raise ValueError(f"Exceeded maximum redirect limit of {MAX_REDIRECTS}.")

            location = resp.headers.get('Location')
            if not location:
                raise ValueError("Redirect received without Location header.")
            current_url = urllib.parse.urljoin(current_url, location)
            continue

        if resp.status_code != 200:
            raise ValueError(f"Server responded with error status code {resp.status_code}.")

        content_type = resp.headers.get('Content-Type', '').lower()
        if 'text/html' not in content_type and 'application/xhtml+xml' not in content_type:
            if 'application/pdf' in content_type:
                raise InvalidContentError("The provided URL points directly to a PDF file. Please use the 'Upload PDF' tab.")
            raise InvalidContentError(f"Expected HTML page, received Content-Type '{content_type}'.")

        content_bytes = resp.raw.read(MAX_RESPONSE_BYTES + 1, decode_content=True)
        if len(content_bytes) > MAX_RESPONSE_BYTES:
            raise ValueError(f"Webpage content exceeds maximum allowed size of {MAX_RESPONSE_BYTES // (1024 * 1024)} MB.")

        encoding = resp.encoding or resp.apparent_encoding or 'utf-8'
        try:
            html_text = content_bytes.decode(encoding, errors='replace')
        except Exception:
            html_text = content_bytes.decode('utf-8', errors='replace')

        return current_url, html_text


def detect_page_type(title: str, text: str) -> str:
    """
    Checks whether the page describes a recruitment notification,
    admit card, result, answer key, or exam date.
    """
    combined = f"{title.lower()} {text[:2000].lower()}"

    # Disqualifying markers
    if any(k in combined for k in ['admit card', 'hall ticket', 'call letter', 'exam city slip']):
        if 'recruitment' not in title.lower() and 'apply online' not in combined and 'vacancy' not in combined:
            return 'admit_card'

    if any(k in combined for k in ['result declared', 'merit list', 'final result', 'score card', 'cut off marks']):
        if 'notification' not in title.lower() and 'apply' not in combined:
            return 'result'

    if any(k in combined for k in ['answer key', 'response sheet', 'objection tracker']):
        return 'answer_key'

    if any(k in combined for k in ['exam date notice', 'revised exam schedule']):
        if 'apply' not in combined and 'vacanc' not in combined:
            return 'exam_date'

    if any(k in combined for k in ['recruitment', 'vacancy', 'vacancies', 'apply online', 'online form', 'advertisement', 'bharti', 'post']):
        return 'recruitment'

    return 'recruitment'


def extract_links_from_soup(soup: BeautifulSoup, base_url: str) -> Dict[str, Optional[str]]:
    """Identifies candidate notification PDF, apply online, and official portal links."""
    notification_url = None
    apply_url = None
    official_website_url = None

    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        link_text = a.get_text().strip().lower()
        full_url = urllib.parse.urljoin(base_url, href)

        if not href or href.startswith(('javascript:', '#', 'tel:', 'mailto:')):
            continue

        if not notification_url:
            if any(term in link_text for term in ['download notification', 'official notification', 'advertisement', 'click here for notification', 'notification pdf']):
                notification_url = full_url
            elif full_url.lower().endswith('.pdf') and ('notif' in full_url.lower() or 'advt' in full_url.lower() or 'cen' in full_url.lower()):
                notification_url = full_url

        if not apply_url:
            if any(term in link_text for term in ['apply online', 'click here to apply', 'online application', 'registration', 'registration link']):
                apply_url = full_url

        if not official_website_url:
            if any(term in link_text for term in ['official website', 'official portal', 'visit official site', 'rrb official website']):
                official_website_url = full_url

    return {
        'notification_url': notification_url,
        'apply_url': apply_url,
        'official_website_url': official_website_url,
    }


def clean_job_title(raw_title: str) -> str:
    """Cleans suffixes like '| Sarkari Result', '- SarkariResult.com' from page title."""
    if not raw_title:
        return "Government Job Recruitment"
    title = re.sub(r'[\s\|\-]+(?:Sarkari\s*Result|FreeJobAlert|Rojgar\s*Result|SarkariResult\.com(?:\.cm)?).*$', '', raw_title, flags=re.I)
    title = re.sub(r'[\s\|\-]+(?:Online\s*Form|Recruitment\s*Online).*$', '', title, flags=re.I)
    return title.strip() or raw_title.strip()


def extract_tables_and_key_values(soup: BeautifulSoup) -> Tuple[List[str], Dict[str, str]]:
    """
    Extracts structured tables and parses key-value pairs (e.g. 'Application Begin : 15/10/2026').
    """
    tables_summary = []
    key_values = {}

    for table in soup.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            cells = [c.get_text(separator=" ", strip=True) for c in tr.find_all(['td', 'th'])]
            if cells:
                rows.append(" | ".join(cells))
                # Check for key-value pairs (e.g. Cell 0: Key, Cell 1: Value)
                if len(cells) == 2:
                    k, v = cells[0].strip(), cells[1].strip()
                    if k and v and len(k) < 60:
                        key_values[k] = v
                elif len(cells) == 1 and ':' in cells[0]:
                    parts = cells[0].split(':', 1)
                    k, v = parts[0].strip(), parts[1].strip()
                    if k and v and len(k) < 60:
                        key_values[k] = v

        if rows:
            tables_summary.append("\n".join(rows))

    return tables_summary, key_values


def extract_webpage_content(url: str) -> Dict[str, Any]:
    """
    Full extraction pipeline for URL input.
    Validates SSRF safety, fetches page, removes script/style noise,
    extracts structured tables, key-value pairs, and returns rich cleaned text.
    """
    final_url, html = fetch_url_safely(url)
    soup = BeautifulSoup(html, 'html.parser')

    # Remove only script, style, nav, footer, header, iframes
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript', 'svg']):
        tag.decompose()

    # Remove specific ad elements ONLY (never remove body or main structural containers!)
    for ad in soup.find_all(['ins', 'div'], class_=re.compile(r'\b(adsbygoogle|google-ad|ad-banner|advertisement)\b', re.I)):
        if ad.name in ('body', 'html', 'main', 'article'):
            continue
        ad.decompose()

    raw_title = soup.title.string.strip() if soup.title and soup.title.string else ""
    if not raw_title:
        h1 = soup.find('h1')
        raw_title = h1.get_text().strip() if h1 else "Government Recruitment Notification"

    page_title = clean_job_title(raw_title)
    detected_links = extract_links_from_soup(soup, final_url)
    tables_summary, key_values = extract_tables_and_key_values(soup)

    # Extract all body text cleanly
    cleaned_text = soup.get_text(separator="\n", strip=True)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

    # Detect page type
    page_type = detect_page_type(page_title, cleaned_text)
    if page_type in ('admit_card', 'result', 'answer_key', 'exam_date'):
        type_names = {
            'admit_card': 'Admit Card / Hall Ticket',
            'result': 'Examination Result / Merit List',
            'answer_key': 'Answer Key / Response Sheet',
            'exam_date': 'Exam Date Announcement'
        }
        raise InvalidContentError(
            f"The provided URL appears to be an {type_names.get(page_type)}, not a recruitment notification. "
            f"CareerSync only accepts active recruitment announcements."
        )

    return {
        'source_url': final_url,
        'page_title': page_title,
        'cleaned_text': cleaned_text[:25000],  # generous 25,000 character context
        'tables': tables_summary[:8],
        'key_values': key_values,
        'detected_links': detected_links,
        'page_type': page_type,
    }
