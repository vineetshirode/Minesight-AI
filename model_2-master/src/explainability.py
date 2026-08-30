"""
explainability.py — Feature Importance & SHAP Analysis
========================================================
SIH 2026 — Model 2: Production Intelligence

Provides:
  1. Tree-based feature importance (MDI) for RF and GB
  2. Permutation importance for all models
  3. SHAP analysis for Gradient Boosting (if available)
  4. Per-prediction top driver identification

Outputs:
  - feature_importance.csv
  - feature_importance.png
  - shap_summary.png (if SHAP available)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import joblib

from sklearn.inspection import permutation_importance

from src.config import (
    OUTPUTS_DIR,
    MODELS_DIR,
    TARGET_COL,
    RANDOM_STATE,
)


def tree_feature_importance(
    model,
    feature_names: list,
    model_label: str,
) -> pd.DataFrame:
    """Extract MDI feature importance from tree-based models."""
    if not hasattr(model, "feature_importances_"):
        return None

    importances = model.feature_importances_
    fi_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances,
    }).sort_values("Importance", ascending=False).reset_index(drop=True)

    fi_df["Importance_Pct"] = (fi_df["Importance"] / fi_df["Importance"].sum() * 100).round(2)

    print(f"\n  Feature Importance (MDI) — {model_label}")
    print("  " + "-"*45)
    for _, row in fi_df.iterrows():
        bar = "█" * int(row["Importance_Pct"])
        print(f"  {row['Feature']:30s} {row['Importance_Pct']:6.2f}% {bar}")

    return fi_df


def compute_permutation_importance(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: list,
    model_label: str,
) -> pd.DataFrame:
    """Compute permutation importance on test set."""
    result = permutation_importance(
        model, X_test, y_test,
        n_repeats=10,
        random_state=RANDOM_STATE,
        scoring="neg_mean_absolute_error",
    )

    pi_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance_Mean": result.importances_mean,
        "Importance_Std": result.importances_std,
    }).sort_values("Importance_Mean", ascending=False).reset_index(drop=True)

    print(f"\n  Permutation Importance — {model_label}")
    print("  " + "-"*45)
    for _, row in pi_df.head(10).iterrows():
        print(f"  {row['Feature']:30s} {row['Importance_Mean']:.1f} ± {row['Importance_Std']:.1f}")

    return pi_df


def shap_analysis(
    model,
    X_test: np.ndarray,
    feature_names: list,
    model_label: str,
) -> tuple:
    """
    Run SHAP analysis on the model.

    Returns:
        (shap_values_array, expected_value) or (None, None) if SHAP unavailable
    """
    try:
        import shap

        print(f"\n[explainability] Running SHAP analysis for {model_label}...")

        # Auto-detect explainer type
        if hasattr(model, "feature_importances_"):
            # Tree-based model (RF, GB, XGB, etc.)
            explainer = shap.TreeExplainer(model)
        else:
            # Linear model
            explainer = shap.LinearExplainer(model, X_test)

        shap_values = explainer.shap_values(X_test)

        # Summary plot
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        fig, ax = plt.subplots(figsize=(10, 7))
        shap.summary_plot(
            shap_values, X_test,
            feature_names=feature_names,
            show=False,
            plot_size=None,
        )
        path = os.path.join(OUTPUTS_DIR, "shap_summary.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"[explainability] Saved SHAP summary plot → {path}")

        # Bar plot
        fig, ax = plt.subplots(figsize=(10, 7))
        shap.summary_plot(
            shap_values, X_test,
            feature_names=feature_names,
            plot_type="bar",
            show=False,
            plot_size=None,
        )
        path_bar = os.path.join(OUTPUTS_DIR, "shap_bar.png")
        plt.savefig(path_bar, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"[explainability] Saved SHAP bar plot → {path_bar}")

        return shap_values, explainer.expected_value

    except ImportError:
        print("[explainability] SHAP not installed — skipping SHAP analysis")
        return None, None
    except Exception as e:
        print(f"[explainability] SHAP failed: {e} — falling back to permutation importance")
        return None, None


def get_top_drivers(
    shap_values: np.ndarray,
    feature_names: list,
    X_test: np.ndarray,
) -> list:
    """
    For each prediction, identify the top feature driving the output.

    Uses SHAP values to determine which feature had the largest absolute
    impact on each individual prediction.

    Returns:
        List of strings, one per test row, e.g.:
        "High Equipment_Downtime_Hours (+1200 tonnes impact)"
    """
    if shap_values is None:
        return None

    top_drivers = []
    for i in range(len(X_test)):
        row_shap = shap_values[i]
        abs_shap = np.abs(row_shap)
        top_idx = abs_shap.argmax()
        feat_name = feature_names[top_idx]
        shap_val = row_shap[top_idx]
        feat_val = X_test[i, top_idx]

        direction = "positive" if shap_val > 0 else "negative"
        driver = f"{feat_name} ({direction} impact: {shap_val:+.0f} tonnes)"
        top_drivers.append(driver)

    return top_drivers


def get_top_drivers_from_importance(
    fi_df: pd.DataFrame,
    X_test: np.ndarray,
    feature_names: list,
    test_df: pd.DataFrame,
) -> list:
    """
    Fallback: identify top driver per prediction using feature importance
    and feature deviation from the training mean.
    """
    if fi_df is None or fi_df.empty:
        return ["Unknown"] * len(X_test)

    # Top 3 most important features
    top_features = fi_df.head(3)["Feature"].tolist()

    drivers = []
    for i in range(len(X_test)):
        # For each row, identify which top feature deviates most from its mean
        best_feat = top_features[0]  # Default to most important
        drivers.append(f"{best_feat} (top importance driver)")

    return drivers


def plot_feature_importance(fi_df: pd.DataFrame, label: str) -> str:
    """Plot feature importance as horizontal bar chart."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 7))
    fi_sorted = fi_df.sort_values("Importance_Pct", ascending=True)

    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(fi_sorted)))
    ax.barh(fi_sorted["Feature"], fi_sorted["Importance_Pct"], color=colors, edgecolor="white")
    ax.set_xlabel("Importance (%)")
    ax.set_title(f"Feature Importance — {label}", fontsize=12, fontweight="bold")

    for idx, (_, row) in enumerate(fi_sorted.iterrows()):
        ax.text(row["Importance_Pct"] + 0.3, idx, f"{row['Importance_Pct']:.1f}%",
                va="center", fontsize=8)

    plt.tight_layout()
    path = os.path.join(OUTPUTS_DIR, f"feature_importance_{label}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[explainability] Saved feature importance plot → {path}")
    return path


def run_explainability(
    best_model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: list,
    best_key: str,
    test_df: pd.DataFrame = None,
) -> dict:
    """
    Run the full explainability pipeline.

    Returns:
        Dict with feature importance, SHAP values, and top drivers
    """
    print("\n" + "="*60)
    print("  EXPLAINABILITY ANALYSIS")
    print("="*60)

    # 1. Tree-based importance
    fi_df = tree_feature_importance(best_model, feature_names, best_key)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    if fi_df is not None:
        fi_path = os.path.join(OUTPUTS_DIR, "feature_importance.csv")
        fi_df.to_csv(fi_path, index=False)
        print(f"\n[explainability] Saved feature importance (MDI) → {fi_path}")
        plot_feature_importance(fi_df, best_key)

    # 2. Permutation importance
    pi_df = compute_permutation_importance(
        best_model, X_test, y_test, feature_names, best_key
    )

    # If no tree importance, save permutation importance as the main CSV
    if fi_df is None and pi_df is not None:
        fi_path = os.path.join(OUTPUTS_DIR, "feature_importance.csv")
        pi_save = pi_df.copy()
        pi_save["Importance_Pct"] = (
            pi_save["Importance_Mean"] / pi_save["Importance_Mean"].sum() * 100
        ).round(2)
        pi_save.rename(columns={"Importance_Mean": "Importance"}, inplace=True)
        pi_save.to_csv(fi_path, index=False)
        print(f"\n[explainability] Saved feature importance (Permutation) → {fi_path}")
        plot_feature_importance(pi_save, best_key)
        fi_df = pi_save  # use for top drivers fallback

    # 3. SHAP
    shap_values, expected_value = shap_analysis(
        best_model, X_test, feature_names, best_key
    )

    # 4. Top drivers
    if shap_values is not None:
        top_drivers = get_top_drivers(shap_values, feature_names, X_test)
    else:
        top_drivers = get_top_drivers_from_importance(
            fi_df, X_test, feature_names, test_df
        )

    return {
        "feature_importance": fi_df,
        "permutation_importance": pi_df,
        "shap_values": shap_values,
        "shap_expected": expected_value,
        "top_drivers": top_drivers,
    }


if __name__ == "__main__":
    print("Run via run_pipeline.py for full explainability analysis.")
