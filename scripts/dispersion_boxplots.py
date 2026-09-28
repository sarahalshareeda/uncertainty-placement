"""Figure 5: distribution of the absolute error and the 80% interval width over the
two test days, for every model and placement under both protocols.

Reads the per-hour forecasts written by notebooks 01-06 into outputs/ and writes
    results/dispersion_hourly_values.csv
    results/dispersion_summary.csv
    results/fig_dispersion_boxplots.png

Usage:  python scripts/dispersion_boxplots.py            (from the repository root)
        SEGAN_OUT=/path/to/outputs python scripts/dispersion_boxplots.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.environ.get("SEGAN_OUT", os.path.join(REPO, "outputs"))
RES = os.path.join(REPO, "results")

MODELS = ["SARIMAX", "XGBoost", "BiLSTM", "BiGRU-LSTM", "TFT", "LLM (ZT)", "LLM (FT)"]

# (folder, file stem) per protocol; route1 = modular, route2 = integrated
_ASYM = {
    "SARIMAX":    ("sarimax_out_asymmetric_NATIVE_hourly", "sarimax_asymmetric_native_hourly"),
    "XGBoost":    ("xgb_out_asymmetric_train5min_testhourly", "xgb_asymmetric_hourly"),
    "BiLSTM":     ("bilstm_out_asymmetric_train5min_testhourly", "bilstm_asymmetric_hourly"),
    "BiGRU-LSTM": ("bigrulstm_out_asymmetric_train5min_testhourly", "bigrulstm_asymmetric_hourly"),
    "TFT":        ("tft_out_asymmetric_FIXED_hourly", "tft_asymmetric_hourly_FIXED"),
    "LLM (ZT)":   ("llm_out_asymmetric_hourly", "llm_zeroshot_asymmetric_hourly"),
    "LLM (FT)":   ("llm_out_asymmetric_hourly", "llm_trained_asymmetric_hourly"),
}
_SYM = {
    "SARIMAX":    ("sarimax_out_symmetric_5min_route1_standardized_recursive", "sarimax_symmetric_5min"),
    "XGBoost":    ("xgb_out_symmetric_5min_route1_standardized", "xgb_symmetric_5min"),
    "BiLSTM":     ("bilstm_out_symmetric_5min_fixed", "bilstm_symmetric_5min"),
    "BiGRU-LSTM": ("bigrulstm_out_symmetric_5min_route1_standardized", "bigrulstm_symmetric_5min"),
    "TFT":        ("tft_out_symmetric_5min_recursive", "tft_symmetric_5min"),
    "LLM (ZT)":   ("llm_out_symmetric_5min_fixed1", "llm_zeroshot_symmetric_5min"),
    "LLM (FT)":   ("llm_out_symmetric_5min_fixed1", "llm_trained_symmetric_5min"),
}


def path(protocol, model, route):
    folder, stem = (_ASYM if protocol == "Asymmetric" else _SYM)[model]
    name = (f"merged_route1_point_uq_series_{stem}.csv" if route == 1
            else f"merged_route2_predictions_prob_{stem}.csv")
    return os.path.join(OUT, folder, name)


def load(p):
    d = pd.read_csv(p)
    d.columns = [c.strip() for c in d.columns]
    return d.rename(columns={"Actual Power (W)": "actual", "q10 (W)": "q10",
                             "q50 (W)": "q50", "q90 (W)": "q90"})


def main():
    rows = []
    for protocol in ("Asymmetric", "Symmetric"):
        for model in MODELS:
            for placement, route in (("Modular", 1), ("Integrated", 2)):
                d = load(path(protocol, model, route))
                rows.append(pd.DataFrame({
                    "protocol": protocol, "model": model, "placement": placement,
                    "abs_err": (d["actual"] - d["q50"]).abs(),
                    "width": d["q90"] - d["q10"]}))
    df = pd.concat(rows, ignore_index=True)
    os.makedirs(RES, exist_ok=True)
    df.to_csv(os.path.join(RES, "dispersion_hourly_values.csv"), index=False)

    q = lambda p: (lambda x: x.quantile(p))
    summ = df.groupby(["protocol", "model", "placement"]).agg(
        err_median=("abs_err", "median"),
        err_iqr=("abs_err", lambda x: x.quantile(.75) - x.quantile(.25)),
        err_p95=("abs_err", q(.95)),
        width_median=("width", "median"),
        width_iqr=("width", lambda x: x.quantile(.75) - x.quantile(.25))).round(1)
    summ.to_csv(os.path.join(RES, "dispersion_summary.csv"))
    print(summ.to_string())

    plt.rcParams.update({"font.size": 11, "axes.labelsize": 12,
                         "xtick.labelsize": 11, "ytick.labelsize": 11})
    runs = [("Asymmetric", "Modular"), ("Asymmetric", "Integrated"),
            ("Symmetric", "Modular"), ("Symmetric", "Integrated")]
    face = dict(zip(runs, ["white", "0.55", "white", "0.85"]))
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    for ax, col, lab in ((axes[0], "abs_err", "Absolute error (W)"),
                         (axes[1], "width", "80% interval width (W)")):
        for k, run in enumerate(runs):
            data = [df[(df.protocol == run[0]) & (df.placement == run[1]) &
                       (df.model == m)][col].values for m in MODELS]
            bp = ax.boxplot(data, positions=[i * 5 + k for i in range(len(MODELS))],
                            widths=0.8, patch_artist=True,
                            flierprops=dict(marker=".", markersize=2),
                            medianprops=dict(color="black"))
            for b in bp["boxes"]:
                b.set(facecolor=face[run], hatch="//" if run[0] == "Symmetric" else None)
            bp["boxes"][0].set_label(f"{run[0]} - {run[1]}")
        ax.set_ylabel(lab)
        ax.grid(axis="y", alpha=0.3)
    axes[1].set_xticks([i * 5 + 1.5 for i in range(len(MODELS))])
    axes[1].set_xticklabels(MODELS)
    axes[0].legend(ncol=4, fontsize=9, loc="upper center",
                   bbox_to_anchor=(0.5, 1.22), frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "fig_dispersion_boxplots.png"), dpi=300, bbox_inches="tight")
    print("saved results/fig_dispersion_boxplots.png")


if __name__ == "__main__":
    main()
