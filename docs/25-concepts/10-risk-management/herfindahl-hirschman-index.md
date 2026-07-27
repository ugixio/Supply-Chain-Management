---
id: concept-herfindahl-hirschman-index
title: "Herfindahl–Hirschman Index — Supply Concentration (CPT-0073)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# Herfindahl–Hirschman Index — Supply Concentration (CPT-0073)

> How concentrated the spend (or supply) is across suppliers: the sum of squared
> shares. The antitrust metric, repurposed as single-point-of-failure detection.

## Formula

    HHI = Σ sᵢ²        where sᵢ is supplier i's share in **percentage points**

| Symbol | Meaning | Unit |
|---|---|---|
| sᵢ | supplier i's share of the category | percentage points (0–100) |
| HHI | concentration | 0–10,000 |

**The input scale is part of the definition, not a convention.** The index as published by the
US DOJ and FTC is computed on percentage points, which is what puts a monopoly at 10,000 and
`n` equal suppliers at `10,000/n`. Computing it on fractions yields the same information on a
0–1 scale, but every published reference value then reads a factor of 10,000 too high — so the
scale must be stated wherever an HHI is reported.

## Inputs and outputs

- **Inputs:** non-negative shares covering the **whole** category. Shares that do not sum to
  100 mean the tail was omitted, which understates concentration; normalizing them silently
  hides that the input was incomplete.
- **Output:** the index on its 0–10,000 scale, plus — usefully — the largest share, since the
  index alone does not say who the concentration is in.

## Assumptions and limits

- **Concentration bands are borrowed, not applicable.** The DOJ/FTC guidelines set bands for
  judging *market* concentration in merger review. Reusing those numbers as supply-risk
  thresholds is an analogy, and a weak one: a category at low concentration with a single
  qualified alternate is riskier than a highly concentrated one with instant substitutes. Where
  a project draws its own lines is its decision, and it should pair the index with
  substitutability rather than read risk off the number.
- **The index is blind to substitutability, geography and tier depth.** Two suppliers with equal
  shares score as diversified even when both buy from the same sub-tier plant.
- Shares must cover the whole category — omitting the tail understates concentration.
- **Does not apply when:** measuring *network* fragility (use CPT-0069 GNN) or
  geographic concentration (compute HHI over regions instead — same formula).

## Worked example

Spend shares 50%/30%/20% → `2500 + 900 + 400 = 3800` → **HIGH** — the 50% supplier is
a structural dependency; dual-sourcing to 35/35/30 drops HHI to 3350… still HIGH:
concentration falls slowly, which is the point of the squared term.

## Governing rules

- **RSK-R5** — a concentration index is a ratio, not a rank, so unlike a matrix score it *can* be
  compared and averaged; do not confuse the two. No rule fixes a concentration limit.

## Related

- CPT-0065 Composite supplier risk — single-source flag is the per-supplier echo.
- Kraljic (CPT-0031) — strategy response to bottleneck concentration.

## References

- US DOJ & FTC Horizontal Merger Guidelines (2010, thresholds retained in 2023) —
  HHI bands; Herfindahl (1950), Hirschman (1945).
