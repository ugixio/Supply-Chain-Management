---
id: concept-stock-balance-projection
title: "Stock Balance Projection — Event Replay (CPT-0113)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
---
# Stock Balance Projection — Event Replay (CPT-0113)

> Rebuilds the current stock level by replaying the immutable movement log — the read
> model of the event-sourced inventory (ADR-0005): balance is derived, never stored.

## Formula

    balance = Σ inbound quantities − Σ outbound quantities   (replay in time order)
    inbound: GOODS_RECEIPT, RETURN_FROM_CUSTOMER, TRANSFER_IN,
             PRODUCTION_OUTPUT, INVENTORY_ADJUSTMENT_IN

| Symbol | Meaning | Unit |
|---|---|---|
| movements/events | the immutable log entries | units, ISO timestamps |

## Inputs and outputs

- **Inputs:** the movement events for a stock-keeping unit at a location, replayed in
  timestamp order. Order matters: the same events applied in a different sequence can pass or
  fail a non-negativity check even though the final balance is identical.
- **Output:** the balance implied by those events.
- **Reservations are not movements.** A reservation changes what is *available* to promise
  without changing what is physically present, so a projection of physical balance ignores it.
  Conflating the two double-counts commitments.
- **Where the non-negativity check belongs is a project decision, and both answers are
  defensible.** Refusing the movement that would drive the balance negative keeps the ledger
  always-valid but requires the writer to know the current balance. Letting the projection
  report a negative balance surfaces it for investigation instead — which is what a *reader*
  of an event log can honestly do, since the impossible state is evidence that something
  upstream was missed.

## Assumptions and limits

- Replay correctness depends on log immutability and idempotent writes
  (retry safety — an engineering concern, ENG-R\*) — a duplicated event silently doubles the balance; the idempotency key
  belongs to the write path, not this projection.
- **Timestamps are not an ordering.** Two movements sharing an instant replay in whatever order the
  list happened to hold them, and the balance can differ between runs if any movement is refused on
  a negative check. Audit-grade replay needs a monotonic sequence number, not only a timestamp
  (SCM-R9 fixes the format, not the ordering).
- Full-log replay is O(N); the standard optimization once logs grow is a periodic snapshot plus the
  delta since. The snapshot is derived, never authoritative — it must be reproducible from the log.
- **Does not apply when:** computing *available-to-promise* — reservations matter
  there (CPT-0085), not here.

## Worked example

Events: receipt +100, issue −30, transfer-in +20, issue −50 → balance **40**.

A further issue of −45 would take the balance to −5, and **where that is caught is a design
decision** (INV-R5): refusing the movement keeps the log always-valid but requires the writer to
know the balance first, while letting the projection report −5 surfaces the gap that already exists
upstream. A *reader* of an event log can honestly only do the latter — it cannot refuse a movement
that was already recorded.

## Governing rules

- **INV-R5** — a physical balance cannot be negative; **SCM-R4** — every
  movement journals; **ENG-R\*** — retry safety; ADR-0005 event sourcing.

## Related

- CPT-0118/0119 — valuation layers ride on the same movements.

## References

- Vernon, *Implementing Domain-Driven Design* (2013), Ch. 8 — event sourcing.
