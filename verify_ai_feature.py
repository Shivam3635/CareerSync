import json
import requests

BASE_URL = "http://127.0.0.1:8000"

def run_verification():
    session = requests.Session()

    print("\n--- 1. ADMIN AUTHENTICATION ---")
    login_res = session.post(f"{BASE_URL}/api/auth/login/", json={
        "email": "admin@careersync.demo",
        "password": "admin123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    user_data = login_res.json()
    assert user_data["role"] == "admin", f"User is not admin: {user_data}"
    print(f"Logged in successfully as {user_data['full_name']} ({user_data['role']})")

    print("\n--- 2. ADMIN STATS VERIFICATION ---")
    stats_res = session.get(f"{BASE_URL}/api/admin/stats/")
    assert stats_res.status_code == 200, f"Stats failed: {stats_res.text}"
    stats = stats_res.json()
    print(f"Platform Stats: Total Jobs: {stats['total_jobs']}, Pending Review: {stats.get('pending_review_jobs', 0)}, Published: {stats['published_jobs']}")
    assert "pending_review_jobs" in stats, "pending_review_jobs missing in admin stats"

    print("\n--- 3. SSRF SECURITY DEFENSE TESTING ---")
    # Test localhost loopback
    res_loopback = session.post(f"{BASE_URL}/api/admin/jobs/extract-url/", json={
        "url": "http://127.0.0.1:8000/django-admin/"
    })
    assert res_loopback.status_code == 400, f"SSRF loopback was not blocked! Status: {res_loopback.status_code}"
    print(f"SSRF Loopback Blocked: {res_loopback.json().get('error')}")

    # Test cloud metadata
    res_meta = session.post(f"{BASE_URL}/api/admin/jobs/extract-url/", json={
        "url": "http://169.254.169.254/latest/meta-data/"
    })
    assert res_meta.status_code == 400, f"SSRF metadata was not blocked! Status: {res_meta.status_code}"
    print(f"SSRF Cloud Metadata Blocked: {res_meta.json().get('error')}")

    # Test file scheme
    res_file = session.post(f"{BASE_URL}/api/admin/jobs/extract-url/", json={
        "url": "file:///etc/passwd"
    })
    assert res_file.status_code == 400, f"SSRF file scheme was not blocked! Status: {res_file.status_code}"
    print(f"SSRF Unsupported Scheme Blocked: {res_file.json().get('error')}")

    print("\n--- 4. MANUAL & AI DRAFT CREATION & PENDING REVIEW STATE ---")
    # Create draft job in pending_review
    draft_payload = {
        "title": "ISRO Space Systems Engineer (AI Draft)",
        "organization": "Indian Space Research Organisation (ISRO)",
        "advertisement_number": "ISRO/ICRB/02/2026",
        "recruitment_year": 2026,
        "category": "Engineering & Tech",
        "application_start_date": "2026-11-01",
        "application_deadline": "2026-12-15",
        "age_cutoff_date": "2026-12-15",
        "min_age": 21,
        "max_age": 30,
        "total_vacancies": 85,
        "source_name": "Official ISRO Gazette",
        "source_type": "url",
        "original_url": "https://isro.gov.in/careers/icrb-02-2026",
        "min_qualification_level": "Graduate",
        "allowed_status": "completed_only",
        "status": "pending_review",
        "is_published": False,
        "ai_extraction_metadata": {
            "confidence_score": 0.94,
            "conflicts": [],
            "warnings": []
        }
    }
    create_res = session.post(f"{BASE_URL}/api/admin/jobs/", json=draft_payload)
    assert create_res.status_code == 201, f"Create draft failed: {create_res.text}"
    draft_job = create_res.json()["job"]
    job_id = draft_job["id"]
    print(f"Created Draft Job #{job_id}: '{draft_job['title']}' [Status: {draft_job['status']}, Published: {draft_job['is_published']}]")
    assert draft_job["status"] == "pending_review", f"Expected pending_review, got {draft_job['status']}"
    assert draft_job["is_published"] is False, "Draft must NEVER be published automatically!"

    print("\n--- 5. ASPIRANT VISIBILITY ISOLATION CHECK ---")
    # Unauthenticated / Student session
    public_res = requests.get(f"{BASE_URL}/api/jobs/")
    public_jobs = public_res.json()
    assert not any(j["id"] == job_id for j in public_jobs), f"CRITICAL: Unapproved draft #{job_id} is visible to public!"
    print(f"Verified: Unapproved draft #{job_id} is strictly HIDDEN from public job listings.")

    student_session = requests.Session()
    student_session.post(f"{BASE_URL}/api/auth/login/", json={
        "email": "student@careersync.demo",
        "password": "password123"
    })
    matches_res = student_session.get(f"{BASE_URL}/api/jobs/matches/")
    matches = matches_res.json()["jobs"]
    assert not any(j["id"] == job_id for j in matches), f"CRITICAL: Unapproved draft #{job_id} is visible in candidate matches!"
    print(f"Verified: Unapproved draft #{job_id} is strictly HIDDEN from candidate personalized matches.")

    print("\n--- 6. ADMIN EXPLICIT APPROVAL & PUBLISHING WORKFLOW ---")
    approve_res = session.post(f"{BASE_URL}/api/admin/jobs/{job_id}/approve/", json={
        "review_notes": "All eligibility criteria, reservation percentages, and cutoff verified against ISRO Gazette."
    })
    assert approve_res.status_code == 200, f"Approve failed: {approve_res.text}"
    approved_data = approve_res.json()
    print(f"Approval Result: {approved_data['message']}")
    assert approved_data["job"]["status"] == "approved", "Expected status approved"
    assert approved_data["job"]["is_published"] is True, "Expected is_published True"

    print("\n--- 7. ASPIRANT VISIBILITY AFTER APPROVAL ---")
    public_after = requests.get(f"{BASE_URL}/api/jobs/").json()
    assert any(j["id"] == job_id for j in public_after), f"Approved job #{job_id} should now be visible publicly!"
    print(f"Verified: Job #{job_id} is now LIVE on public listings for all aspirants!")

    print("\n--- 8. ADMIN REJECTION WORKFLOW ---")
    reject_res = session.post(f"{BASE_URL}/api/admin/jobs/{job_id}/reject/", json={
        "review_notes": "Recruitment withdrawn by commission."
    })
    assert reject_res.status_code == 200, f"Reject failed: {reject_res.text}"
    rejected_data = reject_res.json()
    assert rejected_data["job"]["status"] == "rejected", "Expected status rejected"
    assert rejected_data["job"]["is_published"] is False, "Expected is_published False"
    print(f"Verified: Job #{job_id} marked as rejected and unpublished.")

    # Check unapproved again
    public_after_reject = requests.get(f"{BASE_URL}/api/jobs/").json()
    assert not any(j["id"] == job_id for j in public_after_reject), "Rejected job must not appear in public listings!"
    print(f"Verified: Rejected job #{job_id} is no longer visible to candidates.")

    print("\n==========================================")
    print("ALL AI-ASSISTED JOB POSTING WORKFLOW TESTS PASSED!")
    print("==========================================\n")

if __name__ == "__main__":
    run_verification()
