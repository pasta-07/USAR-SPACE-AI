import urllib.request
import json

def test_url(url, method='GET', data=None):
    req = urllib.request.Request(url, method=method)
    if data:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return resp.status, data
    except Exception as e:
        return 500, str(e)

def main():
    print("================ LIVE API VERIFICATION ================")
    
    s, d = test_url('http://127.0.0.1:8000/')
    print(f"1. Root Endpoint: Status {s}, System = '{d.get('system')}', Status = '{d.get('status')}'")
    assert s == 200

    s, d = test_url('http://127.0.0.1:8000/api/classrooms/available-now')
    print(f"2. Available Now (IST Real): Status {s}, Total Classrooms = {d.get('total_classrooms')}, Free = {d.get('available_now_count')}, Occupied = {d.get('occupied_count')}")
    assert s == 200

    s, d = test_url('http://127.0.0.1:8000/api/classrooms/available-now?simulated_day=Monday&simulated_time=10:15')
    print(f"3. Time Machine (Monday 10:15 AM): Status {s}, Total Classrooms = {d.get('total_classrooms')}, Free = {d.get('available_now_count')}, Occupied = {d.get('occupied_count')}")
    assert s == 200

    s, d = test_url('http://127.0.0.1:8000/api/classrooms/search?day_of_week=Wednesday&start_time=14:00&end_time=16:00')
    print(f"4. Room Search (Wed 14:00 - 16:00): Status {s}, Found {len(d)} free rooms")
    assert s == 200

    s, d = test_url('http://127.0.0.1:8000/api/buildings')
    print(f"5. Buildings: Status {s}, Found {len(d)} buildings: {[b['name'] for b in d]}")
    assert s == 200

    s, d = test_url('http://127.0.0.1:8000/api/admin/conflicts')
    print(f"6. Conflict Center: Status {s}, Detected {len(d)} scheduling conflicts")
    assert s == 200

    s, d = test_url('http://127.0.0.1:8000/api/admin/exceptions')
    print(f"7. Exceptions Manager: Status {s}, Found {len(d)} active campus exceptions")
    assert s == 200

    s, d = test_url('http://127.0.0.1:8000/api/stats/overview')
    print(f"8. Campus Analytics: Status {s}, Total Scheduled Classes = {d.get('total_scheduled_classes')}")
    assert s == 200

    print("================ ALL LIVE ENDPOINTS VERIFIED 100% SUCCESS ================")

if __name__ == "__main__":
    main()
