"""
feature_engineering.py — Feature Engineering Pipeline
======================================================
SIH 2026 — Model 2: Production Intelligence

Engineers the following features (all leakage-safe):

TEMPORAL:
  - Month (1–12): seasonal signal
  - Quarter (1–4): coarser seasonal signal

LAG FEATURES (per mine, using only past data):
  - Production_Lag_1: previous month's actual production
  - Equip_Avail_Lag_1: previous month's equipment availability
  - Downtime_Lag_1: previous month's equipment downtime

ROLLING FEATURES (per mine, using only past data):
  - Production_Rolling_3: 3-month rolling mean of actual production
  - Equip_Avail_Rolling_3: 3-month rolling mean of equipment availability

INTERACTION FEATURES:
  - Downtime_Per_Working_Day: Equipment_Downtime / Working_Days
  - Effective_Capacity: Equipment_Availability × Working_Days / 100

DATA LEAKAGE PREVENTION:
  - All lag/rolling features use shift(1) → only past values
  - NaN values (first month per mine) are filled with that mine's
    TRAINING-PERIOD mean (not overall mean, not test-period data)
  - Rolling windows use min_periods=1 to avoid NaN propagation
"""

import os
import pandas as pd
import numpy as np

from src.config import (
    DATE_COL,
    MINE_ID_COL,
    TARGET_COL,
    DATA_PROCESSED_DIR,
    PROCESSED_CSV,
)


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add Month and Quarter columns from the Date column."""
    df = df.copy()
    df["Month"] = df[DATE_COL].dt.month
    df["Quarter"] = df[DATE_COL].dt.quarter
    return df


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add lagged features per mine.

    Uses shift(1) to ensure only past data is used.
    """
    df = df.copy()
    df = df.sort_values([MINE_ID_COL, DATE_COL]).reset_index(drop=True)

    # Group by mine and shift
    grp = df.groupby(MINE_ID_COL)

    df["Production_Lag_1"] = grp[TARGET_COL].shift(1)
    df["Equip_Avail_Lag_1"] = grp["Equipment_Availability_Pct"].shift(1)
    df["Downtime_Lag_1"] = grp["Equipment_Downtime_Hours"].shift(1)

    return df


def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 3-month rolling averages per mine.

    Uses shift(1) + rolling(3) to ensure no data leakage:
      rolling is calculated on shifted (past-only) values.
    """
    df = df.copy()
    df = df.sort_values([MINE_ID_COL, DATE_COL]).reset_index(drop=True)

    grp = df.groupby(MINE_ID_COL)

    # Shifted series (past only)
    shifted_prod = grp[TARGET_COL].shift(1)
    shifted_avail = grp["Equipment_Availability_Pct"].shift(1)

    # Rolling mean on shifted series (min_periods=1 to reduce NaN)
    df["Production_Rolling_3"] = (
        shifted_prod
        .groupby(df[MINE_ID_COL])
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )
    df["Equip_Avail_Rolling_3"] = (
        shifted_avail
        .groupby(df[MINE_ID_COL])
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    return df


def add_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived interaction features."""
    df = df.copy()
    df["Downtime_Per_Working_Day"] = (
        df["Equipment_Downtime_Hours"] / df["Working_Days"]
    ).round(2)

    df["Effective_Capacity"] = (
        df["Equipment_Availability_Pct"] * df["Working_Days"] / 100
    ).round(2)

    return df


def fill_lag_nans(
    df: pd.DataFrame,
    train_end_date: str = None,
) -> pd.DataFrame:
    """
    Fill NaN values in lag/rolling features.

    Strategy: fill with that mine's TRAINING-PERIOD mean.
    This prevents data leakage from the test set.

    Args:
        df: Full DataFrame (train + test, sorted by Mine_ID then Date)
        train_end_date: Cutoff date string (e.g. '2024-12-31').
                        Only data on or before this date is used for means.
                        If None, uses all data.
    """
    df = df.copy()
    lag_cols = [
        "Production_Lag_1",
        "Equip_Avail_Lag_1",
        "Downtime_Lag_1",
        "Production_Rolling_3",
        "Equip_Avail_Rolling_3",
    ]

    if train_end_date is not None:
        train_subset = df[df[DATE_COL] <= pd.Timestamp(train_end_date)]
    else:
        train_subset = df

    # Compute per-mine training means
    mine_means = train_subset.groupby(MINE_ID_COL)[lag_cols].mean()
    # Global fallback in case a mine has no training data at all
    global_means = train_subset[lag_cols].mean()

    for col in lag_cols:
        for mine_id in df[MINE_ID_COL].unique():
            mask = (df[MINE_ID_COL] == mine_id) & df[col].isna()
            if mask.any():
                if mine_id in mine_means.index:
                    fill_val = mine_means.loc[mine_id, col]
                else:
                    fill_val = global_means[col]
                df.loc[mask, col] = fill_val

    return df


def engineer_features(df: pd.DataFrame, train_size: int = 504) -> pd.DataFrame:
    """
    Full feature engineering pipeline.

    Args:
        df: Encoded DataFrame (sorted by Mine_ID, Date)
        train_size: Number of training rows (not used for NaN filling;
                    we use config.TRAIN_END_DATE for date-based filtering)

    Returns:
        DataFrame with all engineered features
    """
    from src.config import TRAIN_END_DATE

    print("[feature_engineering] Adding temporal features...")
    df = add_temporal_features(df)

    print("[feature_engineering] Adding lag features (shift=1, no leakage)...")
    df = add_lag_features(df)

    print("[feature_engineering] Adding rolling features (window=3, no leakage)...")
    df = add_rolling_features(df)

    print("[feature_engineering] Adding interaction features...")
    df = add_interaction_features(df)

    print("[feature_engineering] Filling NaN in lag features (train-period means)...")
    df = fill_lag_nans(df, train_end_date=TRAIN_END_DATE)

    # Verify no NaN remaining
    nan_count = df.isnull().sum().sum()
    if nan_count > 0:
        print(f"[WARNING] {nan_count} NaN values remain after filling!")
        print(df.isnull().sum()[df.isnull().sum() > 0])
    else:
        print("[feature_engineering] No NaN values [OK]")

    # Save processed data
    os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
    df.to_csv(PROCESSED_CSV, index=False)
    print(f"[feature_engineering] Saved engineered data → {PROCESSED_CSV}")

    return df


if __name__ == "__main__":
    from src.preprocessing import preprocess_pipeline
    raw_df, encoded_df, encoders, _, _ = preprocess_pipeline()
    engineered_df = engineer_features(encoded_df)
    print(f"\nFinal shape: {engineered_df.shape}")
    print(f"Columns: {list(engineered_df.columns)}")
    print(f"\nSample (first 3 rows):\n{engineered_df.head(3).to_string()}")

