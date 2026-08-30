"""
config.py — Configuration and Spatial Parameters for Model 1: Exploration Intelligence
SIH 2026 Problem Statement 26009 — MOIL Ltd. / Ministry of Steel
"""

import os

# Project root for model_1-master
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directories
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
MODELS_DIR = os.path.join(BASE_DIR, "models")

for d in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUTS_DIR, MODELS_DIR]:
    os.makedirs(d, exist_ok=True)

# Raw Occurrence Files
STUDY_OCCURRENCES_CSV = os.path.join(RAW_DATA_DIR, "manganese_occurrences_MOIL_study_area.csv")
ALL_OCCURRENCES_CSV = os.path.join(RAW_DATA_DIR, "manganese_occurrences_SIH26009.csv")

# Processed Feature Outputs
PROCESSED_FEATURES_CSV = os.path.join(PROCESSED_DATA_DIR, "model1_spatial_features.csv")
PROCESSED_FEATURES_GEOJSON = os.path.join(PROCESSED_DATA_DIR, "model1_spatial_features.geojson")

# Coordinate Reference Systems
CRS_WGS84 = "EPSG:4326"        # Geographic WGS 84 (Degrees)
CRS_UTM44N = "EPSG:32644"      # Projected Metric CRS (UTM Zone 44N, metres)

# Study Area Geographic Extent (with ~15-20km regional exploration buffer)
LAT_MIN = 21.15
LAT_MAX = 22.15
LON_MIN = 78.80
LON_MAX = 80.65

# Grid Parameters
GRID_RESOLUTION_M = 1000.0     # 1.0 km x 1.0 km regular polygonal grid

# Kernel Density Bandwidth
KDE_BANDWIDTH_M = 7500.0       # 7.5 km Gaussian kernel bandwidth

# Lineament Endpoints (Sausar Belt Regional Shear Axis)
LINEAMENT_PT1_WGS = (78.90, 21.35)
LINEAMENT_PT2_WGS = (80.50, 22.00)
