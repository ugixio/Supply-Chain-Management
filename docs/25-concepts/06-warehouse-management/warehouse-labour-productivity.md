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

> Output per labour hour for the two big touch processes: picking, measured in lines per hour,
> and receiving, measured in units per hour.

## Formula

    LPH = lines_picked / labour_hours
    UPH = units_received / labour_hours

A measured rate says as much about the **method** as about the people: paper picking, RF
scanning, voice picking and goods-to-person automation occupy visibly different throughput
ranges, so a rate is only comparable against the same technology. What counts as good is a
project's own bar, set from its automation level, product mix and labour market — published
surveys report observed ranges, not requirements.

| Symbol | Meaning | Unit |
|---|---|---|
| lines_picked | order lines completed | count |
| units_received | units processed inbound | count |
| labour_hours | direct labour time | hours |

## Inputs and outputs

- **Inputs:** non-negative counts and **positive** labour hours. Zero hours has no rate; a
  measure that reports one anyway is reporting a division by zero.
- **Outputs:** the rate. Computing it per task from start and completion timestamps only makes
  sense for a *finished* task — an in-progress task has an elapsed time but not a duration.
- **What counts as direct labour hours is a definition to state**, since including or excluding
  breaks, travel and idle time changes the rate substantially and silently.

## Assumptions and limits

- Rates are technology-dependent, so a rate never measures personal performance on its own;
  SKU cube, order profile and travel
  distance move the number materially (Frazelle 2016).
- Receiving benchmark assumes case-level ambient receipt; pallet-in/pallet-out or
  each-level receipt need different bars.
- **Does not apply when:** comparing across warehouses with different order profiles
  without normalising (use cost per line, CPT-0046, for money-comparable output).

## Worked example

Picker completes 540 lines in 6.0 h → `LPH = 90` → RF_SCANNER band.
Receiving crew 960 units in 8 h → `UPH = 120`. Whether 120 is good is not something this
node can say.

## Governing rules

- **WHS-R4** — completion quantities are non-negative; the TS metric reads them.
- **WHS-R2** — LPH only exists for a task that legally reached `COMPLETE`.

## Related

- CPT-0046 Labour cost per line — the financial view of the same output.
- CPT-0049 Labour staffing forecast — uses historical LPH as its input.

## References

- Frazelle (2016) 2nd Ed., Ch. 2; WERC DC Measures Study (2022).
