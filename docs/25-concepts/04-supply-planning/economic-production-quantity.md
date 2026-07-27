---
id: concept-economic-production-quantity
title: "Economic Production Quantity (CPT-0145)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-04-supply-planning }
  - { type: governed-by, target: index-adr }
---
# Economic Production Quantity (CPT-0145)

> EOQ's manufacturing sibling: the optimal production run size when output builds
> inventory gradually at a finite production rate instead of arriving all at once.

## Formula

    EPQ = √( 2·D·S / (H·(1 − D/P)) )
    run length t_p = EPQ/P · max inventory = EPQ·(1 − D/P)

| Symbol | Meaning | Unit |
|---|---|---|
| D | annual demand rate | units/year |
| P | annual production rate (> D) | units/year |
| S | setup cost per run | currency |
| H | holding cost per unit-year | currency |

## Inputs and outputs

- **Inputs:** validated D > 0, P > D, S > 0, H > 0.
- **Output:** run quantity plus run-length and max-inventory diagnostics.

## Assumptions and limits

- The `(1 − D/P)` factor is the whole story: production and consumption overlap,
  so average inventory is lower than EOQ's Q/2 — EPQ > EOQ for the same costs, and
  as P → ∞ EPQ → EOQ.
- P ≤ D is infeasible by construction (capacity cannot even keep up) — validated.
- Same stationarity/no-discount assumptions as EOQ (CPT-0021); setup cost S is the
  *changeover*, whose reduction (SMED) shrinks EPQ toward flow.
- Single product on the resource; multi-product sequencing is the economic lot
  scheduling problem (not implemented).
- **Does not apply when:** demand is lumpy (use CPT-0143/0144 with per-period
  logic).

## Worked example

D = 48,000/yr, P = 120,000/yr, S = 900, H = 3 →
`EPQ = √(2·48,000·900 / (3·(1 − 0.4))) = √(86.4M/1.8) = 6,928` units;
run ≈ 21 days of production, max inventory 4,157.

## Governing rules

- **SPL-R5** — netting conserves; a run quantity larger than the net requirement is a deliberate
  lot-sizing choice, not a netting error. Run quantities feed the MPS (CPT-0146 stability watches the
  consequences).

## Related

- CPT-0021 EOQ — the instantaneous-delivery limit case.

## References

- Taft (1918) — the EPQ extension of Harris (1913); Silver, Pyke & Peterson, Ch. 5.
