---
id: concept-newsvendor-models
title: "Newsvendor Models — Single-Period & Price-Setting (CPT-0121)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
---
# Newsvendor Models — Single-Period & Price-Setting (CPT-0121)

> Optimal one-shot order quantity under uncertain demand (perishables, seasonal buys,
> promotions): balance the cost of overage against underage via the critical ratio —
> plus the Petruzzi–Dada extension that sets price and quantity together.

## Formula

    CR = (p − c) / (p − s)          (underage cost over total unit mismatch cost)
    Q* = F⁻¹(CR)
      NORMAL:  Q* = μ + Φ⁻¹(CR)·σ
      POISSON: smallest Q with F(Q) ≥ CR
    E[stockout] = σ(φ(z) − z(1 − Φ(z)))   (normal loss function)
    E[profit] = p·E[sales] + s·E[leftover] − c·Q*

Price-setting variant: demand D(p) = a − b·p + ε, ε ~ N(0, σ²); grid-search p over
[p_min, p_max], inner newsvendor Q*(p), pick the (p, Q) with max expected profit.

| Symbol | Meaning | Unit |
|---|---|---|
| p / c / s | price / unit cost / salvage (p > c > s) | currency |
| μ, σ | demand mean/std | units |
| a, b | linear demand intercept/slope | units, units/price |

## Inputs and outputs

- **Inputs:** validated p > c, s < c, μ > 0; distribution NORMAL or POISSON; the
  joint model wants b > 0, price bounds, grid size ≥ 2.
- **Outputs:** Q*, CR, expected profit/sales/leftover/stockout, achieved service
  level; joint model adds optimal price and the top-5 price-quantity frontier.

## Assumptions and limits

- Single period, no carryover, no reorder — the defining frame; multi-period
  problems belong to (r,Q)/(s,S) (CPT-0120).
- Normal branch can recommend negative-ish Q at very low CR (clamped to 0); Poisson
  branch is exact for count demand.
- The joint model's grid search is robust but coarse (50 points default) — the
  analytic Petruzzi–Dada conditions would refine; grid granularity bounds price
  precision.
- Unmodelled: goodwill cost of stockouts (add to underage as p − c + goodwill),
  fixed order costs.
- **Does not apply when:** demand is influenced by inventory display (newsvendor
  with demand-stimulating stock) or supply is capacitated.

## Worked example

p = 24, c = 10, s = 4 → CR = 14/20 = 0.70 → z = 0.524; μ = 500, σ = 120 →
**Q* = 563**; E[stockout] = 120·(0.3477 − 0.524·0.30) ≈ 22.9 → E[sales] ≈ 477 →
E[profit] ≈ 24·477 + 4·86 − 10·563 = **6,162**.

## Implementations

- PY: [`newsvendor`](../../../services/calc/05_inventory_management/stock_balance.py)
- PY: [`newsvendor_price_quantity_joint`](../../../services/calc/05_inventory_management/stock_balance.py)

## Governing rules

- **ADR-0028** exact inverse normal for z.

## Related

- CPT-0120 (r,Q)/(s,S) — the multi-period counterpart.
- CPT-0003 Service-level z — the same Φ⁻¹ machinery.

## References

- Arrow, Harris & Marschak (1951); Petruzzi & Dada (1999), *Operations Research*
  47(2); Chopra & Meindl, Ch. 13.
