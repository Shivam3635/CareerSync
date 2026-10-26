import requests

session = requests.Session()
BASE = 'http://127.0.0.1:8000/api'

def test_admin():
    print("=== TESTING CUSTOM ADMIN BACKEND & WORKFLOWS ===")

    # 1. Login admin demo
    login_res = session.post(f'{BASE}/auth/demo-login/', json={'account_type': 'admin'})
    assert login_res.status_code == 200, f'Admin login failed: {login_res.text}'
    user = login_res.json()
    print(f"[OK] Logged in as: {user['email']} (Role: {user['role']})")

    # 2. Retrieve Stats
    stats_res = session.get(f'{BASE}/admin/stats/')
    assert stats_res.status_code == 200, f'Stats failed: {stats_res.text}'
    stats = stats_res.json()
    print(f"[OK] Stats: Total Jobs={stats['total_jobs']}, Published={stats['published_jobs']}, Students={stats['total_students']}")

    # 3. Create a New Job Opportunity
    create_res = session.post(f'{BASE}/admin/jobs/', json={
        'title': 'Test Commission Specialist Officer 2026',
        'organization': 'Central Banking Council',
        'category': 'Banking',
        'application_start_date': '2026-10-01',
        'application_deadline': '2026-12-01',
        'age_cutoff_date': '2026-08-01',
        'min_age': 20,
        'max_age': 30,
        'original_url': 'https://example.com/specialist-officer',
        'source_name': 'CBC Portal',
        'description': 'Recruitment for Specialist Officers.',
        'is_published': False,
        'min_qualification_level': 'Graduate',
        'allowed_status': 'completed_only',
        'domicile_requirement': 'All India',
    })
    assert create_res.status_code == 201, f'Job create failed: {create_res.text}'
    job = create_res.json()['job']
    job_id = job['id']
    print(f"[OK] Created Draft Job ID={job_id}: {job['title']}")

    # 4. Toggle Publish and Dispatch Alerts
    toggle_res = session.post(f'{BASE}/admin/jobs/{job_id}/toggle-publish/')
    assert toggle_res.status_code == 200, f'Toggle failed: {toggle_res.text}'
    toggle_data = toggle_res.json()
    print(f"[OK] Toggled Publish Status: is_published={toggle_data['is_published']}, Alerts Dispatched={toggle_data['notifications_sent']}")

    # 5. Retrieve Registered Aspirants
    stud_res = session.get(f'{BASE}/admin/students/')
    assert stud_res.status_code == 200, f'Students failed: {stud_res.text}'
    students = stud_res.json()
    print(f"[OK] Aspirants List: {len(students)} student(s) found. First: {students[0]['email']} ({students[0]['category']})")

    # 6. Delete Test Job
    del_res = session.delete(f'{BASE}/admin/jobs/{job_id}/')
    assert del_res.status_code == 200, f'Delete failed: {del_res.text}'
    print(f"[OK] Deleted test job ID={job_id}")

    print("\n[SUCCESS] ALL CUSTOM ADMIN OPERATIONS VERIFIED!")

if __name__ == '__main__':
    test_admin()
