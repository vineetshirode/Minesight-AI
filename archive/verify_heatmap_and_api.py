import urllib.request
import json

# 1. Test script.js on server
req = urllib.request.Request('http://127.0.0.1:8000/script.js')
content = urllib.request.urlopen(req).read().decode('utf-8')
assert 'Manganese Prospectivity' in content, 'Manganese Prospectivity not in script.js'
print('[PASS] script.js loaded successfully with Manganese Prospectivity Heatmap.')

# 2. Test data/exploration_scores.json on server
req_exp = urllib.request.Request('http://127.0.0.1:8000/data/exploration_scores.json')
exp_data = json.loads(urllib.request.urlopen(req_exp).read().decode('utf-8'))
num_cells = len(exp_data['cells'])
num_districts = len(exp_data['districts'])
assert num_cells > 1000, f'Expected >1000 cells, got {num_cells}'
assert num_districts == 4, f'Expected 4 districts, got {num_districts}'
print(f'[PASS] exploration_scores.json verified: {num_cells} cells across {num_districts} districts.')

# 3. Test GET /
res_root = urllib.request.urlopen('http://127.0.0.1:8000/')
assert res_root.status == 200, f'GET / returned {res_root.status}'
print('[PASS] GET / returns 200 OK.')

# 4. Test GET /api/health
res_health = urllib.request.urlopen('http://127.0.0.1:8000/api/health')
assert res_health.status == 200
print('[PASS] GET /api/health returns 200 OK.')

# 5. Test POST /api/simulate
payload = json.dumps({'mine_id': 'MOIL-01', 'downtime': 25.0}).encode('utf-8')
req_sim = urllib.request.Request('http://127.0.0.1:8000/api/simulate', data=payload, headers={'Content-Type': 'application/json'})
res_sim = urllib.request.urlopen(req_sim)
assert res_sim.status == 200
print('[PASS] POST /api/simulate returns 200 OK.')

print('\nALL FRONTEND & BACKEND INTEGRATION TESTS PASSED!')
