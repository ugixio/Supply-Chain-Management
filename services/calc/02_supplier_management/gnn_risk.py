"""
Graph Neural Network for supplier network risk assessment.

Models the supply chain as a directed graph where nodes are suppliers/plants
and edges are material flows.  A GNN propagates risk signals through the
network so that a tier-1 supplier's risk score reflects not only its own
KPIs but also the fragility of its upstream supply base.

Architecture:  GraphSAGE (Hamilton et al. 2017) with mean aggregation.
  Node features: [OTD, PPM_score, lead_time_cv, single_source_flag,
                  country_risk, UFLPA_exposure, audit_score, revenue_share]
  Edge features: [spend_fraction, volume_cv, substitutability] (optional)
  Output: per-node risk score in [0,1]

Why GraphSAGE vs GCN vs GAT:
  - GraphSAGE: inductive — can score new suppliers without full retraining.
  - GCN: transductive (full graph at train time) — impractical for live procurement.
  - GAT: best accuracy but 3× compute; worth switching when >500 nodes.

References:
    Hamilton et al., "Inductive Representation Learning on Large Graphs"
    (2017), NeurIPS.
    Kim & Rhee, "Proactive Supply Chain Risk Assessment with GNN" (2023), EJOR.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# Minimal graph data container (avoids PyG dependency for the data structure)
# ---------------------------------------------------------------------------

@dataclass
class SupplierGraph:
    """
    Lightweight graph structure for the supplier network.

    Attributes:
        node_features:  (N, F) float32 array — one row per supplier/plant
        edge_index:     (2, E) int64 array — [source_nodes; target_nodes]
                        edge direction: tier-2 → tier-1 → OEM
        edge_features:  (E, EF) float32 or None — optional flow attributes
        node_ids:       list of supplier identifiers (for result mapping)
        feature_names:  list of column names for node_features (for explainability)
    """
    node_features: np.ndarray
    edge_index: np.ndarray
    edge_features: Optional[np.ndarray]
    node_ids: list[str]
    feature_names: list[str]


# ---------------------------------------------------------------------------
# GraphSAGE layer
# ---------------------------------------------------------------------------

class SAGEConv(nn.Module):
    """
    Single GraphSAGE convolution (mean aggregation).

    out_i = ReLU(W · [h_i || mean_{j∈N(i)} h_j] + b)
    """

    def __init__(self, in_features: int, out_features: int) -> None:
        super().__init__()
        # Concatenate self + neighbour mean → project
        self.linear = nn.Linear(in_features * 2, out_features, bias=True)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            x:          (N, in_features)
            edge_index: (2, E) — row0=source, row1=target

        Returns:
            (N, out_features)
        """
        N = x.size(0)
        src, dst = edge_index[0], edge_index[1]

        # Neighbour mean aggregation (incoming edges = upstream suppliers)
        agg = torch.zeros(N, x.size(1), device=x.device)
        count = torch.zeros(N, 1, device=x.device)
        agg.index_add_(0, dst, x[src])
        count.index_add_(0, dst, torch.ones(len(src), 1, device=x.device))
        count = count.clamp(min=1)
        agg = agg / count

        # Concatenate self + aggregated
        out = torch.cat([x, agg], dim=1)
        return F.relu(self.linear(out))


# ---------------------------------------------------------------------------
# Full GNN model
# ---------------------------------------------------------------------------

class SupplierRiskGNN(nn.Module):
    """
    2-layer GraphSAGE for supplier risk scoring.

    Two layers = 2-hop neighbourhood: tier-1 risk reflects tier-2 exposure.
    Add a 3rd layer for OEMs with deep tier-3 visibility.

    Args:
        n_node_features: dimension of per-supplier feature vector
        hidden_size:     intermediate representation width (64 for <500 nodes)
        dropout:         regularisation between layers
    """

    def __init__(
        self,
        n_node_features: int,
        hidden_size: int = 64,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        self.conv1 = SAGEConv(n_node_features, hidden_size)
        self.conv2 = SAGEConv(hidden_size, hidden_size // 2)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size // 2, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )

    def forward(
        self,
        node_features: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            node_features: (N, F)
            edge_index:    (2, E)

        Returns:
            risk_scores: (N, 1) in [0, 1]
        """
        h = self.conv1(node_features, edge_index)
        h = self.dropout(h)
        h = self.conv2(h, edge_index)
        h = self.dropout(h)
        return self.classifier(h)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_gnn(
    model: SupplierRiskGNN,
    graph: SupplierGraph,
    labels: np.ndarray,
    train_mask: np.ndarray,
    val_mask: np.ndarray,
    epochs: int = 200,
    lr: float = 5e-3,
    weight_decay: float = 1e-4,
    device: Optional[str] = None,
    patience: int = 20,
) -> dict:
    """
    Semi-supervised node classification (Binary Cross-Entropy on labelled nodes).

    Args:
        model:       SupplierRiskGNN
        graph:       SupplierGraph with node_features and edge_index
        labels:      (N,) binary — 1 = HIGH RISK supplier (from audit/incident data)
        train_mask:  (N,) bool — nodes with known labels used for training
        val_mask:    (N,) bool — held-out labelled nodes for early stopping
        epochs:      max training iterations
        lr:          Adam learning rate (5e-3 converges well on small supplier graphs)
        weight_decay: L2 regularisation
        device:      compute device (auto-detected if None)
        patience:    early stopping patience in epochs

    Returns:
        dict with train_losses, val_losses, best_epoch, val_auc.
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    x = torch.tensor(graph.node_features, dtype=torch.float32).to(device)
    ei = torch.tensor(graph.edge_index, dtype=torch.long).to(device)
    y = torch.tensor(labels, dtype=torch.float32).to(device)
    tm = torch.tensor(train_mask, dtype=torch.bool).to(device)
    vm = torch.tensor(val_mask, dtype=torch.bool).to(device)

    # Class imbalance: high-risk suppliers are typically <15% of the network
    pos_weight = torch.tensor([(~train_mask).sum() / max(train_mask.sum(), 1)],
                               dtype=torch.float32).to(device)
    criterion = nn.BCELoss(reduction="mean")

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    train_losses, val_losses = [], []
    best_val, best_epoch, no_improve = float("inf"), 0, 0
    best_state = None

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        scores = model(x, ei).squeeze()
        loss = criterion(scores[tm], y[tm])
        loss.backward()
        optimizer.step()
        train_losses.append(loss.item())

        model.eval()
        with torch.no_grad():
            scores_val = model(x, ei).squeeze()
            val_loss = criterion(scores_val[vm], y[vm]).item()
        val_losses.append(val_loss)

        if val_loss < best_val:
            best_val = val_loss
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
    }


# ---------------------------------------------------------------------------
# Inference and explainability
# ---------------------------------------------------------------------------

def score_supplier_network(
    model: SupplierRiskGNN,
    graph: SupplierGraph,
    device: Optional[str] = None,
    risk_threshold: float = 0.6,
) -> list[dict]:
    """
    Score all suppliers in the graph and return ranked risk assessments.

    Args:
        model:          trained SupplierRiskGNN
        graph:          SupplierGraph to score
        risk_threshold: score above which a supplier is flagged HIGH RISK

    Returns:
        list of dicts (sorted by risk_score descending):
          { supplier_id, risk_score, risk_tier, upstream_exposure }
    """
    if device is None:
        device = next(model.parameters()).device
    model.eval()
    x = torch.tensor(graph.node_features, dtype=torch.float32).to(device)
    ei = torch.tensor(graph.edge_index, dtype=torch.long).to(device)

    with torch.no_grad():
        scores = model(x, ei).squeeze().cpu().numpy()

    # Upstream exposure: fraction of direct upstream neighbours that are HIGH RISK
    src, dst = graph.edge_index[0], graph.edge_index[1]
    upstream_exposure = {}
    for node_idx in range(len(graph.node_ids)):
        up_mask = dst == node_idx
        if up_mask.any():
            up_scores = scores[src[up_mask]]
            upstream_exposure[node_idx] = float(np.mean(up_scores > risk_threshold))
        else:
            upstream_exposure[node_idx] = 0.0

    results = []
    for i, sid in enumerate(graph.node_ids):
        s = float(scores[i])
        results.append({
            "supplier_id": sid,
            "risk_score": round(s, 4),
            "risk_tier": "HIGH" if s >= risk_threshold else "MEDIUM" if s >= 0.35 else "LOW",
            "upstream_exposure": round(upstream_exposure[i], 4),
            "combined_risk": round(0.7 * s + 0.3 * upstream_exposure[i], 4),
        })

    return sorted(results, key=lambda r: r["combined_risk"], reverse=True)
