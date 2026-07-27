//! Purchase-order rules — the ported suite.
//!
//! Carries over every assertion from the retired `tests/unit/purchaseorder.test.ts` and adds
//! the cases the TypeScript could not make: the currency guard, the quantity guard, and the
//! exhaustive transition table.

#![allow(clippy::unwrap_used, clippy::expect_used)]

use rust_decimal::Decimal;
use scm_core::d01_procurement::purchase_order::{
    NewPurchaseOrder, PO_APPROVAL_THRESHOLD_CENTS, PoLine, ProcurementError, PurchaseOrder,
    PurchaseOrderStatus, purchase_order_total,
};
use scm_money::Money;

const NOW: &str = "2026-07-26T10:00:00Z";
const LATER: &str = "2026-07-26T11:30:00Z";

/// One line of `quantity` units at USD 10.00 each.
fn line(quantity: i64) -> PoLine {
    PoLine {
        line_id: "LINE-1".to_owned(),
        sku: "SKU-001".to_owned(),
        description: "Test Widget".to_owned(),
        quantity: Decimal::from(quantity),
        uom: "EA".to_owned(),
        unit_price: Money::new(1_000, "USD"),
        delivery_date: "2026-08-01".to_owned(),
        warehouse_id: "WH-001".to_owned(),
        lot_required: false,
    }
}

fn new_order(lines: Vec<PoLine>, threshold: Option<i64>) -> NewPurchaseOrder {
    NewPurchaseOrder {
        id: "PO-ID-1".to_owned(),
        po_number: "PO-20260726-1001".to_owned(),
        supplier_id: "SUP-001".to_owned(),
        buyer_id: "ORG-001".to_owned(),
        lines,
        currency: "USD".to_owned(),
        incoterm: "FCA".to_owned(),
        incoterm_location: "Chicago, IL".to_owned(),
        requested_delivery_date: "2026-08-01".to_owned(),
        approval_threshold_cents: threshold,
        notes: None,
        created_by: "user@example.com".to_owned(),
        created_at: NOW.to_owned(),
    }
}

fn open(lines: Vec<PoLine>, threshold: Option<i64>) -> PurchaseOrder {
    PurchaseOrder::open(new_order(lines, threshold)).expect("order should open")
}

// ── SCM-R2 — the approval-threshold rule ─────────────────────────────────────────────────

#[test]
fn an_order_below_the_threshold_is_approved_on_creation() {
    // 100 × USD 10.00 = USD 1,000 < USD 50,000
    let order = open(vec![line(100)], Some(5_000_000));
    assert_eq!(order.status, PurchaseOrderStatus::Approved);
    assert!(!order.requires_approval());
}

#[test]
fn an_order_above_the_threshold_waits_for_an_approver() {
    // 1000 × USD 10.00 = USD 10,000 > the USD 5,000 default
    let order = open(vec![line(1_000)], None);
    assert_eq!(order.status, PurchaseOrderStatus::PendingApproval);
    assert_eq!(order.approval_threshold_cents, PO_APPROVAL_THRESHOLD_CENTS);
    assert!(order.requires_approval());
}

#[test]
fn an_order_exactly_at_the_threshold_waits_for_an_approver() {
    // SCM-R2 is "at or above": the order sized exactly to the limit is the one to review.
    let order = open(vec![line(100)], Some(100_000));
    assert_eq!(order.total().unwrap().amount_cents, 100_000);
    assert_eq!(order.status, PurchaseOrderStatus::PendingApproval);
}

#[test]
fn one_cent_below_the_threshold_does_not_need_approval() {
    let order = open(vec![line(100)], Some(100_001));
    assert_eq!(order.status, PurchaseOrderStatus::Approved);
}

// ── CPT-0026 — total committed value ─────────────────────────────────────────────────────

#[test]
fn the_total_is_the_sum_of_the_line_extensions() {
    let mut second = line(3);
    second.line_id = "LINE-2".to_owned();
    second.unit_price = Money::new(2_599, "USD");
    let order = open(vec![line(100), second], Some(i64::MAX));
    // 100 × 1000 + 3 × 2599 = 100_000 + 7_797
    assert_eq!(order.total().unwrap(), Money::new(107_797, "USD"));
}

#[test]
fn a_fractional_quantity_quantizes_once_through_the_money_core() {
    let mut fractional = line(1);
    fractional.quantity = Decimal::from_str_exact("2.5").unwrap();
    fractional.unit_price = Money::new(1_299, "USD");
    // 2.5 × 1299 = 3247.5 → 3248 (ties to even), quantized once, not per operation.
    let total = purchase_order_total(&[fractional], "USD").unwrap();
    assert_eq!(total, Money::new(3_248, "USD"));
}

#[test]
fn an_empty_line_set_totals_zero_but_cannot_be_ordered() {
    assert_eq!(
        purchase_order_total(&[], "USD").unwrap(),
        Money::new(0, "USD")
    );
    assert_eq!(
        PurchaseOrder::open(new_order(vec![], None)),
        Err(ProcurementError::NoLines)
    );
}

// ── Guards the TypeScript version did not have ────────────────────────────────────────────

#[test]
fn a_line_priced_in_another_currency_is_refused() {
    let mut foreign = line(10);
    foreign.unit_price = Money::new(1_000, "EUR");
    let error = PurchaseOrder::open(new_order(vec![foreign], None)).unwrap_err();
    assert_eq!(
        error,
        ProcurementError::LineCurrencyMismatch {
            line_id: "LINE-1".to_owned(),
            expected: "USD".to_owned(),
            found: "EUR".to_owned(),
        }
    );
}

#[test]
fn a_line_with_no_quantity_is_refused() {
    // US UCC Article 2: an enforceable order states a quantity.
    for quantity in [0, -5] {
        let error = PurchaseOrder::open(new_order(vec![line(quantity)], None)).unwrap_err();
        assert_eq!(
            error,
            ProcurementError::NonPositiveQuantity {
                line_id: "LINE-1".to_owned()
            }
        );
    }
}

// ── Approval workflow ─────────────────────────────────────────────────────────────────────

#[test]
fn approving_a_pending_order_records_who_and_when() {
    let approved = open(vec![line(1_000)], None)
        .approve("manager@example.com", LATER)
        .unwrap();
    assert_eq!(approved.status, PurchaseOrderStatus::Approved);
    assert_eq!(approved.approved_by.as_deref(), Some("manager@example.com"));
    assert_eq!(approved.approved_at.as_deref(), Some(LATER));
    assert_eq!(approved.updated_at, LATER);
}

#[test]
fn rejecting_a_pending_order_records_the_reason() {
    let rejected = open(vec![line(1_000)], None)
        .reject("manager@example.com", "Over budget", LATER)
        .unwrap();
    assert_eq!(rejected.status, PurchaseOrderStatus::Rejected);
    assert_eq!(rejected.rejection_reason.as_deref(), Some("Over budget"));
}

#[test]
fn an_order_cannot_be_approved_twice() {
    let approved = open(vec![line(1_000)], None)
        .approve("mgr@example.com", LATER)
        .unwrap();
    assert_eq!(
        approved.approve("mgr@example.com", LATER),
        Err(ProcurementError::IllegalTransition {
            from: PurchaseOrderStatus::Approved,
            action: "approve",
        })
    );
}

#[test]
fn only_an_approved_order_reaches_the_supplier() {
    let sent = open(vec![line(100)], Some(5_000_000))
        .send_to_supplier(LATER)
        .unwrap();
    assert_eq!(sent.status, PurchaseOrderStatus::SentToSupplier);

    let pending = open(vec![line(1_000)], None);
    assert_eq!(
        pending.send_to_supplier(LATER),
        Err(ProcurementError::IllegalTransition {
            from: PurchaseOrderStatus::PendingApproval,
            action: "send to supplier",
        })
    );
}

// ── Cancellation and soft-delete (SCM-R3) ────────────────────────────────────────────────

#[test]
fn cancelling_stores_the_reason_and_the_moment() {
    let cancelled = open(vec![line(100)], Some(100_000))
        .cancel("No longer needed", LATER)
        .unwrap();
    assert_eq!(cancelled.status, PurchaseOrderStatus::Cancelled);
    assert_eq!(cancelled.cancelled_at.as_deref(), Some(LATER));
    assert_eq!(cancelled.notes.as_deref(), Some("No longer needed"));
}

#[test]
fn cancellability_covers_exactly_the_states_with_nothing_received() {
    use PurchaseOrderStatus::{
        Approved, Cancelled, Closed, Draft, FullyReceived, PartiallyReceived, PendingApproval,
        Rejected, SentToSupplier,
    };
    for status in [Draft, PendingApproval, Approved, SentToSupplier] {
        assert!(status.is_cancellable(), "{status} should be cancellable");
    }
    for status in [
        PartiallyReceived,
        FullyReceived,
        Rejected,
        Cancelled,
        Closed,
    ] {
        assert!(!status.is_cancellable(), "{status} must not be cancellable");
    }
}

#[test]
fn only_a_terminal_order_may_be_soft_deleted() {
    let cancelled = open(vec![line(100)], Some(100_000))
        .cancel("No longer needed", LATER)
        .unwrap();
    let deleted = cancelled.soft_delete(LATER).unwrap();
    assert!(deleted.is_deleted);
    assert_eq!(
        deleted.status,
        PurchaseOrderStatus::Cancelled,
        "the record survives"
    );

    let live = open(vec![line(100)], Some(5_000_000));
    assert_eq!(
        live.soft_delete(LATER),
        Err(ProcurementError::NotSoftDeletable {
            from: PurchaseOrderStatus::Approved
        })
    );
}

#[test]
fn a_soft_delete_never_removes_the_lines() {
    let deleted = open(vec![line(100)], Some(100_000))
        .cancel("done", LATER)
        .unwrap()
        .soft_delete(LATER)
        .unwrap();
    assert_eq!(deleted.lines.len(), 1);
    assert_eq!(deleted.total().unwrap(), Money::new(100_000, "USD"));
}

// ── Purity ────────────────────────────────────────────────────────────────────────────────

#[test]
fn opening_the_same_input_twice_yields_the_same_order() {
    // The TypeScript version minted a uuid and read the clock inside the constructor, so this
    // assertion was impossible there. Identity and time are inputs now (ADR-0035).
    let first = open(vec![line(100)], Some(100_000));
    let second = open(vec![line(100)], Some(100_000));
    assert_eq!(first, second);
}

#[test]
fn status_renders_as_the_wire_spelling() {
    assert_eq!(
        PurchaseOrderStatus::PendingApproval.to_string(),
        "PENDING_APPROVAL"
    );
    assert_eq!(
        PurchaseOrderStatus::SentToSupplier.to_string(),
        "SENT_TO_SUPPLIER"
    );
}
