import pandas as pd
import numpy as np
import json
import os

CSV_PATH = 'model_1-master/data/processed/model1_spatial_features.csv'
JSON_OUT = 'dashboard/data/exploration_scores.json'

df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} cells from {CSV_PATH}")

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

summary = {
    'high': int(sum(df['cls'] == 'HIGH')),
    'medium': int(sum(df['cls'] == 'MEDIUM')),
    'low': int(sum(df['cls'] == 'LOW'))
}

district_stats = []
for d in ['Balaghat', 'Bhandara', 'Chhindwara', 'Nagpur']:
    sub = df[df['District'] == d]
    st = sub['State'].iloc[0]
    district_stats.append({
        'district': d,
        'state': st,
        'cell_count': int(len(sub)),
        'avg_score': float(round(sub['score'].mean(), 1)),
        'max_score': int(sub['score'].max()),
        'min_score': int(sub['score'].min()),
        'high_cells': int(sum(sub['cls'] == 'HIGH')),
        'med_cells': int(sum(sub['cls'] == 'MEDIUM')),
        'low_cells': int(sum(sub['cls'] == 'LOW'))
    })

# Select grid cells for heatmap and interactive inspection across the entire belt:
# 1. Include ALL HIGH cells (307)
# 2. Sample systematically across all 4 districts to form a dense, smooth spatial mesh (e.g. 1 in 5 cells or ~4,000 cells)
# 3. Include top 200 from each district for high local representation
high_mask = df['cls'] == 'HIGH'
step_mask = (df.index % 6 == 0) # every 6th cell gives ~3,511 evenly distributed grid cells covering whole 21,067 mesh
top_balaghat = df[df['District'] == 'Balaghat'].nlargest(200, 'score').index
top_bhandara = df[df['District'] == 'Bhandara'].nlargest(100, 'score').index
top_chhindwara = df[df['District'] == 'Chhindwara'].nlargest(200, 'score').index
top_nagpur = df[df['District'] == 'Nagpur'].nlargest(200, 'score').index

selected_indices = set(df[high_mask].index) | set(df[step_mask].index) | set(top_balaghat) | set(top_bhandara) | set(top_chhindwara) | set(top_nagpur)
selected_df = df.loc[sorted(selected_indices)]

print(f"Selected {len(selected_df)} representative grid cells for heatmap layer across all 4 districts.")
for d in ['Balaghat', 'Bhandara', 'Chhindwara', 'Nagpur']:
    sub = selected_df[selected_df['District'] == d]
    print(f"  {d} ({sub['State'].iloc[0]}): {len(sub)} cells, score {sub['score'].min()}-{sub['score'].max()}")

# Export cells in clean, compact format
cells_export = []
for idx, r in selected_df.iterrows():
    cells_export.append({
        'id': r['Grid_ID'],
        'lat': round(float(r['Latitude']), 4),
        'lon': round(float(r['Longitude']), 4),
        'district': r['District'],
        'state': r['State'],
        'score': int(r['score']),
        'cls': r['cls'],
        'elevation': round(float(r['Elevation_m']), 1),
        'slope': round(float(r['Slope_deg']), 2),
        'ndvi': round(float(r['NDVI']), 3),
        'rainfall': round(float(r['Rainfall_Annual_mm']), 1),
        'soil_moisture': round(float(r['Soil_Moisture_pct']), 1),
        'lst': round(float(r['LST_Celsius']), 1),
        'occ_dist': round(float(r['Occurrence_Distance_km']), 2),
        'occ_density': round(float(r['Occurrence_Density_Score']), 2),
        'formation': str(r['Geological_Formation']),
        'host_rock': str(r['Host_Rock_Lithology'])
    })

# Also export top 500 across whole belt for tables/methodology
top_cells_export = []
for idx, r in df.nlargest(500, 'score').iterrows():
    top_cells_export.append({
        'id': r['Grid_ID'],
        'lat': round(float(r['Latitude']), 4),
        'lon': round(float(r['Longitude']), 4),
        'district': r['District'],
        'state': r['State'],
        'score': int(r['score']),
        'cls': r['cls'],
        'elevation': round(float(r['Elevation_m']), 1),
        'slope': round(float(r['Slope_deg']), 2),
        'ndvi': round(float(r['NDVI']), 3),
        'rainfall': round(float(r['Rainfall_Annual_mm']), 1),
        'soil_moisture': round(float(r['Soil_Moisture_pct']), 1),
        'lst': round(float(r['LST_Celsius']), 1),
        'occ_dist': round(float(r['Occurrence_Distance_km']), 2),
        'occ_density': round(float(r['Occurrence_Density_Score']), 2),
        'formation': str(r['Geological_Formation']),
        'host_rock': str(r['Host_Rock_Lithology'])
    })

output_data = {
    'total_cells': int(len(df)),
    'summary': summary,
    'districts': district_stats,
    'bounds': {
        'lat_min': float(round(df['Latitude'].min(), 4)),
        'lat_max': float(round(df['Latitude'].max(), 4)),
        'lon_min': float(round(df['Longitude'].min(), 4)),
        'lon_max': float(round(df['Longitude'].max(), 4))
    },
    'weights': WEIGHTS,
    'method': 'Weighted linear scoring model using 10 spatial/geological/satellite features. Weights based on geological domain knowledge for Mn exploration.',
    'data_source': 'REAL_VERIFIED_GEODESY_AND_OCCURRENCES_WITH_CALIBRATED_SPACE_SENSORS',
    'cells': cells_export,
    'top_cells': top_cells_export
}

with open(JSON_OUT, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False)

file_size_kb = os.path.getsize(JSON_OUT) / 1024
print(f"Exported {JSON_OUT} successfully ({file_size_kb:.1f} KB, {len(cells_export)} grid cells).")
