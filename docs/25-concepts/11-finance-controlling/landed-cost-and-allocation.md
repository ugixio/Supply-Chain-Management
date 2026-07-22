---
id: concept-landed-cost-and-allocation
title: "Landed Cost & Allocation — IAS 2 (CPT-0111)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
---
# Landed Cost & Allocation — IAS 2 (CPT-0111)

> The true cost of an imported unit — goods plus freight, insurance, duty, brokerage,
> handling and non-recoverable tax — and the cent-exact spread of that total across
> the shipment's SKU lines.

## Formula

    total_landed = goods + freight + insurance + duty + broker + handling
                 + nonrecoverable_tax
    unit_landed  = round(total / quantity)
    allocation (BY_VALUE | BY_QUANTITY | BY_WEIGHT):
      alloc_i = round(total × basis_i / Σ basis)
      remainder (± cents) → line with the largest basis   (Σ alloc = total exactly)

| Symbol | Meaning | Unit |
|---|---|---|
| cost elements | import cost components | integer cents |
| basis | value_cents / quantity / weight_kg per line | per method |

## Inputs and outputs

- **Inputs:** validated non-negative integer cents; quantity > 0; allocation lines
  with the chosen basis (zero basis total → even split fallback).
- **Outputs:** totals + unit landed cost + `duty_and_tax_cents` +
  `freight_per_unit_cents` + breakdown; allocation returns lines with
  `allocated_cents` and per-unit cost. TS selectors compute duty+tax and
  freight/unit from the LandedCost aggregate's typed components.

## Assumptions and limits

- **Recoverable VAT/GST is excluded by design** (IAS 2 §11: only non-recoverable
  taxes capitalize into inventory cost); the parameter is explicitly the
  non-recoverable portion.
- The remainder-to-largest-line rule makes allocation *reconcile to the cent* —
  no lost pennies (the property U8 golden vectors should pin cross-language).
- Basis choice is a policy: BY_VALUE matches ad-valorem duty logic; BY_WEIGHT suits
  freight-dominated totals; mixing methods per component (duty by value, freight by
  weight) is the refinement this single-method function doesn't do.
- Incoterms decide *which* elements the buyer owns (CPT-0106-family in logistics) —
  a DDP purchase already embeds duty in the goods price; don't double count.
- **Does not apply when:** costs are period expenses (abnormal waste, storage after
  production — IAS 2 §16 exclusions).

## Worked example

Goods 1,000,000¢ + freight 80,000 + insurance 6,000 + duty 45,000 + broker 12,000 +
handling 9,000 + non-rec tax 20,000 = **1,172,000¢**; 500 units → 2,344¢/unit.
Allocation BY_VALUE over lines 600k/300k/100k → 703,200 / 351,600 / 117,200¢ (sums
exactly).

## Implementations

- PY: [`landed_cost`](../../../services/calc/11_finance_controlling/finance.py)
- PY: [`allocate_landed_cost`](../../../services/calc/11_finance_controlling/finance.py)
- TS: [`dutyAndTaxCents`](../../../packages/domain/src/11-finance-controlling/domain/LandedCost.ts)
- TS: [`freightPerUnitCents`](../../../packages/domain/src/11-finance-controlling/domain/LandedCost.ts)

## Governing rules

- **SCM-R8** — integer cents (Decimal at P5); **SCM-R4** — capitalization journals;
  FIN-R* valuation records.

## Related

- CPT-0033 Total Cost of Ownership — landed cost is its logistics core.
- Inventory valuation (dept 05 catalogue) — consumes unit landed cost.

## References

- IAS 2 *Inventories* §§10–11, 16; ICC Incoterms® 2020 (cost ownership).
