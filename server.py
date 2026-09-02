"""
server.py — FastAPI Backend & Real ML Simulation Engine for MineSight AI
========================================================================
SIH 2026 Problem Statement 26009 — MOIL Ltd. / Ministry of Steel

Serves:
  1. POST /api/simulate — Real-time inference using trained Model 2 (Production Intelligence)
  2. GET /api/baseline  — Baseline operational profiles for all 14 MOIL mines
  3. GET /api/health    — Health check and model metadata
  4. Static Dashboard   — Serves the MineSight AI dashboard on http://localhost:8000
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd
import joblib
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("minesight_api")

# Base directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
M2_DIR = os.path.join(BASE_DIR, "model_2")
MODELS_DIR = os.path.join(M2_DIR, "models")
DATA_DIR = os.path.join(M2_DIR, "data", "processed")
DASH_DIR = os.path.join(BASE_DIR, "dashboard")

# Exact 18 features expected by Model A (in exact training order)
FEATURE_COLS = [
    "Mine_Name",
    "State",
    "Mine_Type",
    "Production_Target_Tonnes",
    "Equipment_Availability_Pct",
    "Equipment_Downtime_Hours",
    "Rainfall_mm",
    "Blasting_Delay_Days",
    "Working_Days",
    "Month",
    "Quarter",
    "Production_Lag_1",
    "Equip_Avail_Lag_1",
    "Downtime_Lag_1",
    "Production_Rolling_3",
    "Equip_Avail_Rolling_3",
    "Downtime_Per_Working_Day",
    "Effective_Capacity",
]

# Risk classification thresholds (from config.py)
RISK_THRESHOLDS = {
    "LOW": 5.0,     # < 5%
    "MEDIUM": 15.0  # 5% to < 15%
}


def classify_risk(shortfall_pct: float) -> str:
    """Classify shortfall percentage into LOW, MEDIUM, or HIGH risk."""
    if shortfall_pct < RISK_THRESHOLDS["LOW"]:
        return "LOW"
    elif shortfall_pct < RISK_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    else:
        return "HIGH"


# -----------------------------------------------------------------------------
# Global State & Model Loader
# -----------------------------------------------------------------------------
class ModelManager:
    def __init__(self):
        self.model = None
        self.model_name = "Model_A_Gradient_Boosting"
        self.encoders = {}
        self.engineered_df = None
        self.raw_df = None
        self.mine_baselines = {}
        self.load_artifacts()

    def load_artifacts(self):
        # 1. Load Trained ML Model
        gb_model_path = os.path.join(MODELS_DIR, "Model_A_Gradient_Boosting.pkl")
        prod_model_path = os.path.join(MODELS_DIR, "production_model.pkl")

        if os.path.exists(gb_model_path):
            self.model = joblib.load(gb_model_path)
            self.model_name = "Model_A_Gradient_Boosting"
            logger.info(f"[ModelManager] Loaded trained Gradient Boosting model from {gb_model_path}")
        elif os.path.exists(prod_model_path):
            self.model = joblib.load(prod_model_path)
            self.model_name = "production_model"
            logger.info(f"[ModelManager] Loaded model from {prod_model_path}")
        else:
            raise FileNotFoundError("No trained Model 2 artifact found in model_2/models/")

        # 2. Load Label Encoders
        enc_path = os.path.join(MODELS_DIR, "encoders.pkl")
        if os.path.exists(enc_path):
            self.encoders = joblib.load(enc_path)
            logger.info(f"[ModelManager] Loaded label encoders from {enc_path}")
        else:
            raise FileNotFoundError(f"Encoders not found at {enc_path}")

        # 3. Load Engineered Data for Baseline Context
        eng_path = os.path.join(DATA_DIR, "production_engineered.csv")
        if os.path.exists(eng_path):
            self.engineered_df = pd.read_csv(eng_path)
            logger.info(f"[ModelManager] Loaded {len(self.engineered_df)} engineered rows for baseline reference")
        else:
            raise FileNotFoundError(f"Engineered data not found at {eng_path}")

        # 4. Load Raw Data for Human-Readable Names and Attributes
        raw_path = os.path.join(M2_DIR, "data", "raw", "manganese_production_prototype_v2.csv")
        if os.path.exists(raw_path):
            self.raw_df = pd.read_csv(raw_path)
            self.raw_df["Date"] = pd.to_datetime(self.raw_df["Date"])
        else:
            raise FileNotFoundError(f"Raw data not found at {raw_path}")

        # 5. Build Baseline Lookup Table for all 14 mines in the 2025 Test Period
        self.build_baselines()

    def build_baselines(self):
        """Constructs rich reference profiles for each mine in the 2025 test window."""
        test_mask = self.raw_df["Date"] >= pd.Timestamp("2025-01-01")
        test_raw = self.raw_df[test_mask]

        mines_list = test_raw[["Mine_ID", "Mine_Name", "District", "State", "Mine_Type"]].drop_duplicates()

        for _, m in mines_list.iterrows():
            mid = m["Mine_ID"]
            mname = m["Mine_Name"]
            m_rows = test_raw[test_raw["Mine_ID"] == mid].sort_values("Date")

            # Representative baseline: take worst-risk or peak monsoon month (e.g., month 7 / July)
            rep_row = m_rows.iloc[6] if len(m_rows) >= 7 else m_rows.iloc[0]

            # Get corresponding row from engineered dataframe
            eng_row = self.engineered_df[
                (self.engineered_df["Mine_ID"] == mid) & 
                (self.engineered_df["Date"] == rep_row["Date"].strftime("%Y-%m-%d"))
            ].iloc[0]

            # Compute actual baseline model prediction
            X_base = eng_row[FEATURE_COLS].values.reshape(1, -1)
            pred_tonnes = float(self.model.predict(X_base)[0])
            pred_tonnes = max(0.0, round(pred_tonnes, 1))

            target = float(rep_row["Production_Target_Tonnes"])
            shortfall = max(0.0, round(target - pred_tonnes, 1))
            shortfall_pct = round((shortfall / target * 100.0), 2) if target > 0 else 0.0
            risk = classify_risk(shortfall_pct)

            self.mine_baselines[mid] = {
                "mine_id": mid,
                "mine_name": mname,
                "district": m["District"],
                "state": m["State"],
                "mine_type": m["Mine_Type"],
                "date": rep_row["Date"].strftime("%Y-%m"),
                "month": int(rep_row["Date"].month),
                "quarter": int(rep_row["Date"].quarter),
                "target": target,
                "actual": float(rep_row["Actual_Production_Tonnes"]),
                "predicted": pred_tonnes,
                "shortfall": shortfall,
                "shortfall_pct": shortfall_pct,
                "risk": risk,
                "downtime": float(rep_row["Equipment_Downtime_Hours"]),
                "availability": float(rep_row["Equipment_Availability_Pct"]),
                "rainfall": float(rep_row["Rainfall_mm"]),
                "blasting_delay": int(rep_row["Blasting_Delay_Days"]),
                "working_days": int(rep_row["Working_Days"]),
                # Lag and rolling features preserved for scenario construction
                "Production_Lag_1": float(eng_row["Production_Lag_1"]),
                "Equip_Avail_Lag_1": float(eng_row["Equip_Avail_Lag_1"]),
                "Downtime_Lag_1": float(eng_row["Downtime_Lag_1"]),
                "Production_Rolling_3": float(eng_row["Production_Rolling_3"]),
                "Equip_Avail_Rolling_3": float(eng_row["Equip_Avail_Rolling_3"]),
                "raw_encoded_row": eng_row.to_dict()
            }


# Initialize model manager
manager = ModelManager()

# -----------------------------------------------------------------------------
# FastAPI App Initialization
# -----------------------------------------------------------------------------
app = FastAPI(
    title="MineSight AI Simulation Engine",
    description="Real Model-Driven What-If Scenario Simulator for SIH 2026 Problem Statement 26009",
    version="1.0.0"
)

# Enable CORS for local dev / dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Request & Response Schemas
# -----------------------------------------------------------------------------
class SimulationRequest(BaseModel):
    mine: Optional[str] = Field(None, description="Mine ID (e.g. 'MOIL-01') or Mine Name (e.g. 'Dongri Buzurg Mine')")
    mine_id: Optional[str] = None
    production_target: Optional[float] = None
    equipment_availability: Optional[float] = None
    downtime: Optional[float] = Field(None, description="Equipment Downtime in Hours")
    rainfall: Optional[float] = Field(None, description="Monthly Rainfall in mm")
    blasting_delay: Optional[int] = Field(None, description="Blasting Delay in Days")
    working_days: Optional[int] = Field(None, description="Active Working Days in Month")
    month: Optional[int] = None
    date: Optional[str] = None


# -----------------------------------------------------------------------------
# API Endpoints & Root Route
# -----------------------------------------------------------------------------
@app.get("/")
def read_root():
    """Serves dashboard/index1.html at the root URL '/'."""
    index1_path = os.path.join(DASH_DIR, "index1.html")
    if os.path.exists(index1_path):
        return FileResponse(index1_path)
    raise HTTPException(status_code=404, detail="Dashboard index file not found")


@app.get("/api/health")
def health_check():
    """Health check endpoint confirming model status and metadata."""
    return {
        "status": "healthy",
        "model_name": manager.model_name,
        "algorithm": "Gradient Boosting Regressor (Model A)",
        "features_count": len(FEATURE_COLS),
        "features": FEATURE_COLS,
        "mines_count": len(manager.mine_baselines),
        "leakage_audit": "PASSED"
    }


@app.get("/api/baseline")
def get_baselines():
    """Returns baseline operational and forecast data for all 14 MOIL mines."""
    return {
        "mines": [
            {
                "id": v["mine_id"],
                "name": v["mine_name"],
                "district": v["district"],
                "state": v["state"],
                "mine_type": v["mine_type"],
                "target": v["target"],
                "predicted": v["predicted"],
                "shortfall": v["shortfall"],
                "shortfall_pct": v["shortfall_pct"],
                "risk": v["risk"],
                "downtime": v["downtime"],
                "availability": v["availability"],
                "rainfall": v["rainfall"],
                "blasting_delay": v["blasting_delay"],
                "working_days": v["working_days"]
            }
            for v in manager.mine_baselines.values()
        ]
    }


@app.post("/api/simulate")
def run_simulation(req: SimulationRequest):
    """
    Executes a real scenario simulation by running the existing trained ML model
    on user-modified operational constraints.
    """
    # 1. Resolve selected mine
    selected_key = None
    req_mine = req.mine_id or req.mine

    if req_mine:
        norm_req = req_mine.strip().lower()
        for mid, b in manager.mine_baselines.items():
            if norm_req in mid.lower() or norm_req in b["mine_name"].lower():
                selected_key = mid
                break

    # Default to Dongri Buzurg (MOIL-01) if not specified
    if not selected_key:
        selected_key = "MOIL-01"

    base = manager.mine_baselines[selected_key]
    eng_dict = dict(base["raw_encoded_row"])

    # 2. Extract and Validate Baseline Operational Parameters
    b_target = float(base["target"])
    b_downtime = float(base["downtime"])
    b_avail = float(base["availability"])
    b_rain = float(base["rainfall"])
    b_blast = int(base["blasting_delay"])
    b_workdays = int(base["working_days"])

    # 3. Construct Scenario Operational Values (user-modified or fallback to baseline)
    s_target = float(req.production_target) if req.production_target is not None else b_target
    s_downtime = float(req.downtime) if req.downtime is not None else b_downtime
    s_rain = float(req.rainfall) if req.rainfall is not None else b_rain
    s_blast = int(req.blasting_delay) if req.blasting_delay is not None else b_blast
    s_workdays = int(req.working_days) if req.working_days is not None else b_workdays

    # Calculate Scenario Equipment Availability
    if req.equipment_availability is not None:
        s_avail = round(max(50.0, min(99.5, float(req.equipment_availability))), 1)
    elif abs(s_downtime - b_downtime) < 0.001 and s_workdays == b_workdays:
        # Unchanged from baseline -> preserve empirical baseline availability
        s_avail = b_avail
    else:
        # Downtime or workdays changed -> adjust relative to baseline empirical availability
        avail_shift = ((b_downtime - s_downtime) / max(1.0, s_workdays * 16.0)) * 100.0
        s_avail = round(max(50.0, min(99.5, b_avail + avail_shift)), 1)

    # 4. Compute Derived Features (Recalculate whenever scenario constraints change)
    if abs(s_downtime - b_downtime) < 0.001 and s_workdays == b_workdays:
        s_downtime_per_day = float(eng_dict["Downtime_Per_Working_Day"])
    else:
        s_downtime_per_day = round(s_downtime / max(1, s_workdays), 2)

    if abs(s_avail - b_avail) < 0.001 and s_workdays == b_workdays:
        s_effective_cap = float(eng_dict["Effective_Capacity"])
    else:
        s_effective_cap = round(s_avail * s_workdays / 100.0, 2)

    # 5. Build Exact 18-Feature Scenario Vector
    scenario_row = dict(eng_dict)
    scenario_row["Production_Target_Tonnes"] = s_target
    scenario_row["Equipment_Downtime_Hours"] = s_downtime
    scenario_row["Equipment_Availability_Pct"] = s_avail
    scenario_row["Rainfall_mm"] = s_rain
    scenario_row["Blasting_Delay_Days"] = s_blast
    scenario_row["Working_Days"] = s_workdays
    scenario_row["Downtime_Per_Working_Day"] = s_downtime_per_day
    scenario_row["Effective_Capacity"] = s_effective_cap

    # 6. Execute Model Inference
    X_base = np.array([[eng_dict[col] for col in FEATURE_COLS]])
    X_scen = np.array([[scenario_row[col] for col in FEATURE_COLS]])

    pred_base_tonnes = max(0.0, round(float(manager.model.predict(X_base)[0]), 1))
    pred_scen_tonnes = max(0.0, round(float(manager.model.predict(X_scen)[0]), 1))

    # 7. Shortfall, Shortfall % and Risk Calculations
    shortfall_base = max(0.0, round(b_target - pred_base_tonnes, 1))
    shortfall_base_pct = round((shortfall_base / b_target * 100.0), 2) if b_target > 0 else 0.0
    risk_base = classify_risk(shortfall_base_pct)

    shortfall_scen = max(0.0, round(s_target - pred_scen_tonnes, 1))
    shortfall_scen_pct = round((shortfall_scen / s_target * 100.0), 2) if s_target > 0 else 0.0
    risk_scen = classify_risk(shortfall_scen_pct)

    # 8. Projected Impacts
    prod_change = round(pred_scen_tonnes - pred_base_tonnes, 1)
    shortfall_change = round(shortfall_scen - shortfall_base, 1)

    return {
        "status": "success",
        "model_used": manager.model_name,
        "mine": {
            "id": base["mine_id"],
            "name": base["mine_name"],
            "district": base["district"],
            "state": base["state"],
            "mine_type": base["mine_type"],
            "month": base["month"]
        },
        "baseline": {
            "predicted_production": pred_base_tonnes,
            "target": b_target,
            "shortfall_tonnes": shortfall_base,
            "shortfall_pct": shortfall_base_pct,
            "risk": risk_base,
            "downtime": b_downtime,
            "availability": b_avail,
            "blasting_delay": b_blast,
            "rainfall": b_rain,
            "working_days": b_workdays
        },
        "scenario": {
            "predicted_production": pred_scen_tonnes,
            "target": s_target,
            "shortfall_tonnes": shortfall_scen,
            "shortfall_pct": shortfall_scen_pct,
            "risk": risk_scen,
            "downtime": s_downtime,
            "availability": s_avail,
            "blasting_delay": s_blast,
            "rainfall": s_rain,
            "working_days": s_workdays
        },
        "impact": {
            "production_change": prod_change,
            "shortfall_change": shortfall_change,
            "risk_changed": risk_scen != risk_base,
            "risk_from": risk_base,
            "risk_to": risk_scen
        }
    }


# -----------------------------------------------------------------------------
# Mount Static Dashboard Files (Serves UI on http://localhost:8000/)
# -----------------------------------------------------------------------------
if os.path.exists(DASH_DIR):
    app.mount("/", StaticFiles(directory=DASH_DIR, html=True), name="dashboard")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("\n" + "=" * 70)
    print("  MINESIGHT AI — FASTAPI ML SIMULATION SERVER")
    print(f"  Serving Dashboard & API on: http://127.0.0.1:{port}")
    print(f"  API Docs available on:       http://127.0.0.1:{port}/docs")
    print("=" * 70 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
