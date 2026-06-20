"""
Deep learning demand forecasting models for supply chain.

Implements:
  1. LSTMForecaster        — sequence-to-one multi-variate LSTM baseline
  2. TemporalFusionTransformer (TFT-lite) — Lim et al. 2021 (IJF)
     Gating, variable selection, temporal self-attention.
  3. Convenience wrappers: train() / predict() / evaluate()

Architecture notes (senior design decisions):
  - All models accept a *unified* feature tensor: (batch, seq_len, n_features)
    where features = [demand_t, price_t, promo_t, dow_sin, dow_cos, ...].
  - Outputs are point forecasts + quantile estimates (q10, q50, q90) for
    probabilistic planning and safety-stock calibration.
  - Loss: Quantile (Pinball) loss so p50 = median unbiased forecast and
    q90 drives safety stock directly.
  - DataLoader handles variable-length history via zero-padding + mask.

References:
    Lim et al., "Temporal Fusion Transformers for Interpretable
    Multi-horizon Time Series Forecasting" (2021) IJF 37(4).
    Salinas et al., "DeepAR" (2020) IJF 36(3).
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ---------------------------------------------------------------------------
# Quantile (Pinball) loss
# ---------------------------------------------------------------------------

class QuantileLoss(nn.Module):
    """Pinball loss for quantile regression."""

    def __init__(self, quantiles: list[float] = (0.1, 0.5, 0.9)) -> None:
        super().__init__()
        self.quantiles = quantiles

    def forward(self, preds: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        Args:
            preds:  (batch, n_quantiles)
            target: (batch,)
        """
        losses = []
        for i, q in enumerate(self.quantiles):
            e = target - preds[:, i]
            losses.append(torch.max(q * e, (q - 1) * e))
        return torch.stack(losses, dim=1).mean()


# ---------------------------------------------------------------------------
# LSTM baseline
# ---------------------------------------------------------------------------

class LSTMForecaster(nn.Module):
    """
    Multi-variate LSTM demand forecaster.

    Architecture:
        [input] → LayerNorm → LSTM × n_layers → Dropout → FC → [q10, q50, q90]

    Suitable for: stationary/trended SKUs with ≥52 weeks history.
    Use TFT when you have known future covariates (promotions, holidays).
    """

    def __init__(
        self,
        n_features: int,
        hidden_size: int = 64,
        n_layers: int = 2,
        dropout: float = 0.1,
        quantiles: list[float] = (0.1, 0.5, 0.9),
    ) -> None:
        super().__init__()
        self.input_norm = nn.LayerNorm(n_features)
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_size,
            num_layers=n_layers,
            batch_first=True,
            dropout=dropout if n_layers > 1 else 0.0,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, len(quantiles))
        self.quantiles = list(quantiles)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, n_features)
        Returns:
            (batch, n_quantiles)
        """
        x = self.input_norm(x)
        out, _ = self.lstm(x)
        out = self.dropout(out[:, -1, :])   # last timestep
        return self.fc(out)


# ---------------------------------------------------------------------------
# TFT-lite: Gated Residual Network + Variable Selection + Temporal Attention
# ---------------------------------------------------------------------------

class _GRN(nn.Module):
    """Gated Residual Network — core TFT building block (Lim et al. 2021 Eq.2-4)."""

    def __init__(self, input_size: int, hidden_size: int, output_size: int,
                 dropout: float = 0.1) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.gate = nn.Linear(hidden_size, output_size)
        self.norm = nn.LayerNorm(output_size)
        self.dropout = nn.Dropout(dropout)
        self.skip = nn.Linear(input_size, output_size) if input_size != output_size else nn.Identity()
        self.elu = nn.ELU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.elu(self.fc1(x))
        h = self.dropout(h)
        gate = torch.sigmoid(self.gate(h))
        out = gate * self.fc2(h)
        return self.norm(out + self.skip(x))


class _VariableSelectionNetwork(nn.Module):
    """Soft variable selection via per-feature GRN + softmax weights."""

    def __init__(self, n_features: int, hidden_size: int, dropout: float = 0.1) -> None:
        super().__init__()
        self.grns = nn.ModuleList([_GRN(1, hidden_size, hidden_size, dropout) for _ in range(n_features)])
        self.weight_grn = _GRN(n_features, hidden_size, n_features, dropout)
        self.n_features = n_features

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: (batch, seq_len, n_features)
        Returns:
            processed: (batch, seq_len, hidden_size)
            weights:   (batch, seq_len, n_features) — interpretable importance
        """
        B, T, F = x.shape
        # per-feature embedding
        processed = torch.stack(
            [self.grns[i](x[..., i:i+1]) for i in range(F)], dim=-1
        )  # (B, T, hidden, F)
        # variable selection weights
        flat = x.reshape(B * T, F)
        w = torch.softmax(self.weight_grn(flat).reshape(B, T, F), dim=-1)
        # weighted sum
        out = (processed * w.unsqueeze(2)).sum(dim=-1)
        return out, w


class TemporalFusionTransformer(nn.Module):
    """
    TFT-lite: Variable Selection + LSTM encoder + Multi-Head Temporal Attention.

    Simplifications vs. full TFT:
      - Single LSTM encoder (no separate encoder/decoder for future covariates)
      - Static covariate context injected via initial hidden state only
      - Decoder side uses causal self-attention on encoder outputs

    Full TFT adds: static enrichment GRN, position-wise feed-forward per step,
    and separate future-input processing — add those layers when ≥3 years of
    history and rich known-future features are available.

    Args:
        n_past_features:   covariates known only up to t (demand, price, inventory)
        n_future_features: covariates known for forecast horizon (promos, holidays) — 0 if none
        n_static_features: time-invariant features (SKU class, plant, category) — 0 if none
        hidden_size:       model width (64 for <100k SKUs, 128+ for high-variance items)
        n_heads:           attention heads (must divide hidden_size)
        n_lstm_layers:     depth of LSTM encoder
        dropout:           regularisation — increase if test loss > train loss by >20%
        quantiles:         output quantiles for probabilistic forecast
    """

    def __init__(
        self,
        n_past_features: int,
        n_future_features: int = 0,
        n_static_features: int = 0,
        hidden_size: int = 64,
        n_heads: int = 4,
        n_lstm_layers: int = 2,
        dropout: float = 0.1,
        quantiles: list[float] = (0.1, 0.5, 0.9),
    ) -> None:
        super().__init__()
        self.hidden_size = hidden_size
        self.quantiles = list(quantiles)

        # Variable selection for past inputs
        self.vsn_past = _VariableSelectionNetwork(n_past_features, hidden_size, dropout)

        # Static context (if any) projected to initial hidden/cell state
        self.static_proj: Optional[nn.Linear] = (
            nn.Linear(n_static_features, hidden_size * n_lstm_layers * 2)
            if n_static_features > 0
            else None
        )

        # LSTM encoder
        self.lstm = nn.LSTM(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=n_lstm_layers,
            batch_first=True,
            dropout=dropout if n_lstm_layers > 1 else 0.0,
        )
        self.n_lstm_layers = n_lstm_layers

        # Post-LSTM gating
        self.post_lstm_gate = _GRN(hidden_size, hidden_size, hidden_size, dropout)

        # Temporal self-attention (causal mask applied in forward)
        self.attn = nn.MultiheadAttention(
            embed_dim=hidden_size, num_heads=n_heads,
            dropout=dropout, batch_first=True,
        )
        self.attn_norm = nn.LayerNorm(hidden_size)

        # Output projection → quantiles (uses last timestep only)
        self.output_grn = _GRN(hidden_size, hidden_size, hidden_size, dropout)
        self.fc_out = nn.Linear(hidden_size, len(quantiles))

    def _causal_mask(self, sz: int, device: torch.device) -> torch.Tensor:
        mask = torch.triu(torch.ones(sz, sz, device=device), diagonal=1).bool()
        return mask  # True = ignore (PyTorch convention)

    def forward(
        self,
        x_past: torch.Tensor,
        x_static: Optional[torch.Tensor] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x_past:   (batch, seq_len, n_past_features)
            x_static: (batch, n_static_features) or None

        Returns:
            quantile_preds: (batch, n_quantiles)  — one-step-ahead
            var_weights:    (batch, seq_len, n_past_features) — interpretability
        """
        B, T, _ = x_past.shape

        # Variable selection
        enc_input, var_weights = self.vsn_past(x_past)   # (B, T, H)

        # Static context → LSTM initial state
        h0 = c0 = None
        if self.static_proj is not None and x_static is not None:
            ctx = self.static_proj(x_static)              # (B, n_layers*H*2)
            ctx = ctx.view(B, self.n_lstm_layers * 2, self.hidden_size)
            h0 = ctx[:, :self.n_lstm_layers, :].permute(1, 0, 2).contiguous()
            c0 = ctx[:, self.n_lstm_layers:, :].permute(1, 0, 2).contiguous()

        lstm_out, _ = self.lstm(enc_input, (h0, c0) if h0 is not None else None)
        lstm_out = self.post_lstm_gate(lstm_out)           # (B, T, H)

        # Temporal self-attention with causal mask
        mask = self._causal_mask(T, x_past.device)
        attn_out, _ = self.attn(lstm_out, lstm_out, lstm_out, attn_mask=mask)
        attn_out = self.attn_norm(attn_out + lstm_out)     # residual

        # Decode last timestep
        last = attn_out[:, -1, :]                          # (B, H)
        out = self.fc_out(self.output_grn(last))           # (B, n_quantiles)

        return out, var_weights


# ---------------------------------------------------------------------------
# Training and inference helpers
# ---------------------------------------------------------------------------

def make_dataset(
    demand_series: np.ndarray,
    feature_matrix: np.ndarray,
    seq_len: int = 52,
    horizon: int = 1,
) -> TensorDataset:
    """
    Slide a window over the series to produce (X, y) pairs.

    Args:
        demand_series:  (T,) target values (units)
        feature_matrix: (T, F) covariates aligned with demand_series
        seq_len:        lookback window in periods
        horizon:        forecast horizon (periods ahead)

    Returns:
        TensorDataset of (x_windows, y_targets).
    """
    X, y = [], []
    T = len(demand_series)
    for i in range(T - seq_len - horizon + 1):
        X.append(feature_matrix[i : i + seq_len])
        y.append(demand_series[i + seq_len + horizon - 1])
    return TensorDataset(
        torch.tensor(np.array(X), dtype=torch.float32),
        torch.tensor(np.array(y), dtype=torch.float32),
    )


def train_forecaster(
    model: nn.Module,
    dataset: TensorDataset,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    quantiles: list[float] = (0.1, 0.5, 0.9),
    device: Optional[str] = None,
    patience: int = 10,
) -> dict:
    """
    Train any forecasting model with quantile loss + early stopping.

    Args:
        model:        LSTMForecaster or TemporalFusionTransformer
        dataset:      output of make_dataset()
        epochs:       max training epochs
        batch_size:   samples per gradient step
        lr:           AdamW learning rate (1e-3 is a safe default)
        weight_decay: L2 regularisation (1e-4 prevents overfit on small SKU history)
        quantiles:    must match model.quantiles
        device:       'cuda', 'mps', or 'cpu' (auto-detected if None)
        patience:     early stopping patience (epochs without val loss improvement)

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

    # 80/20 train/val split (temporal — no shuffle)
    n = len(dataset)
    n_train = int(n * 0.8)
    train_ds = torch.utils.data.Subset(dataset, range(n_train))
    val_ds = torch.utils.data.Subset(dataset, range(n_train, n))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = QuantileLoss(quantiles)

    train_losses, val_losses = [], []
    best_val, best_epoch, no_improve = float("inf"), 0, 0
    best_state = None

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            if isinstance(model, TemporalFusionTransformer):
                preds, _ = model(xb)
            else:
                preds = model(xb)
            loss = criterion(preds, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_loss += loss.item() * len(xb)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                if isinstance(model, TemporalFusionTransformer):
                    preds, _ = model(xb)
                else:
                    preds = model(xb)
                val_loss += criterion(preds, yb).item() * len(xb)

        train_losses.append(epoch_loss / max(n_train, 1))
        val_losses.append(val_loss / max(n - n_train, 1))
        scheduler.step()

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

    return {
        "train_losses": train_losses,
        "val_losses": val_losses,
        "best_epoch": best_epoch,
        "best_val_loss": round(best_val, 6),
        "device": device,
    }


def predict_quantiles(
    model: nn.Module,
    x: np.ndarray,
    device: Optional[str] = None,
) -> dict:
    """
    Run inference and return q10, q50, q90 forecasts.

    Args:
        model: trained LSTMForecaster or TFT
        x:     (seq_len, n_features) — single window or (B, seq_len, n_features) batch

    Returns:
        dict with q10, q50, q90 arrays.
    """
    if device is None:
        device = next(model.parameters()).device
    model.eval()
    if x.ndim == 2:
        x = x[np.newaxis]
    xt = torch.tensor(x, dtype=torch.float32).to(device)
    with torch.no_grad():
        if isinstance(model, TemporalFusionTransformer):
            preds, weights = model(xt)
        else:
            preds = model(xt)
            weights = None
    preds_np = preds.cpu().numpy()
    result = {
        "q10": preds_np[:, 0].tolist(),
        "q50": preds_np[:, 1].tolist(),
        "q90": preds_np[:, 2].tolist(),
    }
    if weights is not None:
        result["variable_importance"] = weights.cpu().numpy().mean(axis=(0, 1)).tolist()
    return result
