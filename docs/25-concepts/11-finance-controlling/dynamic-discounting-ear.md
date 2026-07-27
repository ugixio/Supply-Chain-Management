---
id: concept-dynamic-discounting-ear
title: "Dynamic Discounting — Effective Annual Rate (CPT-0106)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
---
# Dynamic Discounting — Effective Annual Rate (CPT-0106)

> Converts an early-payment discount offer into an annualized rate of return, so
> treasury can compare "pay early for 2%" against the cost of capital.

## Formula

    EAR = (d / (1 − d)) × (365 / days_accelerated)

| Symbol | Meaning | Unit |
|---|---|---|
| d | discount fraction (2% → 0.02) | fraction |
| days_accelerated | days paid earlier than standard terms | days |

## Inputs and outputs

- **Inputs:** `discount_pct ∈ (0,100)` exclusive, positive acceleration days.
- **Output:** EAR as a fraction (0.3724 = 37.24%).

## Assumptions and limits

- This is the **simple-annualized** convention (APICS/corporate-finance textbook);
  compounding the period rate ((1+r)^(365/n) − 1) gives a higher figure — state the
  convention when quoting.
- Decision rule: take the discount when EAR > the buyer's short-term cost of capital;
  the classic 2/10 net 30 at ~37% clears almost any funding cost.
- Assumes the invoice would otherwise be paid exactly on the standard due date —
  habitual late payers gain more than the formula shows (longer acceleration).
- **Does not apply when:** the discount is contractually mandatory (then it is price,
  not a financing choice), or supply-chain-finance (reverse factoring) rates apply
  instead.

## Worked example

2/10 net 30 → d = 0.02, 20 days early → `EAR = (0.02/0.98) × (365/20) = 0.3724 →
37.24%` — take it unless cash costs more than 37% annually.

## Governing rules

- **SCM-R14** — money and rates are exact; an annualized rate compounds errors that a float
  introduces. **SCM-R3** — a payment-term decision is recorded against the invoice by a further
  entry, never by editing the original terms.

## Related

- CPT-0104 C2C — paying early trades DPO for margin; evaluate jointly.

## References

- Brealey, Myers & Allen, *Principles of Corporate Finance* — trade credit;
  APICS CPIM.
