---
id: concept-grievance-resolution-sla
title: "Grievance Resolution SLA (CPT-0097)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
---
# Grievance Resolution SLA (CPT-0097)

> Service-level clocks on the human-rights grievance mechanism: how fast a complaint
> must be acknowledged and resolved, by severity.

## Formula

    CRITICAL: ack 24 h,  resolve 30 d · HIGH: 72 h / 60 d
    MEDIUM:   ack 7 d,   resolve 90 d · LOW: 14 d / 180 d
    overdue_ack ⇔ hours_since_received > ack_hours
    days_to_resolve = (received + resolve_days) − today

| Symbol | Meaning | Unit |
|---|---|---|
| received_at | grievance receipt | ISO 8601 timestamp (Z-aware) |
| severity | CRITICAL/HIGH/MEDIUM/LOW (validated) | enum |

## Inputs and outputs

- **Inputs:** timestamp string and severity; unknown severity raises.
- **Output:** `{sla_acknowledge_hours, sla_resolve_days, is_overdue_ack,
  hours_since_received, days_to_resolve}`.

## Assumptions and limits

- The SLA table is **company policy** giving effect to CSDDD Art. 9 and LkSG §8
  (both require an accessible complaints procedure but set no numeric deadlines) —
  the numbers are governance-set, cite them as policy, not statute.
- Uses wall-clock `now` (UTC) — non-deterministic in tests; inject a clock upstream
  (recorded caveat).
- Calendar time, not business days; severity is assessed at intake and should be
  re-graded as facts emerge (the clock does not restart — by design).
- **Does not apply when:** the complaint enters a legal/whistleblower channel with its
  own statutory deadlines (EU 2019/1937) — those override.

## Worked example

CRITICAL grievance received 2026-07-20T08:00Z; now 2026-07-22 → 48+ h elapsed >
24 h → acknowledgement overdue; resolution due 2026-08-19 (28 days remain).

## Governing rules

- **CMP-R*** — grievance mechanism availability and record-keeping; SCM-R9 UTC
  timestamps.

## Related

- CPT-0098 Composite compliance score — open overdue grievances should depress the
  CSDDD component.

## References

- CSDDD Art. 9 (complaints procedure); LkSG §8; UNGPs Principle 31 (effectiveness
  criteria for grievance mechanisms).
