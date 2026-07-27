---
id: concept-yard-dwell-and-trailer-turns
title: "Yard Dwell Time & Trailer Turn Rate (CPT-0048)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Yard Dwell Time & Trailer Turn Rate (CPT-0048)

> The two yard-management KPIs: how long each trailer sits (dwell) and how many trailers
> a dock door processes per shift (turns). Long dwell burns detention fees; low turns
> reveal stranded dock capacity.

## Formula

    dwell = departure_time − arrival_time
    turns_per_shift = trailers_processed / dock_hours_available × 8

| Symbol | Meaning | Unit |
|---|---|---|
| arrival/departure_time | trailer in/out of yard | hours (same clock) |
| trailers_processed | trailers completed in the period | count |
| dock_hours_available | door-hours staffed | hours |
| turns_per_shift | normalised to an 8-hour shift | turns |

## Inputs and outputs

- **Outputs:** dwell → `{dwell_hours, benchmark_hours: 4.0, benchmark_met,
  detention_risk}` — `detention_risk` fires above **2 h** because most carrier contracts
  give 2 h free time before detention charges; turns → `{turns_per_shift,
  benchmark_turns_per_shift: 3, benchmark_met}` (≥ 3 turns per door per 8-h shift).
- **Guards:** negative dwell raises; `dock_hours_available > 0` required.

## Assumptions and limits

- Same hours-since-midnight caveat as CPT-0047: dwell spanning midnight computes
  negative — convert to a monotonic axis first.
- Benchmark 4 h is the inbound bar; outbound staging typically tolerates ~6 h — the
  implementation carries only the inbound default.
- Turn rate counts *processed trailers*, not appointments — no-shows (DockAppointment
  `markNoShow`) never inflate it.
- **Does not apply when:** drop-and-hook yards intentionally park trailers as mobile
  storage — dwell is then a stock decision, not a performance failure.

## Worked example

Arrive 06:00, depart 11:30 → dwell 5.5 h → benchmark missed, detention risk.
Doors process 21 trailers over 56 door-hours → `21/56×8 = 3.0` turns → benchmark met.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| When the dwell clock starts and stops | Arrival at the gate, at the yard, or at the dock give materially different dwell figures |
| Whether detention-liable time is separated | The commercially meaningful figure is the time the project pays for |

## Governing rules

- **WHS-R5** — task quantities conserve; the task lifecycle itself is the project's design.
  these KPIs consume.

## Related

- CPT-0043 Dock door sizing — chronic dwell above benchmark signals undersized doors.
- CPT-0047 Dock-to-stock — the inside continuation of the inbound clock.

## References

- WERC DC Measures Study (2022); Frazelle (2016) — yard and dock metrics.
