# /scm-review — Supply Chain Code Review

Run a domain-aware review of the current changes focusing on supply chain correctness.

## What this checks
- Inventory transaction idempotency
- Monetary value handling (no floats for money)
- Business rule enforcement (negative stock, approval thresholds)
- Soft-delete compliance on financial records
- Lot/batch tracking for regulated items
- UOM consistency across the transaction

## Usage
Type `/scm-review` in Claude Code to trigger this review on the current diff.

---

Review the current git diff (`git diff HEAD`) for supply chain domain correctness:

1. **Money handling**: Flag any use of float/double for monetary amounts. All prices, costs, and values must use integers (cents) or a Decimal type.
2. **Inventory safety**: Check that no code path allows negative inventory without an explicit backorder/allow-negative flag.
3. **Idempotency**: Verify that inventory transactions and order mutations use an idempotency key or are otherwise safe to retry.
4. **Soft deletes**: Confirm financial records (POs, invoices, GRNs, stock movements) are never hard-deleted.
5. **UOM consistency**: Flag any place where quantities are compared or summed without normalizing the unit of measure.
6. **Approval workflow**: Ensure purchase order creation/modification above threshold triggers approval, not auto-approval.
7. **Audit trail**: All stock movements should record who, what, when, and why.

Report findings grouped by severity: BLOCKER → WARNING → INFO.
