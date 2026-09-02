import os
import sys
import json
import urllib.request

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from server import manager

print("=" * 80)
print("DOWNTIME SENSITIVITY ACROSS 6 OTHER MOIL MINES")
print("=" * 80)

for mid in ['MOIL-07', 'MOIL-03', 'MOIL-05', 'MOIL-08', 'MOIL-11', 'MOIL-12']:
    base = manager.mine_baselines[mid]
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/simulate',
        data=json.dumps({'mine_id': mid, 'downtime': max(5.0, base['downtime'] - 30.0)}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res = json.loads(urllib.request.urlopen(req).read())
    b = res['baseline']
    s = res['scenario']
    imp = res['impact']['production_change']
    print(f"Mine: {mid:8s} | {base['mine_name']:20s} | Dt: {b['downtime']} -> {s['downtime']} hrs | Avail: {b['availability']}% -> {s['availability']}% | Pred: {b['predicted_production']} -> {s['predicted_production']} t | Delta: {imp:+7.1f} t")
