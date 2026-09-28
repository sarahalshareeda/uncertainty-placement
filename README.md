# Uncertainty Placement under Train-Deployment Asymmetry

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23005837.svg)](https://doi.org/10.5281/zenodo.23005837)

Reference implementation for:

> G. Ozdemir and S. Al-Shareeda, *Reliability-Aware Model-Dependent Uncertainty
> Placement under Data Asymmetry for Probabilistic Load Forecasting*,
> Sustainable Energy, Grids and Networks (under review).

Probabilistic load forecasters are often trained on rich data and deployed on
degraded data. This repository compares two ways of attaching uncertainty to a
forecaster, under both conditions, for seven models from five families:

- **Modular placement** (`route1`): a deterministic forecaster plus post-hoc
  residual quantiles, grouped by hour-of-day and day-of-week context and
  estimated on validation data.
- **Integrated placement** (`route2`): the model learns the 0.1, 0.5 and 0.9
  quantiles directly (pinball loss, quantile objective, or native quantiles).

| Family | Model | Notebook |
|---|---|---|
| statistical | SARIMAX | `01_sarimax.ipynb` |
| feature-based | XGBoost | `02_xgboost.ipynb` |
| recurrent | BiLSTM | `03_bilstm.ipynb` |
| recurrent | BiGRU-LSTM | `04_bigrulstm.ipynb` |
| attention-based | Temporal Fusion Transformer | `05_tft.ipynb` |
| pretrained | Chronos-T5-small, zero-tuned and fine-tuned | `06_chronos_llm.ipynb` |

Each model notebook runs two protocols on the same two test days
(Dec 24 and Dec 30, 2024):

- **Symmetric** ($X = X'$): training and testing at 5-minute resolution with
  every channel.
- **Asymmetric** ($X \neq X'$): training on the full multivariate history;
  deployment on hourly data with temperature and calendar features only. The
  missing channels (voltage, current, PV generation) and the lags derived from
  them are filled with hour-of-day means from the training year, so no
  test-day information is used.

## Headline results (asymmetric protocol)

| | modular | integrated |
|---|---|---|
| mean coverage error $\lvert\mathrm{PICP}-0.8\rvert$ over 7 models | **0.235** | 0.512 |
| mean 80% interval width (W) | 973.3 | **665.5** |

The modular placement is more reliable for most models. The integrated
placement gives sharp but under-calibrated intervals for the recurrent,
attention-based and statistical models, and recovers coverage only by widening
its intervals for the pretrained forecaster. XGBoost-modular gives the best
cost-reliability balance (coverage error 0.154 at 1.67 USD/day).

## Reproducing the paper

1. Open the notebooks in Google Colab (or locally, with the packages in
   `requirements.txt`). On Colab, copy this repository to
   `MyDrive/uncertainty-placement`; the notebooks mount Drive and find it
   there. Elsewhere, run them from `notebooks/`, or set `SEGAN_REPO`. To evaluate
   forecasts stored somewhere else, set `SEGAN_OUT` to that folder.
2. Run `01` to `06`. Each writes its per-hour forecasts to `outputs/`. A GPU is
   needed for `06` (fine-tuning takes about 34 min for the symmetric protocol
   and 21 min for the asymmetric one on a T4) and recommended for `03` to `05`.
3. Run `07_evaluation_and_figures.ipynb` for Tables 3 and 4 and Figures 3 and 4.
4. Run `python scripts/paper_numbers.py` from the repository root. It rebuilds
   Table 4 (`results/delta_results_table.csv`) and Table 5
   (`results/cost_table.csv`), and checks all 25 aggregate numbers quoted in the
   paper (averages, percentages, costs) against the main-results tables. It
   runs on the committed `results/` in a second and needs only pandas.
5. `python scripts/dispersion_boxplots.py` draws the boxplot figure (Figure 5)
   from `outputs/`, and `python scripts/count_tft_params.py` reproduces the TFT
   parameter counts in Table 2.

The deep models are trained with a fixed seed (42), but GPU training is not
bit-for-bit deterministic, so a rerun can differ from the committed
`results/` in the last digits.

## Repository layout

```
data/        the two competition files used (CC BY 4.0, see data/README.md)
notebooks/   01-06 model runs, 07 evaluation, tables and figures
scripts/     paper_numbers.py, dispersion_boxplots.py, count_tft_params.py
results/     the tables behind the paper (main results, delta, cost, dispersion)
outputs/     created by the notebooks (per-hour forecasts); not tracked
```

The output folder names inside `outputs/` (for example
`xgb_out_asymmetric_train5min_testhourly`) are the names used when the paper's
experiments were run, kept so that the evaluation notebook reads them
unchanged.

## Configuration

Table 2 of the paper lists every model's architecture, hyperparameters and
parameter count. Hyperparameters are fixed in advance, not tuned per placement,
and within each protocol the modular and the integrated variant of a model
share the same backbone configuration.

## Data

`data/data_v1.0.csv` (one year, 5-minute resolution) and `data/data_v2.0.csv`
(40 days, 5-minute resolution) come from the 2025 Competition on Electric Energy
Consumption Forecast Adopting Multi-criteria Performance Metrics
(Gomes, Vale, Faria, Soares; GECAD, Polytechnic of Porto),
https://doi.org/10.5281/zenodo.16061225, licensed CC BY 4.0. They are CSV
exports of the published `.xlsx` files; see `data/README.md`.

## License

Code: MIT. Data in `data/`: CC BY 4.0, from the source above. See `LICENSE`.

## Citation

If you use this code, please cite the paper and this archive (see
`CITATION.cff`).
