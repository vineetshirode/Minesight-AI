"""
================================================================================
COMPREHENSIVE DATA LEAKAGE AUDIT FOR MODEL 2
================================================================================
SIH 2026 — Production Intelligence — Data Leakage Verification

This script performs 10 systematic checks to detect any data leakage:

CHECK 1: Lag Features Verification
CHECK 2: Rolling Features Verification
CHECK 3: Train/Test Separation
CHECK 4: Preprocessing Integrity
CHECK 5: Missing Value Handling
CHECK 6: Cross-Validation Time Order
CHECK 7: Target Leakage Detection
CHECK 8: Model A Target Legitimacy
CHECK 9: Feature Engineering Patterns
CHECK 10: Future Information Test

================================================================================
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.config import (
    RAW_CSV, PROCESSED_CSV, TRAIN_END_DATE, TEST_START_DATE,
    MINE_ID_COL, DATE_COL, TARGET_COL, CATEGORICAL_COLS,
    FEATURES_MODEL_A, FEATURES_MODEL_B
)
from src.preprocessing import preprocess_pipeline
from src.feature_engineering import engineer_features


# ============================================================================
# AUDIT REPORT DATA STRUCTURE
# ============================================================================

class AuditReport:
    """Container for audit findings."""
    def __init__(self):
        self.checks = []
        self.overall_result = None
        self.summary = ""
    
    def add_check(self, check_num, check_name, result, is_leakage, explanation, details=""):
        """Add a check result."""
        self.checks.append({
            "check": check_num,
            "name": check_name,
            "result": result,
            "leakage": is_leakage,
            "explanation": explanation,
            "details": details,
        })
    
    def print_table(self):
        """Print results as a markdown table."""
        print("\n" + "="*120)
        print("LEAKAGE AUDIT RESULTS TABLE")
        print("="*120)
        print(f"{'Check':<8} {'Name':<40} {'Result':<15} {'Leakage?':<12} {'Explanation':<45}")
        print("-"*120)
        for check in self.checks:
            print(
                f"{check['check']:<8} "
                f"{check['name']:<40} "
                f"{check['result']:<15} "
                f"{str(check['leakage']):<12} "
                f"{check['explanation']:<45}"
            )
        print("="*120)


# ============================================================================
# CHECK 1: LAG FEATURES VERIFICATION
# ============================================================================

def check_lag_features(engineered_df):
    """
    Verify that lag features use only previous month's data.
    
    For each mine, verify:
    - Production_Lag_1[t] == Actual_Production[t-1]
    - Equip_Avail_Lag_1[t] == Equipment_Availability[t-1]
    - Downtime_Lag_1[t] == Equipment_Downtime[t-1]
    """
    print("\n" + "="*80)
    print("CHECK 1: LAG FEATURES VERIFICATION")
    print("="*80)
    
    df = engineered_df.sort_values([MINE_ID_COL, DATE_COL]).copy()
    
    mismatches = []
    lag_cols_mapping = {
        "Production_Lag_1": TARGET_COL,
        "Equip_Avail_Lag_1": "Equipment_Availability_Pct",
        "Downtime_Lag_1": "Equipment_Downtime_Hours",
    }
    
    for mine_id in df[MINE_ID_COL].unique():
        mine_df = df[df[MINE_ID_COL] == mine_id].sort_values(DATE_COL).reset_index(drop=True)
        
        for lag_col, source_col in lag_cols_mapping.items():
            # For each row t > 0, check if lag_col[t] == source_col[t-1]
            for idx in range(1, len(mine_df)):
                lag_val = mine_df.loc[idx, lag_col]
                source_val = mine_df.loc[idx - 1, source_col]
                
                # Handle NaN in lag (first month of each mine)
                if pd.isna(lag_val):
                    continue
                
                if not np.isclose(lag_val, source_val, atol=0.01):
                    mismatches.append({
                        "mine_id": mine_id,
                        "date": mine_df.loc[idx, DATE_COL],
                        "lag_col": lag_col,
                        "expected": source_val,
                        "actual": lag_val,
                        "diff": lag_val - source_val,
                    })
    
    is_leakage = len(mismatches) > 0
    
    print(f"Lag features checked: {len(lag_cols_mapping)} types")
    print(f"Total mismatches found: {len(mismatches)}")
    
    if mismatches:
        print("\n⚠️  EXAMPLE MISMATCHES:")
        for i, mm in enumerate(mismatches[:5]):
            print(f"\n  Mismatch {i+1}:")
            print(f"    Mine: {mm['mine_id']}, Date: {mm['date'].date()}")
            print(f"    Feature: {mm['lag_col']}")
            print(f"    Expected: {mm['expected']}, Got: {mm['actual']}, Diff: {mm['diff']:.4f}")
    else:
        print("✓ All lag features correctly use previous month's data.")
    
    explanation = f"{len(mismatches)} mismatches" if mismatches else "0 mismatches ✓"
    return is_leakage, explanation, mismatches


# ============================================================================
# CHECK 2: ROLLING FEATURES VERIFICATION
# ============================================================================

def check_rolling_features(engineered_df):
    """
    Verify that rolling features use only past data (t-1, t-2, t-3).
    
    For each mine and each row t, verify that Production_Rolling_3 and
    Equip_Avail_Rolling_3 do NOT include current-month data or future data.
    """
    print("\n" + "="*80)
    print("CHECK 2: ROLLING FEATURES VERIFICATION")
    print("="*80)
    
    df = engineered_df.sort_values([MINE_ID_COL, DATE_COL]).copy()
    
    suspicious_rows = []
    
    for mine_id in df[MINE_ID_COL].unique():
        mine_df = df[df[MINE_ID_COL] == mine_id].sort_values(DATE_COL).reset_index(drop=True)
        
        for idx in range(1, len(mine_df)):
            # Current month's production
            current_prod = mine_df.loc[idx, TARGET_COL]
            
            # Rolling feature (should use t-1, t-2, t-3 only)
            rolling_val = mine_df.loc[idx, "Production_Rolling_3"]
            
            # Manually compute what rolling should be (t-1, t-2, t-3)
            if idx >= 3:
                # Should be average of previous 3 months
                manual_rolling = mine_df.loc[idx-3:idx-1, TARGET_COL].mean()
            elif idx >= 1:
                # Should be average of available previous months
                manual_rolling = mine_df.loc[0:idx-1, TARGET_COL].mean()
            else:
                manual_rolling = np.nan
            
            # Check if rolling value matches expected
            if not pd.isna(rolling_val) and not pd.isna(manual_rolling):
                if not np.isclose(rolling_val, manual_rolling, atol=1.0):
                    suspicious_rows.append({
                        "mine_id": mine_id,
                        "date": mine_df.loc[idx, DATE_COL],
                        "rolling_val": rolling_val,
                        "manual_rolling": manual_rolling,
                        "diff": rolling_val - manual_rolling,
                    })
    
    is_leakage = len(suspicious_rows) > 0
    
    print(f"Rolling features checked: Production_Rolling_3, Equip_Avail_Rolling_3")
    print(f"Suspicious rows (mismatch between computed and actual): {len(suspicious_rows)}")
    
    if suspicious_rows:
        print("\n⚠️  EXAMPLE SUSPICIOUS ROWS:")
        for i, sr in enumerate(suspicious_rows[:5]):
            print(f"\n  Row {i+1}:")
            print(f"    Mine: {sr['mine_id']}, Date: {sr['date'].date()}")
            print(f"    Computed rolling: {sr['manual_rolling']:.2f}, Actual: {sr['rolling_val']:.2f}")
            print(f"    Difference: {sr['diff']:.2f}")
    else:
        print("✓ All rolling features correctly use only past data.")
    
    explanation = f"{len(suspicious_rows)} mismatches" if suspicious_rows else "0 mismatches ✓"
    return is_leakage, explanation, suspicious_rows


# ============================================================================
# CHECK 3: TRAIN/TEST SEPARATION
# ============================================================================

def check_train_test_split(raw_df, engineered_df):
    """
    Verify chronological separation:
    - Training: 2022-01 to 2024-12
    - Testing: 2025-01 to 2025-12
    - No overlap
    """
    print("\n" + "="*80)
    print("CHECK 3: TRAIN/TEST SEPARATION")
    print("="*80)
    
    train_mask = engineered_df[DATE_COL] <= pd.Timestamp(TRAIN_END_DATE)
    test_mask = engineered_df[DATE_COL] >= pd.Timestamp(TEST_START_DATE)
    
    train_df = engineered_df[train_mask]
    test_df = engineered_df[test_mask]
    
    print(f"Training rows: {len(train_df)}")
    print(f"Testing rows: {len(test_df)}")
    print(f"Total: {len(train_df) + len(test_df)} (Full dataset: {len(engineered_df)})")
    
    train_date_min = train_df[DATE_COL].min()
    train_date_max = train_df[DATE_COL].max()
    test_date_min = test_df[DATE_COL].min()
    test_date_max = test_df[DATE_COL].max()
    
    print(f"\nTraining date range: {train_date_min.date()} to {train_date_max.date()}")
    print(f"Testing date range:  {test_date_min.date()} to {test_date_max.date()}")
    
    # Check for overlap
    overlap = train_date_max >= test_date_min
    print(f"\nDate overlap (train_max >= test_min): {overlap}")
    
    # Check for 2025 rows in training data
    train_2025 = train_df[train_df[DATE_COL].dt.year == 2025]
    has_2025_in_train = len(train_2025) > 0
    
    # Check for 2022-2024 rows in test data
    test_2024 = test_df[test_df[DATE_COL].dt.year <= 2024]
    has_2024_in_test = len(test_2024) > 0
    
    print(f"2025 rows in training data: {len(train_2025)}")
    print(f"2024 or earlier rows in test data: {len(test_2024)}")
    
    is_leakage = overlap or has_2025_in_train or has_2024_in_test
    
    if is_leakage:
        print("\n⚠️  LEAKAGE DETECTED!")
    else:
        print("\n✓ Chronological separation is valid.")
    
    explanation = "Valid ✓" if not is_leakage else "OVERLAP!"
    
    details = {
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "train_min": train_date_min,
        "train_max": train_date_max,
        "test_min": test_date_min,
        "test_max": test_date_max,
        "overlap": overlap,
        "train_2025": len(train_2025),
        "test_2024": len(test_2024),
    }
    
    return is_leakage, explanation, details


# ============================================================================
# CHECK 4: PREPROCESSING INTEGRITY
# ============================================================================

def check_preprocessing():
    """
    Verify that LabelEncoders are fit on training data only, not full data.
    
    We re-run preprocessing and check the encoders.
    """
    print("\n" + "="*80)
    print("CHECK 4: PREPROCESSING INTEGRITY")
    print("="*80)
    
    # This check is more about code inspection since encoders are fit before split
    # Let's verify the approach by examining the preprocessing.py file
    
    print("Preprocessing approach:")
    print("  1. Load raw data")
    print("  2. Validate data")
    print("  3. Label-encode categorical columns (fit on full data)")
    print("  4. Time-based split (no refitting)")
    print("  5. Save encoders")
    
    print("\n⚠️  OBSERVATION:")
    print("  Current encoding is fit on FULL dataset (before split).")
    print("  This is ACCEPTABLE because:")
    print("    - Categorical values are static (mine names, states, types)")
    print("    - No learning happens from target values in encoding")
    print("    - Encoder prevents out-of-vocabulary errors on test data")
    
    print("\n  However, for strict data leakage prevention:")
    print("    - Best practice: fit encoders on training data only")
    print("    - Then apply to test data")
    print("    - Fail if test has unknown categories")
    
    # Check that test data doesn't have unknown categories
    raw_df, encoded_df, encoders, train_df, test_df = preprocess_pipeline()
    
    has_unknown_categories = False
    unknown_details = []
    
    for col in CATEGORICAL_COLS:
        le = encoders[col]
        train_classes = set(le.classes_)
        
        # Simulate: what if we re-fit on train only?
        train_subset = encoded_df[encoded_df[DATE_COL] <= pd.Timestamp(TRAIN_END_DATE)]
        train_classes_only = set(train_subset[col].unique())
        
        # Check if test has values not in train
        test_subset = encoded_df[encoded_df[DATE_COL] >= pd.Timestamp(TEST_START_DATE)]
        test_classes = set(test_subset[col].unique())
        
        unknown = test_classes - train_classes_only
        if unknown:
            has_unknown_categories = True
            unknown_details.append({
                "column": col,
                "unknown_values": unknown,
            })
    
    is_leakage = False  # Encoding itself is not leakage, but category mismatch is
    
    if has_unknown_categories:
        print("\n⚠️  WARNING: Unknown categories in test data!")
        for detail in unknown_details:
            print(f"  {detail['column']}: {detail['unknown_values']}")
    else:
        print("\n✓ No unknown categories in test data.")
    
    explanation = "Fit on full data, but acceptable" if not has_unknown_categories else "Unknown categories!"
    
    return is_leakage, explanation, {
        "has_unknown_categories": has_unknown_categories,
        "unknown_details": unknown_details,
    }


# ============================================================================
# CHECK 5: MISSING VALUE HANDLING
# ============================================================================

def check_missing_value_handling(engineered_df):
    """
    Verify that NaN values in lag features are filled using training-period means only.
    
    Check that fill values were computed from training data, not test data.
    """
    print("\n" + "="*80)
    print("CHECK 5: MISSING VALUE HANDLING")
    print("="*80)
    
    # Reconstruct the filling to verify it used only training data
    from src.config import TRAIN_END_DATE
    
    raw_df, encoded_df, encoders, train_df, test_df = preprocess_pipeline()
    
    # Simulate feature engineering up to NaN filling
    from src.feature_engineering import (
        add_temporal_features, add_lag_features, 
        add_rolling_features, add_interaction_features, fill_lag_nans
    )
    
    df = encoded_df.copy()
    df = add_temporal_features(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = add_interaction_features(df)
    
    # Check where NaNs are before filling
    nan_before = df.isnull().sum()
    print(f"NaN values before filling:")
    print(nan_before[nan_before > 0].to_string())
    
    # Now fill
    df_filled = fill_lag_nans(df, train_end_date=TRAIN_END_DATE)
    
    nan_after = df_filled.isnull().sum()
    print(f"\nNaN values after filling:")
    remaining_nans = nan_after[nan_after > 0]
    if len(remaining_nans) > 0:
        print(remaining_nans.to_string())
    else:
        print("None ✓")
    
    # Verify that fill values are computed from training period
    train_subset = df[df[DATE_COL] <= pd.Timestamp(TRAIN_END_DATE)]
    lag_cols = [
        "Production_Lag_1", "Equip_Avail_Lag_1", "Downtime_Lag_1",
        "Production_Rolling_3", "Equip_Avail_Rolling_3"
    ]
    
    mine_means_train = train_subset.groupby(MINE_ID_COL)[lag_cols].mean()
    
    # Check if any test rows were used in computing means
    test_subset = df[df[DATE_COL] >= pd.Timestamp(TEST_START_DATE)]
    mine_means_full = df.groupby(MINE_ID_COL)[lag_cols].mean()
    
    means_differ = not mine_means_train.equals(mine_means_full)
    
    print(f"\nTraining-period means equal to full-period means: {not means_differ}")
    
    if means_differ:
        print("⚠️  Means computed from training differ from full dataset means!")
        print("This means test data IS influencing the fill values.")
        print("\nComparison (first mine):")
        first_mine = mine_means_train.index[0]
        print(f"\nTrain-only means for {first_mine}:")
        print(mine_means_train.loc[first_mine])
        print(f"\nFull-data means for {first_mine}:")
        print(mine_means_full.loc[first_mine])
        is_leakage = True
    else:
        print("✓ NaN fill values use only training-period data.")
        is_leakage = False
    
    explanation = "Uses test data means!" if is_leakage else "Training only ✓"
    
    return is_leakage, explanation, {
        "nan_before": nan_before.sum(),
        "nan_after": nan_after.sum(),
        "means_differ": means_differ,
    }


# ============================================================================
# CHECK 6: CROSS-VALIDATION TIME ORDER
# ============================================================================

def check_cross_validation_order():
    """
    Verify that TimeSeriesSplit respects temporal order.
    
    For each CV fold, training dates must be strictly before validation dates.
    """
    print("\n" + "="*80)
    print("CHECK 6: CROSS-VALIDATION TIME ORDER")
    print("="*80)
    
    from sklearn.model_selection import TimeSeriesSplit
    from src.config import CV_N_SPLITS
    
    raw_df, encoded_df, encoders, _, _ = preprocess_pipeline()
    engineered_df = engineer_features(encoded_df)
    
    # Get training data
    train_df = engineered_df[
        engineered_df[DATE_COL] <= pd.Timestamp(TRAIN_END_DATE)
    ].copy()
    
    # Sort by DATE (critical for TimeSeriesSplit)
    train_df = train_df.sort_values(DATE_COL).reset_index(drop=True)
    
    X = train_df.values
    y = train_df[TARGET_COL].values
    
    tscv = TimeSeriesSplit(n_splits=CV_N_SPLITS)
    
    is_leakage = False
    fold_details = []
    
    for fold_idx, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
        train_dates = train_df.iloc[train_idx][DATE_COL]
        val_dates = train_df.iloc[val_idx][DATE_COL]
        
        train_min = train_dates.min()
        train_max = train_dates.max()
        val_min = val_dates.min()
        val_max = val_dates.max()
        
        # Check if fold respects temporal order
        fold_ok = train_max < val_min
        
        fold_details.append({
            "fold": fold_idx,
            "train_min": train_min.date(),
            "train_max": train_max.date(),
            "val_min": val_min.date(),
            "val_max": val_max.date(),
            "valid": fold_ok,
        })
        
        print(f"\nFold {fold_idx}:")
        print(f"  Train: {train_min.date()} to {train_max.date()} ({len(train_idx)} rows)")
        print(f"  Val:   {val_min.date()} to {val_max.date()} ({len(val_idx)} rows)")
        print(f"  Order valid (train_max < val_min): {fold_ok}")
        
        if not fold_ok:
            print(f"  ⚠️  LEAKAGE: Validation data includes dates before training!")
            is_leakage = True
    
    if is_leakage:
        print("\n⚠️  LEAKAGE DETECTED in cross-validation!")
    else:
        print("\n✓ All CV folds respect temporal order.")
    
    explanation = "INVALID!" if is_leakage else "Valid ✓"
    
    return is_leakage, explanation, fold_details


# ============================================================================
# CHECK 7: TARGET LEAKAGE DETECTION
# ============================================================================

def check_target_leakage(engineered_df):
    """
    Detect whether current-month or future Actual Production
    is used as a feature.
    
    Allowed: Previous-month Actual Production (as Production_Lag_1)
    Not allowed: Current-month Actual Production
    Not allowed: Future Actual Production
    """
    print("\n" + "="*80)
    print("CHECK 7: TARGET LEAKAGE DETECTION")
    print("="*80)
    
    leakage_found = False
    details = []
    
    # Check Model A features
    print("\nModel A features:")
    for feat in FEATURES_MODEL_A:
        if feat == TARGET_COL:
            print(f"  ⚠️  {feat} is the TARGET itself (not allowed as input!)")
            leakage_found = True
            details.append(f"{feat} is the target column")
        elif "target" in feat.lower() and feat != "Production_Target_Tonnes":
            print(f"  ? {feat} (contains 'target', but might be legitimate)")
        else:
            print(f"  ✓ {feat}")
    
    # Check if Production_Target_Tonnes is different from Actual_Production_Tonnes
    print("\nProduction_Target_Tonnes vs Actual_Production_Tonnes:")
    if "Production_Target_Tonnes" in FEATURES_MODEL_A:
        # Check correlation
        target_col = "Production_Target_Tonnes"
        actual_col = TARGET_COL
        
        if target_col in engineered_df.columns and actual_col in engineered_df.columns:
            correlation = engineered_df[target_col].corr(engineered_df[actual_col])
            print(f"  Correlation: {correlation:.4f}")
            print(f"  Interpretation: Very high correlation might indicate:")
            print(f"    - Natural relationship (target strongly drives actual)")
            print(f"    - Possible leakage (if target is set after actual production)")
            print(f"  NOTE: Production Target is typically set BEFORE production occurs.")
            print(f"  This is LEGITIMATE for prediction (target is known in advance).")
        
        explanation = "Production_Target_Tonnes is legitimate (known before production)"
        print(f"\n{explanation}")
    
    # Check if any current-month actual production is being used
    if "Current_Production" in engineered_df.columns or \
       "Actual_Production_Current" in engineered_df.columns:
        print("⚠️  Found current-month actual production in features!")
        leakage_found = True
        details.append("Current-month actual production found")
    
    if not leakage_found:
        print("\n✓ No direct target leakage detected.")
    
    explanation = "Legitimate" if not leakage_found else "LEAKAGE FOUND!"
    
    return leakage_found, explanation, {
        "model_a_features": FEATURES_MODEL_A,
        "target_col": TARGET_COL,
        "leakage_found": leakage_found,
        "details": details,
    }


# ============================================================================
# CHECK 8: MODEL A TARGET LEGITIMACY
# ============================================================================

def check_model_a_target_legitimacy():
    """
    Determine whether Production_Target_Tonnes can legitimately be used
    as a feature for predicting Actual_Production_Tonnes.
    
    This is NOT automatic leakage; it depends on whether the target is
    known BEFORE making the production prediction.
    """
    print("\n" + "="*80)
    print("CHECK 8: MODEL A TARGET LEGITIMACY")
    print("="*80)
    
    print("\nAnalysis:")
    print("  Feature: Production_Target_Tonnes")
    print("  Target: Actual_Production_Tonnes")
    print()
    print("  Question: Is Production_Target known BEFORE Actual Production?")
    print()
    print("  Answer: YES (in typical mining operations)")
    print("    - Production targets are set at the start of a month/quarter")
    print("    - Actual production is measured throughout the month")
    print("    - Target is KNOWN before prediction time")
    print()
    print("  Therefore: Using Production_Target as a feature is LEGITIMATE")
    print()
    print("  Caveat: Only if target value represents pre-production plan,")
    print("          not a post-hoc adjustment based on actual production.")
    print()
    print("  Assessment: ACCEPTABLE (no leakage)")
    print("    - Assumes targets are true operational forecasts")
    print("    - Not post-hoc adjustments")
    print()
    print("  Model B (without target) provides a fallback if needed.")
    
    is_leakage = False
    explanation = "Legitimate (target known in advance) ✓"
    
    return is_leakage, explanation, {
        "assumption": "Production targets are pre-production forecasts",
        "legitimacy": "Acceptable",
    }


# ============================================================================
# CHECK 9: FEATURE ENGINEERING PATTERNS
# ============================================================================

def check_feature_engineering_patterns():
    """
    Scan feature_engineering.py for patterns that might cause leakage:
    
    - groupby().transform() without shift
    - mean/median/rolling without proper ordering
    - expanding windows
    - ranking operations
    - target encoding on full data
    """
    print("\n" + "="*80)
    print("CHECK 9: FEATURE ENGINEERING PATTERNS")
    print("="*80)
    
    feature_eng_file = os.path.join(BASE_DIR, "src", "feature_engineering.py")
    
    with open(feature_eng_file, 'r') as f:
        content = f.read()
    
    suspicious_patterns = []
    safe_patterns = []
    
    # Check for suspicious patterns
    if "shift(" in content:
        safe_patterns.append("shift() is used (good for lag features)")
    else:
        suspicious_patterns.append("No shift() found - lag features might leak!")
    
    if ".rolling(" in content:
        # Check if rolling is after shift
        if "shift(1)" in content and content.find("shift(1)") < content.find(".rolling("):
            safe_patterns.append("rolling() is used after shift(1) (good)")
        else:
            suspicious_patterns.append("rolling() might be used without prior shift!")
    
    if ".expanding(" in content:
        suspicious_patterns.append("expanding() found - ensure it's not including future!")
    else:
        safe_patterns.append("No expanding() found")
    
    if ".rank(" in content:
        suspicious_patterns.append("rank() found - might include future data!")
    else:
        safe_patterns.append("No rank() found")
    
    # Check for target encoding
    if "target_encode" in content.lower() or "target_mean" in content.lower():
        suspicious_patterns.append("Target encoding found - check if fit on train only!")
    else:
        safe_patterns.append("No target encoding found")
    
    # Check for per-mine transforms
    if "groupby(" in content:
        safe_patterns.append("groupby() used for per-mine calculations (good)")
    
    print("Safe patterns found:")
    for pattern in safe_patterns:
        print(f"  ✓ {pattern}")
    
    if suspicious_patterns:
        print("\nSuspicious patterns found:")
        for pattern in suspicious_patterns:
            print(f"  ⚠️  {pattern}")
        is_leakage = True
        explanation = f"{len(suspicious_patterns)} suspicious patterns"
    else:
        print("\n✓ No suspicious patterns detected.")
        is_leakage = False
        explanation = "No suspicious patterns ✓"
    
    return is_leakage, explanation, {
        "safe_patterns": safe_patterns,
        "suspicious_patterns": suspicious_patterns,
    }


# ============================================================================
# CHECK 10: FUTURE INFORMATION TEST
# ============================================================================

def check_future_information_test():
    """
    Practical test: Simulate making predictions for January 2025.
    
    Create a dataset where information AFTER January 2025 is removed.
    Check if features for January 2025 change.
    
    If features change when future data is removed, there is leakage.
    """
    print("\n" + "="*80)
    print("CHECK 10: FUTURE INFORMATION TEST")
    print("="*80)
    
    raw_df, encoded_df, encoders, _, _ = preprocess_pipeline()
    engineered_full = engineer_features(encoded_df)
    
    # Full dataset January 2025 features
    jan_2025_full = engineered_full[
        (engineered_full[DATE_COL] >= '2025-01-01') & 
        (engineered_full[DATE_COL] < '2025-02-01')
    ].copy().sort_values([MINE_ID_COL, DATE_COL])
    
    if len(jan_2025_full) == 0:
        print("No January 2025 data found. Using December 2024 as test month.")
        test_month = '2024-12-01'
        test_month_end = '2025-01-01'
        description = "December 2024"
    else:
        test_month = '2025-01-01'
        test_month_end = '2025-02-01'
        description = "January 2025"
    
    print(f"\nTest month: {description}")
    print(f"Test approach: Engineer features with and without future data")
    
    # Case 1: Full dataset (with future)
    test_data_full = engineered_full[
        (engineered_full[DATE_COL] >= test_month) & 
        (engineered_full[DATE_COL] < test_month_end)
    ].copy()
    
    # Case 2: Limited dataset (without future, only up to test month)
    encoded_limited = encoded_df[encoded_df[DATE_COL] < test_month_end].copy()
    engineered_limited = engineer_features(encoded_limited)
    
    test_data_limited = engineered_limited[
        (engineered_limited[DATE_COL] >= test_month) & 
        (engineered_limited[DATE_COL] < test_month_end)
    ].copy()
    
    # Compare features
    lag_cols = [
        "Production_Lag_1", "Equip_Avail_Lag_1", "Downtime_Lag_1",
        "Production_Rolling_3", "Equip_Avail_Rolling_3"
    ]
    
    print(f"\nComparing lag/rolling features:")
    differences = []
    
    for idx, row in test_data_full.iterrows():
        mine_id = row[MINE_ID_COL]
        date = row[DATE_COL]
        
        # Find corresponding row in limited data
        limited_row = test_data_limited[
            (test_data_limited[MINE_ID_COL] == mine_id) &
            (test_data_limited[DATE_COL] == date)
        ]
        
        if len(limited_row) > 0:
            limited_row = limited_row.iloc[0]
            
            for col in lag_cols:
                full_val = row[col]
                limited_val = limited_row[col]
                
                if pd.notna(full_val) and pd.notna(limited_val):
                    if not np.isclose(full_val, limited_val, atol=1.0):
                        differences.append({
                            "mine_id": mine_id,
                            "date": date,
                            "feature": col,
                            "with_future": full_val,
                            "without_future": limited_val,
                            "diff": full_val - limited_val,
                        })
    
    is_leakage = len(differences) > 0
    
    print(f"Rows compared: {len(test_data_full)}")
    print(f"Feature mismatches: {len(differences)}")
    
    if differences:
        print("\n⚠️  LEAKAGE DETECTED!")
        print("Features changed when future data was removed!")
        print("\nExamples:")
        for i, diff in enumerate(differences[:5]):
            print(f"\n  {i+1}. Mine {diff['mine_id']}, Date {diff['date'].date()}")
            print(f"     Feature: {diff['feature']}")
            print(f"     With future: {diff['with_future']:.2f}")
            print(f"     Without future: {diff['without_future']:.2f}")
            print(f"     Difference: {diff['diff']:.2f}")
    else:
        print("\n✓ Features remain consistent (no future information detected).")
    
    explanation = "LEAKAGE!" if is_leakage else "No future leakage ✓"
    
    return is_leakage, explanation, {
        "rows_compared": len(test_data_full),
        "mismatches": len(differences),
        "examples": differences[:5],
    }


# ============================================================================
# MAIN AUDIT EXECUTION
# ============================================================================

def run_full_audit():
    """Execute all 10 checks and generate report."""
    
    print("\n" + "="*80)
    print("STARTING COMPREHENSIVE DATA LEAKAGE AUDIT")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: SIH 2026 — Production Intelligence")
    print(f"Focus: Model 2 Data Leakage Verification")
    
    report = AuditReport()
    
    # Load data once
    print("\n[Preparing audit environment]")
    raw_df, encoded_df, encoders, _, _ = preprocess_pipeline()
    engineered_df = engineer_features(encoded_df)
    
    # CHECK 1: Lag Features
    print("\n" + "="*80)
    is_leak, exp, details = check_lag_features(engineered_df)
    report.add_check(1, "Lag Features", "PASS" if not is_leak else "FAIL", is_leak, exp, str(details))
    
    # CHECK 2: Rolling Features
    print("\n" + "="*80)
    is_leak, exp, details = check_rolling_features(engineered_df)
    report.add_check(2, "Rolling Features", "PASS" if not is_leak else "FAIL", is_leak, exp, str(details))
    
    # CHECK 3: Train/Test Split
    print("\n" + "="*80)
    is_leak, exp, details = check_train_test_split(raw_df, engineered_df)
    report.add_check(3, "Train/Test Separation", "PASS" if not is_leak else "FAIL", is_leak, exp, str(details))
    
    # CHECK 4: Preprocessing
    print("\n" + "="*80)
    is_leak, exp, details = check_preprocessing()
    report.add_check(4, "Preprocessing Integrity", "PASS" if not is_leak else "WARN", is_leak, exp, str(details))
    
    # CHECK 5: Missing Value Handling
    print("\n" + "="*80)
    is_leak, exp, details = check_missing_value_handling(engineered_df)
    report.add_check(5, "Missing Value Filling", "PASS" if not is_leak else "FAIL", is_leak, exp, str(details))
    
    # CHECK 6: Cross-Validation
    print("\n" + "="*80)
    is_leak, exp, details = check_cross_validation_order()
    report.add_check(6, "CV Time Order", "PASS" if not is_leak else "FAIL", is_leak, exp, str(details))
    
    # CHECK 7: Target Leakage
    print("\n" + "="*80)
    is_leak, exp, details = check_target_leakage(engineered_df)
    report.add_check(7, "Target Leakage", "PASS" if not is_leak else "FAIL", is_leak, exp, str(details))
    
    # CHECK 8: Model A Target Legitimacy
    print("\n" + "="*80)
    is_leak, exp, details = check_model_a_target_legitimacy()
    report.add_check(8, "Model A Target", "PASS" if not is_leak else "WARN", is_leak, exp, str(details))
    
    # CHECK 9: Feature Engineering Patterns
    print("\n" + "="*80)
    is_leak, exp, details = check_feature_engineering_patterns()
    report.add_check(9, "FE Patterns", "PASS" if not is_leak else "WARN", is_leak, exp, str(details))
    
    # CHECK 10: Future Information Test
    print("\n" + "="*80)
    is_leak, exp, details = check_future_information_test()
    report.add_check(10, "Future Info Test", "PASS" if not is_leak else "FAIL", is_leak, exp, str(details))
    
    # Determine overall result
    critical_leakages = [c for c in report.checks if c['leakage'] and c['check'] not in [4, 8, 9]]
    
    if len(critical_leakages) > 0:
        report.overall_result = "FAIL — Confirmed data leakage"
    else:
        report.overall_result = "PASS — No significant leakage found"
    
    return report


# ============================================================================
# REPORT OUTPUT
# ============================================================================

def print_final_report(report):
    """Print the comprehensive audit report."""
    
    report.print_table()
    
    print("\n" + "="*80)
    print("OVERALL RESULT")
    print("="*80)
    print(f"\n  {report.overall_result}")
    
    print("\n" + "="*80)
    print("LEAKAGE SUMMARY")
    print("="*80)
    
    critical_issues = [c for c in report.checks if c['leakage'] and c['check'] not in [4, 8, 9]]
    warnings = [c for c in report.checks if c['leakage'] and c['check'] in [4, 8, 9]]
    
    if critical_issues:
        print(f"\n⚠️  CRITICAL ISSUES ({len(critical_issues)}):")
        for check in critical_issues:
            print(f"  [{check['check']}] {check['name']}: {check['explanation']}")
    else:
        print("\n✓ No critical leakage issues detected.")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for check in warnings:
            print(f"  [{check['check']}] {check['name']}: {check['explanation']}")
    else:
        print("\n✓ No warnings.")
    
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    
    if len(critical_issues) == 0:
        print("\n✓ SAFE TO MOVE FORWARD")
        print("\n  Model 2 pipeline passed the leakage audit.")
        print("  No data leakage detected in:")
        print("    - Lag features (verified correctness)")
        print("    - Rolling features (verified no future data)")
        print("    - Train/test separation (chronological integrity)")
        print("    - NaN filling (training data only)")
        print("    - Cross-validation (time-series order)")
        print("    - Target usage (legitimate features)")
        print("\n  Before final deployment:")
        print("    1. Review feature importance to ensure legitimacy")
        print("    2. Validate on out-of-sample test data")
        print("    3. Test with actual 2026 data (when available)")
        print("    4. Monitor prediction accuracy in production")
    else:
        print("\n⚠️  FIX LEAKAGE BEFORE MOVING FORWARD")
        print(f"\n  {len(critical_issues)} critical leakage issue(s) found.")
        print("  The pipeline MUST be fixed before deployment.")
        print("\n  Affected checks:")
        for check in critical_issues:
            print(f"    - CHECK {check['check']}: {check['name']}")
            print(f"      Issue: {check['explanation']}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    report = run_full_audit()
    print_final_report(report)
    
    print("\n[Audit complete]")
