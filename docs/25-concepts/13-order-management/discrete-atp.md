---
id: concept-discrete-atp
title: "Discrete Available-to-Promise (CPT-0086)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
---
# Discrete Available-to-Promise (CPT-0086)

> ATP computed only in periods that receive supply: each supply bucket promises what
> it brings minus the commitments it must cover until the next supply arrives — the
> classic MPS ATP row.

## Formula

    supply_0 = on_hand + supply_0 ; ATP only where supply_t > 0 (t = 0 always)
    ATP_t = max( supply_t − Σ committed_k , 0 )   for k = t .. next_supply_period − 1
    cumulative_atp_t = running Σ ATP_t

| Symbol | Meaning | Unit |
|---|---|---|
| supply_t | scheduled receipt in period t | units |
| committed_k | firm commitments due in k | units |
| on_hand | opening stock (added to period 0) | units |

## Inputs and outputs

- **Inputs:** ordered period dicts `{period, supply, committed}`; optional `on_hand`
  on period 0; empty list → empty result.
- **Output:** the periods enriched with `atp_qty` and `cumulative_atp_qty`.

## Assumptions and limits

- The **max(…, 0) clamp** means a supply bucket over-committed to zero does not borrow
  from later buckets — conservative and standard for the simple (non-look-ahead) MPS
  presentation; the textbook look-ahead variant nets future over-commitments backward.
- Commitments between supply buckets are charged wholly to the *earlier* bucket —
  correct under "consume oldest supply first".
- Firm orders only; forecast never consumes ATP.
- **Does not apply when:** supply timing is continuous (daily receipts) — the bucketed
  form degenerates; use CPT-0085.

## Worked example

on_hand 40; periods: P1 supply 0 committed 30 · P2 supply 100 committed 50 ·
P3 supply 0 committed 20 · P4 supply 80 committed 60.
Buckets: P1 (carries on-hand): 40 − 30 = 10 · P2: 100 − (50+20) = 30 · P4: 80 − 60 = 20.
Cumulative: 10, 40, 40, 60.

## Governing rules

- Same promising discipline as CPT-0085 (INV-R5 and the project's backorder policy).

## Related

- CPT-0085 Cumulative ATP · CPT-0087 CTP — consumes this schedule.

## References

- APICS CPIM — MPS/ATP; Vollmann, Berry & Whybark, *MPC* — the discrete ATP row.
