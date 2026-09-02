# Model 2: Production Intelligence — SIH 2026

**Problem Statement ID:** 26009  
**Problem Statement:** *"Using AI/ML and Space Technology to Identify Manganese Reserves and Overcome Production Shortfalls."*  
**Organization:** Ministry of Steel | **Department:** MOIL Ltd.  
**Sub-System:** Model 2 — Production Intelligence  

---

## 1. Executive Summary & Core Objective

Model 2 addresses the fundamental operational question for mine planning:
> **"How much manganese production can a given mine expect in a specific month, and is there an impending risk of production shortfall?"**

### Operational Intelligence Architecture
```
Operational & Environmental Inputs
 (Equip Avail, Downtime, Rain, Blasting, Working Days, Targets)
                  │
                  ▼
   Leakage-Safe Feature Engineering
 (Lags, 3-Mo Rolling Averages, Effective Capacity, Interactions)
                  │
                  ▼
  Ensemble ML Regressor (Gradient Boosting)
                  │
                  ▼
       Predicted Production (Tonnes)
                  │
                  ▼
         Shortfall Calculation
      (Target - Predicted Production)
                  │
                  ▼
      3-Tier Risk Classification
        (LOW / MEDIUM / HIGH)
                  │
                  ▼
       Top Driver Attribution
          (SHAP / Feature Importance)
                  │
                  ▼
    Rule-Based Prescriptive Actions
  (Maintenance, Blasting SOP, Fleet Deployment)
```

---

## 2. Dataset Description & Transparency Caveat

> [!WARNING]
> **Prototype / Synthetic Dataset:** The dataset (`data/raw/manganese_production_prototype_v2.csv`) is a synthetic prototype created strictly for demonstration and validation of the AI/ML pipeline architecture. It is **not** raw confidential operational data from MOIL Ltd.

* **Dimensions:** 672 monthly observations across 14 MOIL mines over 48 continuous months (January 2022 to December 2025).
* **Mines Represented:** Dongri Buzurg, Gumgaon, Kandri, Munsar, Chikla, Beldongri, Balaghat, Tirodi, Sitapatore, Ukwa, Parsioni, Mansar, Garbham, Koduru.
* **Granularity:** 1 Mine $\times$ 1 Month per record.
* **Target Variable:** `Actual_Production_Tonnes`.
* **Validation Strategy:** Chronological **Time-Based Split**:
  * **Train Set (2022–2024):** 504 rows (75%)
  * **Test Set (2025):** 168 rows (25%)

---

## 3. Dual Forecasting Paradigms: Model A vs. Model B

To ensure complete transparency and prevent target-leakage bias, two distinct modeling experiments are evaluated:

| Experiment | Features Used | Purpose |
| :--- | :--- | :--- |
| **Model A (Planning Forecast)** | Categorical + Production Target + Operational & Environmental Features + Engineered Features | Evaluates if a pre-planned target is realistically achievable under forecast conditions. |
| **Model B (Constraint-Based Forecast)** | Categorical + Operational & Environmental Features + Engineered Features (*No Target*) | Pure bottom-up production capacity forecast based strictly on physical/mechanical constraints. |

---

## 4. Benchmark Performance Comparison (2025 Test Set)

| Experiment | Model | Test MAE (Tonnes) | Test RMSE (Tonnes) | Test $R^2$ | Test MAPE (%) | 5-Fold CV MAE |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Model A** | **Gradient Boosting** ⭐ | **569.74** | **767.08** | **0.9918** | **3.44%** | **612.30** |
| Model A | Random Forest | 642.39 | 870.27 | 0.9895 | 4.02% | 685.12 |
| Model A | Linear Regression | 906.37 | 1189.80 | 0.9804 | 5.90% | 948.40 |
| **Model B** | **Gradient Boosting** ⭐ | **780.92** | **1060.87** | **0.9844** | **4.97%** | **834.15** |
| Model B | Random Forest | 821.83 | 1142.06 | 0.9819 | 4.85% | 879.50 |
| Model B | Linear Regression | 1021.50 | 1383.46 | 0.9734 | 6.86% | 1085.20 |

---

## 5. Shortfall, Risk Tiers & Recommendation Logic

### Shortfall Calculation
$$\text{Predicted Shortfall (Tonnes)} = \max(0, \text{Production Target} - \text{Predicted Production})$$
$$\text{Predicted Surplus (Tonnes)} = \max(0, \text{Predicted Production} - \text{Production Target})$$
$$\text{Shortfall \%} = \frac{\text{Predicted Shortfall}}{\text{Production Target}} \times 100$$

### Configurable Risk Classification
* **LOW RISK** ($\text{Shortfall \%} < 5.0\%$): Production is expected to meet or comfortably approach quota.
* **MEDIUM RISK** ($5.0\% \le \text{Shortfall \%} < 15.0\%$): Moderate shortfall anticipated; proactive adjustments needed.
* **HIGH RISK** ($\text{Shortfall \%} \ge 15.0\%$): Severe shortfall expected; immediate intervention required.

### Rule-Based Prescriptive Actions
* **High Equipment Downtime ($>60$ hrs):** *"Prioritize preventive fleet maintenance and critical spare parts availability."*
* **Low Equipment Availability ($<85\%$):** *"Expedite fleet inspection and evaluate machinery overhaul or redeployment."*
* **Blasting Delays ($\ge 2$ days):** *"Review statutory clearances, explosive magazine logistics, and sequence planning."*
* **Severe Rainfall ($>150$ mm):** *"Activate monsoon SOPs: pit dewatering pumps readiness and haul road maintenance."*
* **Reduced Working Days ($<22$ days):** *"Schedule compensatory shifts or overtime to recover production capacity."*

---

## 6. Project Structure

```
model2_production/
├── data/
│   ├── raw/
│   │   └── manganese_production_prototype_v2.csv   # 672 raw prototype records
│   └── processed/
│       └── production_engineered.csv               # Dataset with lag & rolling features
├── models/
│   ├── production_model.pkl                        # Best trained model (Gradient Boosting)
│   └── encoders.pkl                                # Serialized label encoders
├── outputs/
│   ├── production_predictions.csv                  # 2025 Test predictions + shortfall + recs
│   ├── model_metrics.json                          # JSON metrics for all 6 model configurations
│   ├── model_comparison.csv                        # Formatted comparison table
│   ├── error_analysis.csv                          # Multi-dimensional residual analysis
│   └── feature_importance.csv                      # Tree MDI & Permutation feature importance
├── src/
│   ├── __init__.py
│   ├── config.py                                   # Centralized paths, features & risk thresholds
│   ├── generate_dataset.py                         # Seeded synthetic dataset generator (seed=42)
│   ├── preprocessing.py                            # Data loading, validation, encoding & split
│   ├── feature_engineering.py                      # Leakage-safe temporal, lag & rolling features
│   ├── train.py                                    # Model training & TimeSeriesSplit CV
│   ├── evaluate.py                                 # Evaluation metrics, diagnostics & charts
│   ├── explainability.py                           # SHAP & Feature importance
│   ├── recommendations.py                          # Rule-based decision-support engine
│   └── predict.py                                  # Inference & master predictions exporter
├── run_pipeline.py                                 # End-to-end one-command pipeline runner
└── README.md
```

---

## 7. How to Run

### 1. Prerequisites
```bash
pip install pandas numpy scikit-learn matplotlib joblib shap
```

### 2. Execute Full End-to-End Pipeline
Run the master script to generate data, engineer features, train models, evaluate errors, and output predictions:
```bash
python3 run_pipeline.py
```

### 3. Running Individual Modules
* **Generate Synthetic Data:** `python3 -m src.generate_dataset`
* **Train All Models:** `python3 -m src.train`
* **Evaluate & Error Analysis:** `python3 -m src.evaluate`
* **Feature Explainability:** `python3 -m src.explainability`
* **Generate Predictions & Shortfall CSV:** `python3 -m src.predict`
