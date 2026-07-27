---
id: concept-abc-velocity-slotting
title: "ABC Velocity Slotting (CPT-0038)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# ABC Velocity Slotting (CPT-0038)

> Assigns each SKU to a warehouse zone by its share of cumulative pick volume: the
> fastest movers earn the locations closest to dispatch.

## Formula

Sort SKUs by pick frequency descending, accumulate, and cut the ranked list where the
cumulative share `p` crosses each class boundary:

    p(k) = Σᵢ₌₁..ₖ picksᵢ / Σ picks        →  class(k) = the first class whose bound p exceeds

| Symbol | Meaning | Unit |
|---|---|---|
| p | cumulative pick share after this SKU | fraction of total picks |
| picks | SKU pick frequency in the period | picks/period |

**Slotting effectiveness** — how good the current assignment is against the best possible one:

    effectiveness = optimised_travel_distance / actual_travel_distance

One means the current slotting is already optimal, and `1 − effectiveness` is the travel that
re-slotting would remove.

## Inputs and outputs

- **Inputs:** per-SKU pick frequency (and volume, for the CPOI shown alongside);
  effectiveness takes actual and ABC-optimised travel metres (optimised > 0).
- **Output:** the class, and therefore the zone, per SKU.
- **Degenerate input:** with zero total picks the cumulative share is undefined — there is no
  ranking to cut. Placing everything in the slowest zone is a defensible answer; returning "no
  classification" is another. What is not defensible is dividing by zero and reporting a class.

## Assumptions and limits

- **Pareto-shaped demand is an assumption, not a guarantee.** The method works because a small
  share of SKUs earns most picks. With flat demand every break-point is arbitrary and the
  classification carries no information — check the curve before trusting the classes.
- Frequency measured over a season-representative window; a slotting run on peak-only
  data mis-slots seasonal items.
- **Does not apply when:** picks are goods-to-person automated, or item weight/hazard
  class dictates placement regardless of velocity.

## Project-chosen inputs

- **The number of classes, their names and every break-point.** These follow from the warehouse
  itself: how many distinct zones exist, how much closest-to-dispatch space there is, and how
  much travel a class change actually saves. Two organizations cutting the same ranked list at
  different points are both right for their own building — a break-point copied from elsewhere
  slots SKUs for someone else's layout.
- **The measurement window**, and whether picks are counted by line, by unit or by visit.
- **The re-slotting trigger** — how far below optimal the effectiveness has to fall, and how
  often re-slotting is worth its labour cost.

## Worked example

Picks: S1 = 500, S2 = 300, S3 = 150, S4 = 50 (total 1,000). Ranked cumulative shares are
50%, 80%, 95%, 100%. Where the class boundaries sit decides how those four SKUs split — cutting
at 80/95 puts S1 and S2 in the fastest class, cutting at 50/75 puts only S1 there. The ranking
is the same either way; the classification is not.

## Governing rules

- Advisory output; executing a re-slot is labor work governed by the project's own task lifecycle, and WHS-R5 (task quantities conserve).

## Related

- CPT-0037 CPOI — the volume-aware companion ranking.
- CPT-0036 FEFO — lot-level sequencing within whatever slot the SKU occupies.

## References

- Frazelle (2002), Ch. 4–5; Petersen & Schmenner (1999), *Decision Sciences* 30(2).
- Pareto/ABC framing: APICS/ASCM Dictionary, *ABC classification*.
