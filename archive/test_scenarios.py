import os
import sys
import json
import urllib.request

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from server import manager, FEATURE_COLS

base = manager.mine_baselines['MOIL-01']

scenarios = [
    ('Scenario A: Identical Baseline', {'mine_id': 'MOIL-01'}),
    ('Scenario B: Downtime -10 hrs', {'mine_id': 'MOIL-01', 'downtime': round(base['downtime'] - 10.0, 1)}),
    ('Scenario C: Downtime -30 hrs', {'mine_id': 'MOIL-01', 'downtime': round(base['downtime'] - 30.0, 1)}),
    ('Scenario D: Blasting Delay Reduction (1 -> 0 days)', {'mine_id': 'MOIL-01', 'blasting_delay': 0}),
    ('Scenario E: Equipment Availability Increase (78.6% -> 90.0%)', {'mine_id': 'MOIL-01', 'equipment_availability': 90.0}),
    ('Scenario F: Combined Operational Improvement (Downtime=20h, Blast=0d, Rain=50mm, Workdays=26d)', {'mine_id': 'MOIL-01', 'downtime': 20.0, 'blasting_delay': 0, 'rainfall': 50.0, 'working_days': 26}),
]

print("=" * 80)
print("BENCHMARK OF SCENARIOS A THROUGH F ON MODEL 2 (DONGRI BUZURG MINE)")
print("=" * 80)

for name, payload in scenarios:
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/simulate',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    res = json.loads(urllib.request.urlopen(req).read())
    s = res['scenario']
    b = res['baseline']
    eff_cap = round(s['availability'] * s['working_days'] / 100.0, 2)
    b_eff_cap = round(b['availability'] * b['working_days'] / 100.0, 2)
    
    print(f"\n--- {name} ---")
    print(f"Downtime            : {s['downtime']} hrs (Baseline: {b['downtime']} hrs)")
    print(f"Availability        : {s['availability']}% (Baseline: {b['availability']}%)")
    print(f"Effective Capacity  : {eff_cap} (Baseline: {b_eff_cap})")
    print(f"Predicted Production: {s['predicted_production']} t (Baseline: {b['predicted_production']} t)")
    print(f"Shortfall           : {s['shortfall_tonnes']} t ({s['shortfall_pct']}%)")
    print(f"Risk                : {s['risk']}")
    print(f"Impact Delta        : {res['impact']['production_change']:+.1f} t production | {res['impact']['shortfall_change']:+.1f} t shortfall | Risk changed: {res['impact']['risk_changed']}")
