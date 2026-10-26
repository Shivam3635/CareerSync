import json
import os
import re
import time
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from django.conf import settings
import requests


AI_EXTRACTION_PROMPT = """
You are an expert government job recruitment data parser for CareerSync.
Analyze the provided government job notification text (from a recruitment portal or official PDF)
and extract all key structured details strictly as a JSON object.

CRITICAL RULES:
1. Extract information ONLY from the provided text. Never hallucinate or assume facts.
2. If a field is not present or cannot be determined with certainty, set its value to null.
3. Normalize all dates into ISO format "YYYY-MM-DD". If only month and year are given, use the first day of that month.
4. If there is a contradiction in the text (e.g., two different last dates or conflicting age limits), DO NOT GUESS. Note the contradiction in the "conflicts" list.
5. Identify any missing critical fields and list them in the "warnings" list.
6. Provide an overall confidence score between 0.0 and 1.0.

JSON SCHEMA TO RETURN:
{
  "title": string or null,
  "organization": string or null,
  "advertisement_number": string or null,
  "recruitment_year": integer or null,
  "category": "Civil Services" | "Banking" | "Railways" | "Defense" | "Engineering & Tech" | "Teaching" | "Police & Security" | "General",
  "application_start_date": "YYYY-MM-DD" or null,
  "application_deadline": "YYYY-MM-DD" or null,
  "age_cutoff_date": "YYYY-MM-DD" or null,
  "min_age": integer or 18,
  "max_age": integer or 32,
  "total_vacancies": integer or null,
  "application_fee_details": {
    "General/OBC": string or number,
    "SC/ST": string or number,
    "Female": string or number
  },
  "vacancy_details": [
    {
      "post_name": string,
      "vacancies": integer or null,
      "qualification": string or null
    }
  ],
  "min_qualification_level": "10th" | "12th" | "Graduate" | "Post Graduate" | "Doctorate",
  "additional_certification_requirement": string or null (e.g. "Polytechnic Diploma in Mechanical", "ITI Electrician", "CCC Computer Course", "Typing/Steno", or null if none required),
  "allowed_status": "completed_only" | "appearing_allowed",
  "age_relaxations": {
    "OBC": integer (default 3),
    "SC": integer (default 5),
    "ST": integer (default 5),
    "EWS": integer (default 0),
    "GEN": 0
  },
  "domicile_requirement": string (e.g. "All India" or specific State),
  "selection_process": string,
  "description": string,
  "conflicts": [string],
  "warnings": [string],
  "confidence_score": float
}
"""


def normalize_date_string(date_str: Optional[str]) -> Optional[str]:
    """
    Parses various Indian/British/ISO date formats into 'YYYY-MM-DD'.
    Handles: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, YYYY-MM-DD, 15 October 2026, 13 Nov 2026, Oct 15, 2026.
    """
    if not date_str or not isinstance(date_str, str):
        return None

    cleaned = date_str.strip()
    cleaned = re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', cleaned)  # remove ordinal suffixes
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # Already YYYY-MM-DD
    if re.match(r'^\d{4}-\d{2}-\d{2}$', cleaned):
        try:
            datetime.strptime(cleaned, '%Y-%m-%d')
            return cleaned
        except ValueError:
            return None

    # Common Indian formats: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
    dmy_match = re.search(r'(\b\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})\b', cleaned)
    if dmy_match:
        day, month, year = int(dmy_match.group(1)), int(dmy_match.group(2)), int(dmy_match.group(3))
        try:
            return date(year, month, day).strftime('%Y-%m-%d')
        except ValueError:
            pass

    # Word formats
    for fmt in (
        '%d %B %Y', '%d %b %Y', '%B %d %Y', '%b %d %Y',
        '%B %d, %Y', '%b %d, %Y', '%d-%B-%Y', '%d-%b-%Y',
        '%d/%B/%Y', '%d/%b/%Y'
    ):
        try:
            parsed = datetime.strptime(cleaned, fmt)
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            continue

    return None


def call_gemini_api(source_text: str, custom_api_key: str = "") -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Calls Google Gemini API using active, ultra-fast Gemini 3 Flash Preview model.
    Falls back to Gemini 3.5 Flash if needed.
    Returns (result_dict, error_message).
    """
    api_key = (
        custom_api_key.strip()
        or os.environ.get('GEMINI_API_KEY', '').strip()
        or getattr(settings, 'GEMINI_API_KEY', '').strip()
    )
    if not api_key:
        return None, "No Gemini API key configured. Loaded via heuristic engine."

    candidate_models = ["gemini-3-flash-preview", "gemini-3.5-flash"]
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": AI_EXTRACTION_PROMPT},
                    {"text": f"SOURCE NOTIFICATION CONTENT:\n\n{source_text[:14000]}"}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }

    last_error = None
    for model_name in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            resp = requests.post(url, json=payload, timeout=18)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get('candidates', [])
                if candidates:
                    content_text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    if content_text:
                        parsed = json.loads(content_text)
                        parsed['model_used'] = model_name
                        return parsed, None
            elif resp.status_code == 503:
                last_error = "Google AI Studio is experiencing temporary high demand (HTTP 503)."
                continue
            elif resp.status_code == 429:
                return None, "Gemini API rate limit reached (HTTP 429). Loaded via heuristic engine."
            else:
                last_error = f"Gemini API returned HTTP {resp.status_code} on {model_name}."
                continue
        except requests.exceptions.Timeout:
            last_error = f"Gemini API ({model_name}) timed out."
            continue
        except Exception as e:
            last_error = f"Gemini API connection error: {str(e)[:80]}."
            continue

    return None, f"{last_error or 'Gemini extraction could not complete'}. Loaded via heuristic engine."


def fallback_deterministic_extractor(
    source_text: str,
    detected_title: str = "",
    key_values: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    High-fidelity extraction engine specifically tuned for Indian government recruitment notifications
    (Sarkari Result, FreeJobAlert, UPSC, SSC, IBPS, Railways RRB/RRC, State PSCs).
    """
    text = source_text
    key_values = key_values or {}
    conflicts = []
    warnings = []

    # 1. Clean Title
    title = detected_title.strip() if detected_title else ""
    if not title or title.lower() in ('government job recruitment', 'recruitment notification'):
        # Look for h1/title markers inside text
        first_lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 10][:10]
        for l in first_lines:
            if any(k in l.lower() for k in ['recruitment', 'exam', 'posts', 'online form', 'bharti']):
                title = re.sub(r'[\s\|\-]+(?:Sarkari\s*Result|FreeJobAlert).*$', '', l, flags=re.I).strip()
                break
    if not title:
        title = "Government Recruitment 2026"

    # 2. Organization Identification
    org = "Government Recruitment Commission"
    org_patterns = [
        (r'\b(UPSC|Union Public Service Commission)\b', 'Union Public Service Commission (UPSC)'),
        (r'\b(SSC|Staff Selection Commission)\b', 'Staff Selection Commission (SSC)'),
        (r'\b(IBPS|Institute of Banking Personnel Selection)\b', 'Institute of Banking Personnel Selection (IBPS)'),
        (r'\b(Railway Recruitment Board|RRB|RRC|Railway Recruitment Control Board)\b', 'Railway Recruitment Board (RRB)'),
        (r'\b(State Bank of India|SBI)\b', 'State Bank of India (SBI)'),
        (r'\b(DRDO|Defense Research & Development Organization)\b', 'DRDO'),
        (r'\b(ISRO|Indian Space Research Organisation)\b', 'ISRO'),
        (r'\b(UPPSC|Uttar Pradesh Public Service Commission)\b', 'UPPSC'),
        (r'\b(BPSC|Bihar Public Service Commission)\b', 'BPSC'),
        (r'\b(MPPSC|Madhya Pradesh Public Service Commission)\b', 'MPPSC'),
        (r'\b(DSSSB|Delhi Subordinate Services Selection Board)\b', 'DSSSB'),
        (r'\b(NTA|National Testing Agency)\b', 'National Testing Agency (NTA)'),
    ]
    for pattern, name in org_patterns:
        if re.search(pattern, text, re.I):
            org = name
            break

    # 3. Advertisement Number
    advt_no = ""
    # Look for (Advt No : CEN 07/2026) or Advt No. 05/2024
    advt_match = re.search(
        r'(?:Advt\.?\s*No\.?|Notice\s*No\.?|CEN\s*No\.?|Notification\s*No\.?|\(Advt\s*No)[\s\:\-]+([A-Za-z0-9\/\-\_]+(?:\s+[A-Za-z0-9\/\-\_]+)?)',
        text,
        re.I
    )
    if advt_match:
        advt_no = advt_match.group(1).strip()

    # 4. Recruitment Year
    recruitment_year = datetime.now().year
    year_match = re.search(r'\b(202[4-9]|203[0-5])\b', title) or re.search(r'\b(202[4-9]|203[0-5])\b', text[:2000])
    if year_match:
        recruitment_year = int(year_match.group(1))

    # 5. Category Classification
    category = "General"
    cat_lower = f"{title.lower()} {text[:2500].lower()}"
    if any(k in cat_lower for k in ['railway', 'rrb', 'rrc', 'loco pilot', 'alp', 'ntpc', 'technician', 'trackman']):
        category = "Railways"
    elif any(k in cat_lower for k in ['civil service', 'ias', 'ips', 'ifs', 'administrative', 'uppsc', 'bpsc', 'mppsc']):
        category = "Civil Services"
    elif any(k in cat_lower for k in ['defense', 'army', 'navy', 'air force', 'nda', 'cds', 'afcat', 'crpf', 'bsf', 'cisf', 'itbp', 'paramilitary']):
        category = "Defense"
    elif any(k in cat_lower for k in ['engineer', 'technician', 'polytechnic', 'junior engineer', 'isro', 'drdo', 'bhel', 'ongc']):
        category = "Engineering & Tech"
    elif any(k in cat_lower for k in ['teacher', 'faculty', 'professor', 'kvs', 'nvs', 'tet', 'ctet', 'tgt', 'pgt']):
        category = "Teaching"
    elif any(k in cat_lower for k in ['police', 'constable', 'sub inspector', 'si recruitment', 'jail warder', 'daroga']):
        category = "Police & Security"
    elif any(k in cat_lower for k in ['banking', 'ibps', 'sbi', 'rbi', 'nabard', 'bank po', 'bank clerk', 'specialist officer']):
        category = "Banking"

    # 6. Dates (Start, Deadline, Cutoff)
    start_date = None
    deadline = None
    cutoff_date = None

    # Check key_values from tables first
    for k, v in key_values.items():
        k_lower = k.lower()
        if not start_date and any(t in k_lower for t in ['application begin', 'start date', 'apply start', 'opening date']):
            start_date = normalize_date_string(v)
        if not deadline and any(t in k_lower for t in ['last date', 'apply last date', 'closing date', 'apply online last date']):
            deadline = normalize_date_string(v)
        if not cutoff_date and any(t in k_lower for t in ['age limit as on', 'cutoff date', 'as on']):
            cutoff_date = normalize_date_string(v)

    date_regex_pat = r'([0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+[\,\s]+[0-9]{4}|\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})'

    if not start_date:
        m = re.search(r'(?:Application\s+Begin|Start\s+Date|Online\s+Apply\s+Start\s+Date|Date\s+of\s+Opening|application\s+form\s+has\s+started\s+on)[\s\:\-]+' + date_regex_pat, text, re.I)
        if m:
            start_date = normalize_date_string(m.group(1))

    if not deadline:
        m = re.search(r'(?:Online\s+Apply\s+Last\s+Date|Last\s+Date\s+for\s+Apply|Last\s+Date\s+Online|Registration\s+Last\s+Date|Closing\s+Date|can\s+apply\s+until|Last\s+Date)[\s\:\-]+' + date_regex_pat, text, re.I)
        if m:
            deadline = normalize_date_string(m.group(1))

    if not cutoff_date:
        m = re.search(r'(?:Age\s+Limits?\s+As\s+On|Age\s+Limit\s+as\s+on|Crucial\s+Date\s+for\s+Age|as\s+on)[\s\:\-]+' + date_regex_pat, text, re.I)
        if m:
            cutoff_date = normalize_date_string(m.group(1))
        elif deadline:
            cutoff_date = deadline

    # 7. Age Limits
    min_age = 18
    max_age = 32

    # Check for direct key_values e.g. "Minimum Age : 18 Years"
    min_m = re.search(r'(?:Minimum\s+Age|Min\s+Age)[\s\:\-]+(\d{2})', text, re.I)
    if min_m:
        min_age = int(min_m.group(1))

    max_m = re.search(r'(?:Maximum\s+Age|Max\s+Age)[\s\:\-]+(\d{2})', text, re.I)
    if max_m:
        max_age = int(max_m.group(1))

    # Also check "18-30 Years" or "Between 18 to 32 Years"
    if min_age == 18 and max_age == 32:
        range_m = re.search(r'\b(?:Age\s+Limit|Age)[\s\:\-]+(\d{2})\s*(?:to|\-)\s*(\d{2})\s*Years?', text, re.I)
        if range_m:
            min_age, max_age = int(range_m.group(1)), int(range_m.group(2))

    if min_age > max_age:
        conflicts.append(f"Mismatched age bounds detected: minimum age ({min_age}) is greater than maximum age ({max_age}).")

    # 8. Vacancy Count
    total_vacancies = None
    # Look for "Total Post 1688 Posts" or "This recruitment is for 1688 positions"
    vac_m = (
        re.search(r'(?:Total\s+Post|Total\s+Vacanc(?:y|ies)|recruitment\s+is\s+for|No\.\s+of\s+Posts?)[\s\:\-]+([0-9\,]+)', text, re.I)
        or re.search(r'\b([0-9\,]+)\s+(?:Posts?|Vacancies|positions)\b', text, re.I)
    )
    if vac_m:
        try:
            val_clean = vac_m.group(1).replace(',', '')
            if 1 <= int(val_clean) <= 500000:
                total_vacancies = int(val_clean)
        except ValueError:
            pass

    # 9. Application Fees
    fee_details = {}
    gen_fee_m = re.search(r'(?:General|GEN)[^\:\n]*[\:\-]+[^\d\n]*(\d+)', text, re.I)
    if gen_fee_m:
        fee_details['General/OBC'] = f"Rs. {gen_fee_m.group(1)}"

    sc_fee_m = re.search(r'(?:SC\s*\/\s*ST|SC)[^\:\n]*[\:\-]+[^\d\n]*(\d+|Nil|Zero|Exempted)', text, re.I)
    if sc_fee_m:
        fee_details['SC/ST'] = f"Rs. {sc_fee_m.group(1)}"

    fem_fee_m = re.search(r'(?:Female|All\s+Category\s+Female)[^\:\n]*[\:\-]+[^\d\n]*(\d+|Nil|Zero|Exempted)', text, re.I)
    if fem_fee_m:
        fee_details['Female'] = f"Rs. {fem_fee_m.group(1)}"

    # 10. Educational Qualification & Additional Certification
    min_qualification = "Graduate"
    allowed_status = "completed_only"
    additional_cert = ""

    qual_lower = text.lower()

    # Detect additional certifications / diplomas
    if any(k in qual_lower for k in ['polytechnic diploma', '3 year diploma', 'engineering diploma', 'diploma in engineering']):
        dip_match = re.search(r'(?:3\s*year\s*)?(?:polytechnic\s+)?diploma\s+in\s+([A-Za-z\s]+?)(?:\,|\.|\;|\band\b|\bfrom\b|\bwith\b|\n)', text, re.I)
        if dip_match:
            additional_cert = f"Polytechnic Diploma in {dip_match.group(1).strip()}"
        else:
            additional_cert = "Polytechnic / 3-Year Engineering Diploma"
    elif 'polytechnic' in qual_lower or 'diploma' in qual_lower:
        dip_match = re.search(r'([A-Za-z\s]{0,25}diploma[A-Za-z\s]{0,30})', text, re.I)
        additional_cert = dip_match.group(1).strip() if dip_match else "Diploma Certificate"
    elif 'iti' in qual_lower or 'trade certificate' in qual_lower:
        additional_cert = "ITI / Trade Certificate"
    elif 'ccc' in qual_lower or 'o level' in qual_lower:
        additional_cert = "CCC / O-Level Computer Certificate"
    elif 'b.ed' in qual_lower or 'd.el.ed' in qual_lower:
        additional_cert = "B.Ed / D.El.Ed Teacher Training Certificate"

    # Core academic degree ladder (10th, 12th, Graduate, Post Graduate, Doctorate)
    if any(k in qual_lower for k in ['ph.d', 'doctorate', 'phd']):
        min_qualification = 'Doctorate'
    elif any(k in qual_lower for k in ['post graduate', 'master degree', 'm.tech', 'm.sc', 'm.com', 'm.a', 'mba']):
        min_qualification = 'Post Graduate'
    elif any(k in qual_lower for k in ['bachelor degree', 'graduate', 'degree in any stream', 'b.tech', 'b.sc', 'b.com', 'b.a', 'graduation']):
        min_qualification = 'Graduate'
    elif any(k in qual_lower for k in ['10+2', '10+2 intermediate', '12th standard', 'intermediate exam', 'senior secondary', 'higher secondary']):
        min_qualification = '12th'
    elif any(k in qual_lower for k in ['10th pass', 'matriculation', 'high school', '10th class']):
        min_qualification = '10th'
    elif additional_cert:
        min_qualification = '10th'

    if any(k in qual_lower for k in ['appearing candidate', 'final year appearing', 'appearing allowed', 'awaited result']):
        allowed_status = 'appearing_allowed'

    # Warnings for missing fields
    if not deadline:
        warnings.append("Application deadline was not explicitly stated in source text.")
    if not cutoff_date:
        warnings.append("Age calculation cutoff date was not found; defaulted to deadline.")
    if not total_vacancies:
        warnings.append("Total vacancy count could not be determined.")

    confidence = 0.90
    if warnings:
        confidence -= (len(warnings) * 0.08)
    if conflicts:
        confidence -= 0.25
    confidence = max(0.45, min(1.0, round(confidence, 2)))

    return {
        "title": title,
        "organization": org,
        "advertisement_number": advt_no,
        "recruitment_year": recruitment_year,
        "category": category,
        "application_start_date": start_date or datetime.now().strftime('%Y-%m-%d'),
        "application_deadline": deadline or datetime.now().strftime('%Y-%m-%d'),
        "age_cutoff_date": cutoff_date or deadline or datetime.now().strftime('%Y-%m-%d'),
        "min_age": min_age,
        "max_age": max_age,
        "total_vacancies": total_vacancies,
        "application_fee_details": fee_details,
        "vacancy_details": [],
        "min_qualification_level": min_qualification,
        "additional_certification_requirement": additional_cert,
        "allowed_status": allowed_status,
        "age_relaxations": {
            "OBC": 3,
            "SC": 5,
            "ST": 5,
            "EWS": 0,
            "GEN": 0
        },
        "domicile_requirement": "All India",
        "selection_process": "Written Examination, Skill/Typing Test (if applicable), Document Verification, Medical Exam",
        "description": f"Official recruitment for {title} announced by {org} for {total_vacancies or 'various'} positions.",
        "conflicts": conflicts,
        "warnings": warnings,
        "confidence_score": confidence,
    }


def extract_and_structure_job(
    source_text: str,
    source_url: str = "",
    detected_links: Optional[Dict[str, Optional[str]]] = None,
    source_type: str = "url",
    uploaded_pdf_path: str = "",
    custom_gemini_api_key: str = "",
    page_title: str = "",
    key_values: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Coordinates extraction via Gemini LLM or the high-fidelity rule parser.
    Normalizes dates, numbers, checks constraints, and returns a verified draft payload.
    """
    detected_links = detected_links or {}

    # 1. Attempt Gemini LLM extraction first
    gemini_result, gemini_error = call_gemini_api(source_text, custom_api_key=custom_gemini_api_key)
    
    if gemini_result:
        raw_extracted = gemini_result
        engine_used = f"Google Gemini ({gemini_result.get('model_used', 'gemini-3.5-flash')})"
    else:
        # 2. Use our enhanced deterministic rule parser
        raw_extracted = fallback_deterministic_extractor(
            source_text,
            detected_title=page_title,
            key_values=key_values
        )
        engine_used = "High-Fidelity Heuristic Parser (Offline)"

    # Normalize Dates
    app_start = normalize_date_string(raw_extracted.get('application_start_date'))
    app_deadline = normalize_date_string(raw_extracted.get('application_deadline'))
    age_cutoff = normalize_date_string(raw_extracted.get('age_cutoff_date'))

    today_str = datetime.now().strftime('%Y-%m-%d')
    if not app_start:
        app_start = today_str
    if not app_deadline:
        app_deadline = today_str
    if not age_cutoff:
        age_cutoff = app_deadline

    # Normalize Numbers
    try:
        min_age = int(raw_extracted.get('min_age', 18) or 18)
    except (ValueError, TypeError):
        min_age = 18

    try:
        max_age = int(raw_extracted.get('max_age', 32) or 32)
    except (ValueError, TypeError):
        max_age = 32

    conflicts = list(raw_extracted.get('conflicts') or [])
    warnings = list(raw_extracted.get('warnings') or [])

    if gemini_error and not gemini_result:
        warnings.append(f"AI notice: {gemini_error}")

    # Validate logical consistency
    if min_age > max_age:
        conflicts.append(f"Mismatched age range: minimum age ({min_age}) is greater than maximum age ({max_age}).")

    if app_start and app_deadline and app_start > app_deadline:
        conflicts.append(f"Application start date ({app_start}) is after application deadline ({app_deadline}).")

    # Qualification validation (pure academic ladder)
    valid_levels = ['10th', '12th', 'Graduate', 'Post Graduate', 'Doctorate']
    raw_level = raw_extracted.get('min_qualification_level', 'Graduate')
    if raw_level == 'Diploma':
        min_qualification_level = '10th'
        if not raw_extracted.get('additional_certification_requirement'):
            raw_extracted['additional_certification_requirement'] = 'Diploma / Polytechnic'
    else:
        min_qualification_level = raw_level if raw_level in valid_levels else 'Graduate'

    additional_cert = (raw_extracted.get('additional_certification_requirement') or "").strip()
    raw_status = raw_extracted.get('allowed_status', 'completed_only')
    allowed_status = raw_status if raw_status in ('completed_only', 'appearing_allowed') else 'completed_only'

    official_notification_link = detected_links.get('notification_url') or ""
    original_url = official_notification_link or source_url or detected_links.get('apply_url') or ""

    base_confidence = float(raw_extracted.get('confidence_score', 0.88) or 0.88)
    if conflicts:
        base_confidence = min(base_confidence, 0.65)
    confidence_score = round(max(0.40, min(1.0, base_confidence)), 2)

    cond_summary = f"Minimum qualification: {min_qualification_level} ({allowed_status.replace('_', ' ')})."
    if additional_cert:
        cond_summary += f" Additional requirement: {additional_cert}."
    cond_summary += " Age relaxation applicable per government reservation norms."

    return {
        'job_fields': {
            'title': (raw_extracted.get('title') or "Recruitment Notification").strip(),
            'organization': (raw_extracted.get('organization') or "Government Department").strip(),
            'advertisement_number': (raw_extracted.get('advertisement_number') or "").strip(),
            'recruitment_year': raw_extracted.get('recruitment_year') or datetime.now().year,
            'category': raw_extracted.get('category') or 'General',
            'application_start_date': app_start,
            'application_deadline': app_deadline,
            'age_cutoff_date': age_cutoff,
            'min_age': min_age,
            'max_age': max_age,
            'total_vacancies': raw_extracted.get('total_vacancies'),
            'application_fee_details': raw_extracted.get('application_fee_details') or {},
            'vacancy_details': raw_extracted.get('vacancy_details') or [],
            'selection_process': raw_extracted.get('selection_process') or "Written Exam, Skill Test, Document Verification",
            'original_url': original_url,
            'source_name': "Sarkari Result / Official Notification" if source_type == 'url' else "Official Notification PDF",
            'source_type': source_type,
            'uploaded_pdf': uploaded_pdf_path if uploaded_pdf_path else None,
            'description': raw_extracted.get('description') or "",
            'status': 'pending_review',
            'is_published': False,
        },
        'rule_fields': {
            'min_qualification_level': min_qualification_level,
            'allowed_status': allowed_status,
            'additional_certification_requirement': additional_cert,
            'age_relaxations': raw_extracted.get('age_relaxations') or {
                'OBC': 3,
                'SC': 5,
                'ST': 5,
                'EWS': 0,
                'GEN': 0
            },
            'domicile_requirement': raw_extracted.get('domicile_requirement') or 'All India',
            'min_percentage': None,
            'conditions_summary': cond_summary,
        },
        'metadata': {
            'extraction_engine': engine_used,
            'extraction_timestamp': datetime.now().isoformat(),
            'conflicts': conflicts,
            'warnings': warnings,
            'detected_links': detected_links,
            'confidence_score': confidence_score,
            'source_url': source_url,
            'uploaded_pdf_path': uploaded_pdf_path,
        }
    }
