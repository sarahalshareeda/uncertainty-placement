"""Derive every aggregate number quoted in the paper from the two main-results tables.

Inputs  (written by notebooks/07_evaluation_and_figures.ipynb, copies in results/):
    results/main_results_table_asymmetric.csv
    results/main_results_table_symmetric.csv
Outputs:
    results/delta_results_table.csv   (Table 4)
    results/cost_table.csv            (Table 5)
and a printed check of each quoted number against the value in the paper.

Usage:  python scripts/paper_numbers.py   (from the repository root)
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
ORDER = ["SARIMAX", "XGBoost", "BiLSTM", "BiGRU-LSTM", "TFT", "LLM (ZT)", "LLM (FT)"]
C_ENERGY = 0.12   # USD/kWh, commercial tariff in Turkey (EPDK)
HOURS = 24

asym = pd.read_csv(os.path.join(RES, "main_results_table_asymmetric.csv"))
sym = pd.read_csv(os.path.join(RES, "main_results_table_symmetric.csv"))
key = ["Model", "Formulation"]
asym, sym = asym.set_index(key), sym.set_index(key)
mod = asym.xs("Modular", level="Formulation").loc[ORDER]
itg = asym.xs("Integrated", level="Formulation").loc[ORDER]

checks = []


def check(label, value, paper, tol):
    ok = abs(value - paper) <= tol
    checks.append(ok)
    print(f"  {'OK ' if ok else 'XX '} {label:<62} {value:>10.3f}   paper: {paper}")


# ---- Table 4: symmetric minus asymmetric ---------------------------------
delta = (sym - asym).loc[[(m, f) for m in ORDER for f in ("Modular", "Integrated")]]
delta.columns = ["Delta_MAE", "Delta_Delta_cov", "Delta_MPIW_80", "Delta_QS"]
delta.round(6).to_csv(os.path.join(RES, "delta_results_table.csv"))

# ---- Table 5: cost mapping ------------------------------------------------
rows = []
for m in ORDER:
    for f in ("Modular", "Integrated"):
        r = asym.loc[(m, f)]
        e_s = HOURS * r.MAE / 1000.0
        e_r = HOURS * r.MPIW_80 / 1000.0
        rows.append(dict(Model=m, Formulation=f, Delta_cov=r.Delta_cov,
                         E_sched_kWh=e_s, E_reserve_kWh=e_r,
                         Cost_sched=C_ENERGY * e_s, Cost_reserve=C_ENERGY * e_r,
                         Cost_total=C_ENERGY * (e_s + e_r),
                         # Table 5 prints each total as the sum of its two rounded components
                         Cost_total_table=round(C_ENERGY * e_s, 2) + round(C_ENERGY * e_r, 2)))
cost = pd.DataFrame(rows)
cost.round(4).to_csv(os.path.join(RES, "cost_table.csv"), index=False)

print("\nAsymmetric results (Section 4.4, abstract)")
red = lambda a, b: 100 * (a - b) / a
check("modular reduces mean coverage error vs integrated (%)",
      red(itg.Delta_cov.mean(), mod.Delta_cov.mean()), 54.2, 0.05)
check("modular reduces mean QS vs integrated (%)",
      red(itg.QS.mean(), mod.QS.mean()), 52.5, 0.05)
check("integrated reduces mean MPIW80 vs modular (%)",
      red(mod.MPIW_80.mean(), itg.MPIW_80.mean()), 31.6, 0.05)
check("placement shift in scheduling mismatch, mean |int-mod|/mod (%)",
      100 * (np.abs(itg.MAE - mod.MAE) / mod.MAE).mean(), 18.2, 0.05)
check("placement shift in reserve-band width, mean |int-mod|/mod (%)",
      100 * (np.abs(itg.MPIW_80 - mod.MPIW_80) / mod.MPIW_80).mean(), 84.3, 0.05)

print("\nSymmetric vs asymmetric (Section 4.5, abstract): 14 model-placement configurations")
wider = int((delta.Delta_MPIW_80 < 0).sum())
worse = int((delta.Delta_Delta_cov < 0).sum())
check("configurations whose interval is wider under asymmetry (%)", 100 * wider / 14, 71.4, 0.05)
check("configurations whose calibration is worse under asymmetry (%)", 100 * worse / 14, 57.1, 0.05)
check("largest width reduction, LLM (ZT)-integrated (W)",
      -delta.loc[("LLM (ZT)", "Integrated"), "Delta_MPIW_80"], 2148.54, 0.005)

print("\nTransfer learning, LLM (ZT) vs LLM (FT) (Section 4.4)")
check("MAE, zero-tuned", asym.loc[("LLM (ZT)", "Modular"), "MAE"], 595.87, 0.005)
check("MAE, fine-tuned", asym.loc[("LLM (FT)", "Modular"), "MAE"], 573.77, 0.005)
check("modular coverage error, zero-tuned", asym.loc[("LLM (ZT)", "Modular"), "Delta_cov"], 0.425, 0.0005)
check("modular coverage error, fine-tuned", asym.loc[("LLM (FT)", "Modular"), "Delta_cov"], 0.300, 0.0005)
check("integrated width, fine-tuned (W)", asym.loc[("LLM (FT)", "Integrated"), "MPIW_80"], 1129.17, 0.005)

print("\nConclusion")
check("TFT: integrated width reduction vs modular (%)",
      red(mod.loc["TFT", "MPIW_80"], itg.loc["TFT", "MPIW_80"]), 76.1, 0.05)
check("LLM (FT): integrated coverage-error reduction vs modular (%)",
      red(mod.loc["LLM (FT)", "Delta_cov"], itg.loc["LLM (FT)", "Delta_cov"]), 48.6, 0.05)
check("LLM (FT): integrated interval expansion vs modular (%)",
      -red(mod.loc["LLM (FT)", "MPIW_80"], itg.loc["LLM (FT)", "MPIW_80"]), 16.1, 0.05)

print("\nCost table (Table 5)")
c = cost.set_index(["Model", "Formulation"])
check("XGBoost-modular total cost (USD/day)", c.loc[("XGBoost", "Modular"), "Cost_total_table"], 1.67, 0.005)
check("XGBoost-integrated total cost (USD/day)", c.loc[("XGBoost", "Integrated"), "Cost_total_table"], 3.42, 0.005)
check("SARIMAX-modular total cost (USD/day)", c.loc[("SARIMAX", "Modular"), "Cost_total_table"], 5.94, 0.005)
check("SARIMAX-integrated total cost (USD/day)", c.loc[("SARIMAX", "Integrated"), "Cost_total_table"], 3.14, 0.005)
check("SARIMAX reserve band, modular (kWh/day)", c.loc[("SARIMAX", "Modular"), "E_reserve_kWh"], 27.37, 0.005)
check("SARIMAX reserve band, integrated (kWh/day)", c.loc[("SARIMAX", "Integrated"), "E_reserve_kWh"], 3.98, 0.005)
check("LLM (ZT)-integrated reserve cost (USD/day)", c.loc[("LLM (ZT)", "Integrated"), "Cost_reserve"], 6.21, 0.005)
check("LLM (FT)-modular total cost (USD/day)", c.loc[("LLM (FT)", "Modular"), "Cost_total_table"], 4.45, 0.005)
check("LLM (FT)-integrated total cost (USD/day)", c.loc[("LLM (FT)", "Integrated"), "Cost_total_table"], 4.90, 0.005)

print(f"\n{sum(checks)}/{len(checks)} quoted numbers reproduced.")
print("Wrote results/delta_results_table.csv and results/cost_table.csv")
sys.exit(0 if all(checks) else 1)
