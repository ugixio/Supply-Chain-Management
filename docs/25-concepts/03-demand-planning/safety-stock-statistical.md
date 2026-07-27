---
id: concept-safety-stock-statistical
title: "Safety Stock — Statistical Method (CPT-0014)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-service-level-z-score }
---
# Safety Stock — Statistical Method (CPT-0014)

> Buffer sized to a stated service level, given demand variability over a **constant** lead
> time. The most widely used of the safety-stock formulations, and the one whose assumption
> fails most often.

## Formula

    ss = z · σ_D · √LT

The √LT arises because the variances of LT independent daily demands add:
σ over the lead time = √(LT · σ_D²) = σ_D · √LT.

| Symbol | Meaning | Unit |
|---|---|---|
| z | Service-level multiplier (CPT-0003) | dimensionless |
| σ_D | Standard deviation of **daily** demand | units/day |
| LT | Average lead time | days |
| ss | Safety stock | units |

## Inputs and outputs

- **Inputs:** the standard deviation of daily demand, the average lead time in days, and the
  service-level multiplier `z` (CPT-0003).
- **`z` and the service level are not interchangeable.** Passing a service level of 0.95 where
  `z` is expected understates the buffer by more than 40%, and the result looks entirely
  plausible — so whichever the interface takes must be unambiguous in its name.
- **Output:** a quantity in units. Rounding up to an orderable quantity happens at the ordering
  boundary, not inside the formula.
- **Negative σ_D or LT are not meaningful** and produce a silently wrong number rather than an
  error unless the caller checks — σ_D is a standard deviation and LT a duration; neither can be
  below zero.

## Assumptions and limits

- **Lead time is constant.** This is the assumption that fails most often in practice; a
  supplier whose lead time swings ±3 days is not covered by this formula at all, and the
  resulting service level will fall short of target. Use CPT-0015.
- Daily demands are **independent and identically distributed**. Autocorrelated demand
  (promotions, weekday patterns) makes the √LT scaling understate true variability.
- σ_D and LT must use the **same time unit**. Mixing weekly σ with daily LT is the single
  most common error here and produces a buffer wrong by √7.
- Normality — inherited from CPT-0003.

## Worked example

σ_D = 20 units/day, LT = 9 days, and a project-chosen cycle service level of 95%:

    z = Φ⁻¹(0.95) = 1.6449          exact inverse normal (CPT-0003, ADR-0028)
    ss = 1.6449 × 20 × √9 = 1.6449 × 20 × 3 = 98.69 → 99 units when rounded up

A rounded table value of `1.65` gives 99.0 here, so the two agree after rounding — but they do not
agree in general: an interpolated table over-estimates z by up to ~1.6% at some service levels, and
that bias lands in every safety stock derived from it. **Use the exact inverse normal**; the
rounding to whole units belongs at the end, once.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The cycle service level | A service commitment weighed against the cost of capital; it sets z |
| The demand-variability estimate and its window | σ_D from a chosen history, and sample versus population estimator applied consistently |
| Whether lead time is treated as stable | This form assumes it; if it varies, use the combined form (CPT-0015) |

## Governing rules

- **INV-R5** — a physical balance cannot be negative; whether a shortfall is refused or recorded for investigation is the project's decision.

## Related

- CPT-0003 Z-score — the multiplier and its scale trap.
- CPT-0015 Combined variability — drop the constant-lead-time assumption.
- CPT-0016 Reorder point — where ss is added to cycle stock.
- CPT-0018 XYZ classification — X items justify this method; Z items rarely do.

## References

- Chopra & Meindl, 6th Ed., Ch. 11; Holt (1957); APICS CPIM 9.0.
