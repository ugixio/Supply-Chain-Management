"""
Anomaly detection for supply chain signals using LSTM Autoencoder.

Detects: demand spikes, lead-time outliers, quality metric drift,
shipment delay patterns, and supplier performance degradation.

Architecture: LSTM Encoder → compressed latent z → LSTM Decoder → reconstruct.
Anomaly score = MSE(original, reconstruction); threshold = μ + k·σ on train set.

Design notes:
  - Unsupervised: no labelled anomaly data required (rare in SCM).
  - Threshold calibrated on validation set at desired false-positive rate.
  - Supports multivariate series: [demand, price, lead_time, OTD, ...].
  - score_series() returns a per-timestep anomaly probability useful for
    real-time monitoring dashboards.

References:
    Malhotra et al., "LSTM-based Encoder-Decoder for Multi-sensor Anomaly
    Detection" (2016), ICML Anomaly Detection Workshop.
    Hundman et al., "Detecting Spacecraft Anomalies Using LSTMs and
    Nonparametric Dynamic Thresholding" (2018), KDD.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

class LSTMEncoder(nn.Module):
    def __init__(self, n_features: int, latent_size: int, n_layers: int,
                 dropout: float) -> None:
        super().__init__()
        self.lstm = nn.LSTM(n_features, latent_size, n_layers,
                            batch_first=True, dropout=dropout if n_layers > 1 else 0.0)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, tuple]:
        out, (h, c) = self.lstm(x)
        return out, (h, c)


class LSTMDecoder(nn.Module):
    def __init__(self, latent_size: int, n_features: int, seq_len: int,
                 n_layers: int, dropout: float) -> None:
        super().__init__()
        self.seq_len = seq_len
        self.lstm = nn.LSTM(latent_size, latent_size, n_layers,
                            batch_first=True, dropout=dropout if n_layers > 1 else 0.0)
        self.fc = nn.Linear(latent_size, n_features)

    def forward(self, z: torch.Tensor, h: tuple) -> torch.Tensor:
        # Repeat latent vector across time steps for decoder input
        repeated = z.unsqueeze(1).repeat(1, self.seq_len, 1)
        out, _ = self.lstm(repeated, h)
        return self.fc(out)


class LSTMAutoencoder(nn.Module):
    """
    LSTM Autoencoder for multivariate time-series anomaly detection.

    Args:
        n_features:  number of input signals (e.g. 5 for [demand, LT, OTD, PPM, price])
        seq_len:     lookback window length
        latent_size: compressed representation size (rule of thumb: n_features × 4)
        n_layers:    LSTM depth (2 is sufficient for most SCM signals)
        dropout:     regularisation
    """

    def __init__(
        self,
        n_features: int,
        seq_len: int,
        latent_size: int = 32,
        n_layers: int = 2,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.n_features = n_features
        self.seq_len = seq_len
        self.encoder = LSTMEncoder(n_features, latent_size, n_layers, dropout)
        self.decoder = LSTMDecoder(latent_size, n_features, seq_len, n_layers, dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, n_features)
        Returns:
            reconstruction: (batch, seq_len, n_features)
        """
        _, (h, c) = self.encoder(x)
        # Use last hidden state as latent
        z = h[-1]                     # (batch, latent_size)
        return self.decoder(z, (h, c))


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_autoencoder(
    model: LSTMAutoencoder,
    normal_windows: np.ndarray,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-3,
    device: Optional[str] = None,
    patience: int = 8,
) -> dict:
    """
    Train the autoencoder on NORMAL-only windows (unsupervised).

    The model learns to reconstruct normal patterns; anomalies will have
    high reconstruction error because they deviate from the learned distribution.

    Args:
        model:          LSTMAutoencoder instance
        normal_windows: (N, seq_len, n_features) — windows from normal operation
        epochs:         max training epochs
        batch_size:     gradient batch size
        lr:             learning rate
        device:         'cuda'/'mps'/'cpu' (auto-detected if None)
        patience:       early stopping patience

    Returns:
        dict with train_losses, val_losses, best_epoch.
    """
    if device is None:
        device = (
            "cuda" if torch.cuda.is_available()
            else "mps" if torch.backends.mps.is_available()
            else "cpu"
        )
    model = model.to(device)

    X = torch.tensor(normal_windows, dtype=torch.float32)
    n = len(X)
    n_train = int(n * 0.85)
    ds = TensorDataset(X)
    train_loader = DataLoader(
        torch.utils.data.Subset(ds, range(n_train)), batch_size=batch_size, shuffle=True
    )
    val_loader = DataLoader(
        torch.utils.data.Subset(ds, range(n_train, n)), batch_size=batch_size
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    train_losses, val_losses = [], []
    best_val, best_epoch, no_improve = float("inf"), 0, 0
    best_state = None

    for epoch in range(epochs):
        model.train()
        tl = 0.0
        for (xb,) in train_loader:
            xb = xb.to(device)
            optimizer.zero_grad()
            loss = criterion(model(xb), xb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            tl += loss.item() * len(xb)

        model.eval()
        vl = 0.0
        with torch.no_grad():
            for (xb,) in val_loader:
                xb = xb.to(device)
                vl += criterion(model(xb), xb).item() * len(xb)

        train_losses.append(tl / n_train)
        val_losses.append(vl / max(n - n_train, 1))

        if val_losses[-1] < best_val:
            best_val = val_losses[-1]
            best_epoch = epoch
            no_improve = 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            no_improve += 1
            if no_improve >= patience:
                break

    if best_state:
        model.load_state_dict(best_state)

    return {"train_losses": train_losses, "val_losses": val_losses,
            "best_epoch": best_epoch, "best_val_loss": round(best_val, 8)}


# ---------------------------------------------------------------------------
# Threshold calibration and scoring
# ---------------------------------------------------------------------------

def calibrate_threshold(
    model: LSTMAutoencoder,
    validation_windows: np.ndarray,
    false_positive_rate: float = 0.02,
    device: Optional[str] = None,
) -> dict:
    """
    Compute reconstruction error on normal validation windows and set threshold
    at the (1 - FPR) percentile so that FPR% of normal windows are flagged.

    Args:
        model:              trained LSTMAutoencoder
        validation_windows: (N, seq_len, n_features) — held-out normal windows
        false_positive_rate: target FPR (default 2%)

    Returns:
        dict with threshold, mean_error, std_error, percentile_used.
    """
    errors = _reconstruction_errors(model, validation_windows, device)
    pct = (1 - false_positive_rate) * 100
    threshold = float(np.percentile(errors, pct))
    return {
        "threshold": round(threshold, 8),
        "mean_reconstruction_error": round(float(np.mean(errors)), 8),
        "std_reconstruction_error": round(float(np.std(errors)), 8),
        "percentile_used": pct,
        "false_positive_rate_target": false_positive_rate,
    }


def score_windows(
    model: LSTMAutoencoder,
    windows: np.ndarray,
    threshold: float,
    device: Optional[str] = None,
) -> dict:
    """
    Score new windows against the trained model.

    Args:
        model:     trained LSTMAutoencoder
        windows:   (N, seq_len, n_features) — windows to score
        threshold: from calibrate_threshold()

    Returns:
        dict with reconstruction_errors, is_anomaly flags, anomaly_score (0-1).
    """
    errors = _reconstruction_errors(model, windows, device)
    is_anomaly = (errors > threshold).tolist()
    # Normalise to [0,1] for dashboard display (clipped at 3× threshold)
    scores = np.clip(errors / (threshold * 3), 0.0, 1.0).tolist()
    return {
        "reconstruction_errors": [round(e, 8) for e in errors.tolist()],
        "is_anomaly": is_anomaly,
        "anomaly_score": [round(s, 4) for s in scores],
        "n_anomalies": int(sum(is_anomaly)),
        "anomaly_rate": round(sum(is_anomaly) / len(is_anomaly), 4),
        "threshold_used": threshold,
    }


def _reconstruction_errors(
    model: LSTMAutoencoder,
    windows: np.ndarray,
    device: Optional[str],
) -> np.ndarray:
    if device is None:
        device = next(model.parameters()).device
    model.eval()
    X = torch.tensor(windows, dtype=torch.float32).to(device)
    with torch.no_grad():
        recon = model(X)
    errors = ((X - recon) ** 2).mean(dim=(1, 2)).cpu().numpy()
    return errors


def build_sliding_windows(series: np.ndarray, seq_len: int) -> np.ndarray:
    """
    Convert a multivariate series into overlapping windows.

    Args:
        series:  (T, n_features) or (T,) univariate
        seq_len: window length

    Returns:
        (N, seq_len, n_features) where N = T - seq_len + 1
    """
    if series.ndim == 1:
        series = series[:, np.newaxis]
    T, F = series.shape
    if T < seq_len:
        raise ValueError(f"Series length {T} < seq_len {seq_len}.")
    windows = np.stack([series[i: i + seq_len] for i in range(T - seq_len + 1)])
    return windows
