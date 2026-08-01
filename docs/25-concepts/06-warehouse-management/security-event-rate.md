---
id: concept-security-event-rate
title: "Warehouse Security-Event Rate (CPT-0166)"
type: concept
owner: orchestrator
status: active
since: 2026-08-01
updated: 2026-08-01
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Warehouse Security-Event Rate (CPT-0166)

> How many security events a site recorded in a period. A **flow** — and the only indicator here
> where the count is the least useful part of the measurement.

## Formula

    event_rate = recorded_events / period        (optionally per class and per severity)

| Symbol | Meaning | Unit |
|---|---|---|
| recorded_events | security events recorded in the period | count |
| period | the interval counted over | shift, day or month |
| event_rate | output | events per period |

## Inputs and outputs

- **Inputs:** the recorded events, each carrying at minimum its **class, severity, location and
  instant**.
- **Outputs:** the count per period, and the same count broken down by class and severity.
- **A count is not the record.** "Three events" supports no decision: acting needs *what*, *where*
  and *who*. The count belongs in a metric series; the **event belongs in its own record** — as
  ADR-0036 already anticipated for bursty events.

## Assumptions and limits

- **The obligation to manage incidents is external; the taxonomy is not.** ISO 28000:2022 requires a
  security management system that identifies, records and reviews security incidents, and ISO
  28000 certification is what CPT-0035 checks for validity. **What ISO 28000 does not fix** is the
  class list, the severity scale, or what counts as reportable — those are the project's, and they
  are where two sites' numbers stop being comparable.
- **A rising rate is ambiguous, and reading it as bad is the standard error.** It can mean more
  incidents or better reporting: a site that just trained its staff looks worse than one that
  under-reports, and the under-reporting site is the one at risk. Read it against reporting coverage.
- **Near-misses and actual losses do not belong in one count** unless the classes separate them.
- **Personal data.** An event record naming an individual is personal data under GDPR where the EU
  applies; retention and access are then legal constraints, not operational preferences.
- **Does not apply as a shrinkage measure.** Inventory loss is measured against book quantity; a
  security event may or may not cause it.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The event class list and the severity scale | ISO 28000 requires incident management, not a taxonomy. The classes follow from what the site intends to act on. |
| What counts as reportable | Follows from the site's own control environment; it sets the denominator of everything above. |
| Retention and access for records naming individuals | Follows from the data-protection law that applies, and from SCM-R7 where due-diligence retention governs. |
| The level that triggers escalation | Follows from risk appetite, which is the project's (see the risk-management department). |

## Worked example

*Illustrative only.* A month records 7 events: 4 unauthorised-access attempts at one perimeter door,
2 seal discrepancies on inbound trailers, 1 confirmed loss. Rate **7 per month**. The decision comes
not from 7 but from *4 at one door* — a physical control to fix — and from the seal discrepancies,
which point at a carrier rather than the site.

## Governing rules

- **SCM-R9** — the event instant is an ISO 8601 UTC timestamp, or events across sites cannot be
  ordered or correlated.
- **SCM-R7** — where due-diligence retention applies, records are kept at least five years; a
  retention shorter than the legal floor is not a configuration choice.

## Related

- CPT-0035 Certification and contract validity — ISO 28000 certification as a supplier control.
- CPT-0161 Goods-receipt throughput — seal and receipt discrepancies surface at the same dock.
- CPT-0163 Outbound shipment backlog — waiting trailers are themselves a security condition.

## References

- ISO 28000:2022 — security management systems for the supply chain; incident identification,
  recording and review.
- ISO 31000:2018 — risk management process vocabulary.
- APICS/ASCM Supply Chain Dictionary, 16th Ed. (2024) — *supply chain security*.
