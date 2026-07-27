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
> between the original and revised plan. Target > 0.85 (< 15% nervousness).

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
churn = 40 + 40 = 80 → `SI = 1 − 80/400 = 0.80` — below the 0.85 bar; find the
driver before the shop floor does.

## Governing rules

- **SPL-R*** — MPS changes inside the frozen fence require authorization (the
  index evidences the policy).

## Related

- CPT-0143/0144 — lot-sizing-induced nervousness; CPT-0074 bullwhip — the
  inter-company echo of the same churn.

## References

- APICS CPIM — master scheduling; Blackburn, Kropp & Millen (1986) — MRP
  nervousness.
