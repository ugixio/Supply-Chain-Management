---
id: concept-aql-sampling-plan
title: "AQL Sampling Plan — ISO 2859-1 (CPT-0050)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
---
# AQL Sampling Plan — ISO 2859-1 (CPT-0050)

> How many units to inspect from an incoming lot, and when to accept or reject it —
> single sampling by attributes, indexed by Acceptance Quality Limit (AQL).

## Formula

Lookup, not arithmetic: lot size → `(n, Ac, Re)` from the ISO 2859-1 single-sampling
normal-inspection table (General Inspection Level II). Disposition:

    defects ≤ Ac → ACCEPT · defects ≥ Re → REJECT · Ac < defects < Re → SORT_100PCT

| Symbol | Meaning | Unit |
|---|---|---|
| n | sample size (2, 3, 5, 8, 13, 20, 32, 50, 80, 125, 200, 315, 500, 800…) | units |
| Ac / Re | acceptance / rejection number | defect count |
| AQL | worst tolerable process average | percent defective |

## Inputs and outputs

- **Inputs:** `lot_size ≥ 2`; AQL parameter (only **1.0%** table implemented in PY;
  the TS side carries Ac/Re for 1.5/4.0 but `getAQLSampleSize` returns n only).
- **Output:** PY `(n, Ac, Re)` + a `LotDisposition`; TS the sample size, capped at 200
  for lots > 3,200.
- Very large lots (> 500,000) fall back to n = 1250, Ac 21/Re 22 (PY).

## Assumptions and limits

- The standard's full scheme walks **code letters** (lot size × inspection level →
  letter → plan) and includes switching rules (normal ↔ tightened ↔ reduced,
  ISO 2859-1 §9). The implementation hardcodes the Level II / AQL 1.0 path and has
  **no switching rules** — sustained poor quality does not tighten inspection
  automatically (recorded gap).
- Single sampling only; double/multiple plans are out of scope.
- Under ISO 2859-1 single sampling, `Re = Ac + 1`, so the `SORT_100PCT` branch is
  unreachable with the built-in table — it exists for future double-sampling support.
- **Does not apply when:** inspection is by variables (ISO 3951) or 100% inspection is
  mandated (safety-critical characteristics).

## Worked example

Lot of 1,000 → row (501–1200): `n = 80, Ac = 5, Re = 6`. 4 defects → ACCEPT;
6 defects → REJECT.

## Implementations

- PY: [`get_aql_sample`](../../../services/calc/08_quality_management/quality.py)
- PY: [`lot_disposition`](../../../services/calc/08_quality_management/quality.py)
- TS: [`getAQLSampleSize`](../../../packages/domain/src/08-quality-management/domain/InspectionRecord.ts)

## Governing rules

- **QMS-R*** (incoming inspection invariants) — the inspection record lifecycle consumes
  this plan; ISO 9001:2015 §8.4/§8.6 anchor the process requirement.

## Related

- CPT-0051 PPM — the outgoing quality metric the plan protects.
- CPT-0059 NCR/SCAR cycle metrics — what a rejected lot triggers.

## References

- ISO 2859-1:1999 (Ed. 2; 2026 edition current) — single sampling, normal inspection.
- ANSI/ASQ Z1.4 — the equivalent US table family.
