Tables behind the paper, as produced from the runs reported in it.

| file | paper | produced by |
|---|---|---|
| `main_results_table_asymmetric.csv` | Table 3 | notebook 07, section 1 (`MODE="asymmetric"`) |
| `main_results_table_symmetric.csv` | input to Table 4 | notebook 07, section 1 (`MODE="symmetric"`) |
| `delta_results_table.csv` | Table 4 (symmetric minus asymmetric) | `scripts/paper_numbers.py` |
| `cost_table.csv` | Table 5 | `scripts/paper_numbers.py` |
| `dispersion_summary.csv` | Section 4.6, Figure 5 | `scripts/dispersion_boxplots.py` |

Columns: `MAE` in W; `Delta_cov` = |PICP - 0.8| for the 80% interval
[q0.1, q0.9]; `MPIW_80` in W; `QS` = mean pinball loss over q0.1, q0.5, q0.9.
The modular MAE uses the point forecast and the integrated MAE uses q0.5.
Costs use 0.12 USD/kWh; Table 5 prints each total as the sum of its two
rounded components.
