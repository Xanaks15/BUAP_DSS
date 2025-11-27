import urllib.request
import json

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/dashboard/kpis/general") as response:
        if response.status == 200:
            data = json.loads(response.read().decode())
            print("Keys in response:", list(data.keys()))
            print("Productivity:", data.get("productivity"))
            print("Defects by Phase:", data.get("defects_by_phase"))
            print("Tasks Completed %:", data.get("tasks_completed_pct"))
            print("Tasks Delayed %:", data.get("tasks_delayed_pct"))
            print("Total AC:", data.get("total_ac"))
            print("Total PV:", data.get("total_pv"))
        else:
            print("Error:", response.status)
except Exception as e:
    print("Exception:", e)
