"""
recommendations.py — Rule-Based Operational Recommendation Engine
===================================================================
SIH 2026 — Model 2: Production Intelligence
MOIL Ltd. / Ministry of Steel

Generates actionable, rule-based recommendations for mine management
based on predicted shortfalls and top contributing operational constraints.

IMPORTANT:
These are decision-support recommendations to assist mine planners.
They are NOT automated mine-control actions.
"""

import pandas as pd
import numpy as np


def generate_single_recommendation(
    shortfall_tonnes: float,
    shortfall_pct: float,
    risk_level: str,
    top_driver: str,
    equip_avail: float,
    downtime_hours: float,
    rainfall_mm: float,
    blasting_delay: int,
    working_days: int,
) -> str:
    """
    Generate an actionable recommendation string for a single prediction row.

    Rules evaluate operational thresholds when shortfall risk exists.
    """
    if risk_level == "LOW" and shortfall_tonnes <= 0:
        return "Production on track to meet/exceed target. Maintain standard operating procedures and preventive maintenance schedule."

    recommendations = []

    # 1. Equipment Availability Constraint
    if equip_avail < 85.0:
        recommendations.append(
            f"Low equipment availability ({equip_avail:.1f}%): Expedite fleet inspection and consider machinery redeployment."
        )

    # 2. Equipment Downtime Constraint
    if downtime_hours > 60.0:
        recommendations.append(
            f"High equipment downtime ({downtime_hours:.0f} hrs): Prioritize preventive maintenance and ensure critical spare parts buffer."
        )

    # 3. Blasting Delay Constraint
    if blasting_delay >= 2:
        recommendations.append(
            f"Blasting delays ({blasting_delay} days): Review statutory clearances, explosive magazine logistics, and sequence planning."
        )

    # 4. Monsoon / Heavy Rainfall Constraint
    if rainfall_mm >= 150.0:
        recommendations.append(
            f"Severe weather impact ({rainfall_mm:.1f} mm rain): Activate monsoon SOPs, ensure pit dewatering pumps readiness, and reinforce haul roads."
        )

    # 5. Working Days Constraint
    if working_days < 22:
        recommendations.append(
            f"Reduced working days ({working_days} days): Plan compensatory shifts or overtime to recover production loss."
        )

    # Fallback if specific thresholds didn't trigger but risk is Medium/High
    if not recommendations:
        if "Target" in top_driver:
            recommendations.append(
                "Aggressive production target relative to historical capacity. Re-evaluate monthly quota feasibility."
            )
        elif "Downtime" in top_driver or "Equip" in top_driver:
            recommendations.append(
                "Fleet operational bottlenecks detected. Review maintenance logs and mechanical availability."
            )
        elif "Rainfall" in top_driver:
            recommendations.append(
                "Weather sensitivity observed. Adjust operating plan for seasonal environmental factors."
            )
        else:
            recommendations.append(
                "Moderate shortfall anticipated. Review operational workflow and monitor weekly output closely."
            )

    return " | ".join(recommendations)


def add_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add operational recommendations and top driver summaries to prediction DataFrame.

    Requires columns:
        - Predicted_Shortfall_Tonnes
        - Shortfall_Pct
        - Risk_Level
        - Top_Driver
        - Equipment_Availability_Pct
        - Equipment_Downtime_Hours
        - Rainfall_mm
        - Blasting_Delay_Days
        - Working_Days
    """
    df = df.copy()

    recs = []
    for _, row in df.iterrows():
        rec = generate_single_recommendation(
            shortfall_tonnes=row.get("Predicted_Shortfall_Tonnes", 0),
            shortfall_pct=row.get("Shortfall_Pct", 0),
            risk_level=row.get("Risk_Level", "LOW"),
            top_driver=str(row.get("Top_Driver", "None")),
            equip_avail=row.get("Equipment_Availability_Pct", 90.0),
            downtime_hours=row.get("Equipment_Downtime_Hours", 0.0),
            rainfall_mm=row.get("Rainfall_mm", 0.0),
            blasting_delay=int(row.get("Blasting_Delay_Days", 0)),
            working_days=int(row.get("Working_Days", 26)),
        )
        recs.append(rec)

    df["Actionable_Recommendation"] = recs
    return df
