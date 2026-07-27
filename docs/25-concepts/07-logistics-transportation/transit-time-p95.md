---
id: concept-transit-time-p95
title: "Transit Time P95 Commitment (CPT-0127)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-07-logistics-transportation }
  - { type: governed-by, target: index-adr }
---
# Transit Time P95 Commitment (CPT-0127)

> The delivery promise you can keep 95% of the time: mean transit plus 1.645
> standard deviations, under a normal transit-time model.

## Formula

    P95 = μ + 1.645 × σ

| Symbol | Meaning | Unit |
|---|---|---|
| μ, σ | lane transit-time mean / std | days |
| 1.645 | z at the 95th percentile | dimensionless |

## Inputs and outputs

- **Output:** committed days (2 dp) — the lane input to ATP/CTP date promising
  (CPT-0087).

## Assumptions and limits

- **Hardcoded z = 1.645** — a rounded constant, not the ADR-0028 exact inverse
  normal, and not parameterized by service level (recorded divergence; the repo's
  canonical z machinery should supply it).
- Transit times are right-skewed in practice (customs holds, weather) — a normal
  model *understates* the true P95; with enough history prefer the empirical 95th
  percentile.
- μ and σ must come from the same lane/mode/season segment; pooling lanes inflates σ
  and pads every promise.
- **Does not apply when:** n is small (< ~30 shipments) — the normal approximation
  and the σ estimate are both unstable.

## Worked example

Lane μ = 6.2 days, σ = 1.4 → `P95 = 6.2 + 1.645 × 1.4 = 8.50 days` — promise 9
calendar days.

## Governing rules

- **ADR-0028** — the z-score source this should adopt.

## Related

- CPT-0087 CTP — consumes lane promises; CPT-0003 service-level z — the canonical z.

## References

- Chopra & Meindl, Ch. 13 — service-time promising; ADR-0028.
