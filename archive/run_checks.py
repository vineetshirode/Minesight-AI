import urllib.request
import json

port = 8001
for p in [8001, 8000]:
    try:
        res = urllib.request.urlopen(f'http://127.0.0.1:{p}/api/health', timeout=2)
        if res.status == 200:
            port = p
            break
    except Exception:
        pass

print(f'Testing server on port {port}...')

# 1. GET /
res_root = urllib.request.urlopen(f'http://127.0.0.1:{port}/')
assert res_root.status == 200
html = res_root.read().decode('utf-8')
assert 'leaflet.heat' in html, 'leaflet.heat not in index1.html'
print('[PASS] GET / returned 200 with leaflet.heat included.')

# 2. GET /script.js
res_js = urllib.request.urlopen(f'http://127.0.0.1:{port}/script.js')
assert res_js.status == 200
js_text = res_js.read().decode('utf-8')
assert 'Manganese Occurrence Density' in js_text, 'Legend title not in script.js'
assert 'L.heatLayer' in js_text, 'L.heatLayer not in script.js'
print('[PASS] GET /script.js returned 200 with Manganese Occurrence Density Heatmap.')

# 3. GET /data/manganese_occurrences_MOIL_study_area.csv
res_csv = urllib.request.urlopen(f'http://127.0.0.1:{port}/data/manganese_occurrences_MOIL_study_area.csv')
assert res_csv.status == 200
csv_text = res_csv.read().decode('utf-8')
print(f'[PASS] Occurrence CSV loaded successfully ({len(csv_text.splitlines())} lines).')

# 4. GET /data/exploration_scores.json
res_json = urllib.request.urlopen(f'http://127.0.0.1:{port}/data/exploration_scores.json')
assert res_json.status == 200
exp = json.loads(res_json.read().decode('utf-8'))
num_cells = len(exp.get('cells', []))
num_districts = len(exp.get('districts', []))
print(f'[PASS] exploration_scores.json loaded: {num_cells} cells, {num_districts} districts.')

# 5. GET /api/health & /api/baseline
assert urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health').status == 200
assert urllib.request.urlopen(f'http://127.0.0.1:{port}/api/baseline').status == 200
print('[PASS] /api/health and /api/baseline return 200 OK.')

# 6. POST /api/simulate
payload = json.dumps({'mine_id': 'MOIL-01', 'downtime': 25.0}).encode('utf-8')
req_sim = urllib.request.Request(f'http://127.0.0.1:{port}/api/simulate', data=payload, headers={'Content-Type': 'application/json'})
res_sim = urllib.request.urlopen(req_sim)
assert res_sim.status == 200
sim_res = json.loads(res_sim.read().decode('utf-8'))
assert sim_res['status'] == 'success'
print('[PASS] /api/simulate returns 200 OK with valid ML prediction.')

print('\nALL SERVER & FRONTEND VALIDATION CHECKS PASSED!')
