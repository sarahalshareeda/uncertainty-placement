"""Trainable-parameter counts of the TFT configurations in Table 2.

Builds each configuration used in notebooks/05_tft.ipynb, fits it for one epoch on
random data (only to instantiate the network; the weights do not affect the count)
and counts the trainable parameters.

Expected output:
    Symmetric 5-min   | point: 22248 | quantile: 22122
    Asymmetric hourly | point: 39405 | quantile: 39167

Requires: pip install "u8darts[torch]"
"""
import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.models import TFTModel
from darts.utils.likelihood_models import QuantileRegression


def count_tft(hidden, in_len, out_len, n_cov, freq, prob):
    idx = pd.date_range("2024-01-01", periods=3000, freq=freq)
    y = TimeSeries.from_times_and_values(idx, np.random.rand(3000, 1).astype(np.float32))
    cov = TimeSeries.from_times_and_values(idx, np.random.rand(3000, n_cov).astype(np.float32))
    kw = dict(likelihood=QuantileRegression([0.1, 0.5, 0.9])) if prob else {}
    m = TFTModel(input_chunk_length=in_len, output_chunk_length=out_len, hidden_size=hidden,
                 lstm_layers=1, num_attention_heads=2, dropout=0.2, batch_size=16,
                 n_epochs=1, add_relative_index=True, random_state=42,
                 pl_trainer_kwargs={"enable_progress_bar": False}, **kw)
    m.fit(y, past_covariates=cov, future_covariates=cov, verbose=False)
    return sum(p.numel() for p in m.model.parameters() if p.requires_grad)


if __name__ == "__main__":
    # symmetric: hidden 8, 288-step input, 1-step output, 14 covariates at 5 min
    print("Symmetric 5-min   | point:", count_tft(8, 288, 1, 14, "5min", False),
          "| quantile:", count_tft(8, 288, 1, 14, "5min", True))
    # asymmetric: hidden 16, 24-step input and output, 11 covariates hourly
    print("Asymmetric hourly | point:", count_tft(16, 24, 24, 11, "h", False),
          "| quantile:", count_tft(16, 24, 24, 11, "h", True))
