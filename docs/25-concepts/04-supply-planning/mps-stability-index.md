---
id: concept-mps-stability-index
title: "MPS Stability Index (CPT-0146)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-04-supply-planning }
  - { type: governed-by, target: index-adr }
---
# MPS Stability Index (CPT-0146)

> How nervous the master production schedule is: one minus the relative churn
> between the original and revised plan. What stability is acceptable is a planning-process
> decision, and it trades against responsiveness to real demand changes.

## Formula

    SI = 1 − Σ|revised_t − original_t| / Σ original_t

| Symbol | Meaning | Unit |
|---|---|---|
| original / revised | MPS quantities per period, same horizon | units |

## Inputs and outputs

- **Inputs:** two aligned MPS vectors.
- **Output:** index ≤ 1 (1 = unchanged). Churn beyond 100% of volume drives SI
  negative — meaningful as "worse than replanning from scratch".

## Assumptions and limits

- Volume-weighted: a 10-unit move on a 1,000-unit schedule barely registers; a
  timing shift of a large order counts twice (out of one bucket, into another) —
  which is fair, since MRP explodes both changes downstream.
- Zero original volume → division by zero; guard the empty-schedule case upstream
  (recorded caveat).
- Nervousness *causes* are lot-sizing resonance (CPT-0143's known side effect),
  forecast churn (CPT-0024 FVA territory) and inside-fence changes; the index
  measures, the freeze fence cures.
- Compare like horizons only (same buckets, same items); measure inside the
  frozen/slushy fences separately — churn in the free zone is normal.
- **Does not apply when:** schedules are re-baselined (a new product ramp
  legitimately rewrites the MPS).

## Worked example

Original [100, 100, 100, 100]; revised [100, 60, 140, 100] →
churn = 40 + 40 = 80 → `SI = 1 − 80/400 = **0.80**`. A fifth of the plan moved, and note that the
*total* did not change at all — the churn is pure re-timing, which is exactly the kind of change a
capacity plan absorbs and a shop floor does not. Whether 0.80 is acceptable is the project's bar.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The fence structure — frozen, firm, free | How far out the plan may not change is a capacity and lead-time decision, not a standard |
| Who may authorize a change inside a fence | A fence nobody enforces is a comment |
| The measurement window | Churn measured over a quarter and over a week are different claims |

## Governing rules

- **SOP-R5** — attainment is measured against the plan as committed, which is what makes the
  stability of that plan measurable at all. Whether changes inside a fence require authorization is
  the project's policy; this index is the evidence of whether that policy is being kept.

## Related

- CPT-0143/0144 — lot-sizing-induced nervousness; CPT-0074 bullwhip — the
  inter-company echo of the same churn.

## References

- APICS CPIM — master scheduling; Blackburn, Kropp & Millen (1986) — MRP
  nervousness.
