---
id: concept-carrier-performance-score
title: "Carrier Performance Score (CPT-0131)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-07-logistics-transportation }
  - { type: governed-by, target: index-adr }
---
# Carrier Performance Score (CPT-0131)

> One 0–100 grade per carrier: on-time delivery (60%), cargo-claim rate (25%) and
> transit-time consistency (15%).

## Formula

    otd_score      = otd% / 100 × 60
    claim_score    = (1 − min(claim%/5, 1)) × 25       (5% claims zeroes it)
    variance_score = max(0, 1 − |transit_variance_days| / 3) × 15
    score = otd_score + claim_score + variance_score

| Symbol | Meaning | Unit |
|---|---|---|
| otd% | on-time delivery rate (CPT-0126) | 0–100 |
| claim% | claims per shipment | percent |
| transit_variance_days | mean deviation from scheduled transit | days |

## Inputs and outputs

- **Output:** score, 4 dp. TS and PY implement the identical formula (the PY
  docstring states it deliberately mirrors the TS) — a rare already-converged
  pair; pin it with a U8 golden vector before it drifts.

## Assumptions and limits

- OTD dominance (60%) is the design: a carrier cannot buy back lateness with low
  claims. Claim saturation at 5% and the 3-day variance window are policy constants.
- `transit_variance_days` is a symmetric penalty (|x|) — being consistently *early*
  also costs points, deliberately (early arrivals disrupt dock schedules,
  CPT-0043/0048).
- Volume-blind: a 98% carrier on 10 shipments outscores a 96% carrier on 10,000 —
  weight by volume or require minimum shipment counts before ranking.
- **Does not apply when:** comparing across modes (sea variance days ≫ parcel) —
  score within mode peer groups.

## Worked example

OTD 94%, claims 1.2%, variance 0.8 days →
`56.4 + (1 − 0.24)·25 + (1 − 0.2667)·15 = 56.4 + 19 + 11 = **86.4**`.

## Governing rules

- **LOG-R*** — carrier records period-stamped and soft-deleted (SCM-R3).

## Related

- CPT-0126 OTD — the dominant input; CPT-0060 supplier scorecard — the same pattern
  for suppliers.

## References

- Carrier scorecard practice (APICS CLTD); SCOR RL/RS carrier metrics.
