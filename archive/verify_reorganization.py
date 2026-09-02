import os
import sys
import json
import urllib.request
import subprocess

print("=" * 75)
print("MINESIGHT AI — REORGANIZATION VERIFICATION SUITE")
print("=" * 75)

# 1. Structure Verification
required_paths = [
    "dashboard/index1.html",
    "dashboard/script.js",
    "dashboard/styles.css",
    "dashboard/data/exploration_scores.json",
    "dashboard/data/feature_importance.json",
    "dashboard/data/model_metadata.json",
    "dashboard/data/predictions.json",
    "dashboard/data/manganese_occurrences_MOIL_study_area.csv",
    "dashboard/data/manganese_production_prototype_v2.csv",
    "model_1/src/config.py",
    "model_1/src/grid_generator.py",
    "model_1/src/feature_engineering.py",
    "model_1/src/visualize.py",
    "model_1/data/raw/manganese_occurrences_MOIL_study_area.csv",
    "model_1/data/raw/manganese_occurrences_SIH26009.csv",
    "model_1/data/processed/model1_spatial_features.csv",
    "model_1/data/processed/model1_spatial_features.geojson",
    "model_1/outputs/model1_validation_diagnostics.png",
    "model_1/model1_pipeline.py",
    "model_1/run_pipeline.py",
    "model_1/README.md",
    "model_1/MODEL1_DATA_QUALITY_REPORT.md",
    "model_2/src/config.py",
    "model_2/src/preprocessing.py",
    "model_2/src/feature_engineering.py",
    "model_2/src/train.py",
    "model_2/src/evaluate.py",
    "model_2/src/explainability.py",
    "model_2/src/recommendations.py",
    "model_2/src/predict.py",
    "model_2/data/raw/manganese_production_prototype_v2.csv",
    "model_2/data/processed/production_engineered.csv",
    "model_2/models/Model_A_Gradient_Boosting.pkl",
    "model_2/models/encoders.pkl",
    "model_2/models/production_model.pkl",
    "model_2/outputs/model_metrics.json",
    "model_2/outputs/model_comparison.csv",
    "model_2/outputs/error_analysis.csv",
    "model_2/outputs/feature_importance.csv",
    "model_2/outputs/production_predictions.csv",
    "model_2/audit/AUDIT_REPORT.txt",
    "model_2/audit/CHECK5_DEEP_ANALYSIS.py",
    "model_2/audit/FINAL_MODEL_SELECTION_AUDIT.py",
    "model_2/audit/FINAL_VERDICT.txt",
    "model_2/audit/LEAKAGE_AUDIT.py",
    "model_2/audit/QUICK_REFERENCE.txt",
    "model_2/audit/audit_output.txt",
    "model_2/run_pipeline.py",
    "model_2/README.md",
    "data/manganese_occurrences_MOIL_study_area.csv",
    "data/manganese_occurrences_SIH26009.csv",
    "data/manganese_production_dataset (1).csv",
    "data/manganese_production_prototype_v2.csv",
    "backend/__init__.py",
    "backend/server.py",
    "tests/__init__.py",
    "tests/test_simulator_api.py",
    "docs/MODEL1_DATA_QUALITY_REPORT.md",
    "scripts/model1_pipeline.py",
    "notebooks/mvp.ipynb",
    "outputs/model1_validation_diagnostics.png",
    "scratch/reorganize_repo.py",
    "_archive/model1_spatial_features.csv",
    "requirements.txt",
    "server.py",
    "README.md",
    ".gitignore",
    ".python-version"
]

missing = []
for p in required_paths:
    if not os.path.exists(p):
        missing.append(p)

if missing:
    print(f"[FAIL] Missing {len(missing)} required paths:")
    for m in missing:
        print(f"  - {m}")
    sys.exit(1)
else:
    print(f"[PASS] All {len(required_paths)} target structure paths verified present.")

# 2. Test Backend Server via TestClient
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from backend.server import app, manager, FEATURE_COLS

client = TestClient(app)

res = client.get("/")
assert res.status_code == 200, f"GET / status: {res.status_code}"
assert "<!doctype html>" in res.text.lower(), "GET / did not return HTML"
print("[PASS] GET / serves dashboard HTML correctly.")

res_health = client.get("/api/health")
assert res_health.status_code == 200
h_data = res_health.json()
assert h_data["status"] == "healthy"
assert h_data["model_name"] == "Model_A_Gradient_Boosting"
assert h_data["features_count"] == 18
assert h_data["mines_count"] == 14
print(f"[PASS] GET /api/health returned 200 OK (Model: {h_data['model_name']}, Features: {h_data['features_count']}).")

res_base = client.get("/api/baseline")
assert res_base.status_code == 200
b_data = res_base.json()
assert len(b_data["mines"]) == 14
print(f"[PASS] GET /api/baseline returned 200 OK ({len(b_data['mines'])} mines).")

# Simulate request test
sim_payload = {
    "mine": "Dongri Buzurg Mine",
    "production_target": 26584.0,
    "equipment_availability": 85.0,
    "equipment_downtime": 25.0,
    "rainfall": 15.0,
    "blasting_delay": 0,
    "working_days": 26
}
res_sim = client.post("/api/simulate", json=sim_payload)
assert res_sim.status_code == 200
s_data = res_sim.json()
assert s_data["status"] == "success"
assert "scenario" in s_data
assert "impact" in s_data
scen_pred = s_data["scenario"]["predicted_production"]
risk = s_data["scenario"]["risk"]
prod_change = s_data["impact"]["production_change"]
print(f"[PASS] POST /api/simulate returned 200 OK (Scenario Pred: {scen_pred} t, Risk: {risk}, Delta: {prod_change:+} t).")

print("\n" + "=" * 75)
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY — REORGANIZATION 100% VALIDATED!")
print("=" * 75)
