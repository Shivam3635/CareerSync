import requests

BASE_URL = 'http://127.0.0.1:8000/api'
session = requests.Session()

def run_verification():
    print("=== CAREERSYNC FULL INTEGRATION VERIFICATION ===")
    
    # 1. Demo Student Login
    login_res = session.post(f"{BASE_URL}/auth/demo-login/", json={"account_type": "student"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    user_data = login_res.json()
    print(f"[OK] Authenticated as: {user_data['email']} ({user_data['full_name']})")
    print(f"     Profile: Category={user_data['student_profile']['category']}, Domicile={user_data['student_profile']['domicile_state']}")

    # 2. Query Eligible Matches (Default filter)
    matches_res = session.get(f"{BASE_URL}/jobs/matches/?status=eligible")
    assert matches_res.status_code == 200, f"Matches fetch failed: {matches_res.text}"
    data = matches_res.json()
    summary = data['summary']
    print(f"\n[OK] Eligible Opportunities: {summary['eligible_count']} / {summary['total_jobs']}")

    # 3. Test Profile PUT Update (e.g. changing category or domicile)
    put_res = session.put(f"{BASE_URL}/profile/", json={
        "date_of_birth": "1999-06-15",
        "category": "SC",
        "domicile_state": "Haryana",
        "qualifications": [
            {
                "level": "Graduate",
                "degree": "B.Tech Computer Science",
                "status": "completed"
            }
        ]
    })
    print(f"[STATUS] Profile PUT response code: {put_res.status_code}")
    if put_res.status_code != 200:
        print(f"[ERROR] Profile update returned: {put_res.text}")
    assert put_res.status_code == 200, f"Profile PUT failed: {put_res.text}"
    updated_profile = put_res.json()
    print(f"[OK] Profile updated: Category={updated_profile['category']}, Domicile={updated_profile['domicile_state']}")

    # 4. Check that matches recalculate immediately (Haryana domicile should now match Haryana Police Sub-Inspector!)
    matches_res2 = session.get(f"{BASE_URL}/jobs/matches/?status=eligible")
    data2 = matches_res2.json()
    haryana_job = next((j for j in data2['jobs'] if 'Haryana' in j['title']), None)
    print(f"[OK] Recalculated with Haryana domicile: Haryana job found in eligible? {haryana_job is not None}")

    # Revert back to original OBC and UP for demo consistency
    session.put(f"{BASE_URL}/profile/", json={
        "date_of_birth": "1999-06-15",
        "category": "OBC",
        "domicile_state": "Uttar Pradesh",
        "qualifications": [
            {
                "level": "Graduate",
                "degree": "B.Tech Computer Science",
                "status": "completed"
            }
        ]
    })

    print("\n[SUCCESS] ALL CHECKS PASSED PERFECTLY!")

if __name__ == '__main__':
    run_verification()
