"""
preprocessing.py — Data Loading, Cleaning & Encoding
=====================================================
SIH 2026 — Model 2: Production Intelligence

Handles:
  1. Load raw CSV and parse dates
  2. Validate data quality (no missing values, correct shape)
  3. Label-encode categorical features
  4. Time-based train/test split (2022–2024 / 2025)
  5. Save encoder artifacts for reproducibility
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

from src.config import (
    RAW_CSV,
    DATA_PROCESSED_DIR,
    MODELS_DIR,
    TRAIN_END_DATE,
    TEST_START_DATE,
    CATEGORICAL_COLS,
    DATE_COL,
    TARGET_COL,
    MINE_ID_COL,
)


def load_raw_data(path: str = RAW_CSV) -> pd.DataFrame:
    """Load the raw CSV and parse the Date column."""
    df = pd.read_csv(path, parse_dates=[DATE_COL])
    df = df.sort_values([MINE_ID_COL, DATE_COL]).reset_index(drop=True)
    print(f"[preprocessing] Loaded {len(df)} rows from {path}")
    return df


def validate_data(df: pd.DataFrame) -> None:
    """Run sanity checks on the loaded dataset."""
    assert df.shape[0] == 672, f"Expected 672 rows, got {df.shape[0]}"
    assert df.shape[1] == 13, f"Expected 13 columns, got {df.shape[1]}"
    assert df.isnull().sum().sum() == 0, "Found missing values!"
    assert df.duplicated().sum() == 0, "Found duplicate rows!"
    assert df[MINE_ID_COL].nunique() == 14, "Expected 14 unique mines"
    print("[preprocessing] Data validation passed [OK]")


def encode_categoricals(
    df: pd.DataFrame,
    fit: bool = True,
    encoders: dict = None,
) -> tuple:
    """
    Label-encode categorical columns.

    Args:
        df: DataFrame to encode
        fit: If True, fit new encoders. If False, use provided encoders.
        encoders: Pre-fitted encoders (required when fit=False)

    Returns:
        (encoded_df, encoders_dict)
    """
    df = df.copy()
    if encoders is None:
        encoders = {}

    for col in CATEGORICAL_COLS:
        if fit:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            encoders[col] = le
        else:
            le = encoders[col]
            df[col] = le.transform(df[col])

    return df, encoders


def save_encoders(encoders: dict) -> str:
    """Save label encoders to models/ directory."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, "encoders.pkl")
    joblib.dump(encoders, path)
    print(f"[preprocessing] Saved encoders → {path}")
    return path


def load_encoders() -> dict:
    """Load saved label encoders."""
    path = os.path.join(MODELS_DIR, "encoders.pkl")
    return joblib.load(path)


def time_based_split(df: pd.DataFrame) -> tuple:
    """
    Split dataset chronologically.

    Training: 2022-01 to 2024-12 (504 rows)
    Testing:  2025-01 to 2025-12 (168 rows)

    Returns:
        (train_df, test_df)
    """
    train_mask = df[DATE_COL] <= pd.Timestamp(TRAIN_END_DATE)
    test_mask = df[DATE_COL] >= pd.Timestamp(TEST_START_DATE)

    train_df = df[train_mask].copy().reset_index(drop=True)
    test_df = df[test_mask].copy().reset_index(drop=True)

    assert len(train_df) == 504, f"Expected 504 train rows, got {len(train_df)}"
    assert len(test_df) == 168, f"Expected 168 test rows, got {len(test_df)}"

    print(f"[preprocessing] Train: {len(train_df)} rows "
          f"({train_df[DATE_COL].min().date()} to {train_df[DATE_COL].max().date()})")
    print(f"[preprocessing] Test:  {len(test_df)} rows "
          f"({test_df[DATE_COL].min().date()} to {test_df[DATE_COL].max().date()})")

    return train_df, test_df


def preprocess_pipeline(raw_path: str = RAW_CSV) -> tuple:
    """
    Full preprocessing pipeline.

    Returns:
        (raw_df, encoded_df, encoders, train_df, test_df)
    """
    # Load
    raw_df = load_raw_data(raw_path)
    validate_data(raw_df)

    # Keep a copy before encoding (for error analysis / reporting)
    raw_df_copy = raw_df.copy()

    # Encode
    encoded_df, encoders = encode_categoricals(raw_df)
    save_encoders(encoders)

    # Split
    train_df, test_df = time_based_split(encoded_df)

    return raw_df_copy, encoded_df, encoders, train_df, test_df


if __name__ == "__main__":
    raw_df, encoded_df, encoders, train_df, test_df = preprocess_pipeline()
    print(f"\nEncoded columns: {list(encoded_df.columns)}")
    print(f"Encoder mappings:")
    for col, le in encoders.items():
        print(f"  {col}: {dict(zip(le.classes_, le.transform(le.classes_)))}")
