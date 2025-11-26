import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_health():
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Health Check Failed: {e}")

def test_dashboard():
    try:
        r = requests.get(f"{BASE_URL}/dashboard/kpis/general")
        if r.status_code == 200:
            print("✅ Dashboard KPIs: OK")
            print(json.dumps(r.json(), indent=2))
        else:
            print(f"❌ Dashboard KPIs Failed: {r.status_code} - {r.text}")
            
        r = requests.get(f"{BASE_URL}/dashboard/projects?limit=5")
        if r.status_code == 200:
            print(f"✅ Projects List: OK ({len(r.json())} projects fetched)")
        else:
            print(f"❌ Projects List Failed: {r.status_code}")
    except Exception as e:
        print(f"Dashboard Test Failed: {e}")

def test_prediction():
    payload = {
        "total_defects": 100,
        "peak_time": 12.5,
        "duration_weeks": 25
    }
    headers = {"X-Role": "ProjectManager"}
    
    try:
        # Test Success
        r = requests.post(f"{BASE_URL}/predictions/predict", json=payload, headers=headers)
        if r.status_code == 200:
            print("✅ Prediction (Authorized): OK")
            # print(json.dumps(r.json(), indent=2))
        else:
            print(f"❌ Prediction (Authorized) Failed: {r.status_code} - {r.text}")

        # Test Forbidden
        r = requests.post(f"{BASE_URL}/predictions/predict", json=payload, headers={"X-Role": "Developer"})
        if r.status_code == 403:
            print("✅ Prediction (Unauthorized): OK (Correctly Forbidden)")
        else:
            print(f"❌ Prediction (Unauthorized) Failed: Expected 403, got {r.status_code}")
            
    except Exception as e:
        print(f"Prediction Test Failed: {e}")

if __name__ == "__main__":
    print("--- Testing API ---")
    test_health()
    test_dashboard()
    test_prediction()
