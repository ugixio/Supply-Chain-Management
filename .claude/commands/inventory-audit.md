# /inventory-audit — Inventory Logic Auditor

Audits inventory-related code for correctness, safety, and compliance with SCM business rules.

## Usage
`/inventory-audit [file or feature]`

---

Audit the inventory logic in: $ARGUMENTS

Check for:
1. **Negative stock guard** — is there a check before decrementing inventory?
2. **Concurrent update safety** — are stock movements using optimistic locking or row-level locks?
3. **Transaction atomicity** — do multi-step movements (pick + ship) run in a single DB transaction?
4. **Lot/serial tracking** — are lot-tracked items enforcing FEFO (First Expired First Out)?
5. **Reconciliation hooks** — does the code emit events that feed into inventory reconciliation reports?
6. **Warehouse location accuracy** — are bin/location codes validated against the master location list?
7. **UOM conversion** — are unit-of-measure conversions using the conversion factor table, not hardcoded values?

Output a checklist with PASS / FAIL / NEEDS REVIEW for each item, with line references.
