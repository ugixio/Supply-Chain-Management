# S&OP / Integrated Business Planning (IBP) — Enterprise Implementation Guide

**Department:** 12 — S&OP / Integrated Business Planning  
**Standard:** SCOR Digital Standard (SCOR-DS) · Wallace S&OP Methodology · IBP Best Practices  
**Version:** 1.0  
**Date:** 2026-06-20  
**Classification:** Internal — Senior Leadership & Programme Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Prerequisites & Dependencies](#2-prerequisites--dependencies)
3. [Phase 0: Assessment & AS-IS Analysis](#3-phase-0-assessment--as-is-analysis)
4. [Phase 1: Foundation & Master Data](#4-phase-1-foundation--master-data)
5. [Phase 2: Process Standardisation & Core Analytics](#5-phase-2-process-standardisation--core-analytics)
6. [Phase 3: Mathematical Models](#6-phase-3-mathematical-models)
7. [Phase 4: ML/AI Pipeline](#7-phase-4-mlai-pipeline)
8. [Phase 5: Integration & Automation](#8-phase-5-integration--automation)
9. [Phase 6: Continuous Improvement](#9-phase-6-continuous-improvement)
10. [Technology Stack & Architecture](#10-technology-stack--architecture)
11. [Change Management & Training](#11-change-management--training)
12. [Implementation KPIs](#12-implementation-kpis)
13. [Risk & Mitigation](#13-risk--mitigation)
14. [Timeline Summary](#14-timeline-summary)
15. [References](#15-references)

---

## 1. Executive Summary

Sales & Operations Planning (S&OP) and its evolved form, Integrated Business Planning (IBP), represent the single most impactful management process for aligning a firm's commercial ambitions with its operational realities across a 24-to-36-month rolling horizon. When executed with rigour, S&OP/IBP closes the chronic gap between what Sales promises, what Operations can deliver, and what Finance expects — a gap that, according to Gartner research, costs the median enterprise between 2 and 4 percent of annual revenue in suboptimal inventory positions, expediting costs, and missed customer commitments.

This implementation guide provides a complete, enterprise-grade blueprint for designing, deploying, and continuously improving an S&OP/IBP capability aligned with:

- **SCOR Digital Standard (SCOR-DS)** — PLAN process group metrics and cycle definitions
- **Wallace 5-Step S&OP Cycle** — the foundational cadence architecture
- **Oliver Wight Class A IBP** — the maturity benchmark for world-class performance
- **Chopra & Meindl Supply Chain Management, 6th Ed.** — quantitative demand/supply balancing
- **APICS Dictionary, 16th Ed.** — canonical terminology

The programme is structured across six implementation phases spanning approximately 18 months, with measurable value expected from Month 4 onwards. The target state is a monthly IBP cycle producing a single, reconciled, financially validated volume-and-value plan that drives every downstream supply chain decision.

**Target Outcomes:**

| Outcome | Baseline (Typical) | World-Class Target |
|---------|-------------------|--------------------|
| Forecast Accuracy (MAPE) | 35-50% | <15% at product family level |
| Bias (MPE) | +/-15% systematic | <+/-2% |
| Perfect Order Forecast Accuracy (SCOR) | 60-70% | >92% |
| S&OP Cycle Time (SCOR SC.1.1) | 15-20 days | <10 days |
| On-Time In-Full (OTIF) | 85-90% | >98% |
| Inventory Days Outstanding (DIO) | 55-75 days | 30-45 days |
| Revenue leakage from OOS/expediting | 2-4% of revenue | <0.5% |

---

## 2. Prerequisites & Dependencies

### 2.1 Organisational Prerequisites

Before committing to Phase 1 implementation, the programme sponsor must confirm all of the following gates are cleared:

1. **Executive Sponsor** — A C-suite owner (COO or Supply Chain VP) with budget authority and the credibility to hold Sales, Finance, and Operations accountable to a single number. Without this, S&OP collapses into a statistical exercise with no commercial teeth.

2. **Cross-functional Mandate** — Formal sign-off from Sales, Marketing, Finance, Operations, and Procurement that the IBP output is the authoritative plan and supersedes departmental shadow plans.

3. **Data Readiness** — ERP actuals (shipments, production, purchases) available at weekly granularity for a minimum of 24 months. SKU-level history for ABC-A items; product-family level acceptable for C items.

4. **Process Baseline** — A documented AS-IS process map (Phase 0 output) confirming which S&OP steps already exist, even informally, and at what maturity.

### 2.2 Technical Dependencies

```
src/departments/
  01-procurement/          # PO actuals feed into supply plan
  02-inventory/            # Stock position and DIO inputs
  03-demand-planning/      # Statistical forecasts consumed by S&OP demand review
  04-supplier-management/  # Supplier capacity constraints for supply review
  07-logistics/            # Lead time and OTIF actuals
  12-sop-planning/         # This module (IBP engine)

python/
  03_demand_planning/      # Statistical models (SMA/SES/Holt/Holt-Winters)
  12_sop_planning/         # NEW — IBP reconciliation, RCCP, scenario engine
```

**Upstream data feeds required:**

| Feed | Source System | Frequency | Format |
|------|--------------|-----------|--------|
| Sales actuals (shipped units) | ERP (SAP/Oracle) | Daily | EDIFACT INVOIC / REST |
| Open order book | CRM / OMS | Daily | REST JSON |
| Production actuals | MES / ERP | Daily | REST JSON |
| Inventory positions | WMS | Daily | REST JSON |
| Supplier confirmed capacity | Supplier portal | Weekly | EDIFACT ORDCHG |
| Financial budget (revenue, COGS) | ERP Finance | Monthly | CSV / API |
| Promotional calendar | Trade Marketing | Monthly | Excel / API |

### 2.3 Module Interface Contract

```typescript
// src/departments/12-sop-planning/domain/IBPTypes.ts

export type PlanHorizon = {
  startMonth: string;   // ISO YYYY-MM
  endMonth: string;     // ISO YYYY-MM — must be startMonth + 23 months minimum
};

export type PlanningUnit = "PRODUCT_FAMILY" | "SKU" | "CUSTOMER_SEGMENT";

export type ScenarioTag = "BASE" | "UPSIDE" | "DOWNSIDE" | "STRESS";

export type IBPCycleStatus =
  | "DEMAND_REVIEW_OPEN"
  | "SUPPLY_REVIEW_OPEN"
  | "FINANCE_REVIEW_OPEN"
  | "RECONCILIATION_OPEN"
  | "EXEC_REVIEW_OPEN"
  | "APPROVED"
  | "LOCKED";
```

---

## 3. Phase 0: Assessment & AS-IS Analysis

**Duration:** 4 weeks  
**Owner:** Programme Lead + External Facilitator (recommended)  
**Deliverable:** S&OP Maturity Assessment Report + Gap Analysis

### 3.1 Maturity Assessment Framework

Use the Oliver Wight Class A checklist adapted for SCOR-DS Plan process:

| Dimension | Level 1 (Informal) | Level 2 (Reactive) | Level 3 (Proactive) | Level 4 (Optimised) |
|-----------|-------------------|-------------------|--------------------|--------------------|
| Forecast Process | Ad hoc / spreadsheet | Monthly statistical | Consensus + bias mgmt | ML ensemble + auto-bias correction |
| Cadence | No fixed cycle | Monthly, no agenda | Fixed 5-step Wallace | <10-day cycle, exception mgmt |
| Horizon | <3 months | 3-12 months | 18-24 months | 24-36 months rolling |
| Financial Integration | None | Revenue waterfall | P&L reconciled | Driver-based financial model |
| Scenario Planning | None | Best/worst case | 3 scenarios + probabilities | RL-optimised scenario set |
| Data Quality | Manual, inconsistent | Partly automated | ERP-integrated | Real-time event-driven |

### 3.2 AS-IS Interview Protocol

Conduct structured 90-minute interviews with:
- VP Sales / Commercial Director
- VP Supply Chain / Operations
- CFO / Finance Business Partner
- Demand Planning Manager
- Procurement Director
- Warehouse / Logistics Manager

Interview questions must cover: How is the current forecast created? Who owns the number? What happens when Sales and Operations disagree? How far out does planning currently extend? What percentage of decisions are exception-driven vs. plan-driven?

### 3.3 Data Audit

```python
# python/12_sop_planning/assessment/data_audit.py
"""
AS-IS data quality audit for S&OP readiness assessment.
Checks completeness, consistency, and history depth of demand actuals.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def audit_demand_history(actuals_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Audit demand actuals for S&OP readiness.

    Parameters
    ----------
    actuals_df : pd.DataFrame
        Columns: sku_code, date (YYYY-MM-DD), shipped_units, product_family

    Returns
    -------
    dict with readiness score (0-100) and findings
    """
    findings = {}

    # History depth
    months_available = (
        actuals_df["date"].max() - actuals_df["date"].min()
    ).days / 30.44
    findings["history_months"] = round(months_available, 1)
    findings["history_adequate"] = months_available >= 24

    # Missing month detection
    sku_months = actuals_df.groupby("sku_code")["date"].nunique()
    findings["skus_with_gaps"] = int((sku_months < months_available * 0.9).sum())

    # Zero-sales periods (differentiate true zero from missing)
    zero_pct = (actuals_df["shipped_units"] == 0).mean()
    findings["zero_sales_pct"] = round(zero_pct * 100, 1)

    # Outlier detection (>3 sigma spikes)
    z_scores = np.abs(
        (actuals_df["shipped_units"] - actuals_df["shipped_units"].mean())
        / actuals_df["shipped_units"].std()
    )
    findings["outlier_count"] = int((z_scores > 3).sum())

    # Readiness score
    score = 100
    if not findings["history_adequate"]:
        score -= 30
    if findings["skus_with_gaps"] > actuals_df["sku_code"].nunique() * 0.1:
        score -= 20
    if findings["zero_sales_pct"] > 20:
        score -= 10
    if findings["outlier_count"] > len(actuals_df) * 0.02:
        score -= 10

    findings["readiness_score"] = max(score, 0)
    return findings
```

### 3.4 Gap Analysis Output

Produce a gap-to-target matrix covering all five Wallace S&OP steps, documenting current state, target state, root-cause, and remediation owner for each gap. This document becomes the Phase 1 work programme.

---

## 4. Phase 1: Foundation & Master Data

**Duration:** 6 weeks  
**Owner:** S&OP Process Owner + IT  
**Deliverable:** Clean master data, product hierarchy, S&OP calendar, governance charter

### 4.1 Product Hierarchy Design

The S&OP plan must operate at the correct level of aggregation. Too granular (SKU) and the signal is lost in noise; too aggregate (division) and the plan is operationally useless.

**Recommended 3-level hierarchy:**

```
Level 3 (Strategic / Exec Review): Business Unit / Brand
Level 2 (S&OP Review): Product Family (10-30 families typical)
Level 1 (Operational): SKU / Item
```

```typescript
// src/departments/12-sop-planning/domain/ProductHierarchy.ts

export type ProductHierarchyNode = {
  readonly id: string;
  readonly name: string;
  readonly level: 1 | 2 | 3;
  readonly parentId: string | null;
  readonly planningUnit: PlanningUnit;
  readonly abcClass: "A" | "B" | "C";
  readonly xyzClass: "X" | "Y" | "Z";
  readonly isActive: boolean;
};

export function buildFamilyRollup(
  skuActuals: SkuActuals[],
  hierarchy: ProductHierarchyNode[]
): FamilyRollup[] {
  const familyMap = new Map<string, number[]>();

  for (const actual of skuActuals) {
    const node = hierarchy.find(h => h.id === actual.skuCode && h.level === 1);
    if (!node || !node.parentId) continue;

    if (!familyMap.has(node.parentId)) {
      familyMap.set(node.parentId, []);
    }
    familyMap.get(node.parentId)!.push(actual.units);
  }

  return Array.from(familyMap.entries()).map(([familyId, units]) => ({
    familyId,
    totalUnits: units.reduce((a, b) => a + b, 0),
    skuCount: units.length,
  }));
}
```

### 4.2 S&OP Governance Charter

Document the following and obtain C-suite signatures:

- **Meeting cadence:** Fixed monthly cycle with locked dates 12 months ahead
- **Decision rights:** RACI matrix (Responsible, Accountable, Consulted, Informed) for each Wallace step
- **Escalation path:** Any gap exceeding 10% of plan escalates to Exec Review with mandatory resolution
- **One-number principle:** IBP output is the single authoritative plan; departmental shadow plans are prohibited post-go-live
- **Freeze horizon:** SKU-level plan frozen within 4 weeks of execution; family-level frozen within 8 weeks

### 4.3 S&OP Calendar Template

| Week of Month | Activity | Owner | Output |
|--------------|---------|-------|--------|
| Week 1, Days 1-2 | Statistical forecast generation | Demand Planning | Baseline statistical forecast |
| Week 1, Days 3-5 | Demand Review preparation | Commercial team | Adjusted consensus forecast |
| Week 2, Days 1-2 | Demand Review meeting | VP Sales + Demand Planning | Signed-off demand plan |
| Week 2, Days 3-5 | Supply Review preparation | Operations + Procurement | Constrained supply plan |
| Week 3, Days 1-2 | Supply Review meeting | VP Operations | Supply commitment plan |
| Week 3, Days 3-5 | Finance reconciliation | Finance BP | Revenue + P&L projection |
| Week 4, Days 1-2 | Pre-IBP reconciliation | S&OP Process Owner | Gap-resolved integrated plan |
| Week 4, Days 3-4 | Executive IBP Review | C-suite | Approved plan + decisions |
| Week 4, Day 5 | Plan publication & ERP upload | IT/Planning | Locked plan in systems |

---

## 5. Phase 2: Process Standardisation & Core Analytics

**Duration:** 8 weeks  
**Owner:** S&OP Process Owner + Demand Planning Manager  
**Deliverable:** Standardised meeting templates, KPI dashboards, bias reporting

### 5.1 Demand Review Standardisation

Every Demand Review must produce a structured output covering:

1. Statistical baseline forecast (algorithmically generated, no human override at this stage)
2. Market intelligence adjustments (promotions, new product launches, competitive events, channel shifts)
3. Unconstrained consensus demand plan by product family, month-by-month for 24 months
4. Forecast accuracy retrospective (prior month actuals vs. plan — mandatory accountability step)

### 5.2 Forecast Accuracy Reporting

```python
# python/12_sop_planning/analytics/forecast_accuracy.py
"""
Forecast accuracy computation for S&OP Demand Review reporting.
Implements MAPE, MPE (bias), RMSE, and SCOR Perfect Order Forecast Accuracy.
"""

import numpy as np
import pandas as pd
from typing import Tuple


def compute_accuracy_metrics(
    actuals: np.ndarray,
    forecast: np.ndarray,
    family_name: str
) -> dict:
    """
    Compute standard S&OP forecast accuracy metrics.

    Parameters
    ----------
    actuals : array of actual shipped units
    forecast : array of forecasted units (same length, same periods)
    family_name : product family name for reporting

    Returns
    -------
    dict of metrics per SCOR-DS and Wallace S&OP convention
    """
    assert len(actuals) == len(forecast), "Arrays must be same length"

    errors = actuals - forecast
    abs_errors = np.abs(errors)
    pct_errors = errors / np.where(actuals == 0, np.nan, actuals)

    mape = float(np.nanmean(np.abs(pct_errors)) * 100)
    mpe = float(np.nanmean(pct_errors) * 100)   # negative = over-forecast (bias)
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    mad = float(np.mean(abs_errors))

    # SCOR Perfect Order Forecast Accuracy: % periods where |error| <= 10%
    within_10pct = np.abs(pct_errors) <= 0.10
    pofa = float(np.nanmean(within_10pct) * 100)

    return {
        "family": family_name,
        "mape_pct": round(mape, 1),
        "mpe_pct": round(mpe, 1),           # positive = under-forecast
        "rmse_units": round(rmse, 0),
        "mad_units": round(mad, 0),
        "perfect_order_forecast_accuracy_pct": round(pofa, 1),
        "bias_flag": "OVER" if mpe < -5 else "UNDER" if mpe > 5 else "NEUTRAL",
    }
```

### 5.3 Supply Review Standardisation

The Supply Review translates the unconstrained demand plan into a constrained supply plan by applying:
- Confirmed supplier capacity (per `src/departments/04-supplier-management/`)
- Production/manufacturing capacity (from RCCP — see Phase 3)
- Inventory buffer policy (safety stock, min/max levels)
- Lead times and confirmed PO pipeline

The output is a **constrained supply commitment** — what Operations can actually deliver — compared against the unconstrained demand plan to produce the gap register.

---

## 6. Phase 3: Mathematical Models

**Duration:** 10 weeks (parallel with Phase 2 from Week 4)  
**Owner:** S&OP Analytics Lead + Supply Chain Modelling Team  
**Deliverable:** All mathematical models implemented, tested, and integrated into the monthly cycle

---

### 6.1 Wallace 5-Step S&OP Cycle Implementation

Tom Wallace's foundational S&OP architecture defines five sequential steps that must execute in order within each monthly cycle. The implementation below encodes the state machine that governs cycle progression.

```typescript
// src/departments/12-sop-planning/domain/WallaceCycle.ts

export type WallaceStep =
  | "STEP_1_DATA_GATHERING"
  | "STEP_2_DEMAND_PLANNING"
  | "STEP_3_SUPPLY_PLANNING"
  | "STEP_4_PRE_SOP_MEETING"
  | "STEP_5_EXECUTIVE_SOP";

export type StepOutcome = {
  step: WallaceStep;
  completedAt: string;        // ISO timestamp UTC
  approvedBy: string;         // User ID of step owner
  consensusForecastUnits: number[];   // by month, 24-36 periods
  openIssues: string[];
  escalationRequired: boolean;
};

export class WallaceCycleOrchestrator {
  private completedSteps: Map<WallaceStep, StepOutcome> = new Map();

  advanceStep(outcome: StepOutcome): void {
    const SEQUENCE: WallaceStep[] = [
      "STEP_1_DATA_GATHERING",
      "STEP_2_DEMAND_PLANNING",
      "STEP_3_SUPPLY_PLANNING",
      "STEP_4_PRE_SOP_MEETING",
      "STEP_5_EXECUTIVE_SOP",
    ];

    const expectedNext = SEQUENCE[this.completedSteps.size];
    if (outcome.step !== expectedNext) {
      throw new Error(
        `S&OP cycle violation: expected ${expectedNext}, received ${outcome.step}`
      );
    }

    this.completedSteps.set(outcome.step, outcome);
  }

  isComplete(): boolean {
    return this.completedSteps.size === 5;
  }

  getEscalations(): string[] {
    return Array.from(this.completedSteps.values())
      .filter(s => s.escalationRequired)
      .flatMap(s => s.openIssues);
  }
}
```

**Step 1 — Data Gathering (Days 1-3):**
Pull actuals from ERP, refresh statistical forecasts, update inventory positions, pull open POs and confirmed supply orders. Automated via the ERP integration layer (Phase 5).

**Step 2 — Demand Planning Meeting (Days 4-8):**
Commercial teams review statistical baseline, apply market intelligence, produce unconstrained consensus demand plan. Output: signed demand plan matrix (families x months).

**Step 3 — Supply Planning Meeting (Days 9-12):**
Operations reviews demand plan against capacity constraints, inventory positions, and supplier commitments. Output: constrained supply plan + gap register.

**Step 4 — Pre-S&OP / Reconciliation Meeting (Days 13-16):**
S&OP process owner and Finance reconcile demand plan to supply plan, resolve gaps, produce integrated plan with financial projection. Issues that cannot be resolved are packaged as decision items for Step 5.

**Step 5 — Executive S&OP / IBP Review (Days 17-20):**
C-suite reviews integrated plan, makes binding decisions on unresolved gaps, approves the plan. Output is the locked monthly plan published to ERP.

---

### 6.2 Consensus Forecast Reconciliation (Bottom-Up vs. Top-Down)

Enterprise forecasting requires reconciling two independent views that are structurally biased in opposite directions: the bottom-up SKU-level statistical forecast (typically too granular and noisy) and the top-down commercial revenue target (typically too optimistic and financially anchored).

```python
# python/12_sop_planning/models/consensus_reconciliation.py
"""
Consensus forecast reconciliation: bottom-up statistical vs. top-down commercial.
Uses weighted proportional disaggregation (Athanasopoulos et al., 2017).
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List


@dataclass
class ForecastInput:
    family_id: str
    month: str              # YYYY-MM
    statistical_units: float    # from Holt-Winters / SES
    commercial_units: float     # from Sales team judgment
    statistical_weight: float   # 0.0-1.0, calibrated from historical accuracy
    commercial_weight: float    # 0.0-1.0, must sum to 1.0 with statistical_weight


def consensus_forecast(inputs: List[ForecastInput]) -> pd.DataFrame:
    """
    Produce weighted consensus forecast for each family/month combination.

    The weights are calibrated monthly based on relative MAPE performance
    of each input stream over the trailing 6 months. Lower MAPE => higher weight.

    Returns DataFrame with columns:
        family_id, month, consensus_units, bias_adjustment, final_units
    """
    records = []
    for inp in inputs:
        assert abs(inp.statistical_weight + inp.commercial_weight - 1.0) < 1e-6, \
            "Weights must sum to 1.0"

        consensus = (
            inp.statistical_units * inp.statistical_weight
            + inp.commercial_units * inp.commercial_weight
        )

        # Bias adjustment: remove systematic over/under-forecast
        # Calibrated from trailing 12-month MPE
        bias_factor = 1.0   # Override with calibrated value from accuracy tracker
        final = consensus * bias_factor

        records.append({
            "family_id": inp.family_id,
            "month": inp.month,
            "statistical_units": round(inp.statistical_units, 0),
            "commercial_units": round(inp.commercial_units, 0),
            "consensus_units": round(consensus, 0),
            "bias_adjustment": round(bias_factor, 4),
            "final_units": round(final, 0),
        })

    return pd.DataFrame(records)


def calibrate_weights(
    accuracy_history: pd.DataFrame,
    trailing_months: int = 6
) -> dict:
    """
    Calibrate statistical vs. commercial weights from MAPE history.

    Parameters
    ----------
    accuracy_history : DataFrame with columns:
        month, stream ('statistical'|'commercial'), mape_pct
    trailing_months : rolling window for calibration

    Returns
    -------
    dict mapping stream -> weight
    """
    recent = accuracy_history.nlargest(trailing_months, "month")
    avg_mape = recent.groupby("stream")["mape_pct"].mean()

    # Inverse MAPE weighting: lower error -> higher weight
    inv_mape = 1.0 / avg_mape
    total = inv_mape.sum()
    weights = (inv_mape / total).to_dict()
    return weights
```

**Top-Down Disaggregation** for the 24-month horizon beyond the operational detail range: apply family-level consensus forecast proportionally to SKUs based on each SKU's trailing 12-month share of family volume (historical proportional split). This ensures SKU-level plans are self-consistent with the family-level IBP plan.

---

### 6.3 Financial Reconciliation (Volume Plan → Revenue Plan → P&L)

The IBP process is not complete until the volume plan is converted to a financial projection and reconciled against the Board-approved budget. This step closes the loop between Supply Chain and Finance.

```python
# python/12_sop_planning/models/financial_reconciliation.py
"""
Volume-to-value financial reconciliation for IBP Finance Review.
Converts unit volume plan to Revenue, Gross Margin, and Net Contribution.
All monetary values in integer cents per the project Money standard.
"""

import pandas as pd
from dataclasses import dataclass
from typing import List


@dataclass
class PricingMaster:
    family_id: str
    sku_code: str
    list_price_cents: int       # integer cents, never float
    standard_cogs_cents: int    # standard cost per unit, integer cents
    trade_discount_pct: float   # e.g. 0.15 for 15%


@dataclass
class VolumeRow:
    family_id: str
    month: str
    consensus_units: float
    scenario: str               # BASE | UPSIDE | DOWNSIDE


def volume_to_revenue(
    volume_plan: List[VolumeRow],
    pricing: List[PricingMaster],
    budget_revenue_cents: int
) -> pd.DataFrame:
    """
    Convert unit volume plan to financial P&L projection.

    Returns DataFrame with columns:
        month, scenario, gross_revenue_cents, net_revenue_cents,
        standard_cogs_cents_total, gross_margin_cents, gross_margin_pct,
        budget_variance_cents, budget_variance_pct
    """
    pricing_df = pd.DataFrame([p.__dict__ for p in pricing])
    volume_df = pd.DataFrame([v.__dict__ for v in volume_plan])

    # Average net price per family (volume-weighted across SKUs)
    avg_price = pricing_df.copy()
    avg_price["net_price_cents"] = (
        avg_price["list_price_cents"] * (1 - avg_price["trade_discount_pct"])
    ).astype(int)

    family_avg = avg_price.groupby("family_id").agg(
        avg_net_price=("net_price_cents", "mean"),
        avg_cogs=("standard_cogs_cents", "mean"),
    ).reset_index()

    merged = volume_df.merge(family_avg, on="family_id", how="left")
    merged["gross_revenue_cents"] = (
        merged["consensus_units"] * merged["avg_net_price"]
    ).astype(int)
    merged["cogs_total_cents"] = (
        merged["consensus_units"] * merged["avg_cogs"]
    ).astype(int)
    merged["gross_margin_cents"] = (
        merged["gross_revenue_cents"] - merged["cogs_total_cents"]
    )
    merged["gross_margin_pct"] = (
        merged["gross_margin_cents"] / merged["gross_revenue_cents"] * 100
    ).round(1)

    summary = merged.groupby(["month", "scenario"]).agg(
        gross_revenue_cents=("gross_revenue_cents", "sum"),
        cogs_total_cents=("cogs_total_cents", "sum"),
        gross_margin_cents=("gross_margin_cents", "sum"),
    ).reset_index()

    summary["gross_margin_pct"] = (
        summary["gross_margin_cents"] / summary["gross_revenue_cents"] * 100
    ).round(1)

    base_monthly_budget = budget_revenue_cents // 12
    summary["budget_variance_cents"] = (
        summary["gross_revenue_cents"] - base_monthly_budget
    )
    summary["budget_variance_pct"] = (
        summary["budget_variance_cents"] / base_monthly_budget * 100
    ).round(1)

    return summary
```

**Finance Review Gate Rules:**
- Revenue variance from budget > +/-5%: mandatory CFO escalation
- Gross margin drop > 2 percentage points vs. prior cycle: root-cause required before plan approval
- Cumulative 3-month forward variance > +/-10%: Board notification trigger

---

### 6.4 Rough-Cut Capacity Planning (RCCP)

RCCP validates that the consensus demand plan is achievable given the key resource constraints (manufacturing capacity, warehouse throughput, carrier capacity) without the computational overhead of full MRP/MPS. This is the supply-side reality check in the Supply Review.

```python
# python/12_sop_planning/models/rccp.py
"""
Rough-Cut Capacity Planning (RCCP) implementation.
Validates volume plan against key resource profiles (Bills of Resources).
Reference: APICS CPIM Part 2 — Master Planning of Resources.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ResourceProfile:
    """Bill of Resources: units of capacity consumed per unit produced per family."""
    family_id: str
    resource_id: str        # e.g. 'LINE_A', 'WAREHOUSE_DOCK_1', 'CARRIER_TRUCKLOADS'
    hours_per_unit: float   # or equivalent capacity unit


@dataclass
class ResourceCapacity:
    resource_id: str
    month: str
    available_hours: float
    utilisation_target_pct: float = 85.0  # world-class OEE target


def run_rccp(
    volume_plan: pd.DataFrame,      # columns: family_id, month, consensus_units
    profiles: List[ResourceProfile],
    capacities: List[ResourceCapacity],
) -> pd.DataFrame:
    """
    Run Rough-Cut Capacity Planning load vs. capacity analysis.

    Returns DataFrame with columns:
        resource_id, month, load_hours, available_hours, utilisation_pct,
        capacity_status ('OK' | 'WARNING' | 'OVERLOADED')
    """
    profile_df = pd.DataFrame([p.__dict__ for p in profiles])
    capacity_df = pd.DataFrame([c.__dict__ for c in capacities])

    # Compute load: sum(units * hours_per_unit) by resource and month
    load = (
        volume_plan
        .merge(profile_df, on="family_id", how="left")
        .assign(load_hours=lambda df: df["consensus_units"] * df["hours_per_unit"])
        .groupby(["resource_id", "month"])["load_hours"]
        .sum()
        .reset_index()
    )

    result = load.merge(capacity_df, on=["resource_id", "month"], how="left")
    result["utilisation_pct"] = (
        result["load_hours"] / result["available_hours"] * 100
    ).round(1)

    def classify(row: pd.Series) -> str:
        if row["utilisation_pct"] > 100:
            return "OVERLOADED"
        if row["utilisation_pct"] > row["utilisation_target_pct"]:
            return "WARNING"
        return "OK"

    result["capacity_status"] = result.apply(classify, axis=1)
    return result
```

**Interpretation rules:**
- `OVERLOADED`: Supply Review must reduce demand allocation, source alternative capacity, or defer to outer horizon. This gap goes to the reconciliation register.
- `WARNING`: Monitor; escalate if two consecutive cycles exceed target utilisation.
- `OK`: Proceed to financial reconciliation.

---

### 6.5 Supply/Demand Gap Analysis with Priority Rules

When supply is constrained below demand, a priority allocation algorithm determines which customers, channels, or regions receive available supply. This prevents the informal "squeaky wheel" allocation that typically favours the loudest Sales representative.

```typescript
// src/departments/12-sop-planning/domain/GapAnalysis.ts

export type AllocationPriority =
  | "CONTRACTUAL_OBLIGATION"   // penalty clauses, frame agreements
  | "STRATEGIC_ACCOUNT"        // top-tier customers
  | "REGULATORY_REQUIREMENT"   // e.g. healthcare, defence
  | "STANDARD"
  | "OPPORTUNISTIC";

export type GapRecord = {
  readonly familyId: string;
  readonly month: string;
  readonly demandUnits: number;
  readonly supplyUnits: number;
  readonly gapUnits: number;            // demand - supply (positive = shortfall)
  readonly gapValueCents: number;
  readonly allocationRules: AllocationRule[];
};

export type AllocationRule = {
  customerId: string;
  requestedUnits: number;
  allocatedUnits: number;
  priority: AllocationPriority;
  allocationPct: number;
};

export function allocateConstrainedSupply(
  demandLines: { customerId: string; units: number; priority: AllocationPriority }[],
  availableUnits: number
): AllocationRule[] {
  const PRIORITY_ORDER: AllocationPriority[] = [
    "REGULATORY_REQUIREMENT",
    "CONTRACTUAL_OBLIGATION",
    "STRATEGIC_ACCOUNT",
    "STANDARD",
    "OPPORTUNISTIC",
  ];

  const sorted = [...demandLines].sort(
    (a, b) =>
      PRIORITY_ORDER.indexOf(a.priority) - PRIORITY_ORDER.indexOf(b.priority)
  );

  let remaining = availableUnits;
  return sorted.map(line => {
    const allocated = Math.min(line.units, remaining);
    remaining -= allocated;
    return {
      customerId: line.customerId,
      requestedUnits: line.units,
      allocatedUnits: allocated,
      priority: line.priority,
      allocationPct: line.units > 0 ? (allocated / line.units) * 100 : 0,
    };
  });
}
```

---

### 6.6 IBP 24-36 Month Rolling Horizon

The IBP rolling horizon is the key differentiator between S&OP (operational, 12-18 months) and full IBP (strategic, 24-36 months). The outer horizon (months 13-36) drives long-lead procurement decisions, capacity investment, and strategic sourcing.

```python
# python/12_sop_planning/models/rolling_horizon.py
"""
IBP rolling horizon management.
Maintains a continuously updated 36-month forward view.
"""

import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def generate_rolling_horizon(
    anchor_month: str,      # YYYY-MM, typically current month
    horizon_months: int = 36
) -> pd.DataFrame:
    """
    Generate the rolling IBP planning horizon calendar.

    Horizon zones:
    - Months 1-3:   Execution zone (frozen at SKU level, execution only)
    - Months 4-12:  Operational S&OP zone (monthly review, family level)
    - Months 13-24: Tactical IBP zone (quarterly review, category level)
    - Months 25-36: Strategic IBP zone (semi-annual review, business unit level)
    """
    anchor = datetime.strptime(anchor_month, "%Y-%m")
    rows = []

    for i in range(horizon_months):
        month_dt = anchor + relativedelta(months=i)
        month_str = month_dt.strftime("%Y-%m")

        if i < 3:
            zone = "EXECUTION"
            review_frequency = "LOCKED"
            planning_level = "SKU"
        elif i < 12:
            zone = "OPERATIONAL"
            review_frequency = "MONTHLY"
            planning_level = "PRODUCT_FAMILY"
        elif i < 24:
            zone = "TACTICAL"
            review_frequency = "QUARTERLY"
            planning_level = "CATEGORY"
        else:
            zone = "STRATEGIC"
            review_frequency = "SEMI_ANNUAL"
            planning_level = "BUSINESS_UNIT"

        rows.append({
            "month": month_str,
            "offset": i + 1,
            "zone": zone,
            "review_frequency": review_frequency,
            "planning_level": planning_level,
        })

    return pd.DataFrame(rows)
```

---

### 6.7 SCOR Plan Metrics (POFA and SC Planning Cycle Time)

SCOR-DS defines two primary Plan-level metrics that must be tracked and reported every cycle:

**SC.1.1 — Perfect Order Forecast Accuracy (POFA):**
The percentage of planning periods where the absolute forecast error at the product family level does not exceed 10% of actual demand.

Formula: `POFA = (Periods where |Forecast - Actual| / Actual <= 10%) / Total Periods * 100`

**SC.1.2 — S&OP / SC Planning Cycle Time:**
Calendar days from Day 1 of the cycle (data extraction) to Day N when the approved plan is published to ERP. World-class target: 10 calendar days.

```typescript
// src/departments/12-sop-planning/domain/SCORMetrics.ts

export function computePOFA(
  periods: { actual: number; forecast: number }[]
): number {
  if (periods.length === 0) return 0;
  const within = periods.filter(p => {
    if (p.actual === 0) return false;
    return Math.abs(p.forecast - p.actual) / p.actual <= 0.10;
  });
  return (within.length / periods.length) * 100;
}

export function computePlanningCycleTime(
  cycleStartISO: string,    // ISO timestamp of first data pull
  planPublishedISO: string  // ISO timestamp of ERP publication
): number {
  const start = new Date(cycleStartISO);
  const end = new Date(planPublishedISO);
  return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
}
```

---

### 6.8 Scenario Planning (Base / Upside / Downside with Probability Weights)

Scenario planning elevates S&OP from a single-point forecast to a risk-informed decision process. Three to five scenarios are maintained simultaneously, each with a probability weight, and the probability-weighted expected value is used for financial provisioning.

```python
# python/12_sop_planning/models/scenario_planning.py
"""
S&OP scenario planning engine.
Maintains Base/Upside/Downside scenarios with probability weighting.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List


@dataclass
class Scenario:
    tag: str                # BASE | UPSIDE | DOWNSIDE | STRESS
    probability: float      # 0.0-1.0, all scenarios must sum to 1.0
    description: str
    demand_adjustment_pct: float    # e.g. +0.15 for Upside = +15% vs Base
    supply_adjustment_pct: float
    revenue_adjustment_pct: float


def validate_scenarios(scenarios: List[Scenario]) -> None:
    total_prob = sum(s.probability for s in scenarios)
    if abs(total_prob - 1.0) > 1e-6:
        raise ValueError(
            f"Scenario probabilities must sum to 1.0, got {total_prob:.4f}"
        )


def expected_value_plan(
    base_units: np.ndarray,
    scenarios: List[Scenario]
) -> dict:
    """
    Compute probability-weighted expected value across all scenarios.

    Parameters
    ----------
    base_units : monthly unit forecast for Base scenario (24-36 months)
    scenarios : list of Scenario objects

    Returns
    -------
    dict with expected_units, p10_units, p50_units, p90_units
    """
    validate_scenarios(scenarios)

    scenario_arrays = []
    weights = []

    for s in scenarios:
        adjusted = base_units * (1 + s.demand_adjustment_pct)
        scenario_arrays.append(adjusted)
        weights.append(s.probability)

    stacked = np.vstack(scenario_arrays)
    expected = np.average(stacked, axis=0, weights=weights)

    return {
        "expected_units": expected.round(0),
        "p10_units": np.percentile(stacked, 10, axis=0).round(0),
        "p50_units": np.percentile(stacked, 50, axis=0).round(0),
        "p90_units": np.percentile(stacked, 90, axis=0).round(0),
        "scenarios": [
            {
                "tag": s.tag,
                "probability": s.probability,
                "units": scenario_arrays[i].round(0).tolist(),
            }
            for i, s in enumerate(scenarios)
        ],
    }
```

**Standard IBP Scenario Set:**

| Scenario | Probability | Driver | Demand Adj. | Revenue Adj. |
|---------|------------|--------|------------|--------------|
| Base | 55% | Consensus plan | 0% | 0% |
| Upside | 20% | Market share gain / demand spike | +15% | +12% (mix effect) |
| Downside | 20% | Demand softening / lost account | -15% | -18% |
| Stress | 5% | Supply disruption / recession | -35% | -40% |

---

## 7. Phase 4: ML/AI Pipeline

**Duration:** 12 weeks (overlapping with Phase 3 from Week 6)  
**Owner:** Data Science Lead + S&OP Analytics Lead  
**Deliverable:** Production ML models integrated into the monthly S&OP data pipeline

---

### 7.1 Ensemble Demand Consensus (Statistical + Commercial + ML Weighted)

The ensemble model replaces the manual weighting of statistical vs. commercial forecasts with a dynamic, data-driven weighting that continuously self-calibrates.

```python
# python/12_sop_planning/ml/ensemble_demand.py
"""
Ensemble demand consensus model for IBP.
Combines statistical (Holt-Winters), commercial (Sales input), and
ML (LightGBM gradient boosting) streams with inverse-error weighting.
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_percentage_error
from typing import Tuple, List


def build_lgbm_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer time-series features for LightGBM demand model.
    Features: lags, rolling stats, calendar, promotions, price.
    """
    df = df.copy().sort_values("date")
    df["lag_1"] = df["units"].shift(1)
    df["lag_3"] = df["units"].shift(3)
    df["lag_12"] = df["units"].shift(12)
    df["rolling_mean_3"] = df["units"].rolling(3).mean()
    df["rolling_std_3"] = df["units"].rolling(3).std()
    df["rolling_mean_12"] = df["units"].rolling(12).mean()
    df["month_of_year"] = pd.to_datetime(df["date"]).dt.month
    df["year"] = pd.to_datetime(df["date"]).dt.year
    return df.dropna()


def train_lgbm_model(
    train_df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str = "units"
) -> lgb.Booster:
    """Train LightGBM model for demand forecasting."""
    params = {
        "objective": "regression",
        "metric": "mape",
        "learning_rate": 0.05,
        "num_leaves": 31,
        "min_data_in_leaf": 10,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": -1,
    }

    dtrain = lgb.Dataset(train_df[feature_cols], label=train_df[target_col])
    model = lgb.train(params, dtrain, num_boost_round=200)
    return model


def ensemble_forecast(
    statistical_forecast: np.ndarray,
    commercial_forecast: np.ndarray,
    ml_forecast: np.ndarray,
    stream_mapes: dict  # {"statistical": 12.3, "commercial": 18.1, "ml": 9.7}
) -> np.ndarray:
    """
    Produce inverse-MAPE weighted ensemble forecast.

    The stream with the lowest trailing MAPE receives the highest weight.
    This ensures the ensemble automatically adapts as model performance shifts.
    """
    inv_mapes = {k: 1.0 / v for k, v in stream_mapes.items()}
    total = sum(inv_mapes.values())
    w = {k: v / total for k, v in inv_mapes.items()}

    ensemble = (
        w["statistical"] * statistical_forecast
        + w["commercial"] * commercial_forecast
        + w["ml"] * ml_forecast
    )

    return ensemble.round(0)
```

**Model governance requirements:**
- Retrain LightGBM monthly on rolling 36-month window
- Shadow-run new model for 3 cycles before replacing production weights
- MAPE monitoring: alert if ensemble MAPE exceeds 20% at family level (triggers manual review)
- Feature importance logged monthly to detect input drift

---

### 7.2 Automated S&OP Gap Alert (Threshold-Based + ML Anomaly)

A dual-layer alert system: deterministic threshold rules fire immediately when plan vs. actual variance crosses defined limits; the ML anomaly layer detects subtler distributional shifts that precede forecast breaks.

```python
# python/12_sop_planning/ml/gap_alert.py
"""
Dual-layer S&OP gap alert system.
Layer 1: Rule-based threshold alerts (deterministic, immediate)
Layer 2: Isolation Forest anomaly detection on forecast error patterns
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from dataclasses import dataclass
from typing import List


@dataclass
class ThresholdAlert:
    family_id: str
    metric: str
    actual_value: float
    threshold: float
    severity: str   # INFO | WARNING | CRITICAL


THRESHOLD_RULES = {
    "forecast_vs_actual_pct": {"WARNING": 10.0, "CRITICAL": 20.0},
    "supply_vs_demand_gap_pct": {"WARNING": 5.0, "CRITICAL": 15.0},
    "inventory_days_outstanding": {"WARNING": 60.0, "CRITICAL": 90.0},
    "otif_pct": {"WARNING": 95.0, "CRITICAL": 90.0},  # BELOW threshold
}


def evaluate_thresholds(
    metrics: pd.DataFrame   # columns: family_id, metric_name, current_value
) -> List[ThresholdAlert]:
    """Evaluate deterministic threshold rules against current cycle metrics."""
    alerts = []
    below_metrics = {"otif_pct"}  # Alert when value is BELOW threshold

    for _, row in metrics.iterrows():
        rule = THRESHOLD_RULES.get(row["metric_name"])
        if not rule:
            continue

        for severity in ["CRITICAL", "WARNING"]:
            threshold = rule[severity]
            if row["metric_name"] in below_metrics:
                triggered = row["current_value"] < threshold
            else:
                triggered = abs(row["current_value"]) > threshold

            if triggered:
                alerts.append(ThresholdAlert(
                    family_id=row["family_id"],
                    metric=row["metric_name"],
                    actual_value=row["current_value"],
                    threshold=threshold,
                    severity=severity,
                ))
                break  # Only fire the highest severity

    return alerts


def train_anomaly_detector(
    error_history: pd.DataFrame,    # columns: family_id, month, error features
    feature_cols: List[str],
    contamination: float = 0.05     # expected anomaly rate
) -> IsolationForest:
    """
    Train Isolation Forest on historical forecast error patterns.
    Detects emerging forecast breakdown before threshold breach.
    """
    model = IsolationForest(
        contamination=contamination,
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )
    model.fit(error_history[feature_cols])
    return model


def score_anomalies(
    model: IsolationForest,
    current_errors: pd.DataFrame,
    feature_cols: List[str]
) -> pd.DataFrame:
    """
    Score current cycle errors against trained anomaly model.
    Negative score indicates anomaly; threshold typically -0.1.
    """
    current_errors = current_errors.copy()
    current_errors["anomaly_score"] = model.score_samples(
        current_errors[feature_cols]
    )
    current_errors["is_anomaly"] = current_errors["anomaly_score"] < -0.1
    return current_errors
```

---

### 7.3 NLP for Meeting Minutes → Action Item Extraction

IBP effectiveness degrades rapidly when action items from Executive Review meetings are not captured, assigned, and tracked systematically. This NLP pipeline automates extraction from meeting transcripts or notes.

```python
# python/12_sop_planning/ml/minutes_extraction.py
"""
NLP pipeline for extracting action items from S&OP/IBP meeting minutes.
Uses spaCy NER + rule-based pattern matching + HuggingFace zero-shot classification.
"""

import spacy
from transformers import pipeline
from dataclasses import dataclass
from typing import List
import re


nlp = spacy.load("en_core_web_sm")
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

ACTION_PATTERNS = [
    r"\b(will|must|shall|to|action:)\s+(\w[\w\s]{5,60})\s+by\s+(\w[\w\s/\-]{3,20})",
    r"\bAI\b[:\s]+(.{10,120}?)(?:\.|$)",   # "AI: [person] to [action]"
    r"\b(\w+)\s+to\s+([\w\s]{5,60})\s+by\s+([\w\s/\-]+\d{4})",
]

CANDIDATE_LABELS = [
    "action item with owner and deadline",
    "general discussion",
    "decision made",
    "information only",
]


@dataclass
class ActionItem:
    raw_text: str
    owner: str
    action: str
    due_date: str
    confidence: float
    source_step: str   # which Wallace step this came from


def extract_action_items(
    minutes_text: str,
    source_step: str = "UNKNOWN"
) -> List[ActionItem]:
    """
    Extract structured action items from free-text meeting minutes.

    Parameters
    ----------
    minutes_text : raw meeting minutes text
    source_step : Wallace S&OP step identifier

    Returns
    -------
    list of ActionItem objects, sorted by confidence descending
    """
    doc = nlp(minutes_text)
    candidates = []

    # Sentence-level classification
    for sent in doc.sents:
        result = classifier(
            sent.text,
            candidate_labels=CANDIDATE_LABELS,
            multi_label=False
        )
        if result["labels"][0] == "action item with owner and deadline":
            confidence = result["scores"][0]

            # Extract entities: PERSON, DATE
            persons = [e.text for e in sent.ents if e.label_ == "PERSON"]
            dates = [e.text for e in sent.ents if e.label_ == "DATE"]

            owner = persons[0] if persons else "UNASSIGNED"
            due_date = dates[0] if dates else "NOT_SPECIFIED"

            candidates.append(ActionItem(
                raw_text=sent.text.strip(),
                owner=owner,
                action=sent.text.strip(),
                due_date=due_date,
                confidence=confidence,
                source_step=source_step,
            ))

    return sorted(candidates, key=lambda x: x.confidence, reverse=True)
```

**Integration:** Action items are persisted to the IBP action register, assigned owners notified via the workflow engine, and open items reviewed at the start of each subsequent Executive Review as a mandatory first agenda item.

---

### 7.4 Reinforcement Learning for Scenario Optimisation Under Uncertainty

The RL agent learns, over successive monthly cycles, the optimal policy for allocating constrained supply across competing demand streams and scenarios. This replaces the heuristic priority rules with a learned policy that explicitly optimises for a configurable reward function (e.g., maximising revenue while maintaining OTIF > 98%).

```python
# python/12_sop_planning/ml/rl_scenario_optimizer.py
"""
Reinforcement Learning agent for S&OP scenario optimisation.
Uses Stable-Baselines3 PPO on a custom Gym environment.
Reference: Schulman et al. (2017) Proximal Policy Optimization.
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from typing import Tuple


class SandOPEnv(gym.Env):
    """
    Custom Gymnasium environment for S&OP allocation optimisation.

    State: [demand_units, supply_units, inventory_units, scenario_probs x 4]
    Action: allocation fractions across N customer segments
    Reward: weighted combination of revenue, OTIF, and inventory cost
    """

    def __init__(self, n_segments: int = 5, horizon_months: int = 12):
        super().__init__()
        self.n_segments = n_segments
        self.horizon = horizon_months
        self.current_step = 0

        # Observation: demand, supply, inventory + scenario probs (4 scenarios)
        obs_dim = 3 + 4
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(obs_dim,), dtype=np.float32
        )

        # Action: allocation fraction per segment (sums to 1.0 via softmax)
        self.action_space = spaces.Box(
            low=0.0, high=1.0, shape=(n_segments,), dtype=np.float32
        )

    def reset(self, seed=None) -> Tuple[np.ndarray, dict]:
        super().reset(seed=seed)
        self.current_step = 0
        obs = self._get_obs()
        return obs.astype(np.float32), {}

    def _get_obs(self) -> np.ndarray:
        """Return normalised observation. In production, pull from IBP data feed."""
        demand = np.random.uniform(0.5, 1.0)
        supply = np.random.uniform(0.4, demand)
        inventory = np.random.uniform(0.1, 0.4)
        scenario_probs = np.array([0.55, 0.20, 0.20, 0.05])
        return np.array([demand, supply, inventory, *scenario_probs])

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, dict]:
        # Normalise action to valid allocation fractions
        allocation = np.exp(action) / np.exp(action).sum()

        supply_fraction = np.random.uniform(0.6, 1.0)
        fulfilled = allocation * supply_fraction
        otif_score = np.mean(np.minimum(fulfilled, allocation) / (allocation + 1e-9))
        revenue_score = np.sum(fulfilled) * 0.8
        inventory_penalty = max(0, 0.3 - supply_fraction) * 0.2

        reward = float(0.5 * revenue_score + 0.4 * otif_score - 0.1 * inventory_penalty)

        self.current_step += 1
        done = self.current_step >= self.horizon
        obs = self._get_obs()
        return obs.astype(np.float32), reward, done, False, {}


def train_rl_agent(total_timesteps: int = 500_000) -> PPO:
    """
    Train PPO agent on the S&OP allocation environment.

    Parameters
    ----------
    total_timesteps : number of environment steps for training.
                     500k is sufficient for convergence on this problem size.

    Returns
    -------
    Trained PPO model ready for inference in monthly S&OP cycle.
    """
    env = SandOPEnv()
    check_env(env)

    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.95,
        verbose=1,
    )
    model.learn(total_timesteps=total_timesteps)
    return model
```

**Deployment pattern:** The RL agent runs in shadow mode for the first 6 months, producing recommended allocations alongside the human decision. After 6 months of validation against actual outcomes, the agent recommendations are elevated to the default allocation proposal with human override capability maintained.

---

## 8. Phase 5: Integration & Automation

**Duration:** 10 weeks (overlapping with Phase 4)  
**Owner:** IT / Integration Architect + S&OP Process Owner  
**Deliverable:** Automated data pipelines, ERP push, dashboard publication

### 8.1 SAP IBP Integration

SAP IBP (Integrated Business Planning) is the system-of-record for customers running SAP S/4HANA. The integration pattern uses SAP's OData V4 APIs for data exchange.

```typescript
// src/departments/12-sop-planning/integration/SAPIBPAdapter.ts

export type SAPIBPPlanVersion = {
  readonly planningVersionId: string;
  readonly description: string;
  readonly planningHorizonStart: string;
  readonly planningHorizonEnd: string;
};

export type SAPIBPKeyFigure = {
  readonly productId: string;
  readonly locationId: string;
  readonly period: string;       // YYYYMM
  readonly keyFigureId: string;  // e.g. "CONSENSUS_DEMAND", "SUPPLY_COMMIT"
  readonly quantity: number;
  readonly uom: string;
};

export async function pushConsensusToSAPIBP(
  keyFigures: SAPIBPKeyFigure[],
  config: { baseUrl: string; apiKey: string; planVersionId: string }
): Promise<{ success: boolean; uploadedCount: number; errors: string[] }> {
  const errors: string[] = [];
  let uploaded = 0;

  // Batch in groups of 500 to respect SAP OData batch size limits
  const batches = chunkArray(keyFigures, 500);

  for (const batch of batches) {
    const payload = {
      planVersionId: config.planVersionId,
      keyFigures: batch,
    };

    try {
      const response = await fetch(`${config.baseUrl}/odata/v4/KeyFigures`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "APIKey": config.apiKey,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        errors.push(`Batch failed: HTTP ${response.status}`);
      } else {
        uploaded += batch.length;
      }
    } catch (err) {
      errors.push(`Network error: ${String(err)}`);
    }
  }

  return { success: errors.length === 0, uploadedCount: uploaded, errors };
}

function chunkArray<T>(arr: T[], size: number): T[][] {
  return Array.from({ length: Math.ceil(arr.length / size) }, (_, i) =>
    arr.slice(i * size, i * size + size)
  );
}
```

### 8.2 Kinaxis RapidResponse Integration

Kinaxis is the leading platform for concurrent planning. Integration uses its REST API for scenario upload and supply feasibility response pull.

```typescript
// src/departments/12-sop-planning/integration/KinaxisAdapter.ts

export async function uploadScenarioToKinaxis(
  scenario: { tag: string; demandLines: object[] },
  config: { tenantUrl: string; bearerToken: string }
): Promise<string> {   // returns scenarioId
  const response = await fetch(
    `${config.tenantUrl}/api/v1/scenarios`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${config.bearerToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        scenarioName: `IBP_${scenario.tag}_${new Date().toISOString().slice(0, 7)}`,
        demandForecast: scenario.demandLines,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(`Kinaxis upload failed: ${response.status}`);
  }

  const body = await response.json();
  return body.scenarioId as string;
}
```

### 8.3 Anaplan Integration

Anaplan is the platform-of-choice for connected financial planning. The integration uses Anaplan's CloudWorks REST API to push the volume-to-value financial reconciliation.

```python
# python/12_sop_planning/integration/anaplan_adapter.py
"""
Anaplan CloudWorks REST API integration for IBP financial reconciliation upload.
"""

import requests
from typing import List, Dict


def push_financial_plan_to_anaplan(
    rows: List[Dict],
    config: dict
) -> bool:
    """
    Push financial reconciliation data to Anaplan model.

    Parameters
    ----------
    rows : list of dicts (month, scenario, gross_revenue_cents, gross_margin_cents)
    config : dict with keys: workspace_id, model_id, api_token, base_url

    Returns
    -------
    bool — True if upload succeeded
    """
    endpoint = (
        f"{config['base_url']}/workspaces/{config['workspace_id']}"
        f"/models/{config['model_id']}/imports"
    )

    headers = {
        "Authorization": f"AnaplanAuthToken {config['api_token']}",
        "Content-Type": "application/json",
    }

    # Convert cents to dollars for Anaplan (which stores in base currency units)
    formatted = [
        {
            "month": r["month"],
            "scenario": r["scenario"],
            "gross_revenue": r["gross_revenue_cents"] / 100,
            "gross_margin": r["gross_margin_cents"] / 100,
            "gross_margin_pct": r["gross_margin_pct"],
        }
        for r in rows
    ]

    response = requests.post(endpoint, headers=headers, json={"data": formatted})
    return response.status_code in (200, 201)
```

### 8.4 Power BI / Tableau S&OP Dashboard

The IBP dashboard must surface five critical views:
1. **Waterfall Chart** — Forecast evolution over rolling 6 cycles (prior plan vs. current plan vs. actuals)
2. **Supply/Demand Gap Heatmap** — By family and month, RAG status
3. **Scenario Fan Chart** — Base/Upside/Downside/Stress revenue bands
4. **SCOR Metric Scorecard** — POFA, cycle time, OTIF, DIO in KPI tiles
5. **Action Register** — Open items, owners, due dates, overdue flags

The dashboard data is served from a dedicated S&OP data mart table refreshed automatically after each cycle's plan is locked.

### 8.5 Excel / Google Sheets Legacy Transition

During the 6-month transition period before full ERP integration, provide read-only Excel exports for each Wallace step output. Use a structured template with:
- Protected formula cells (no manual override of system-generated numbers)
- Colour-coded variance columns (>10% red, 5-10% amber, <5% green)
- Macro-free design (compatibility with standard Office 365 without admin privileges)

### 8.6 ERP Actuals Feed

Daily automated pull of actuals from ERP via REST or EDIFACT INVOIC, loaded to the demand history table. Failures trigger a PagerDuty alert. The feed must include:
- Shipped quantity by SKU by day
- Booked (unshipped) orders
- Cancelled orders (critical for unmasking true demand)
- Returns by reason code

---

## 9. Phase 6: Continuous Improvement

**Duration:** Ongoing from Month 12  
**Owner:** S&OP Process Owner  
**Cadence:** Quarterly process review + annual deep-dive

### 9.1 Forecast Accuracy Improvement Programme

- **Root-cause analysis** every quarter for product families where MAPE > 20%
- **Outlier post-mortem** for months where actuals deviate > 20% from plan: classify as Model Error, Event Not Captured, or True Demand Shift
- **Weight recalibration** of ensemble model every quarter using trailing 6-month MAPE
- **New data source evaluation** annually (e.g., point-of-sale data, web traffic, commodity price indices)

### 9.2 Process Maturity Advancement

Annual Oliver Wight Class A assessment with third-party validation. Roadmap from Level 2 (reactive) to Level 4 (optimised) over 3 years:

| Year | Target Maturity | Focus |
|------|----------------|-------|
| Year 1 | Level 2 → Level 3 | Process discipline, data quality, POFA >85% |
| Year 2 | Level 3 → Level 3.5 | ML ensemble, financial integration, POFA >90% |
| Year 3 | Level 3.5 → Level 4 | RL optimisation, real-time event-driven, POFA >95% |

### 9.3 Bullwhip Monitoring

Compute the Bullwhip Ratio monthly at product family level:

```python
def compute_bullwhip_ratio(
    order_series: np.ndarray,
    demand_series: np.ndarray
) -> float:
    """
    Bullwhip Ratio = Var(orders) / Var(demand).
    Target: ratio close to 1.0. >2.0 indicates amplification requiring investigation.
    Reference: Lee, Padmanabhan, Whang (1997), MIT Sloan Management Review.
    """
    var_orders = np.var(order_series, ddof=1)
    var_demand = np.var(demand_series, ddof=1)
    if var_demand == 0:
        return float("nan")
    return round(var_orders / var_demand, 3)
```

---

## 10. Technology Stack & Architecture

### 10.1 Component Architecture

```
IBP Platform
├── Data Ingestion Layer
│   ├── ERP Actuals Connector (REST / EDIFACT)
│   ├── CRM Pipeline Connector (REST)
│   └── Supplier Portal Connector (EDI ORDERS/ORDCHG)
│
├── Planning Engine (Python)
│   ├── Statistical Forecasting (statsforecast / statsmodels)
│   ├── ML Ensemble (LightGBM + XGBoost + Prophet)
│   ├── RCCP Engine (custom numpy)
│   ├── Scenario Engine (Monte Carlo + RL agent)
│   └── Financial Reconciliation (pandas)
│
├── Process Orchestration (TypeScript)
│   ├── Wallace Cycle State Machine
│   ├── Gap Analysis & Allocation Engine
│   ├── Action Register
│   └── Plan Locking & ERP Upload
│
├── Integration Adapters (TypeScript + Python)
│   ├── SAP IBP Adapter
│   ├── Kinaxis RapidResponse Adapter
│   ├── Anaplan Adapter
│   └── Power BI / Tableau Data Push
│
└── Presentation Layer
    ├── IBP Dashboard (Power BI / Tableau)
    ├── Excel Export Templates
    └── Action Register UI
```

### 10.2 Data Model

```typescript
// src/departments/12-sop-planning/domain/IBPPlan.ts

export type IBPPlan = {
  readonly planId: string;              // UUID
  readonly cycleMonth: string;          // YYYY-MM
  readonly status: IBPCycleStatus;
  readonly horizon: PlanHorizon;
  readonly scenarios: IBPScenario[];
  readonly approvedAt: string | null;   // ISO UTC timestamp
  readonly approvedBy: string | null;
  readonly isDeleted: boolean;          // soft-delete only
  readonly createdAt: string;
  readonly updatedAt: string;
};

export type IBPScenario = {
  readonly scenarioId: string;
  readonly planId: string;
  readonly tag: ScenarioTag;
  readonly probability: number;
  readonly demandLines: DemandLine[];
  readonly supplyLines: SupplyLine[];
  readonly financialProjection: FinancialProjection;
};

export type DemandLine = {
  readonly familyId: string;
  readonly month: string;
  readonly consensusUnits: number;
  readonly statisticalUnits: number;
  readonly commercialUnits: number;
  readonly mlUnits: number;
};
```

---

## 11. Change Management & Training

### 11.1 Stakeholder Engagement Plan

The single most common cause of S&OP failure is not technology failure but organisational resistance. Sales teams perceive a collaborative planning process as a threat to their autonomy; Finance teams resist surrendering the budget as the primary planning anchor.

**Engagement sequence:**
1. **Month 0:** Executive alignment workshop — present business case with financial impact of current planning gap
2. **Month 1-2:** Cross-functional design workshops — co-create the process with representatives from each function (ownership increases adoption)
3. **Month 3-4:** Pilot cycle with shadow plan — run IBP alongside existing process to demonstrate value without risk
4. **Month 5+:** Full transition — shadow plan retired, IBP output is the single plan

### 11.2 Training Curriculum

| Audience | Programme | Duration | Delivery |
|---------|-----------|---------|---------|
| Executive sponsors | IBP leadership workshop | 4 hours | Facilitated |
| S&OP process owner | Full IBP practitioner course | 3 days | Classroom + simulation |
| Demand planning team | Forecasting methods + ML tools | 2 days | Classroom |
| Commercial / Sales | Demand Review participation | Half day | Facilitated |
| Finance BPs | Financial reconciliation module | 1 day | Classroom |
| IT / integration team | Platform and API training | 3 days | Technical workshop |

### 11.3 Communications Plan

Monthly newsletter to all stakeholders covering: cycle completion status, POFA trend, top 3 decisions from Executive Review, next cycle calendar. Transparency builds trust in the process.

---

## 12. Implementation KPIs

### 12.1 Process KPIs (SCOR-DS Aligned)

| KPI | SCOR Metric | Baseline | Month 6 Target | Month 12 Target | World-Class |
|-----|------------|---------|----------------|-----------------|-------------|
| Perfect Order Forecast Accuracy | SC.1.1 | 60% | 78% | 88% | >92% |
| S&OP Planning Cycle Time (days) | SC.1.2 | 18 | 14 | 10 | <10 |
| Forecast Bias (MPE) | Internal | +/-15% | +/-8% | +/-3% | <+/-2% |
| MAPE at family level | Internal | 40% | 25% | 17% | <15% |
| OTIF | RS.3.111 | 87% | 92% | 96% | >98% |
| Days Inventory Outstanding | AM.2.1 | 68 | 58 | 45 | 30-45 |
| Revenue leakage (OOS/expedite) | Internal | 3.2% | 2.0% | 1.0% | <0.5% |

### 12.2 Programme Delivery KPIs

| KPI | Target |
|-----|--------|
| Wallace Cycle steps completed on-time | >95% of cycles |
| Action items closed within SLA (2 weeks) | >85% |
| Executive Review attendance | 100% mandatory attendees |
| ERP actuals feed uptime | >99.5% |
| Dashboard refresh latency | <4 hours post cycle lock |

---

## 13. Risk & Mitigation

| # | Risk | Probability | Impact | Mitigation |
|---|------|------------|--------|-----------|
| R1 | Executive sponsor loses interest / changes role | Medium | Critical | Document mandate formally; identify backup sponsor; tie to personal OKRs |
| R2 | Sales refuses to share demand intelligence | High | High | Demonstrate WIIFM (improved OTIF means fewer escalation calls); executive mandate |
| R3 | Data quality too poor to support ML ensemble | Medium | High | Phase 0 data audit triggers data cleansing sprint before Phase 3; statistical-only fallback |
| R4 | ERP actuals feed latency / failure | Medium | Medium | Daily SLA monitoring; automated alerting; manual extraction fallback procedure |
| R5 | SAP IBP / Kinaxis integration API changes | Low | Medium | Version-pin API clients; quarterly compatibility test; adapter pattern isolates changes |
| R6 | RL agent produces suboptimal allocations in production | Medium | High | 6-month shadow mode mandatory; human override always available; reward function audit |
| R7 | Financial reconciliation rejected by CFO | Low | High | CFO Finance BP co-designs reconciliation logic in Phase 1; pre-alignment before automation |
| R8 | Forecast MAPE worsens post-ML deployment | Low | Medium | Champion-challenger framework; fallback to statistical baseline if ensemble degrades >3pp |
| R9 | SCOR POFA target missed after 12 months | Medium | Medium | Root-cause diagnostic protocol; bring in external S&OP coach for targeted intervention |
| R10 | NLP action extraction mis-classifies discussion as action | Medium | Low | All extracted items require human confirmation before assignment; minimum 0.75 confidence threshold |

---

## 14. Timeline Summary

| Phase | Weeks | Key Activities | Milestones |
|-------|-------|---------------|-----------|
| Phase 0: Assessment | 1-4 | Maturity assessment, data audit, stakeholder interviews | AS-IS report signed off |
| Phase 1: Foundation | 5-10 | Product hierarchy, governance charter, S&OP calendar | Charter signed; calendar published |
| Phase 2: Process Standardisation | 11-18 | Meeting templates, forecast accuracy reporting, demand/supply review cadence | First guided S&OP cycle complete |
| Phase 3: Mathematical Models | 15-24 | Wallace orchestrator, RCCP, consensus reconciliation, financial reconciliation, scenario engine | All models in UAT; POFA baseline established |
| Phase 4: ML/AI Pipeline | 21-32 | Ensemble model, anomaly detection, NLP extraction, RL agent (shadow) | Ensemble in production; RL in shadow |
| Phase 5: Integration | 27-36 | SAP IBP, Kinaxis, Anaplan, Power BI, ERP actuals feed | All integrations live; dashboard published |
| Phase 6: Continuous Improvement | 37+ | Quarterly reviews, maturity advancement, RL agent promotion | Oliver Wight Class A assessment Year 1 |

**Total programme duration:** 18 months to full IBP capability  
**First measurable value:** Month 4 (Process discipline + improved forecast accuracy from Phase 2)  
**Full ROI realisation:** Month 15-18 (ML ensemble + RL optimisation + financial integration complete)

---

## 15. References

1. Wallace, T.F. & Stahl, R.A. (2008). *Sales & Operations Planning: The How-To Handbook*, 3rd Edition. T.F. Wallace & Company.

2. Chopra, S. & Meindl, P. (2016). *Supply Chain Management: Strategy, Planning, and Operation*, 6th Edition. Pearson Education.

3. Lapide, L. (2004). "Sales and Operations Planning Part I: The Process." *Journal of Business Forecasting*, 23(3), 17-19.

4. ASCM / APICS (2024). *APICS Dictionary*, 16th Edition. Association for Supply Chain Management.

5. ASCM (2019). *SCOR Digital Standard (SCOR-DS)*. Supply Chain Operations Reference model. Association for Supply Chain Management.

6. Oliver Wight International (2023). *The Oliver Wight Class A Checklist for Business Excellence*, 7th Edition.

7. Gartner (2024). *Magic Quadrant for Supply Chain Planning Solutions*. Gartner Research.

8. McKinsey & Company (2022). *The S&OP renaissance: Why integrated business planning is more important than ever*. McKinsey Operations Practice.

9. Athanasopoulos, G., Hyndman, R.J., Kourentzes, N., & Petropoulos, F. (2017). "Forecasting with temporal hierarchies." *European Journal of Operational Research*, 262(1), 60-74.

10. Lee, H.L., Padmanabhan, V., & Whang, S. (1997). "The Bullwhip Effect in Supply Chains." *MIT Sloan Management Review*, 38(3), 93-102.

11. Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). *Proximal Policy Optimization Algorithms*. arXiv:1707.06347.

12. Ballou, R.H. (2004). *Business Logistics / Supply Chain Management*, 5th Edition. Pearson Education.

13. Christopher, M. (2022). *Logistics and Supply Chain Management*, 6th Edition. FT Publishing International.

14. ICC (2019). *Incoterms® 2020*. International Chamber of Commerce.

15. ISO 28000:2022. *Security and resilience — Supply chain security management systems*. International Organization for Standardization.

---

*This document is maintained by the S&OP Programme Team. Review annually or upon material change to the IBP process. All updates must pass /scm-review and /code-review before merging.*
