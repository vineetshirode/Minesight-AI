"""
evaluate.py — Evaluation, Error Analysis & Visualization
==========================================================
SIH 2026 — Model 2: Production Intelligence

Performs:
  1. Per-model metric comparison table
  2. Error analysis by mine, month, mine type, district
  3. Error analysis by operational condition bands
  4. Residual analysis and distribution
  5. Model comparison plots
  6. Saves error_analysis.csv and plots
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.config import (
    OUTPUTS_DIR,
    TARGET_COL,
    DATE_COL,
    MINE_ID_COL,
    MINE_NAME_COL,
)
from src.train import mape


def generate_comparison_table(all_results: dict) -> pd.DataFrame:
    """Create a DataFrame comparing all 6 models."""
    rows = []
    for experiment, models in all_results.items():
        for model_name, info in models.items():
            row = {"Experiment": experiment, "Model": model_name}
            row.update(info["metrics"])
            rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sort_values("MAE").reset_index(drop=True)

    print("\n" + "="*70)
    print("  MODEL COMPARISON TABLE")
    print("="*70)
    print(df.to_string(index=False))
    print()

    # Save
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    path = os.path.join(OUTPUTS_DIR, "model_comparison.csv")
    df.to_csv(path, index=False)
    print(f"[evaluate] Saved comparison table → {path}")

    return df


def error_analysis(
    test_df: pd.DataFrame,
    y_pred: np.ndarray,
    raw_test_df: pd.DataFrame,
    label: str = "Best_Model",
) -> pd.DataFrame:
    """
    Comprehensive error analysis by multiple dimensions.

    Args:
        test_df: Encoded test DataFrame
        y_pred: Model predictions
        raw_test_df: Raw (unencoded) test DataFrame for readable labels
        label: Model label for output naming
    """
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    y_true = test_df[TARGET_COL].values
    errors = y_true - y_pred
    abs_errors = np.abs(errors)

    # Build analysis DataFrame using raw labels
    analysis = raw_test_df[["Mine_ID", "Mine_Name", "District", "State",
                            "Mine_Type", "Date"]].copy()
    analysis["Actual"] = y_true
    analysis["Predicted"] = np.round(y_pred, 0)
    analysis["Error"] = np.round(errors, 0)
    analysis["Abs_Error"] = np.round(abs_errors, 0)
    analysis["Pct_Error"] = np.where(
        y_true != 0,
        np.round(abs_errors / y_true * 100, 2),
        0,
    )
    analysis["Month"] = pd.to_datetime(analysis["Date"]).dt.month

    # ── Save full error analysis ──
    path = os.path.join(OUTPUTS_DIR, "error_analysis.csv")
    analysis.to_csv(path, index=False)
    print(f"[evaluate] Saved error analysis → {path}")

    # ── Error by Mine ──
    print("\n" + "-"*50)
    print("  Error by Mine")
    print("-"*50)
    by_mine = (
        analysis.groupby("Mine_Name")
        .agg(
            MAE=("Abs_Error", "mean"),
            Median_Error=("Abs_Error", "median"),
            Max_Error=("Abs_Error", "max"),
            Mean_Pct_Error=("Pct_Error", "mean"),
            Count=("Abs_Error", "count"),
        )
        .round(1)
        .sort_values("MAE", ascending=False)
    )
    print(by_mine.to_string())

    # ── Error by Month ──
    print("\n" + "-"*50)
    print("  Error by Month")
    print("-"*50)
    by_month = (
        analysis.groupby("Month")
        .agg(
            MAE=("Abs_Error", "mean"),
            Median_Error=("Abs_Error", "median"),
            Mean_Pct_Error=("Pct_Error", "mean"),
            Count=("Abs_Error", "count"),
        )
        .round(1)
    )
    print(by_month.to_string())

    # ── Error by Mine Type ──
    print("\n" + "-"*50)
    print("  Error by Mine Type")
    print("-"*50)
    by_type = (
        analysis.groupby("Mine_Type")
        .agg(
            MAE=("Abs_Error", "mean"),
            Median_Error=("Abs_Error", "median"),
            Mean_Pct_Error=("Pct_Error", "mean"),
            Count=("Abs_Error", "count"),
        )
        .round(1)
    )
    print(by_type.to_string())

    # ── Error by District ──
    print("\n" + "-"*50)
    print("  Error by District")
    print("-"*50)
    by_district = (
        analysis.groupby("District")
        .agg(
            MAE=("Abs_Error", "mean"),
            Median_Error=("Abs_Error", "median"),
            Mean_Pct_Error=("Pct_Error", "mean"),
            Count=("Abs_Error", "count"),
        )
        .round(1)
        .sort_values("MAE", ascending=False)
    )
    print(by_district.to_string())

    # ── Error by Rainfall bands ──
    print("\n" + "-"*50)
    print("  Error by Rainfall Band")
    print("-"*50)
    analysis["Rainfall_Band"] = pd.cut(
        raw_test_df["Rainfall_mm"],
        bins=[0, 20, 50, 150, 500],
        labels=["Dry (0-20)", "Low (20-50)", "Moderate (50-150)", "Heavy (>150)"],
    )
    by_rain = (
        analysis.groupby("Rainfall_Band", observed=True)
        .agg(MAE=("Abs_Error", "mean"), Mean_Pct_Error=("Pct_Error", "mean"), Count=("Abs_Error", "count"))
        .round(1)
    )
    print(by_rain.to_string())

    # ── Error by Equipment Availability bands ──
    print("\n" + "-"*50)
    print("  Error by Equipment Availability Band")
    print("-"*50)
    analysis["Equip_Band"] = pd.cut(
        raw_test_df["Equipment_Availability_Pct"],
        bins=[0, 75, 85, 95, 100],
        labels=["Low (<75)", "Medium (75-85)", "Good (85-95)", "Excellent (>95)"],
    )
    by_equip = (
        analysis.groupby("Equip_Band", observed=True)
        .agg(MAE=("Abs_Error", "mean"), Mean_Pct_Error=("Pct_Error", "mean"), Count=("Abs_Error", "count"))
        .round(1)
    )
    print(by_equip.to_string())

    # ── Error by Blasting Delay ──
    print("\n" + "-"*50)
    print("  Error by Blasting Delay")
    print("-"*50)
    analysis["Blast_Group"] = np.where(
        raw_test_df["Blasting_Delay_Days"] == 0, "No Delay", "Delay (>=1 day)"
    )
    by_blast = (
        analysis.groupby("Blast_Group")
        .agg(MAE=("Abs_Error", "mean"), Mean_Pct_Error=("Pct_Error", "mean"), Count=("Abs_Error", "count"))
        .round(1)
    )
    print(by_blast.to_string())

    return analysis


def plot_model_comparison(all_results: dict) -> str:
    """Generate model comparison bar charts."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Model Comparison — Model A vs Model B", fontsize=14, fontweight="bold")

    metrics_to_plot = ["MAE", "RMSE", "R2", "MAPE"]
    titles = [
        "MAE (Tonnes) — Lower is Better",
        "RMSE (Tonnes) — Lower is Better",
        "R² — Higher is Better",
        "MAPE (%) — Lower is Better",
    ]

    for idx, (metric, title) in enumerate(zip(metrics_to_plot, titles)):
        ax = axes[idx // 2][idx % 2]
        labels = []
        values = []
        colors = []

        for experiment, models in all_results.items():
            for model_name, info in models.items():
                labels.append(f"{experiment}\n{model_name.replace('_', ' ')}")
                values.append(info["metrics"][metric])
                colors.append("#2196F3" if experiment == "Model_A" else "#FF9800")

        bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=0.5)
        ax.set_title(title, fontsize=10)
        ax.tick_params(axis="x", labelsize=7)

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:.2f}",
                ha="center", va="bottom", fontsize=7,
            )

    plt.tight_layout()
    path = os.path.join(OUTPUTS_DIR, "model_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[evaluate] Saved comparison plot → {path}")
    return path


def plot_error_distribution(y_true: np.ndarray, y_pred: np.ndarray, label: str) -> str:
    """Plot residual distribution and actual vs predicted scatter."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    errors = y_true - y_pred
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"Error Analysis — {label}", fontsize=13, fontweight="bold")

    # 1. Residual histogram
    ax = axes[0]
    ax.hist(errors, bins=30, color="#4CAF50", edgecolor="white", alpha=0.8)
    ax.axvline(0, color="red", linestyle="--", linewidth=1)
    ax.set_xlabel("Prediction Error (Actual - Predicted)")
    ax.set_ylabel("Frequency")
    ax.set_title("Residual Distribution")
    ax.text(0.05, 0.95, f"Mean: {errors.mean():.0f}\nStd: {errors.std():.0f}",
            transform=ax.transAxes, va="top", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    # 2. Actual vs Predicted scatter
    ax = axes[1]
    ax.scatter(y_true, y_pred, alpha=0.5, s=15, c="#2196F3", edgecolors="none")
    lims = [min(y_true.min(), y_pred.min()) * 0.9, max(y_true.max(), y_pred.max()) * 1.1]
    ax.plot(lims, lims, "r--", linewidth=1, label="Perfect prediction")
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("Actual Production (Tonnes)")
    ax.set_ylabel("Predicted Production (Tonnes)")
    ax.set_title("Actual vs Predicted")
    ax.legend(fontsize=8)

    # 3. Error by prediction magnitude
    ax = axes[2]
    pct_errors = np.where(y_true != 0, np.abs(errors) / y_true * 100, 0)
    ax.scatter(y_true, pct_errors, alpha=0.5, s=15, c="#FF5722", edgecolors="none")
    ax.set_xlabel("Actual Production (Tonnes)")
    ax.set_ylabel("Absolute % Error")
    ax.set_title("Error % vs Production Level")
    ax.axhline(5, color="green", linestyle="--", linewidth=0.8, alpha=0.7, label="5% threshold")
    ax.legend(fontsize=8)

    plt.tight_layout()
    path = os.path.join(OUTPUTS_DIR, f"error_distribution_{label}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[evaluate] Saved error distribution plot → {path}")
    return path


def plot_error_by_mine(analysis_df: pd.DataFrame) -> str:
    """Bar chart of MAE by mine."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    by_mine = (
        analysis_df.groupby("Mine_Name")["Abs_Error"]
        .mean()
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(by_mine.index, by_mine.values, color="#3F51B5", edgecolor="white")
    ax.set_xlabel("Mean Absolute Error (Tonnes)")
    ax.set_title("Prediction Error by Mine", fontsize=12, fontweight="bold")

    for bar, val in zip(bars, by_mine.values):
        ax.text(val + 10, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}", va="center", fontsize=8)

    plt.tight_layout()
    path = os.path.join(OUTPUTS_DIR, "error_by_mine.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[evaluate] Saved error-by-mine plot → {path}")
    return path


def plot_error_by_month(analysis_df: pd.DataFrame) -> str:
    """Line chart of MAE by month."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    by_month = (
        analysis_df.groupby("Month")["Abs_Error"]
        .mean()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(by_month.index, by_month.values, "o-", color="#E91E63", linewidth=2, markersize=6)
    ax.set_xlabel("Month")
    ax.set_ylabel("Mean Absolute Error (Tonnes)")
    ax.set_title("Prediction Error by Month", fontsize=12, fontweight="bold")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUTS_DIR, "error_by_month.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[evaluate] Saved error-by-month plot → {path}")
    return path


def run_evaluation(
    all_results: dict,
    test_df: pd.DataFrame,
    raw_test_df: pd.DataFrame,
    best_key: str,
    best_predictions: np.ndarray,
) -> dict:
    """
    Run the full evaluation pipeline.

    Returns:
        Dict with comparison table, analysis DataFrame, and plot paths
    """
    print("\n" + "="*60)
    print("  EVALUATION & ERROR ANALYSIS")
    print("="*60)

    # Model comparison table
    comparison_df = generate_comparison_table(all_results)

    # Detailed error analysis for best model
    analysis_df = error_analysis(test_df, best_predictions, raw_test_df, best_key)

    # Plots
    plot_model_comparison(all_results)
    plot_error_distribution(
        test_df[TARGET_COL].values, best_predictions, best_key
    )
    plot_error_by_mine(analysis_df)
    plot_error_by_month(analysis_df)

    return {
        "comparison_df": comparison_df,
        "analysis_df": analysis_df,
    }


if __name__ == "__main__":
    print("Run via run_pipeline.py for full evaluation.")
