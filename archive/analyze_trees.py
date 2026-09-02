import os
import sys
import pandas as pd
import numpy as np
import joblib

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from server import FEATURE_COLS, manager

model = manager.model
base = manager.mine_baselines['MOIL-01']
eng_dict = base['raw_encoded_row']
X_base = np.array([[eng_dict[col] for col in FEATURE_COLS]])

# Scenario
scen_dict = dict(eng_dict)
target_dt = 25.0
b_avail = float(base['availability'])
b_downtime = float(base['downtime'])
s_workdays = int(base['working_days'])

avail_shift = ((b_downtime - target_dt) / (s_workdays * 16.0)) * 100.0
s_avail = round(max(50.0, min(99.5, b_avail + avail_shift)), 1)
s_downtime_per_day = round(target_dt / s_workdays, 2)
s_effective_cap = round(s_avail * s_workdays / 100.0, 2)

scen_dict['Equipment_Downtime_Hours'] = target_dt
scen_dict['Equipment_Availability_Pct'] = s_avail
scen_dict['Downtime_Per_Working_Day'] = s_downtime_per_day
scen_dict['Effective_Capacity'] = s_effective_cap
X_scen = np.array([[scen_dict[col] for col in FEATURE_COLS]])

print("=" * 80)
print("TREE DECISION PATH ANALYSIS")
print("=" * 80)

# Check top 5 trees with largest negative deltas:
tree_deltas = []
for idx, tree_est in enumerate(model.estimators_):
    tree = tree_est[0]
    tb = tree.predict(X_base)[0] * model.learning_rate
    ts = tree.predict(X_scen)[0] * model.learning_rate
    tdiff = ts - tb
    tree_deltas.append((idx, tb, ts, tdiff))

tree_deltas.sort(key=lambda x: x[3])

print("Top 5 trees causing negative prediction delta:")
for tidx, tb, ts, td in tree_deltas[:5]:
    tree_obj = model.estimators_[tidx][0].tree_
    print(f"\n--- Tree #{tidx} (Delta: {td:+.2f} t) ---")
    for name, X_val in [('Baseline', X_base), ('Scenario', X_scen)]:
        node = 0
        path = []
        while tree_obj.children_left[node] != -1:
            feat_idx = tree_obj.feature[node]
            thresh = tree_obj.threshold[node]
            val = X_val[0, feat_idx]
            go_left = val <= thresh
            path.append(f"{FEATURE_COLS[feat_idx]} ({val:.2f} <= {thresh:.2f} ? {'YES' if go_left else 'NO'})")
            node = tree_obj.children_left[node] if go_left else tree_obj.children_right[node]
        leaf_val = tree_obj.value[node][0, 0] * model.learning_rate
        print(f"  {name:8s}: Leaf={leaf_val:+.2f} | Path: {' -> '.join(path)}")

print("\n" + "=" * 80)
print("TRAINING DATASET CONTEXT (Dongri Buzurg in Monsoon Months)")
print("=" * 80)
df_eng = pd.read_csv(os.path.join(root_dir, 'model_2-master', 'data', 'processed', 'production_engineered.csv'))
dongri_monsoon = df_eng[(df_eng['Mine_ID'] == 'MOIL-01') & (df_eng['Month'].isin([6, 7, 8, 9]))]
print(dongri_monsoon[['Date', 'Production_Target_Tonnes', 'Actual_Production_Tonnes', 'Equipment_Downtime_Hours', 'Equipment_Availability_Pct', 'Rainfall_mm', 'Working_Days', 'Effective_Capacity', 'Downtime_Per_Working_Day']].to_string(index=False))
