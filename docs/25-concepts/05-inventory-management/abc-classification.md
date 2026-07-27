---
id: concept-abc-classification
title: "ABC Classification by Consumption Value (CPT-0114)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
---
# ABC Classification by Consumption Value (CPT-0114)

> Pareto ranking of SKUs by Annual Consumption Value — A-items get tight control and
> frequent counting; C-items get simple rules.

## Formula

Sort by ACV descending, accumulate share `p`:

    p ≤ 80% → A · p ≤ 95% → B · else → C
    ACV = annual_demand × unit_cost

| Symbol | Meaning | Unit |
|---|---|---|
| ACV | annual consumption value per SKU | currency |
| p | cumulative ACV share | fraction |

## Inputs and outputs

- **Inputs:** `SKUMetrics(sku_id, annual_consumption_value, demand_history)` list.
- **Output:** `{sku_id: A|B|C}`. Zero total ACV → all C (no consumption, no
  priority).

## Assumptions and limits

- Break-points (80/95) are convention, not law — but they are *this repo's* stated
  convention (mirrors CPT-0038's velocity slotting); change by decision, not
  per-analysis.
- ACV ranks by **money**, not criticality — a cheap part that stops the line is C by
  ACV and critical by consequence; pair with a criticality dimension (Kraljic,
  CPT-0031) for control policy.
- Cumulative-share classification is boundary-sensitive: a SKU near a break-point flips class on a
  small demand change, and each flip changes its control policy. Hysteresis — requiring a margin,
  or a sustained period, before reclassifying — is what stops the churn, and it belongs wherever
  the class is written rather than wherever it is computed.
- **Does not apply when:** new SKUs with no history (classify provisionally by plan).

## Worked example

ACVs 500k/300k/150k/50k (total 1M): cumulative 50%→A, 80%→A, 95%→B, 100%→C.

## Governing rules

- **INV-R4** — the value that drives the ranking is the sum of movements over a stated period;
  change the period and the ranking changes. **No rule fixes the class boundaries** — they are a
  project decision, and the class is written back deliberately, never ad hoc.

## Related

- CPT-0115 ABC-XYZ 9-box — adds the variability axis.
- CPT-0038 ABC velocity slotting — the warehouse cousin ranked by picks, not money.

## References

- Silver, Pyke & Peterson (1998) §3.3; Pareto (1896) — the 80/20 lineage.
