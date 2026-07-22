---
id: concept-fx-revaluation
title: "Period-End FX Revaluation — IAS 21 (CPT-0110)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
---
# Period-End FX Revaluation — IAS 21 (CPT-0110)

> Retranslates foreign-currency monetary balances at the closing rate and books the
> gain/loss — the month-end FX step for AP/AR held in other currencies.

## Formula

Per balance:

    original_value = round(amount × original_rate)
    revalued       = round(amount × closing_rate)
    gain_loss      = revalued − original_value        (all in target-currency cents)

| Symbol | Meaning | Unit |
|---|---|---|
| amount | balance in foreign currency | integer cents (foreign) |
| original_rate / closing_rate | target units per 1 foreign unit | rate |

## Inputs and outputs

- **Inputs:** non-empty balances `[{currency, amount_cents, original_rate}]`, target
  ISO 4217 code, closing `rates` dict (target itself implied 1.0; missing rate
  raises; non-positive rates raise).
- **Output:** per-balance detail, net `fx_gain_loss_cents`, per-currency subtotals.

## Assumptions and limits

- **Monetary items only** (cash, AR, AP, loans) — IAS 21.23(a): non-monetary items at
  historical cost are *not* retranslated; don't feed inventory balances through this.
- Gains/losses go to P&L (IAS 21.28); net investment hedges and OCI treatment are out
  of scope.
- Rounding at cent level per balance (SCM-R8) — sub-cent drift across many balances
  is possible vs a whole-portfolio rounding; immaterial but note for reconciliation.
- Rate convention is *direct* quotation (target per foreign) — inverting by mistake
  is the classic error; the positive-rate guard won't catch it.
- **Does not apply when:** hyperinflationary economies (IAS 29 restatement first).

## Worked example

EUR AP of −50,000¢ (owed), original 1.08, closing 1.11 →
original −54,000¢, revalued −55,500¢ → **loss 1,500¢** (the payable grew in
target terms).

## Implementations

- PY: [`period_end_fx_revaluation`](../../../services/calc/11_finance_controlling/finance.py)

## Governing rules

- **SCM-R4** — the resulting journal (FX gain/loss ↔ balance) posts double-entry;
  SCM-R8 money.

## Related

- CPT-0111 Landed cost — duty/valuation uses customs rates, a different rate source.

## References

- IAS 21 §§23, 28 — closing-rate retranslation of monetary items.
