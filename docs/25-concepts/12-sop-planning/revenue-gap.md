---
id: concept-revenue-gap
title: "S&OP Revenue Gap (CPT-0151)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-12-sop-planning }
  - { type: governed-by, target: index-adr }
---
# S&OP Revenue Gap (CPT-0151)

> The money bridge in the S&OP executive review: what the demand plan is worth at
> plan prices, minus the financial budget — the gap the meeting must close or
> accept.

## Formula

    gap = Σ_i qty_i × price_i − budget_revenue

| Symbol | Meaning | Unit |
|---|---|---|
| qty_i / price_i | demand plan units and plan price per item | units, currency |
| budget_revenue | the financial commitment for the horizon | currency |

## Inputs and outputs

- **Inputs:** equal-length quantity and price vectors (validated); budget scalar.
- **Output:** signed gap — positive = plan above budget (upside or capacity
  question), negative = shortfall (demand actions or budget re-forecast).

## Assumptions and limits

- Plan prices must match the budget's price basis (list vs pocket price,
  currency, period) — a "gap" that is really a price-basis mismatch wastes an
  executive meeting.
- Revenue, not margin: mix shifts can close the revenue gap while opening a
  margin gap — pair with a margin bridge for the finance review (Wallace's
  integrated reconciliation).
- The gap is horizon-total; a per-period gap profile locates *when* the miss
  happens (back-loaded gaps are riskier).
- **Does not apply when:** budget and plan cover different scopes (channels,
  new-product carve-outs) — reconcile scope first.

## Worked example

Plan: 10,000 × 120 + 4,000 × 250 = 2.2M; budget 2.35M → **gap −150k** —
the demand review either finds volume/mix or finance re-forecasts.

## Governing rules

- **SOP-R*** — the executive S&OP records the gap decision (close/accept) per
  cycle.

## Related

- CPT-0147 Consensus forecast — the quantity source.
- CPT-0152 Scenarios — gap under P10/P90 demand.

## References

- Wallace (2004) — integrated reconciliation; APICS S&OP body of knowledge.
