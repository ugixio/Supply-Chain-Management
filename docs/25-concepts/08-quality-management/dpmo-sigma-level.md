---
id: concept-dpmo-sigma-level
title: "DPMO & Sigma Level (CPT-0052)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
---
# DPMO & Sigma Level (CPT-0052)

> Defects per million opportunities, and its translation to a Six Sigma process level.
> DPMO normalizes quality across products of different complexity by counting *chances
> to fail*, not just failed units.

## Formula

    DPMO = defects / (units × opportunities_per_unit) × 1,000,000
    σ_level = Φ⁻¹(1 − DPMO/10⁶) + 1.5

| Symbol | Meaning | Unit |
|---|---|---|
| defects | total defects observed (a unit may contribute several) | count |
| opportunities_per_unit | independent ways a unit can be defective | count |
| Φ⁻¹ | inverse standard normal CDF | z |
| 1.5 | Motorola long-term drift shift | σ |

## Inputs and outputs

- **Inputs:** counts ≥ 0; zero denominator → 0.0.
- **Outputs:** DPMO (PY rounds 4 dp; TS returns raw float — same formula, different
  rounding); sigma level rounded 3 dp, clamped to 6.0 at DPMO ≤ 0 and 0.0 at
  DPMO ≥ 10⁶.
- The exact inverse normal (`scipy.stats.norm.ppf`) is the canonical z per **ADR-0028**.

## Assumptions and limits

- The **+1.5σ shift** is a convention (Motorola's allowance for long-term process
  drift), not a law of nature — "6σ = 3.4 DPMO" already includes it. Report whether a
  sigma level is short- or long-term when comparing programs.
- Opportunity counting is the soft spot: inflating opportunities deflates DPMO. Fix the
  opportunity model per product family and never revise it to make a number look better.
- **Does not apply when:** defects are not independent or opportunities are undefined
  (service processes often prefer defects-per-unit / FPY, CPT-0055).

## Worked example

12 defects across 500 units × 8 opportunities → `12/4000 × 10⁶ = 3000 DPMO`;
σ = Φ⁻¹(0.997) + 1.5 = 2.748 + 1.5 ≈ **4.248**.

## Implementations

- PY: [`calculate_dpmo`](../../../services/calc/08_quality_management/quality.py)
- PY: [`dpmo_to_sigma_level`](../../../services/calc/08_quality_management/quality.py)
- TS: [`calculateDPMO`](../../../packages/domain/src/08-quality-management/domain/InspectionRecord.ts)

## Governing rules

- **ADR-0028** — canonical z-score is the exact inverse normal; no lookup tables.

## Related

- CPT-0051 PPM — unit-based; DPMO generalizes it (PPM = DPMO at 1 opportunity/unit).
- CPT-0053 Cp/Cpk — the capability view of the same distribution.

## References

- Pyzdek & Keller, *The Six Sigma Handbook* 4th Ed.; Montgomery (2013), Ch. 1.
- Harry & Schroeder — 1.5σ shift convention.
