"""
run_pipeline.py — Master Pipeline Execution Script
===================================================
SIH 2026 — Model 2: Production Intelligence
MOIL Ltd. / Ministry of Steel

Executes the entire end-to-end pipeline in sequence:
  1. Generate / Verify Prototype Dataset (data/raw/manganese_production_prototype_v2.csv)
  2. Data Preprocessing & Validation & Temporal Split (2022-2024 Train / 2025 Test)
  3. Leakage-Safe Feature Engineering (Lags, Rolling Stats, Interactions)
  4. Model Training & Cross-Validation (Model A & Model B across 3 Algorithms)
  5. Evaluation, Comparison Table & Granular Error Diagnostics
  6. Explainability & Feature Importance (MDI, Permutation, SHAP)
  7. Predictions, Shortfall, Risk Classification & Actionable Recommendations
  8. Generates All Deliverables & Reports
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.config import RAW_CSV, OUTPUTS_DIR, MODELS_DIR, FEATURES_MODEL_A, TARGET_COL
from src.generate_dataset import generate_dataset, save_dataset
from src.preprocessing import preprocess_pipeline
from src.feature_engineering import engineer_features
from src.train import train_all_models
from src.evaluate import run_evaluation
from src.explainability import run_explainability
from src.predict import generate_predictions_pipeline


def main():
    print("\n" + "="*75)
    print("  SIH 2026 — MODEL 2: PRODUCTION INTELLIGENCE PIPELINE")
    print("  MOIL Ltd. / Ministry of Steel")
    print("="*75)

    # ------------------------------------------------------------
    # Step 1: Data Ingestion / Generation
    # ------------------------------------------------------------
    print("\n[STEP 1/7] Ingesting / Generating Prototype Dataset...")
    if not os.path.exists(RAW_CSV):
        print(f"  Raw dataset not found at {RAW_CSV}. Generating now...")
        raw_gen_df = generate_dataset()
        save_dataset(raw_gen_df)
    else:
        print(f"  Existing dataset verified at {RAW_CSV}")

    # ------------------------------------------------------------
    # Step 2: Preprocessing & Validation
    # ------------------------------------------------------------
    print("\n[STEP 2/7] Preprocessing & Time-Based Splitting...")
    raw_df, encoded_df, encoders, train_encoded, test_encoded = preprocess_pipeline()

    # Extract raw (unencoded) test set for human-readable error analysis & reporting
    from src.config import TEST_START_DATE
    raw_test_df = raw_df[raw_df["Date"] >= pd.Timestamp(TEST_START_DATE)].copy().reset_index(drop=True)

    # ------------------------------------------------------------
    # Step 3: Feature Engineering
    # ------------------------------------------------------------
    print("\n[STEP 3/7] Feature Engineering (Lags, Rolling Stats, Interactions)...")
    engineered_df = engineer_features(encoded_df)

    # ------------------------------------------------------------
    # Step 4: Model Training & TimeSeriesSplit CV
    # ------------------------------------------------------------
    print("\n[STEP 4/7] Training & Cross-Validating Models (Model A vs Model B)...")
    train_results = train_all_models(engineered_df)
    all_results = train_results["all_results"]
    best_key = train_results["best_key"]
    best_info = train_results["best_info"]
    best_model = best_info["model"]
    test_engineered = train_results["test_df"]

    # ------------------------------------------------------------
    # Step 5: Evaluation & Deep Error Analysis
    # ------------------------------------------------------------
    print("\n[STEP 5/7] Evaluating Performance & Multi-Dimensional Error Analysis...")
    y_pred_best = best_info["predictions"]
    eval_results = run_evaluation(
        all_results=all_results,
        test_df=test_engineered,
        raw_test_df=raw_test_df,
        best_key=best_key,
        best_predictions=y_pred_best,
    )

    # ------------------------------------------------------------
    # Step 6: Explainability & SHAP Analysis
    # ------------------------------------------------------------
    print("\n[STEP 6/7] Running Explainability & Feature Attribution...")
    X_test = test_engineered[FEATURES_MODEL_A].values
    y_test = test_engineered[TARGET_COL].values
    explain_results = run_explainability(
        best_model=best_model,
        X_test=X_test,
        y_test=y_test,
        feature_names=FEATURES_MODEL_A,
        best_key=best_key,
        test_df=test_engineered,
    )

    # ------------------------------------------------------------
    # Step 7: Prediction, Shortfall, Risk & Recommendations
    # ------------------------------------------------------------
    print("\n[STEP 7/7] Generating Predictions, Shortfall, Risk & Recommendations...")
    pred_df = generate_predictions_pipeline(
        engineered_df=engineered_df,
        raw_df=raw_df,
        model=best_model,
        model_name=best_key,
        features=FEATURES_MODEL_A,
    )

    # ------------------------------------------------------------
    # Final Summary Checklist
    # ------------------------------------------------------------
    print("\n" + "="*75)
    print("  PIPELINE EXECUTION COMPLETE — ALL DELIVERABLES GENERATED")
    print("="*75)
    print(f"  1. Prototype Dataset:       {RAW_CSV}")
    print(f"  2. Engineered Dataset:      data/processed/production_engineered.csv")
    print(f"  3. Production Model:        models/production_model.pkl")
    print(f"  4. Label Encoders:          models/encoders.pkl")
    print(f"  5. Model Metrics JSON:      outputs/model_metrics.json")
    print(f"  6. Model Comparison Table:  outputs/model_comparison.csv")
    print(f"  7. Error Analysis Report:   outputs/error_analysis.csv")
    print(f"  8. Feature Importance:      outputs/feature_importance.csv")
    print(f"  9. Predictions & Shortfall: outputs/production_predictions.csv")
    print("="*75 + "\n")


if __name__ == "__main__":
    main()

