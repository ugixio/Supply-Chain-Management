/**
 * Procurement domain — barrel export.
 *
 * Aggregates and value objects for the Source (SCOR) bounded context:
 *  - Supplier        — master record, Kraljic segmentation
 *  - RFQ             — request for quotation / proposal
 *  - Contract        — frame agreements, blanket POs
 *  - PurchaseOrder   — PO with approval workflow
 *  - GoodsReceipt    — GRN / RECADV, receiving + 3-way match leg
 */

export * from './Supplier';
export * from './RFQ';
export * from './Contract';
export * from './PurchaseOrder';
export * from './GoodsReceipt';
