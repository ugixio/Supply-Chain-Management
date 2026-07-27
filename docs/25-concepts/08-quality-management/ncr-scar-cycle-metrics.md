---
id: concept-ncr-scar-cycle-metrics
title: "NCR/SCAR Cycle Metrics (CPT-0059)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
---
# NCR/SCAR Cycle Metrics (CPT-0059)

> The clock-and-progress arithmetic on quality records: how long a nonconformance or
> supplier corrective action has been open, whether the supplier is past its SLA, and
> how far through the 8D disciplines the response is.

## Formula

    days_open = ⌊(end − start) / 86,400,000 ms⌋
      NCR:  start = detectedDate  · SCAR: start = issuedDate
      end  = closedDate, else now
    ack_overdue      = ¬acknowledged ∧ status ≠ CLOSED ∧ now > acknowledgementDueDate
    response_overdue = status ≠ CLOSED ∧ now > responseRequiredByDate 23:59:59Z
    completed_disciplines = |{8D steps with completed = true}|   ∈ [0, 8]

| Symbol | Meaning | Unit |
|---|---|---|
| detectedDate / issuedDate / closedDate | record milestones | ISO 8601 |
| acknowledgementDueDate | supplier D1 deadline | ISO timestamp |
| responseRequiredByDate | full 8D response deadline | ISO date (end-of-day UTC) |

## Inputs and outputs

- **Inputs:** the NCR/SCAR aggregate; overdue checks take `now` (defaults to UTC now —
  injectable for tests).
- **Outputs:** integer calendar days (floored); booleans; discipline count 0–8.
- Response deadline is evaluated at **23:59:59Z** of the due date — a date-only field
  read as an end-of-day instant.

## Assumptions and limits

- Calendar days, not business days — SLA contracts written in business days need a
  calendar adapter before comparison.
- An open record's `days_open` uses wall-clock `Date.now()` — non-deterministic in
  tests unless the record is closed (recorded testing caveat).
- The 8D discipline model is the AIAG/automotive standard (D1 team … D8 recognition);
  `completedDisciplineCount` assumes exactly 8 steps exist on the record.
- **Does not apply when:** the record is voided (excluded from cycle KPIs).

## Worked example

SCAR issued 2026-07-01, ack due 2026-07-03, not acknowledged, now 2026-07-05 →
`ack_overdue = true`, `days_open = 4`; 3 of 8 disciplines completed.

## Governing rules

- **SCM-R9** — ISO 8601/UTC dates; **SCM-R3** — NCR/SCAR records soft-delete only.
- NCR/SCAR state machines (QMS rule family) own the transitions these metrics observe.

## References

- AIAG — 8D problem-solving discipline; ISO 9001:2015 §8.7, §10.2 (nonconformity and
  corrective action).
