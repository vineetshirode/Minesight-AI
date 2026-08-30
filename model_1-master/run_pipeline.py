"""
run_pipeline.py — Master Pipeline Execution Script for Model 1: Exploration Intelligence
SIH 2026 Problem Statement 26009 — MOIL Ltd. / Ministry of Steel

Executes the entire end-to-end Model 1 data alignment and feature engineering pipeline:
  1. Ingests and standardizes historical manganese occurrence coordinates.
  2. Generates the 1.0 km x 1.0 km common spatial grid in UTM Zone 44N (EPSG:32644).
  3. Extracts proximity, density, lithological, topographic, and space technology indicators.
  4. Exports model1_spatial_features.csv and model1_spatial_features.geojson.
  5. Produces comprehensive diagnostic validation maps in outputs/.
"""

import os
import sys
import pandas as pd

# Ensure model_1-master root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.config import (
    STUDY_OCCURRENCES_CSV, ALL_OCCURRENCES_CSV,
    PROCESSED_FEATURES_CSV, PROCESSED_FEATURES_GEOJSON,
    OUTPUTS_DIR
)
from src.grid_generator import generate_spatial_grid
from src.feature_engineering import load_and_project_occurrences, extract_spatial_features
from src.visualize import generate_validation_plots

def main():
    print("\n" + "="*75)
    print("  SIH 2026 — MODEL 1: EXPLORATION INTELLIGENCE PIPELINE")
    print("  MOIL Ltd. / Ministry of Steel")
    print("="*75)

    # Step 1: Load and project occurrences
    print("\n[STEP 1/5] Loading and projecting historical occurrences (EPSG:4326 -> EPSG:32644)...")
    df_study, df_all = load_and_project_occurrences(STUDY_OCCURRENCES_CSV, ALL_OCCURRENCES_CSV)
    print(f"  Study Area Occurrences: {len(df_study)}")
    print(f"  National Reference Occurrences: {len(df_all)}")

    # Step 2: Generate 1.0 km common spatial grid
    print("\n[STEP 2/5] Constructing common 1.0 km x 1.0 km spatial grid mesh...")
    gdf_grid, easting, northing, lat, lon = generate_spatial_grid()
    print(f"  Total Common Grid Cells Generated: {len(gdf_grid):,}")

    # Step 3: Extract multi-source features
    print("\n[STEP 3/5] Extracting proximity, density, geology, terrain and satellite indicators...")
    gdf_populated = extract_spatial_features(gdf_grid, easting, northing, lat, lon, df_study, df_all)
    print(f"  Extracted {len(gdf_populated.columns) - 1} spatial features across {len(gdf_populated):,} cells.")

    # Step 4: Export Deliverables
    print("\n[STEP 4/5] Exporting unified spatial feature deliverables...")
    df_export = pd.DataFrame(gdf_populated.drop(columns=["geometry"]))
    df_export.to_csv(PROCESSED_FEATURES_CSV, index=False, encoding="utf-8-sig")
    print(f"  [SAVED] Tabular Feature Matrix: {PROCESSED_FEATURES_CSV}")
    
    gdf_populated.to_file(PROCESSED_FEATURES_GEOJSON, driver="GeoJSON")
    print(f"  [SAVED] Vector GeoJSON Layer:   {PROCESSED_FEATURES_GEOJSON}")

    # Step 5: Visual Diagnostics
    print("\n[STEP 5/5] Generating visual validation diagnostics and thematic maps...")
    generate_validation_plots(gdf_populated, df_study)

    # Final Summary Checklist
    print("\n" + "="*75)
    print("  PIPELINE EXECUTION COMPLETE — ALL DELIVERABLES READY")
    print("="*75)
    print(f"  1. Raw Study Occurrences:   {STUDY_OCCURRENCES_CSV}")
    print(f"  2. Raw All Occurrences:     {ALL_OCCURRENCES_CSV}")
    print(f"  3. Processed CSV Feature:   {PROCESSED_FEATURES_CSV}")
    print(f"  4. Processed GeoJSON Layer: {PROCESSED_FEATURES_GEOJSON}")
    print(f"  5. Diagnostic Visuals:      {OUTPUTS_DIR}")
    print("="*75 + "\n")

if __name__ == "__main__":
    main()
