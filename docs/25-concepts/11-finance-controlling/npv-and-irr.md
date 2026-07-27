---
id: concept-npv-and-irr
title: "NPV & IRR — Capital Project Evaluation (CPT-0112)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
---
# NPV & IRR — Capital Project Evaluation (CPT-0112)

> Discounted-cashflow arithmetic for supply-chain investments (automation, network
> changes): present value at a hurdle rate, and the rate at which the project breaks
> even.

## Formula

    NPV = Σ_t CF_t / (1 + r)^t          (t = 0, 1, …; CF_0 usually negative)
    IRR: the r where NPV(r) = 0          (Brent root-search; polynomial fallback)

| Symbol | Meaning | Unit |
|---|---|---|
| CF_t | periodic cashflows | integer cents |
| r | per-period discount rate (0.10 = 10%) | fraction |

## Inputs and outputs

- **NPV:** non-empty flows, rate > −1 → integer cents (rounded once at the end).
- **IRR:** requires at least one sign change (validated); returns the per-period rate
  as float; `NaN` when no real root exists. Implementation prefers
  `scipy.optimize.brentq` (bracketed, robust) and falls back to `numpy.roots` on the
  polynomial in x = 1/(1+r), taking the smallest real positive root.

## Assumptions and limits

- Periods must match the rate (annual flows with an annual rate); mid-period timing
  is not modelled.
- **Multiple IRRs exist** whenever flows change sign more than once (Descartes) —
  the fallback's "smallest positive root" is then a *choice*, not the answer; rank
  such projects by NPV at the hurdle rate instead.
- IRR assumes reinvestment at IRR itself — optimistic for high-IRR projects (MIRR is
  the fix; not implemented).
- NPV in integer cents keeps SCM-R8 discipline; intermediate float discounting is
  acceptable because rounding happens once.
- **Does not apply when:** comparing different-length projects without a common
  horizon (equivalent-annual-annuity needed).

## Worked example

Flows (¢): −10,000,000; +3,000,000 × 5 years; r = 10% →
NPV = −10M + 3M×3.7908 = **+1,372,360¢** → accept; IRR ≈ 15.24% > hurdle.

## Governing rules

- **SCM-R8** — money precision; decision records for capital approvals (FIN-R*).

## Related

- CPT-0072 EAL — risk-side annualization that often feeds these cashflows.

## References

- Brealey, Myers & Allen, *Principles of Corporate Finance*, Ch. 2 & 5.
