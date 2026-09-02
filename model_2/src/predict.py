"""
predict.py — Production Prediction, Shortfall, Risk & Output Generation
========================================================================
SIH 2026 — Model 2: Production Intelligence
MOIL Ltd. / Ministry of Steel

Generates the comprehensive final predictions CSV on the holdout test set (2025).
Computes:
  1. Predicted Production (Tonnes)
  2. Prediction Error & Absolute Error
  3. Shortfall (Tonnes) & Shortfall %
  4. Surplus (Tonnes) if production exceeds target
  5. Configurable 3-tier Risk Level (LOW / MEDIUM / HIGH)
  6. Per-sample Top Driver Attribution (via SHAP / Importance)
  7. Actionable Decision-Support Recommendations

Outputs:
  - outputs/production_predictions.csv
"""

import os
import joblib
import numpy as np
import pandas as pd

from src.config import (
    MODELS_DIR,
    OUTPUTS_DIR,
    TARGET_COL,
    PRODUCTION_TARGET_COL,
    DATE_COL,
    MINE_ID_COL,
    MINE_NAME_COL,
    DISTRICT_COL,
    STATE_COL,
    MINE_TYPE_COL,
    FEATURES_MODEL_A,
    FEATURES_MODEL_B,
    RISK_THRESHOLDS,
    TEST_START_DATE,
)
from src.recommendations import add_recommendations


def classify_risk(shortfall_pct: float, thresholds: dict = RISK_THRESHOLDS) -> str:
    """
    Classify risk level based on shortfall percentage of production target.

    Configurable thresholds (from config.py):
        - LOW:    shortfall_pct < 5.0%
        - MEDIUM: 5.0% <= shortfall_pct < 15.0%
        - HIGH:   shortfall_pct >= 15.0%
    """
    if shortfall_pct < thresholds["LOW"]:
        return "LOW"
    elif shortfall_pct < thresholds["MEDIUM"]:
        return "MEDIUM"
    else:
        return "HIGH"


def generate_predictions_pipeline(
    engineered_df: pd.DataFrame,
    raw_df: pd.DataFrame,
    model=None,
    model_name: str = "Model_A_Gradient_Boosting",
    features: list = None,
) -> pd.DataFrame:
    """
    Execute full prediction, shortfall, risk classification and recommendation pipeline.

    Args:
        engineered_df: Processed DataFrame with all engineered features
        raw_df: Original unencoded DataFrame for human-readable labels
        model: Trained model instance (or loads from models/production_model.pkl)
        model_name: Name of model for reporting
        features: Feature list to use (defaults to FEATURES_MODEL_A)

    Returns:
        pd.DataFrame containing all detailed prediction and operational columns.
    """
    if features is None:
        features = FEATURES_MODEL_A

    if model is None:
        model_path = os.path.join(MODELS_DIR, "production_model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Run train.py first.")
        model = joblib.load(model_path)

    # Filter to test set (2025)
    test_mask = engineered_df[DATE_COL] >= pd.Timestamp(TEST_START_DATE)
    test_engineered = engineered_df[test_mask].copy().reset_index(drop=True)
    test_raw = raw_df[test_mask].copy().reset_index(drop=True)

    X_test = test_engineered[features].values
    y_true = test_engineered[TARGET_COL].values

    # 1. Model Inference
    y_pred = model.predict(X_test)
    y_pred = np.maximum(0, y_pred)  # Production cannot be negative

    # 2. Base DataFrame with Metadata
    results = pd.DataFrame()
    results["Mine_ID"] = test_raw[MINE_ID_COL]
    results["Mine_Name"] = test_raw[MINE_NAME_COL]
    results["District"] = test_raw[DISTRICT_COL]
    results["State"] = test_raw[STATE_COL]
    results["Mine_Type"] = test_raw[MINE_TYPE_COL]
    results["Date"] = test_raw[DATE_COL].dt.strftime("%Y-%m")

    # 3. Targets and Predictions
    results["Production_Target_Tonnes"] = test_raw[PRODUCTION_TARGET_COL]
    results["Actual_Production_Tonnes"] = np.round(y_true, 1)
    results["Predicted_Production_Tonnes"] = np.round(y_pred, 1)

    # 4. Error Metrics
    results["Prediction_Error_Tonnes"] = np.round(y_true - y_pred, 1)
    results["Absolute_Error_Tonnes"] = np.round(np.abs(y_true - y_pred), 1)

    # 5. Shortfall and Surplus Calculation
    target_vals = results["Production_Target_Tonnes"].values
    shortfall_vals = np.maximum(0, target_vals - y_pred)
    surplus_vals = np.maximum(0, y_pred - target_vals)
    shortfall_pcts = np.where(
        target_vals > 0,
        (shortfall_vals / target_vals) * 100,
        0.0
    )

    results["Predicted_Shortfall_Tonnes"] = np.round(shortfall_vals, 1)
    results["Shortfall_Pct"] = np.round(shortfall_pcts, 2)
    results["Predicted_Surplus_Tonnes"] = np.round(surplus_vals, 1)

    # 6. Risk Level Assignment
    results["Risk_Level"] = [classify_risk(pct) for pct in results["Shortfall_Pct"]]

    # 7. Identify Top Driver per Sample (Tree Feature Importance or Permutation)
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        top_feature_idx = np.argmax(importances)
        top_driver_name = features[top_feature_idx]
    else:
        top_driver_name = "Operational Capacity"

    # Row-specific driver heuristic based on dominant negative constraint
    row_drivers = []
    for idx, row in test_raw.iterrows():
        if row["Equipment_Availability_Pct"] < 85.0:
            row_drivers.append("Low Equipment Availability")
        elif row["Equipment_Downtime_Hours"] > 60.0:
            row_drivers.append("High Equipment Downtime")
        elif row["Blasting_Delay_Days"] >= 2:
            row_drivers.append("Blasting Delays")
        elif row["Rainfall_mm"] > 150.0:
            row_drivers.append("Heavy Rainfall")
        else:
            row_drivers.append(top_driver_name)

    results["Top_Driver"] = row_drivers

    # Attach operational columns for recommendation engine
    results["Equipment_Availability_Pct"] = test_raw["Equipment_Availability_Pct"]
    results["Equipment_Downtime_Hours"] = test_raw["Equipment_Downtime_Hours"]
    results["Rainfall_mm"] = test_raw["Rainfall_mm"]
    results["Blasting_Delay_Days"] = test_raw["Blasting_Delay_Days"]
    results["Working_Days"] = test_raw["Working_Days"]

    # 8. Generate Actionable Recommendations
    results = add_recommendations(results)

    # Save output
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    out_csv = os.path.join(OUTPUTS_DIR, "production_predictions.csv")
    results.to_csv(out_csv, index=False)
    print(f"\n[predict] Generated {len(results)} predictions → {out_csv}")
    print(f"  Risk distribution in 2025 Test Set:")
    print(f"    LOW:    {(results['Risk_Level'] == 'LOW').sum()} months")
    print(f"    MEDIUM: {(results['Risk_Level'] == 'MEDIUM').sum()} months")
    print(f"    HIGH:   {(results['Risk_Level'] == 'HIGH').sum()} months")

    return results


if __name__ == "__main__":
    from src.preprocessing import preprocess_pipeline
    from src.feature_engineering import engineer_features
    from src.train import train_all_models

    raw_df, encoded_df, encoders, _, _ = preprocess_pipeline()
    engineered_df = engineer_features(encoded_df)
    train_results = train_all_models(engineered_df)
    best_model = train_results["best_info"]["model"]

    pred_df = generate_predictions_pipeline(
        engineered_df=engineered_df,
        raw_df=raw_df,
        model=best_model,
        model_name=train_results["best_key"],
    )
