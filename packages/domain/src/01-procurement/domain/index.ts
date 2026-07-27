/**
 * Procurement domain — barrel export.
 *
 * Aggregates and value objects for the Source (SCOR) bounded context:
 *  - Supplier        — master record, Kraljic segmentation
 *  - RFQ             — request for quotation / proposal
 *  - Contract        — frame agreements, blanket POs
 *  - GoodsReceipt    — GRN / RECADV, receiving + 3-way match leg
 *
 * PurchaseOrder moved to the Rust core at L3b — `crates/scm-core/src/d01_procurement/`
 * (ADR-0035, ENG-R10). Business rules, invariants and state machines are the core's
 * responsibility; TypeScript keeps none of them. The remaining aggregates here follow.
 */

export * from './Supplier';
export * from './RFQ';
export * from './Contract';
export * from './GoodsReceipt';
