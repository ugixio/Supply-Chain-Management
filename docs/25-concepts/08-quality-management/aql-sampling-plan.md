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

- **Inputs:** the lot size, the inspection level, and the **AQL — which the project supplies**
  from its customer contract. An implementation that supports only one AQL column does not have a
  configurable plan; it has one plan with an AQL-shaped parameter, and the mismatch is invisible
  until a contract specifies a different level.
- **Output:** the sample size `n` with **both** `Ac` and `Re`. Returning `n` alone is not a plan:
  without the acceptance number there is nothing to compare the defect count against.
- **Read from the table, never interpolated or extrapolated** (QMS-R5). Lots beyond the largest
  tabulated range use that last row — the sample size stops growing, which is a property of the
  standard, not a shortcut.

## Assumptions and limits

- **The full scheme is more than one lookup.** ISO 2859-1 walks lot size × inspection level → a
  **code letter** → the plan, and it includes **switching rules** (normal ↔ tightened ↔ reduced,
  §9). A system with no switching does not tighten inspection when quality degrades — the part of
  the standard that actually protects the buyer is the part most often left out.
- Single sampling here; double and multiple plans have their own tables and their own acceptance
  logic — not derivable from these.
- Under single sampling `Re = Ac + 1`, so there is no gap between accept and reject: any
  "inspect further" branch belongs to double sampling, not to this plan.
- **Does not apply when:** inspection is by variables (ISO 3951) or 100% inspection is
  mandated (safety-critical characteristics).

## Worked example

*Illustrative — the AQL below is an example, not a recommendation.*

Lot of 1,000 at AQL 1.0%, general inspection level II → row (501–1200): `n = 80, Ac = 5, Re = 6`.
4 defects → accept; 6 → reject. Note what accepting means: 5 defects in 80 is 6.25% of the sample,
and the lot is still accepted — the plan bounds the *probability* of accepting a lot worse than the
AQL, it does not certify 1% quality (QMS-R6).

## Governing rules

- **QMS-R5** — the plan is read from the ISO 2859-1 table for the lot size, inspection level and
  AQL; never interpolated. **QMS-R6** — accepting a sample is not accepting a lot.
  **QMS-R7** — a defect rate is stated with its opportunity base.

## Related

- CPT-0051 PPM — the outgoing quality metric the plan protects.
- CPT-0059 NCR/SCAR cycle metrics — what a rejected lot triggers.

## References

- ISO 2859-1:1999 (Ed. 2; 2026 edition current) — single sampling, normal inspection.
- ANSI/ASQ Z1.4 — the equivalent US table family.
