---
id: concept-transport-mode-selection
title: "Transport Mode Selection (CPT-0130)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-07-logistics-transportation }
  - { type: governed-by, target: index-adr }
---
# Transport Mode Selection (CPT-0130)

> Ranks road/sea/air/rail/multimodal for a shipment on weighted cost (40%), transit
> time (35%) and CO₂ (25%), with feasibility gates on the time and carbon budgets.

## Formula

Per mode, from profile (cost/t-km, speed km/h, kgCO₂e/t-km):

    est_cost = cost_rate × tonnes × km · est_days = km / speed / 24
    est_co2 = co2_rate × tonnes × km
    feasible ⇔ est_days ≤ budget ∧ (co2_budget absent ∨ est_co2 ≤ co2_budget)
    score = (1 − cost/max_cost)·40 + (1 − days/max_days)·35 + (1 − co2/max_co2)·25
    rank by (feasible desc, score desc)

| Symbol | Meaning | Unit |
|---|---|---|
| profiles | ROAD (0.15, 80, 0.062) · SEA (0.01, 25, 0.008) · AIR (4.50, 800, 0.602) · RAIL (0.05, 100, 0.022) · MULTIMODAL (0.08, 60, 0.030) | $/t-km, km/h, kg/t-km |

## Inputs and outputs

- **Inputs:** distance, weight, volume (accepted but unused — recorded gap: no
  volumetric cost leg), transit budget days, optional CO₂ budget.
- **Output:** ranked mode list with estimates, feasibility and scores +
  `recommended` (the top-ranked — note it is the best *scored*, which may be an
  infeasible mode if none are feasible; check the flag).

## Assumptions and limits

- Max-normalized scoring makes scores **relative to the candidate set** — adding or
  removing a mode changes every score; compare within one run only.
- Speeds are port-to-port cruising averages — no dwell, customs or transshipment
  time; sea/multimodal real doors-to-door times are materially longer.
- **CO₂ factor divergence (recorded):** this table (SEA 0.008, RAIL 0.022,
  MULTIMODAL 0.030) differs from the module's own `EMISSION_FACTORS`
  (0.010/0.028/0.045) used by CPT-0123 — same file, two carbon truths; align.
- Weights 40/35/25 are policy — governed values.
- **Does not apply when:** the lane has contracted carriers/rates — use the lane
  card (CPT-0124), not generic profiles.

## Worked example

8,000 km, 12 t, budget 15 days: AIR feasible (0.4 d) but cost 432k$; SEA 13.3 d
feasible at 960$; RAIL 3.3 d at 4,800$ → RAIL typically wins the blend
(cheap-enough, fast-enough, low CO₂).

## Implementations

- PY: [`mode_selection`](../../../services/calc/07_logistics_transportation/logistics.py)

## Governing rules

- Advisory; the executed choice prices via CPT-0124 and reports via CPT-0123.

## Related

- CPT-0123 CO₂ · CPT-0124 freight cost · CPT-0127 transit P95.

## References

- Ballou (2004), Ch. 6 — mode selection economics.
