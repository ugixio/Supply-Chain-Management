---
id: concept-rq-and-ss-policies
title: "(r,Q) and (s,S) Replenishment Policies (CPT-0120)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-service-level-z-score }
---
# (r,Q) and (s,S) Replenishment Policies (CPT-0120)

> The two classical replenishment policies: continuous review — order Q when the
> position hits r; periodic review — every R periods, if position ≤ s order up to S.

## Formula

    (r,Q):  μ_L = μ·L · σ_L = σ·√L · z = Φ⁻¹(SL)
            r = μ_L + z·σ_L · Q = EOQ = √(2·D_annual·S / (h·c))
            D_annual = μ × 52 (weekly-period assumption)
    (s,S):  effective lead time L' = L + R
            s = μ_{L'} + z·σ_{L'} · S = s + EOQ · Q_avg = S − s

| Symbol | Meaning | Unit |
|---|---|---|
| μ, σ | demand mean/std per period | units |
| L / R | lead time / review period | periods |
| SL | cycle service level ∈ (0,1) | fraction |
| S (ordering), h·c | order cost; holding rate × unit cost | currency |

## Inputs and outputs

- **Inputs:** validated positives; SL in (0,1); z via exact inverse normal
  (ADR-0028).
- **Outputs:** (r,Q): full cost breakdown (annual holding = ½·Q·h·c, ordering =
  D/Q·S); (s,S): `{s, S, Q_avg, safety_stock, effective_lead_time}` — the (s,S)
  computation *reuses* the (r,Q) function at L+R.

## Assumptions and limits

- Normal lead-time demand; lead time deterministic (σ_LT = 0 — the Method-4 variant
  with lead-time variance is CPT-0013's territory).
- **Hardcoded 52 periods/year** in the EOQ annualization — daily-period users get a
  wrong D_annual by 7×; parametrize before non-weekly use (recorded caveat).
- Setting S = s + EOQ is a standard heuristic, not the optimal (s,S) (which needs
  stochastic dynamic programming); good when EOQ ≫ σ_L.
- Cycle service level (α), not fill rate (β) — CPT-0088 note applies.
- **Does not apply when:** demand intermittent (CPT-0006) or capacity-constrained
  ordering.

## Worked example

μ = 200/wk, σ = 40, L = 2, SL 0.95 (z = 1.645), S = $50, h·c = $2/unit/yr:
μ_L = 400, σ_L = 56.57 → ss = 93.05 → **r = 493**; D = 10,400/yr →
EOQ = √(2·10400·50/2) = 721 → **Q = 721**. (s,S) with R = 1: L' = 3 →
s = 600 + 1.645·69.28 = 714 → S = 714 + 721 = **1,435**.

## Implementations

- PY: [`reorder_point_and_quantity`](../../../services/calc/05_inventory_management/stock_balance.py)
- PY: [`sS_policy_parameters`](../../../services/calc/05_inventory_management/stock_balance.py)

## Governing rules

- **ADR-0028** exact z; **SCM-R1** — the policy triggers orders; it never authorizes
  negative stock.

## Related

- CPT-0021 EOQ · CPT-0012/0013 safety stock · CPT-0122 RL policy (the learned
  alternative benchmarked against (s,S)).

## References

- Silver, Pyke & Peterson, Ch. 7–8; Chopra & Meindl, Ch. 11–12; Harris (1913) EOQ.
