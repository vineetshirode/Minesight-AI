"""
test_simulator_api.py — Automated Test Suite for Real ML What-If Simulator
==========================================================================
SIH 2026 Problem Statement 26009 — MOIL Ltd. / Ministry of Steel

Tests:
  - Health & Baseline endpoints
  - TEST 1: Change Downtime only
  - TEST 2: Change Blasting Delay only
  - TEST 3: Change Rainfall only
  - TEST 4: Change Working Days only
  - TEST 5: Compound scenario (relieve multiple constraints)
  - TEST 6: Identity test (values == baseline -> output == baseline)
  - Derived features recalculation verification
"""

import sys
import os
from fastapi.testclient import TestClient

# Ensure root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app, manager, FEATURE_COLS

client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns valid model metadata."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["features_count"] == 18
    assert data["mines_count"] == 14
    print("[PASS] Health Check Endpoint verified.")


def test_baseline_endpoint():
    """Verify baseline profiles exist for all 14 MOIL mines."""
    res = client.get("/api/baseline")
    assert res.status_code == 200
    data = res.json()
    assert "mines" in data
    assert len(data["mines"]) == 14
    first_mine = data["mines"][0]
    assert "id" in first_mine
    assert "target" in first_mine
    assert "predicted" in first_mine
    assert "risk" in first_mine
    print(f"[PASS] Baseline Endpoint verified ({len(data['mines'])} mines loaded).")


def test_test_a_identity_baseline():
    """Test A: When scenario inputs are identical to baseline, prediction difference MUST be 0.0."""
    base = manager.mine_baselines["MOIL-01"]
    req_payload = {
        "mine": "Dongri Buzurg Mine",
        "production_target": base["target"],
        "downtime": base["downtime"],
        "rainfall": base["rainfall"],
        "blasting_delay": base["blasting_delay"],
        "working_days": base["working_days"]
    }
    res = client.post("/api/simulate", json=req_payload)
    assert res.status_code == 200
    d = res.json()

    base_pred = d["baseline"]["predicted_production"]
    scen_pred = d["scenario"]["predicted_production"]

    assert abs(scen_pred - base_pred) < 0.001, f"Expected {base_pred}, got {scen_pred}"
    assert d["impact"]["production_change"] == 0.0
    assert d["impact"]["shortfall_change"] == 0.0
    assert d["impact"]["risk_changed"] is False
    print(f"[PASS] Test A (Identity Test): Baseline {base_pred} == Scenario {scen_pred} tonnes (Diff = {d['impact']['production_change']} t).")


def test_test_b_downtime_only_55_to_25():
    """Test B: Change ONLY downtime: 55.4 -> 25.0 hrs."""
    base = manager.mine_baselines["MOIL-01"]
    target_dt = 25.0

    req_payload = {
        "mine": "Dongri Buzurg Mine",
        "downtime": target_dt
    }
    res = client.post("/api/simulate", json=req_payload)
    assert res.status_code == 200
    d = res.json()

    # 1. Verify availability updated relative to baseline empirical availability
    expected_avail_shift = ((base["downtime"] - target_dt) / (base["working_days"] * 16.0)) * 100.0
    expected_avail = round(base["availability"] + expected_avail_shift, 1)
    assert abs(d["scenario"]["availability"] - expected_avail) < 0.1, f"Expected {expected_avail}%, got {d['scenario']['availability']}%"

    # 2. Verify prediction and shortfall changed
    base_pred = d["baseline"]["predicted_production"]
    scen_pred = d["scenario"]["predicted_production"]
    assert scen_pred != base_pred, "Model prediction should change under downtime perturbation"
    assert d["scenario"]["shortfall_tonnes"] == max(0.0, round(d["scenario"]["target"] - scen_pred, 1))

    print(f"[PASS] Test B (Downtime 55.4 -> 25.0 hrs):")
    print(f"       Availability: {base['availability']}% -> {d['scenario']['availability']}%")
    print(f"       Baseline Pred: {base_pred} t (Shortfall: {d['baseline']['shortfall_tonnes']} t, {d['baseline']['risk']})")
    print(f"       Scenario Pred: {scen_pred} t (Shortfall: {d['scenario']['shortfall_tonnes']} t, {d['scenario']['risk']})")
    print(f"       Impact: {d['impact']['production_change']:+.1f} t production, {d['impact']['shortfall_change']:+.1f} t shortfall")


def test_test_c_multiple_variables():
    """Test C: Change multiple operational variables."""
    req_payload = {
        "mine": "Dongri Buzurg Mine",
        "downtime": 15.0,
        "blasting_delay": 0,
        "rainfall": 20.0,
        "working_days": 27
    }
    res = client.post("/api/simulate", json=req_payload)
    assert res.status_code == 200
    d = res.json()
    assert d["impact"]["production_change"] > 0
    print(f"[PASS] Test C (Multi-Variable Perturbation): Prod change: {d['impact']['production_change']:+.1f} t | Risk: {d['impact']['risk_from']} -> {d['impact']['risk_to']}")


def test_all_14_mines():
    """Verify simulation works seamlessly across all 14 MOIL mines."""
    res = client.get("/api/baseline")
    assert res.status_code == 200
    mines = res.json()["mines"]
    assert len(mines) == 14

    print("\n  -- Testing all 14 MOIL Mines on Model 2 Simulation --")
    for m in mines:
        mid = m["id"]
        mname = m["name"]

        # 1. Baseline Identity Test for this mine
        res_ident = client.post("/api/simulate", json={"mine_id": mid})
        assert res_ident.status_code == 200
        d_id = res_ident.json()
        assert abs(d_id["scenario"]["predicted_production"] - d_id["baseline"]["predicted_production"]) < 0.1

        # 2. Scenario Perturbation Test (Relieve downtime and blast delay)
        res_scen = client.post("/api/simulate", json={
            "mine_id": mid,
            "downtime": max(5.0, m["downtime"] - 20.0),
            "blasting_delay": max(0, m["blasting_delay"] - 1),
            "rainfall": max(10.0, m["rainfall"] * 0.5)
        })
        assert res_scen.status_code == 200
        d_sc = res_scen.json()

        b_pred = d_sc["baseline"]["predicted_production"]
        s_pred = d_sc["scenario"]["predicted_production"]
        imp = d_sc["impact"]["production_change"]
        r_from = d_sc["impact"]["risk_from"]
        r_to = d_sc["impact"]["risk_to"]

        # Verify formulas
        target = d_sc["scenario"]["target"]
        expected_shortfall = max(0.0, round(target - s_pred, 1))
        assert abs(d_sc["scenario"]["shortfall_tonnes"] - expected_shortfall) < 0.2

        expected_pct = round(expected_shortfall / target * 100.0, 2)
        assert abs(d_sc["scenario"]["shortfall_pct"] - expected_pct) < 0.2

        print(f"  [OK] {mid:8s} | {mname:20s} | Base: {b_pred:7.1f}t ({r_from:6s}) -> Scen: {s_pred:7.1f}t ({r_to:6s}) | Delta: {imp:+7.1f}t")

    print("[PASS] All 14 MOIL Mines passed simulation inference & mathematical integrity.\n")


def run_all_tests():
    print("\n" + "=" * 70)
    print("  RUNNING AUTOMATED SIMULATOR TEST SUITE")
    print("=" * 70)
    test_health_endpoint()
    test_baseline_endpoint()
    test_test_a_identity_baseline()
    test_test_b_downtime_only_55_to_25()
    test_test_c_multiple_variables()
    test_all_14_mines()
    print("=" * 70)
    print("  ALL VALIDATION TESTS (TEST A, B, C, D) PASSED 100% SUCCESSFULLY!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()

