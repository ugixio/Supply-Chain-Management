---
id: concept-warehouse-labour-productivity
title: "Warehouse Labour Productivity (CPT-0045)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Warehouse Labour Productivity (CPT-0045)

> Output per labour hour for the two big touch processes — picking (lines per hour) and
> receiving (units per hour) — graded against technology-tier benchmarks.

## Formula

    LPH = lines_picked / labour_hours
    UPH = units_received / labour_hours

Picking grade (PY): `<60 BELOW_STANDARD · 60–120 RF_SCANNER · 120–200 VOICE_PICKING ·
>200 AUTOMATED`. Receiving benchmark: world-class ≥ 120 units/h (WERC 2022).

| Symbol | Meaning | Unit |
|---|---|---|
| lines_picked | order lines completed | count |
| units_received | units processed inbound | count |
| labour_hours | direct labour time | hours |

## Inputs and outputs

- **Inputs:** counts ≥ 0; hours > 0 (PY receiving raises on 0; PY picking returns a
  N/A record; TS returns `null`).
- **Outputs:** rate + benchmark grade. TS `linesPerHour` computes per-task LPH from the
  task's `startedAt`/`completedAt` timestamps, rounded to 2 dp, and returns `null`
  unless the task is `COMPLETE` with positive duration.

## Assumptions and limits

- Rates are technology-dependent — the grade bands identify *which* technology the
  measured rate resembles, not personal performance; SKU cube, order profile and travel
  distance move the number materially (Frazelle 2016).
- Receiving benchmark assumes case-level ambient receipt; pallet-in/pallet-out or
  each-level receipt need different bars.
- **Does not apply when:** comparing across warehouses with different order profiles
  without normalising (use cost per line, CPT-0046, for money-comparable output).

## Worked example

Picker completes 540 lines in 6.0 h → `LPH = 90` → RF_SCANNER band.
Receiving crew 960 units in 8 h → `UPH = 120` → benchmark met (world-class threshold).

## Implementations

- PY: [`picking_productivity`](../../../services/calc/06_warehouse_management/slotting.py)
- PY: [`receiving_productivity`](../../../services/calc/06_warehouse_management/warehouse_kpis.py)
- TS: [`linesPerHour`](../../../packages/domain/src/06-warehouse-management/domain/LaborTask.ts)

## Governing rules

- **WHS-R4** — completion quantities are non-negative; the TS metric reads them.
- **WHS-R2** — LPH only exists for a task that legally reached `COMPLETE`.

## Related

- CPT-0046 Labour cost per line — the financial view of the same output.
- CPT-0049 Labour staffing forecast — uses historical LPH as its input.

## References

- Frazelle (2016) 2nd Ed., Ch. 2; WERC DC Measures Study (2022).
