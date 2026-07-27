---
id: concept-first-pass-and-rolled-yield
title: "First Pass Yield & Rolled Throughput Yield (CPT-0055)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
---
# First Pass Yield & Rolled Throughput Yield (CPT-0055)

> FPY: the share of units that pass a step right first time, no rework. RTY: the chance
> a unit survives *every* step first time — the product of the step yields, and always
> worse than the worst single step suggests.

## Formula

    FPY = (units_in − defectives) / units_in × 100
    RTY = Π FPY_i / 100 × 100        (over process steps i = 1..k)

| Symbol | Meaning | Unit |
|---|---|---|
| units_in | units entering the step | count |
| defectives | units failing first time (incl. reworked) | count |
| FPY_i | step yields | percent |

## Inputs and outputs

- **Inputs:** counts ≥ 0 (`units_in = 0` → 0.0); RTY takes step FPYs as percentages
  0–100 (empty list → 0.0).
- **Output:** percentages rounded 4 dp.

## Assumptions and limits

- FPY must count **reworked units as failures** — counting rework as pass turns FPY
  into plain yield and hides the hidden factory. The defectives input must be
  first-time failures.
- RTY multiplies yields as if steps fail independently; correlated failure modes make
  the true RTY higher (double-counting) or lower (cascades) — treat as an estimate.
- **Does not apply when:** steps are optional/branching (weight by routing mix first).

## Worked example

Steps: 98%, 96%, 99% → `RTY = 0.98 × 0.96 × 0.99 = 0.9314 → 93.14%` — even with no
step below 96%, ~7 of 100 units need rework somewhere.

## Governing rules

- `isMeetingTarget` (CPT-0051) couples the FPY target with PPM — a supplier passes on
  both or neither.

## Related

- CPT-0052 DPMO — RTY ≈ e^(−DPU); the yield/defect dual.
- CPT-0054 COPQ — the money the hidden factory burns.

## References

- Pyzdek & Keller, *Six Sigma Handbook* 4th Ed. — FPY/RTY; Montgomery (2013), Ch. 1.
