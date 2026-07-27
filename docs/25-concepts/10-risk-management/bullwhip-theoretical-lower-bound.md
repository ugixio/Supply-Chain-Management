---
id: concept-bullwhip-theoretical-lower-bound
title: "Bullwhip Theoretical Lower Bound (CPT-0075)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-bullwhip-ratio }
---
# Bullwhip Theoretical Lower Bound (CPT-0075)

> The floor on the bullwhip ratio that your forecasting policy and lead time impose —
> amplification you cannot remove with better information sharing, only with shorter
> lead times or calmer forecasting.

## Formula

Chen et al. (2000):

    Moving Average(p):            LB = 1 + 2L/p + 2(L/p)²        (eq. 3)
    Exponential Smoothing(α):     LB ≈ 1 + 2αL + (αL)²           (eq. 7)

| Symbol | Meaning | Unit |
|---|---|---|
| L | replenishment lead time | periods |
| p | MA window | periods |
| α | smoothing constant | 0–1 |

## Inputs and outputs

- **Inputs:** `lead_time_periods ≥ 1`; exactly one of `smoothing_alpha ∈ (0,1]` or
  `ma_window ≥ 1` (both or neither raises).
- **Output:** `{lower_bound, lead_time, forecast_method, interpretation}` (6 dp).

## Assumptions and limits

- Derived for an order-up-to policy with i.i.d.-error demand estimated by MA/ES —
  the bound is per-echelon; multi-echelon chains multiply bounds stage by stage.
- The ES bound is the paper's approximation (the exact form has a variance-ratio
  correction); treat digits past ~2 dp as indicative.
- The design levers are explicit in the formula: halving L or doubling p (or halving α)
  attacks the bound directly; information sharing only removes the *excess* above it.
- **Does not apply when:** orders are placed with full-demand-history optimal
  forecasting or the policy is not order-up-to.

## Worked example

L = 2, α = 0.3 → `LB = 1 + 2·0.6 + 0.36 = 2.56` — an observed ratio of 2.6 is nearly
all structural; the fix is lead time or α, not more data sharing.

## Governing rules

- Advisory analytics feeding CPT-0076's decomposition.

## Related

- CPT-0074 Bullwhip ratio — the observed value the bound is compared with.
- CPT-0076 Decomposition — uses `observed − LB` as excess amplification.

## References

- Chen, Drezner, Ryan & Simchi-Levi (2000), *Management Science* 46(3), eqs. 3 & 7.
