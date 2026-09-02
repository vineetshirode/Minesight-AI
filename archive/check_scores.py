import pandas as pd
import numpy as np
import json

df = pd.read_csv('model_1-master/data/processed/model1_spatial_features.csv')
print('Total cells in model1_spatial_features.csv:', len(df))

WEIGHTS = {
    'Occurrence_Density_Score': 0.25,
    'Occurrence_Distance_km': -0.2,
    'Host_Rock_Favorability_Score': 0.15,
    'Elevation_m': -0.05,
    'Slope_deg': -0.05,
    'NDVI': -0.1,
    'Soil_Moisture_pct': -0.05,
    'LST_Celsius': 0.05,
    'Rainfall_Annual_mm': -0.05,
    'Lineament_Distance_km': -0.05
}

FAV_MAP = {
    'highly favorable': 1.0,
    'favorable': 0.8,
    'moderate': 0.5,
    'low': 0.2,
    'unfavorable': 0.0
}

stats = {}
for k in WEIGHTS:
    if k != 'Host_Rock_Favorability_Score':
        vals = df[k].dropna()
        stats[k] = {'min': float(vals.min()), 'max': float(vals.max())}

scores = []
for idx, r in df.iterrows():
    s = 0.0
    for k, w in WEIGHTS.items():
        if k == 'Host_Rock_Favorability_Score':
            fav_str = str(r['Host_Rock_Favorability']).lower()
            fav_val = 0.0
            for pat, v in FAV_MAP.items():
                if pat in fav_str:
                    fav_val = v
                    break
            s += w * fav_val
        else:
            v = float(r[k])
            mi, ma = stats[k]['min'], stats[k]['max']
            norm = (v - mi) / (ma - mi) if ma > mi else 0.5
            if w < 0:
                s += abs(w) * (1.0 - norm)
            else:
                s += w * norm
    score_int = int(np.clip(round(s * 100), 0, 100))
    scores.append(score_int)

df['score'] = scores
df['cls'] = ['HIGH' if s >= 70 else ('MEDIUM' if s >= 40 else 'LOW') for s in scores]

print('Total scored:', len(df))
print('Class breakdown:', df['cls'].value_counts().to_dict())
for d in ['Balaghat', 'Bhandara', 'Chhindwara', 'Nagpur']:
    sub = df[df['District'] == d]
    st = sub['State'].iloc[0]
    print(f'{d:12s} ({st:15s}): count={len(sub)}, min={sub["score"].min()}, max={sub["score"].max()}, mean={sub["score"].mean():.1f}, HIGH={sum(sub["cls"]=="HIGH")}, MED={sum(sub["cls"]=="MEDIUM")}, LOW={sum(sub["cls"]=="LOW")}')
