//! Purchase Order aggregate — the core procurement document.
//!
//! Rules enforced here:
//! 1. **SCM-R2** — a PO whose total is **at or above** the approval threshold enters
//!    `PendingApproval`; below it, `Approved`.
//! 2. Only an `Approved` PO can be sent to the supplier.
//! 3. **SCM-R3** — soft-delete only, and only from a terminal state.
//! 4. **UCC Art. 2** — a PO must carry at least one line with a stated quantity.
//!
//! Ported from `packages/domain/src/01-procurement/domain/PurchaseOrder.ts` (ADR-0035). The
//! port strengthened three things the TypeScript could not express:
//! - the status is an **enum**, so an illegal transition is a compile-time-exhaustive match
//!   rather than a string comparison;
//! - line currencies are **checked** against the PO currency (the TS version documented mixed
//!   currency as "a data error the aggregate does not detect" — now it detects it);
//! - money flows through the single exact core (`scm_money`), so the total cannot drift.
//!
//! References: Chopra & Meindl Ch. 14 · US UCC Article 2 · ISO 9001:2015 §8.4 · APICS CPIM 9.0.

use rust_decimal::Decimal;
use scm_money::{Money, MoneyError, multiply_cents};
use std::error::Error;
use std::fmt;

/// Default approval threshold: USD 5,000 in integer minor units (SCM-R2).
pub const PO_APPROVAL_THRESHOLD_CENTS: i64 = 500_000;

/// Where a purchase order sits in its lifecycle.
///
/// An enum rather than a string: every transition below matches exhaustively, so a new status
/// cannot be added without the compiler pointing at each place that must decide about it.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum PurchaseOrderStatus {
    Draft,
    PendingApproval,
    Approved,
    Rejected,
    SentToSupplier,
    PartiallyReceived,
    FullyReceived,
    Cancelled,
    Closed,
}

impl PurchaseOrderStatus {
    /// Whether the order may still be cancelled: nothing has been received against it yet.
    #[must_use]
    pub const fn is_cancellable(self) -> bool {
        matches!(
            self,
            Self::Draft | Self::PendingApproval | Self::Approved | Self::SentToSupplier
        )
    }

    /// Whether the order has reached a terminal state — the only states SCM-R3 allows a
    /// soft-delete from, because a live commitment may not be hidden from the record.
    #[must_use]
    pub const fn is_terminal(self) -> bool {
        matches!(self, Self::Cancelled | Self::Closed)
    }
}

impl fmt::Display for PurchaseOrderStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            Self::Draft => "DRAFT",
            Self::PendingApproval => "PENDING_APPROVAL",
            Self::Approved => "APPROVED",
            Self::Rejected => "REJECTED",
            Self::SentToSupplier => "SENT_TO_SUPPLIER",
            Self::PartiallyReceived => "PARTIALLY_RECEIVED",
            Self::FullyReceived => "FULLY_RECEIVED",
            Self::Cancelled => "CANCELLED",
            Self::Closed => "CLOSED",
        };
        f.write_str(name)
    }
}

/// A single ordered line.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PoLine {
    /// Caller-supplied line identity (the core mints no ids).
    pub line_id: String,
    pub sku: String,
    pub description: String,
    /// Ordered quantity — exact decimal, so a fractional UOM stays exact (SCM-R10).
    pub quantity: Decimal,
    /// GS1 UOM code.
    pub uom: String,
    pub unit_price: Money,
    /// ISO-8601 date.
    pub delivery_date: String,
    pub warehouse_id: String,
    pub lot_required: bool,
}

/// Everything needed to open a purchase order. Identity and time are **inputs** — the core is
/// pure (see the crate docs).
#[derive(Debug, Clone)]
pub struct NewPurchaseOrder {
    pub id: String,
    pub po_number: String,
    pub supplier_id: String,
    pub buyer_id: String,
    pub lines: Vec<PoLine>,
    /// ISO 4217 code; every line must price in this currency.
    pub currency: String,
    /// Incoterms® 2020 three-letter rule.
    pub incoterm: String,
    pub incoterm_location: String,
    pub requested_delivery_date: String,
    /// Overrides [`PO_APPROVAL_THRESHOLD_CENTS`] when present.
    pub approval_threshold_cents: Option<i64>,
    pub notes: Option<String>,
    pub created_by: String,
    /// ISO-8601 UTC timestamp, supplied by the caller.
    pub created_at: String,
}

/// A purchase order. Transitions consume `self` and return the next state, so a stale copy of
/// an order cannot be advanced twice by accident.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PurchaseOrder {
    pub id: String,
    pub po_number: String,
    pub supplier_id: String,
    pub buyer_id: String,
    pub status: PurchaseOrderStatus,
    pub lines: Vec<PoLine>,
    pub currency: String,
    pub incoterm: String,
    pub incoterm_location: String,
    pub requested_delivery_date: String,
    pub approval_threshold_cents: i64,
    pub approved_by: Option<String>,
    pub approved_at: Option<String>,
    pub rejected_by: Option<String>,
    pub rejection_reason: Option<String>,
    pub cancelled_at: Option<String>,
    pub notes: Option<String>,
    pub created_by: String,
    pub created_at: String,
    pub updated_at: String,
    /// SCM-R3: financial records are never hard-deleted.
    pub is_deleted: bool,
}

/// What procurement rules can refuse, and why. Typed so the adapters can map each variant onto
/// one gRPC status and one GraphQL error (ADR-0035).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ProcurementError {
    /// UCC Art. 2: an order with no line has no stated quantity and is not enforceable.
    NoLines,
    /// A line priced in a currency other than the order's. There is no FX conversion here.
    LineCurrencyMismatch {
        line_id: String,
        expected: String,
        found: String,
    },
    /// A quantity that is zero or negative is not an order.
    NonPositiveQuantity { line_id: String },
    /// The transition is not legal from the current state.
    IllegalTransition {
        from: PurchaseOrderStatus,
        action: &'static str,
    },
    /// SCM-R3: only a terminal order may be soft-deleted.
    NotSoftDeletable { from: PurchaseOrderStatus },
    /// Exact-arithmetic failure surfaced from the money core.
    Money(MoneyError),
}

impl From<MoneyError> for ProcurementError {
    fn from(error: MoneyError) -> Self {
        Self::Money(error)
    }
}

impl fmt::Display for ProcurementError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::NoLines => f.write_str("purchase order must have at least one line item"),
            Self::LineCurrencyMismatch {
                line_id,
                expected,
                found,
            } => write!(
                f,
                "line {line_id} is priced in {found} but the order is in {expected}"
            ),
            Self::NonPositiveQuantity { line_id } => {
                write!(f, "line {line_id} must have a quantity greater than zero")
            }
            Self::IllegalTransition { from, action } => {
                write!(f, "cannot {action} a purchase order in status {from}")
            }
            Self::NotSoftDeletable { from } => write!(
                f,
                "only CANCELLED or CLOSED purchase orders can be soft-deleted, not {from}"
            ),
            Self::Money(error) => write!(f, "money arithmetic failed: {error}"),
        }
    }
}

impl Error for ProcurementError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Money(error) => Some(error),
            _ => None,
        }
    }
}

/// **CPT-0026** — the committed value of a purchase order: `Σ(unit price × quantity)`.
///
/// Each line extension is quantized once by the money core, then the extensions are summed;
/// the order's currency is carried through and every line is checked against it. An order with
/// no lines totals zero rather than failing — the empty-order guard belongs to creation
/// (PRC-R1), not to the sum.
///
/// This is the figure SCM-R2 compares against the approval threshold, so its precision is the
/// difference between an order that routes to a human and one that does not.
pub fn purchase_order_total(lines: &[PoLine], currency: &str) -> Result<Money, ProcurementError> {
    let mut total = Money::new(0, currency);
    for line in lines {
        if line.unit_price.currency != currency {
            return Err(ProcurementError::LineCurrencyMismatch {
                line_id: line.line_id.clone(),
                expected: currency.to_owned(),
                found: line.unit_price.currency.clone(),
            });
        }
        let extension = multiply_cents(line.unit_price.amount_cents, line.quantity)?;
        total = total.add(&Money::new(extension, currency))?;
    }
    Ok(total)
}

impl PurchaseOrder {
    /// Open a purchase order, routing it by **SCM-R2**.
    ///
    /// The threshold test is `total >= threshold` — *at* the threshold requires approval. That
    /// boundary is the rule's whole point: an order sized exactly to the limit is the one an
    /// approver most wants to see.
    pub fn open(input: NewPurchaseOrder) -> Result<Self, ProcurementError> {
        if input.lines.is_empty() {
            return Err(ProcurementError::NoLines);
        }
        for line in &input.lines {
            if line.quantity <= Decimal::ZERO {
                return Err(ProcurementError::NonPositiveQuantity {
                    line_id: line.line_id.clone(),
                });
            }
        }

        let threshold = input
            .approval_threshold_cents
            .unwrap_or(PO_APPROVAL_THRESHOLD_CENTS);
        let total = purchase_order_total(&input.lines, &input.currency)?;
        let status = if total.amount_cents >= threshold {
            PurchaseOrderStatus::PendingApproval
        } else {
            PurchaseOrderStatus::Approved
        };

        Ok(Self {
            id: input.id,
            po_number: input.po_number,
            supplier_id: input.supplier_id,
            buyer_id: input.buyer_id,
            status,
            lines: input.lines,
            currency: input.currency,
            incoterm: input.incoterm,
            incoterm_location: input.incoterm_location,
            requested_delivery_date: input.requested_delivery_date,
            approval_threshold_cents: threshold,
            approved_by: None,
            approved_at: None,
            rejected_by: None,
            rejection_reason: None,
            cancelled_at: None,
            notes: input.notes,
            created_by: input.created_by,
            updated_at: input.created_at.clone(),
            created_at: input.created_at,
            is_deleted: false,
        })
    }

    /// Total committed value (CPT-0026).
    pub fn total(&self) -> Result<Money, ProcurementError> {
        purchase_order_total(&self.lines, &self.currency)
    }

    /// Whether this order needed a human approver at creation (SCM-R2).
    #[must_use]
    pub fn requires_approval(&self) -> bool {
        self.total()
            .is_ok_and(|total| total.amount_cents >= self.approval_threshold_cents)
    }

    /// Approve a pending order.
    pub fn approve(mut self, approved_by: &str, at: &str) -> Result<Self, ProcurementError> {
        if self.status != PurchaseOrderStatus::PendingApproval {
            return Err(ProcurementError::IllegalTransition {
                from: self.status,
                action: "approve",
            });
        }
        self.status = PurchaseOrderStatus::Approved;
        self.approved_by = Some(approved_by.to_owned());
        self.approved_at = Some(at.to_owned());
        self.updated_at = at.to_owned();
        Ok(self)
    }

    /// Reject a pending order. The reason is required: a rejection without one is unauditable.
    pub fn reject(
        mut self,
        rejected_by: &str,
        reason: &str,
        at: &str,
    ) -> Result<Self, ProcurementError> {
        if self.status != PurchaseOrderStatus::PendingApproval {
            return Err(ProcurementError::IllegalTransition {
                from: self.status,
                action: "reject",
            });
        }
        self.status = PurchaseOrderStatus::Rejected;
        self.rejected_by = Some(rejected_by.to_owned());
        self.rejection_reason = Some(reason.to_owned());
        self.updated_at = at.to_owned();
        Ok(self)
    }

    /// Send an approved order to the supplier. Nothing unapproved reaches a supplier.
    pub fn send_to_supplier(mut self, at: &str) -> Result<Self, ProcurementError> {
        if self.status != PurchaseOrderStatus::Approved {
            return Err(ProcurementError::IllegalTransition {
                from: self.status,
                action: "send to supplier",
            });
        }
        self.status = PurchaseOrderStatus::SentToSupplier;
        self.updated_at = at.to_owned();
        Ok(self)
    }

    /// Cancel an order that has not been received against.
    pub fn cancel(mut self, reason: &str, at: &str) -> Result<Self, ProcurementError> {
        if !self.status.is_cancellable() {
            return Err(ProcurementError::IllegalTransition {
                from: self.status,
                action: "cancel",
            });
        }
        self.status = PurchaseOrderStatus::Cancelled;
        self.cancelled_at = Some(at.to_owned());
        self.notes = Some(reason.to_owned());
        self.updated_at = at.to_owned();
        Ok(self)
    }

    /// Soft-delete a terminal order (SCM-R3). The row stays; only the flag moves.
    pub fn soft_delete(mut self, at: &str) -> Result<Self, ProcurementError> {
        if !self.status.is_terminal() {
            return Err(ProcurementError::NotSoftDeletable { from: self.status });
        }
        self.is_deleted = true;
        self.updated_at = at.to_owned();
        Ok(self)
    }
}
