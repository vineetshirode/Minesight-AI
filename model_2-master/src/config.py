"""
config.py — Central Configuration for Model 2: Production Intelligence
========================================================================
SIH 2026 — AI/ML for Manganese Production Prediction
MOIL Ltd. / Ministry of Steel

All configurable parameters, file paths, feature lists, and thresholds
are defined here. Modify this file to adjust the pipeline behaviour
without touching the core logic.

NOTE: The dataset used is a PROTOTYPE / SYNTHETIC dataset created for
demonstrating the ML pipeline. It is NOT official MOIL operational data.
"""

import os

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

RAW_CSV = os.path.join(DATA_RAW_DIR, "manganese_production_prototype_v2.csv")
PROCESSED_CSV = os.path.join(DATA_PROCESSED_DIR, "production_engineered.csv")

# ============================================================
# RANDOM SEED (reproducibility)
# ============================================================
RANDOM_STATE = 42

# ============================================================
# TIME-BASED SPLIT
# ============================================================
TRAIN_END_DATE = "2024-12-31"  # Training: 2022-01 to 2024-12
TEST_START_DATE = "2025-01-01"  # Testing:  2025-01 to 2025-12

# ============================================================
# FEATURE DEFINITIONS
# ============================================================
# Original columns
TARGET_COL = "Actual_Production_Tonnes"
DATE_COL = "Date"
MINE_ID_COL = "Mine_ID"
MINE_NAME_COL = "Mine_Name"
DISTRICT_COL = "District"
STATE_COL = "State"
MINE_TYPE_COL = "Mine_Type"
PRODUCTION_TARGET_COL = "Production_Target_Tonnes"

# Categorical columns (to be label-encoded)
CATEGORICAL_COLS = ["Mine_Name", "State", "Mine_Type"]

# Numerical operational/environmental columns (original)
NUMERICAL_COLS = [
    "Equipment_Availability_Pct",
    "Equipment_Downtime_Hours",
    "Rainfall_mm",
    "Blasting_Delay_Days",
    "Working_Days",
]

# Engineered features
ENGINEERED_FEATURES = [
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

# ── Model A features (with Production Target) ──
FEATURES_MODEL_A = (
    CATEGORICAL_COLS
    + [PRODUCTION_TARGET_COL]
    + NUMERICAL_COLS
    + ENGINEERED_FEATURES
)

# ── Model B features (without Production Target) ──
FEATURES_MODEL_B = (
    CATEGORICAL_COLS
    + NUMERICAL_COLS
    + ENGINEERED_FEATURES
)

# ============================================================
# MODEL HYPERPARAMETERS
# ============================================================
RF_PARAMS = dict(
    n_estimators=200,
    max_depth=12,
    min_samples_leaf=5,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

GB_PARAMS = dict(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    min_samples_leaf=5,
    random_state=RANDOM_STATE,
)

# ============================================================
# RISK CLASSIFICATION THRESHOLDS (shortfall % of target)
# ============================================================
# These are CONFIGURABLE. Adjust after analysing the data distribution.
RISK_THRESHOLDS = {
    "LOW": 5.0,      # shortfall_pct < 5%  → LOW
    "MEDIUM": 15.0,   # 5% ≤ shortfall_pct < 15% → MEDIUM
    # shortfall_pct ≥ 15% → HIGH
}

# ============================================================
# CROSS-VALIDATION
# ============================================================
CV_N_SPLITS = 5  # TimeSeriesSplit folds

# ============================================================
# DATASET GENERATION PARAMETERS
# ============================================================
NUM_MINES = 14
MONTHS_PER_MINE = 48  # Jan 2022 – Dec 2025
START_YEAR = 2022
START_MONTH = 1
