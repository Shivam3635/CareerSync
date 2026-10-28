import os
import django
import requests
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.management.commands.populate_latest_jobs import LATEST_JOBS_DATA

def main():
    session = requests.Session()
    print("1. Authenticating as Admin on Render...")
    login_res = session.post('https://careersync-api-unpo.onrender.com/api/auth/login/', json={
        'email': 'singhshivamop36@gmail.com',
        'password': 'Admin@CareerSync2026'
    })
    
    if login_res.status_code != 200:
        print("Login failed:", login_res.status_code, login_res.text)
        return

    print("Logged in successfully as:", login_res.json().get('full_name'), f"({login_res.json().get('role')})")

    print("\n2. Fetching existing jobs on Render...")
    existing_res = session.get('https://careersync-api-unpo.onrender.com/api/admin/jobs/')
    if existing_res.status_code == 200:
        existing_titles = {j['title'].strip().lower() for j in existing_res.json()}
        print(f"Found {len(existing_titles)} existing job(s) on Render.")
    else:
        existing_titles = set()
        print("Warning: could not fetch existing jobs:", existing_res.status_code)

    print("\n3. Creating latest job postings on Render...")
    created_count = 0
    for item in LATEST_JOBS_DATA:
        title = item['title'].strip()
        if title.lower() in existing_titles:
            print(f"= Already exists: {title}")
            continue

        payload = dict(item)
        rule = payload.pop('rule', {})

        payload['min_qualification_level'] = rule.get('min_qualification_level', 'Graduate')
        payload['allowed_status'] = rule.get('allowed_status', 'completed_only')
        payload['additional_certification_requirement'] = rule.get('additional_certification_requirement', '')
        payload['age_relaxations'] = rule.get('age_relaxations', {})
        payload['domicile_requirement'] = rule.get('domicile_requirement', 'All India')
        payload['min_percentage'] = rule.get('min_percentage')
        payload['conditions_summary'] = rule.get('conditions_summary', '')

        for k in ['application_start_date', 'application_deadline', 'age_cutoff_date']:
            if isinstance(payload.get(k), (date,)):
                payload[k] = payload[k].isoformat()

        res = session.post('https://careersync-api-unpo.onrender.com/api/admin/jobs/', json=payload)
        if res.status_code == 201:
            created_count += 1
            print(f"+ Created on Render: {title}")
        else:
            print(f"- Error creating {title}: {res.status_code} {res.text[:200]}")

    print(f"\nCompleted! Total new jobs published on Render: {created_count}")

    # Verify public job listings count
    public_res = session.get('https://careersync-api-unpo.onrender.com/api/jobs/')
    if public_res.status_code == 200:
        print(f"Total published jobs accessible to students on live site: {len(public_res.json())}")

if __name__ == '__main__':
    main()
