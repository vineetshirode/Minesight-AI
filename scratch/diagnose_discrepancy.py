import os
import sys
import pandas as pd
import numpy as np
import joblib

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from server import FEATURE_COLS

model = joblib.load(os.path.join(root_dir, 'model_2-master', 'models', 'Model_A_Gradient_Boosting.pkl'))
df = pd.read_csv(os.path.join(root_dir, 'model_2-master', 'data', 'processed', 'production_engineered.csv'))

print("=== 1. Searching all 672 rows in dataset for 19724.7 ===")
for idx, r in df.iterrows():
    X = np.array([[r[c] for c in FEATURE_COLS]])
    p = round(float(model.predict(X)[0]), 1)
    if abs(p - 19724.7) < 2.0:
        print(f"Row Match: Mine={r['Mine_ID']} Date={r['Date']} Pred={p}")

print("\n=== 2. Testing what inputs on Dongri Buzurg produce 19724.7 ===")
# Base row is July 2025 (Month 7, rep row in server.py)
base_row = df[(df['Mine_ID'] == 'MOIL-01') & (df['Date'] == '2025-07-01')].iloc[0].to_dict()

# Let's test with the initial script.js defaults:
# In script.js / index1.html:
# target = 30000 or 32543 or 365289/12 = 30440
# downtime = 30 or 34.4 or 46.8 or 48 or 55.4
# blast = 0 or 1 or 1.8
# rain = 6.7 or 89.4 or 95 or 100 or 278.7
# workdays = 24 or 25 or 26
test_cases = [
    ("User prompt example payload", {"Production_Target_Tonnes": 30000, "Equipment_Downtime_Hours": 30, "Equipment_Availability_Pct": 82, "Rainfall_mm": 100, "Blasting_Delay_Days": 1, "Working_Days": 25}),
    ("July 2025 raw baseline values", {"Production_Target_Tonnes": 26584, "Equipment_Downtime_Hours": 55.4, "Equipment_Availability_Pct": 78.6, "Rainfall_mm": 278.7, "Blasting_Delay_Days": 1, "Working_Days": 26}),
    ("July 2025 with availability recomputed via formula", {"Production_Target_Tonnes": 26584, "Equipment_Downtime_Hours": 55.4, "Equipment_Availability_Pct": round(100 - (55.4/(26*16))*100, 1), "Rainfall_mm": 278.7, "Blasting_Delay_Days": 1, "Working_Days": 26}),
    ("Annual average baseline values", {"Production_Target_Tonnes": 30440, "Equipment_Downtime_Hours": 46.8, "Equipment_Availability_Pct": 84.8, "Rainfall_mm": 89.4, "Blasting_Delay_Days": 1, "Working_Days": 24}),
    ("Jan 2025 baseline values", {"Production_Target_Tonnes": 32543, "Equipment_Downtime_Hours": 34.4, "Equipment_Availability_Pct": 90.5, "Rainfall_mm": 6.7, "Blasting_Delay_Days": 0, "Working_Days": 24}),
]

for name, params in test_cases:
    scen = dict(base_row)
    scen.update(params)
    scen['Downtime_Per_Working_Day'] = round(scen['Equipment_Downtime_Hours'] / scen['Working_Days'], 2)
    scen['Effective_Capacity'] = round(scen['Equipment_Availability_Pct'] * scen['Working_Days'] / 100.0, 2)
    X = np.array([[scen[c] for c in FEATURE_COLS]])
    p = round(float(model.predict(X)[0]), 1)
    print(f"\nTest Case: {name}")
    print(f"  Inputs: dt={scen['Equipment_Downtime_Hours']}, av={scen['Equipment_Availability_Pct']}, rain={scen['Rainfall_mm']}, blast={scen['Blasting_Delay_Days']}, wk={scen['Working_Days']}, tgt={scen['Production_Target_Tonnes']}")
    print(f"  Derived: dt_per_day={scen['Downtime_Per_Working_Day']}, eff_cap={scen['Effective_Capacity']}")
    print(f"  Prediction: {p:.1f} t")

# Broad search:
print("\n=== 3. Exhaustive search across grid ===")
for rain in [0, 6.7, 50, 89.4, 100, 150, 200, 250, 278.7, 300]:
    for dt in [0, 10, 20, 30, 34.4, 40, 46.8, 50, 55.4, 60, 70, 80]:
        for wk in [20, 22, 24, 25, 26, 27]:
            for blast in [0, 1, 2, 3]:
                for av in [70, 75, 78.6, 80, 82, 84.8, 86.7, 90, 90.5, 95]:
                    for tgt in [24800, 26584, 28000, 30000, 32543]:
                        scen = dict(base_row)
                        scen['Production_Target_Tonnes'] = tgt
                        scen['Equipment_Downtime_Hours'] = dt
                        scen['Equipment_Availability_Pct'] = av
                        scen['Rainfall_mm'] = rain
                        scen['Blasting_Delay_Days'] = blast
                        scen['Working_Days'] = wk
                        scen['Downtime_Per_Working_Day'] = round(dt / wk, 2)
                        scen['Effective_Capacity'] = round(av * wk / 100.0, 2)
                        X = np.array([[scen[c] for c in FEATURE_COLS]])
                        p = round(float(model.predict(X)[0]), 1)
                        if abs(p - 19724.7) < 0.2:
                            print(f"FOUND MATCH: tgt={tgt}, dt={dt}, av={av}, rain={rain}, blast={blast}, wk={wk}, eff_cap={scen['Effective_Capacity']}, dt_per_day={scen['Downtime_Per_Working_Day']} -> {p}")
