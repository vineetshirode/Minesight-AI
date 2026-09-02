"""
train.py — Model Training & Cross-Validation
==============================================
SIH 2026 — Model 2: Production Intelligence

Trains 6 model configurations:
  - Model A (with Production Target) × {Linear Regression, Random Forest, Gradient Boosting}
  - Model B (without Production Target) × {Linear Regression, Random Forest, Gradient Boosting}

Uses TimeSeriesSplit for cross-validation on the training set.
Saves all trained models and identifies the best performer.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_validate
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    make_scorer,
)

from src.config import (
    FEATURES_MODEL_A,
    FEATURES_MODEL_B,
    TARGET_COL,
    DATE_COL,
    TRAIN_END_DATE,
    TEST_START_DATE,
    MODELS_DIR,
    OUTPUTS_DIR,
    RANDOM_STATE,
    RF_PARAMS,
    GB_PARAMS,
    CV_N_SPLITS,
)


def mape(y_true, y_pred):
    """Mean Absolute Percentage Error."""
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def get_models():
    """Return dict of model name → model instance."""
    return {
        "Linear_Regression": LinearRegression(),
        "Random_Forest": RandomForestRegressor(**RF_PARAMS),
        "Gradient_Boosting": GradientBoostingRegressor(**GB_PARAMS),
    }


def train_and_evaluate(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    features: list,
    experiment_name: str,
) -> dict:
    """
    Train all 3 models for a given feature set.

    Args:
        train_df: Training DataFrame
        test_df: Test DataFrame
        features: List of feature column names
        experiment_name: "Model_A" or "Model_B"

    Returns:
        Dict of results including metrics, trained models, and predictions
    """
    X_train = train_df[features].values
    y_train = train_df[TARGET_COL].values
    X_test = test_df[features].values
    y_test = test_df[TARGET_COL].values

    results = {}
    models = get_models()

    print(f"\n{'='*60}")
    print(f"  {experiment_name} — {len(features)} features")
    print(f"  Features: {features}")
    print(f"{'='*60}")

    for name, model in models.items():
        print(f"\n  Training {name}...")

        # ── TimeSeriesSplit cross-validation on training data ──
        tscv = TimeSeriesSplit(n_splits=CV_N_SPLITS)
        cv_scores = cross_validate(
            model, X_train, y_train,
            cv=tscv,
            scoring={
                "neg_mae": "neg_mean_absolute_error",
                "neg_rmse": make_scorer(
                    lambda y, yp: -np.sqrt(mean_squared_error(y, yp))
                ),
                "r2": "r2",
            },
            return_train_score=False,
        )

        cv_mae = -cv_scores["test_neg_mae"].mean()
        cv_r2 = cv_scores["test_r2"].mean()

        # ── Fit on full training data ──
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # ── Test metrics ──
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape_val = mape(y_test, y_pred)

        print(f"    CV MAE:   {cv_mae:.2f} tonnes")
        print(f"    CV R²:    {cv_r2:.4f}")
        print(f"    Test MAE: {mae:.2f} tonnes")
        print(f"    Test RMSE:{rmse:.2f} tonnes")
        print(f"    Test R²:  {r2:.4f}")
        print(f"    Test MAPE:{mape_val:.2f}%")

        # Save model
        model_key = f"{experiment_name}_{name}"
        model_path = os.path.join(MODELS_DIR, f"{model_key}.pkl")
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(model, model_path)

        results[name] = {
            "model": model,
            "model_path": model_path,
            "predictions": y_pred,
            "metrics": {
                "MAE": round(mae, 2),
                "RMSE": round(rmse, 2),
                "R2": round(r2, 4),
                "MAPE": round(mape_val, 2),
                "CV_MAE": round(cv_mae, 2),
                "CV_R2": round(cv_r2, 4),
            },
        }

    return results


def find_best_model(all_results: dict) -> tuple:
    """
    Find the best model across all experiments.

    Selection criteria: lowest test MAE (production prediction accuracy).

    Returns:
        (best_key, best_info) where best_key = "Model_A_Gradient_Boosting" etc.
    """
    best_key = None
    best_mae = float("inf")
    best_info = None

    for experiment, models in all_results.items():
        for model_name, info in models.items():
            mae = info["metrics"]["MAE"]
            if mae < best_mae:
                best_mae = mae
                best_key = f"{experiment}_{model_name}"
                best_info = info

    return best_key, best_info


def save_metrics(all_results: dict, best_key: str) -> str:
    """Save all model metrics to JSON."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    metrics_path = os.path.join(OUTPUTS_DIR, "model_metrics.json")

    output = {"best_model": best_key, "experiments": {}}
    for experiment, models in all_results.items():
        output["experiments"][experiment] = {}
        for model_name, info in models.items():
            output["experiments"][experiment][model_name] = info["metrics"]

    with open(metrics_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n[train] Saved metrics → {metrics_path}")
    return metrics_path


def save_best_model(best_key: str, best_info: dict) -> str:
    """Save the best model as production_model.pkl."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, "production_model.pkl")
    joblib.dump(best_info["model"], path)
    print(f"[train] Saved best model ({best_key}) → {path}")
    return path


def train_all_models(engineered_df: pd.DataFrame) -> dict:
    """
    Main training entry point.

    1. Splits engineered data into train/test
    2. Trains Model A (with target) and Model B (without target)
    3. Compares all 6 models
    4. Saves the best model

    Returns:
        Dict with all results, best model info, and split data
    """
    # Time-based split on engineered data
    train_df = engineered_df[
        engineered_df[DATE_COL] <= pd.Timestamp(TRAIN_END_DATE)
    ].copy()
    test_df = engineered_df[
        engineered_df[DATE_COL] >= pd.Timestamp(TEST_START_DATE)
    ].copy()

    # CRITICAL: Sort training data by DATE for TimeSeriesSplit CV.
    # The data comes sorted by Mine_ID then Date, which would cause
    # TimeSeriesSplit to split across mines instead of across time.
    train_df = train_df.sort_values(DATE_COL).reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    print(f"[train] Train: {len(train_df)} rows | Test: {len(test_df)} rows")

    # Train both experiments
    all_results = {}
    all_results["Model_A"] = train_and_evaluate(
        train_df, test_df, FEATURES_MODEL_A, "Model_A"
    )
    all_results["Model_B"] = train_and_evaluate(
        train_df, test_df, FEATURES_MODEL_B, "Model_B"
    )

    # Find best
    best_key, best_info = find_best_model(all_results)
    print(f"\n{'='*60}")
    print(f"  BEST MODEL: {best_key}")
    print(f"  MAE:  {best_info['metrics']['MAE']} tonnes")
    print(f"  RMSE: {best_info['metrics']['RMSE']} tonnes")
    print(f"  R²:   {best_info['metrics']['R2']}")
    print(f"  MAPE: {best_info['metrics']['MAPE']}%")
    print(f"{'='*60}")

    # Save
    save_metrics(all_results, best_key)
    save_best_model(best_key, best_info)

    return {
        "all_results": all_results,
        "best_key": best_key,
        "best_info": best_info,
        "train_df": train_df,
        "test_df": test_df,
    }


if __name__ == "__main__":
    from src.preprocessing import preprocess_pipeline
    from src.feature_engineering import engineer_features

    raw_df, encoded_df, encoders, _, _ = preprocess_pipeline()
    engineered_df = engineer_features(encoded_df)
    results = train_all_models(engineered_df)
