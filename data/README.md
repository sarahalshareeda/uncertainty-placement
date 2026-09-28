# Data

| file | content | rows |
|---|---|---|
| `data_v1.0.csv` | one year, 5-minute readings (training, $D_1$) | 105,119 |
| `data_v2.0.csv` | 40 days, 5-minute readings (validation and test, $D_2$) | 11,519 |

Columns: `time`, `power (W)`, `voltage (V)`, `amperage (A)`, `generation (w)`,
`temperature (ºC)`, `Total Consumption`. The notebooks match these by name, so
the `.xlsx` originals exported to CSV also work.

**Source.** L. Gomes, Z. Vale, P. Faria, J. Soares, *2025 Competition on
Electric Energy Consumption Forecast Adopting Multi-criteria Performance
Metrics*, v4.5.1, GECAD, Polytechnic Institute of Porto, Zenodo, 2025,
https://doi.org/10.5281/zenodo.16061225. License: CC BY 4.0.

**Changes.** The published `data_v1.0.xlsx` and `data_v2.0.xlsx` were exported
to CSV. No values were changed. The files carry times of day only; the
notebooks assign dates (v1.0 from 2023-12-01, v2.0 from 2024-12-01) and resample
to a complete 5-minute grid, which is why the notebooks report 105,408 training
rows. The test days are Dec 24 and Dec 30, 2024; the rest of v2.0 is used for
validation.

MD5 checksums:
```
21167d50536d68d18c8acc6e70b0af45  data_v1.0.csv
56f6dceed619d32e4190f7d6dcf60c05  data_v2.0.csv
```
