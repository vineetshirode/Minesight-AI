"""
generate_dataset.py — Synthetic Prototype Dataset Generator
=============================================================
SIH 2026 — Model 2: Production Intelligence

Generates manganese_production_prototype_v2.csv with:
  - 14 mines (real MOIL mine names/locations)
  - 48 months per mine (Jan 2022 – Dec 2025)
  - 672 total rows
  - 13 columns: Mine_ID, Mine_Name, District, State, Mine_Type, Date,
    Production_Target_Tonnes, Actual_Production_Tonnes,
    Equipment_Availability_Pct, Equipment_Downtime_Hours,
    Rainfall_mm, Blasting_Delay_Days, Working_Days

IMPORTANT: This is a PROTOTYPE / SYNTHETIC dataset created for
demonstrating the ML pipeline.  It is NOT official MOIL operational data.

Reproducibility: numpy random seed = 42
"""

import os
import numpy as np
import pandas as pd
from src.config import DATA_RAW_DIR, RAW_CSV, RANDOM_STATE

np.random.seed(RANDOM_STATE)

# ============================================================
# MINE DEFINITIONS (based on publicly-known MOIL mines)
# ============================================================
MINES = [
    # (Mine_ID, Mine_Name, District, State, Mine_Type, base_target)
    ("MOIL-01", "Dongri Buzurg Mine",   "Bhandara",  "Maharashtra",    "Underground", 30000),
    ("MOIL-02", "Gumgaon Mine",         "Nagpur",     "Maharashtra",    "Underground", 22000),
    ("MOIL-03", "Kandri Mine",          "Nagpur",     "Maharashtra",    "Opencast",    18000),
    ("MOIL-04", "Munsar Mine",          "Nagpur",     "Maharashtra",    "Opencast",    12000),
    ("MOIL-05", "Chikla Mine",          "Bhandara",   "Maharashtra",    "Underground", 15000),
    ("MOIL-06", "Beldongri Mine",       "Nagpur",     "Maharashtra",    "Underground", 10000),
    ("MOIL-07", "Balaghat Mine",        "Balaghat",   "Madhya Pradesh", "Underground", 28000),
    ("MOIL-08", "Tirodi Mine",          "Balaghat",   "Madhya Pradesh", "Opencast",    20000),
    ("MOIL-09", "Sitapatore Mine",      "Jhabua",     "Madhya Pradesh", "Opencast",     8000),
    ("MOIL-10", "Ukwa Mine",            "Jhabua",     "Madhya Pradesh", "Opencast",     9000),
    ("MOIL-11", "Parsioni Mine",        "Nagpur",     "Maharashtra",    "Underground", 11000),
    ("MOIL-12", "Mansar Mine",          "Nagpur",     "Maharashtra",    "Opencast",    14000),
    ("MOIL-13", "Garbham Mine",         "Vizianagaram","Andhra Pradesh", "Opencast",     9000),
    ("MOIL-14", "Koduru Mine",          "Vizianagaram","Andhra Pradesh", "Opencast",     7000),
]


def _monthly_rainfall(month: int, state: str) -> float:
    """Simulate monthly rainfall (mm) with strong monsoon seasonality."""
    # Monsoon pattern: Jun-Sep heavy, Oct-Nov moderate, Dec-May dry
    base_rainfall = {
        1: 8, 2: 12, 3: 15, 4: 20, 5: 35,
        6: 180, 7: 280, 8: 260, 9: 190,
        10: 65, 11: 25, 12: 10,
    }
    scale = 1.0
    if state == "Madhya Pradesh":
        scale = 1.15  # slightly higher rainfall belt
    elif state == "Andhra Pradesh":
        scale = 0.85
    base = base_rainfall[month] * scale
    noise = np.random.normal(0, base * 0.25)
    return max(0, round(base + noise, 1))


def _working_days(month: int, year: int) -> int:
    """Estimate working days (excluding Sundays + a few holidays)."""
    from calendar import monthrange
    _, days_in_month = monthrange(year, month)
    # Roughly 4-5 Sundays + 1-2 holidays
    sundays = sum(1 for d in range(1, days_in_month + 1)
                  if pd.Timestamp(year, month, d).weekday() == 6)
    holidays = np.random.choice([1, 2, 3], p=[0.5, 0.35, 0.15])
    wd = days_in_month - sundays - holidays
    return max(18, min(wd, 27))


def _equipment_availability(month: int, mine_type: str) -> float:
    """Simulate equipment availability (%). Underground mines have slightly
    lower baseline. Monsoon months reduce availability."""
    base = 90.0 if mine_type == "Opencast" else 87.0
    # Monsoon penalty
    if month in (6, 7, 8, 9):
        base -= np.random.uniform(3, 8)
    noise = np.random.normal(0, 3)
    return round(np.clip(base + noise, 60, 99), 1)


def _equipment_downtime(equip_avail: float, working_days: int) -> float:
    """Derive downtime from availability. Lower availability → more downtime."""
    # Total possible hours ≈ working_days × 16 (two 8-hr shifts)
    total_hours = working_days * 16
    downtime_frac = (100 - equip_avail) / 100
    downtime = total_hours * downtime_frac * np.random.uniform(0.6, 1.0)
    return round(max(0, downtime), 1)


def _blasting_delay(month: int, mine_type: str) -> int:
    """Simulate blasting delays (days). Higher in monsoon and for opencast."""
    if mine_type == "Underground":
        base_prob = 0.15
    else:
        base_prob = 0.25
    if month in (6, 7, 8, 9):
        base_prob += 0.20
    if np.random.random() < base_prob:
        return int(np.random.choice([1, 2, 3, 4, 5], p=[0.35, 0.30, 0.20, 0.10, 0.05]))
    return 0


def _production_target(base_target: float, month: int, year: int) -> float:
    """Generate monthly production target with seasonal + yearly trend."""
    # Slight yearly growth (1-3% per year)
    year_factor = 1.0 + 0.02 * (year - 2022)
    # Monsoon reduction in target (mines plan lower during monsoon)
    monsoon_factor = 1.0
    if month in (7, 8):
        monsoon_factor = 0.80
    elif month in (6, 9):
        monsoon_factor = 0.88
    elif month in (10,):
        monsoon_factor = 0.95
    noise = np.random.normal(0, base_target * 0.03)
    target = base_target * year_factor * monsoon_factor + noise
    return round(max(base_target * 0.5, target), 0)


def _actual_production(
    target: float,
    equip_avail: float,
    downtime: float,
    rainfall: float,
    blasting_delay: int,
    working_days: int,
    mine_type: str,
) -> float:
    """
    Simulate actual production as a function of target and constraints.

    The key relationship:
        actual ≈ target × efficiency_factor × constraint_penalties

    Constraint penalties:
      - Equipment availability below 85% reduces output
      - High downtime reduces output
      - Heavy rainfall (> 100 mm) reduces output
      - Blasting delays directly reduce output
      - Fewer working days reduce output
    """
    # Base efficiency: mines typically achieve 85-98% of target
    base_efficiency = np.random.normal(0.92, 0.04)

    # Equipment penalty
    if equip_avail < 85:
        equip_penalty = 1 - (85 - equip_avail) * 0.008
    elif equip_avail < 75:
        equip_penalty = 1 - (85 - equip_avail) * 0.012
    else:
        equip_penalty = 1.0

    # Rainfall penalty
    if rainfall > 200:
        rain_penalty = 0.88
    elif rainfall > 100:
        rain_penalty = 0.94
    elif rainfall > 50:
        rain_penalty = 0.97
    else:
        rain_penalty = 1.0

    # Blasting delay penalty (~3-4% per day of delay)
    blast_penalty = 1 - blasting_delay * np.random.uniform(0.025, 0.04)

    # Working days factor (normalised around 24 days)
    wd_factor = working_days / 24.0

    # Mine type factor (underground slightly less efficient)
    type_factor = 0.97 if mine_type == "Underground" else 1.0

    # Combined
    actual = (
        target
        * base_efficiency
        * equip_penalty
        * rain_penalty
        * blast_penalty
        * wd_factor
        * type_factor
    )

    # Add final noise (±2%)
    noise = np.random.normal(0, target * 0.02)
    actual = actual + noise

    return round(max(0, actual), 0)


def generate_dataset() -> pd.DataFrame:
    """Generate the full 672-row prototype dataset."""
    records = []

    for mine_id, mine_name, district, state, mine_type, base_target in MINES:
        for month_offset in range(48):
            year = 2022 + (month_offset // 12)
            month = (month_offset % 12) + 1
            date_str = f"{year}-{month:02d}-01"

            rainfall = _monthly_rainfall(month, state)
            wd = _working_days(month, year)
            equip_avail = _equipment_availability(month, mine_type)
            downtime = _equipment_downtime(equip_avail, wd)
            blast_delay = _blasting_delay(month, mine_type)
            target = _production_target(base_target, month, year)
            actual = _actual_production(
                target, equip_avail, downtime, rainfall,
                blast_delay, wd, mine_type
            )

            records.append({
                "Mine_ID": mine_id,
                "Mine_Name": mine_name,
                "District": district,
                "State": state,
                "Mine_Type": mine_type,
                "Date": date_str,
                "Production_Target_Tonnes": target,
                "Actual_Production_Tonnes": actual,
                "Equipment_Availability_Pct": equip_avail,
                "Equipment_Downtime_Hours": downtime,
                "Rainfall_mm": rainfall,
                "Blasting_Delay_Days": blast_delay,
                "Working_Days": wd,
            })

    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])

    # Ensure correct dtypes
    df["Production_Target_Tonnes"] = df["Production_Target_Tonnes"].astype(float)
    df["Actual_Production_Tonnes"] = df["Actual_Production_Tonnes"].astype(float)
    df["Blasting_Delay_Days"] = df["Blasting_Delay_Days"].astype(int)
    df["Working_Days"] = df["Working_Days"].astype(int)

    return df


def save_dataset(df: pd.DataFrame) -> str:
    """Save dataset to data/raw/ and return file path."""
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    df.to_csv(RAW_CSV, index=False)
    print(f"[generate_dataset] Saved {len(df)} rows → {RAW_CSV}")
    return RAW_CSV


if __name__ == "__main__":
    df = generate_dataset()
    save_dataset(df)

    # Quick summary
    print(f"\nDataset shape: {df.shape}")
    print(f"Unique mines:  {df['Mine_ID'].nunique()}")
    print(f"Date range:    {df['Date'].min()} to {df['Date'].max()}")
    print(f"Missing values:\n{df.isnull().sum().to_string()}")
    print(f"\nNumerical summary:\n{df.describe().round(1).to_string()}")
