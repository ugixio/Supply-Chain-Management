---
id: concept-s-shape-routing
title: "S-Shape Pick Routing (CPT-0039)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# S-Shape Pick Routing (CPT-0039)

> The serpentine routing heuristic: traverse every aisle that contains a pick end-to-end,
> alternating direction, skipping empty aisles. Simple, near-optimal at high pick
> density, and the basis for the travel-distance estimate slotting is judged against.

## Formula

    distance ≈ |aisles_with_picks| × 2 × aisle_depth

Sequencing (`batch_pick_sequence`): even-indexed aisles front-to-back, odd back-to-front;
on the **last** aisle, return routing (2 × deepest pick) is used when shorter than a full
traversal.

| Symbol | Meaning | Unit |
|---|---|---|
| aisles_with_picks | distinct aisles containing ≥ 1 pick | count |
| aisle_depth | physical aisle length | m |
| (aisle, position) | pick location coordinate | index, slots from front |

## Inputs and outputs

- **Inputs:** pick locations as `(aisle_index, position)` tuples; aisle depth in metres.
- **Outputs:** `s_shape_travel_distance` → estimated metres;
  `batch_pick_sequence` → the pick list re-ordered into the walk sequence.

## Assumptions and limits

- Single block, cross-aisles only at front and back; picker enters at the front.
- The distance formula charges **2 × depth per visited aisle** — a simplification that
  ignores the front cross-aisle travel between aisles and the last-aisle return shortcut
  the sequencer applies, so it slightly overstates short routes.
- **Does not apply when:** pick density is sparse (< ~2 picks/aisle — return or largest-gap
  routing wins, Petersen & Schmenner 1999) or the layout has mid-block cross-aisles.

## Worked example

Picks in aisles {0, 2, 5}, depth 30 m → `3 × 2 × 30 = 180 m`.
Sequence: aisle 0 ascending, aisle 2 descending, aisle 5: deepest pick at slot 4 →
return = 8 < 30 ⇒ visit ascending and turn back.

## Governing rules

- None direct — travel estimation is advisory; executing the route is a labor task under
  the project's task lifecycle.

## Related

- CPT-0040 Wave optimization — batches the orders whose picks this heuristic sequences.
- CPT-0038 ABC velocity slotting — good slotting shrinks the set of visited aisles.

## References

- de Koster, Le-Duc & Roodbergen (2007), *EJOR* 182(2), 481–501.
- Petersen & Schmenner (1999), *Decision Sciences* 30(2) — routing policy comparison.
