/**
 * Bill of Materials (BOM) domain model.
 *
 * A BOM defines the parent-component structure of a manufactured item:
 * which components (and how many of each) are consumed to make one unit
 * of the parent SKU. Multi-level explosion is performed downstream in
 * python/04_supply_planning/mrp.py bom_explosion().
 *
 * Aligns with SQL table supply_planning.bill_of_materials (schema.sql):
 *   parent_sku, component_sku, quantity_per, unit_of_measure,
 *   lead_time_periods, scrap_factor, bom_type, effective_from/to, is_active.
 *
 * BOM types:
 *   MANUFACTURING — production BOM consumed on the shop floor.
 *   ENGINEERING   — as-designed structure (eBOM), pre-production.
 *   PHANTOM       — non-stocked transient assembly; requirements pass through
 *                   to its children (lead_time_offset typically 0).
 *   PLANNING      — super-BOM / modular planning bill (option percentages).
 *
 * References:
 *  - Orlicky, J. "Material Requirements Planning" 3rd Ed. (McGraw-Hill, 2022) Ch.5
 *  - APICS CPIM 9.0 — Plan Supply (Bills of Material)
 *  - GS1 General Specifications v23 (UOM codes)
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, SKU, UOMCode, nowUTC } from '@scm/shared/types';

export type BOMType = 'MANUFACTURING' | 'ENGINEERING' | 'PHANTOM' | 'PLANNING';
export type BOMStatus = 'ACTIVE' | 'DRAFT' | 'OBSOLETE';

/**
 * A single component line of a parent BOM (value object).
 * quantityPer is the quantity of this component consumed to produce
 * exactly one unit of the parent SKU, before scrap inflation.
 */
export type BOMComponent = {
  readonly componentSku: SKU;
  readonly quantityPer: number;          // qty of component per 1 parent (> 0)
  readonly uom: UOMCode;                  // GS1 unit of measure
  readonly scrapFactorPct: number;       // scrap allowance %, default 0
  readonly sequenceNo: number;           // line ordering on the BOM
  readonly isPhantom: boolean;           // pass-through (non-stocked) component
  readonly leadTimeOffsetDays: number;   // offset receipt relative to parent
};

export type BillOfMaterialsRecord = {
  readonly id: string;
  readonly parentSku: SKU;
  readonly bomType: BOMType;
  readonly version: string;
  readonly status: BOMStatus;
  readonly effectiveFrom: ISODate;
  readonly effectiveTo?: ISODate;
  readonly components: readonly BOMComponent[];
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ── Creation ──────────────────────────────────────────────────────────────────

function create(
  parentSku: SKU,
  bomType: BOMType,
  version: string,
  effectiveFrom: ISODate = nowUTC().substring(0, 10),
): BillOfMaterialsRecord {
  if (!parentSku || parentSku.trim() === '') {
    throw new Error('BillOfMaterials: parentSku is required');
  }
  if (!version || version.trim() === '') {
    throw new Error('BillOfMaterials: version is required');
  }
  const ts = nowUTC();
  return {
    id: uuidv4(),
    parentSku,
    bomType,
    version,
    status: 'DRAFT',
    effectiveFrom,
    effectiveTo: undefined,
    components: [],
    isDeleted: false,
    createdAt: ts,
    updatedAt: ts,
  };
}

// ── Component mutation (immutable — returns new record) ─────────────────────────

function addComponent(
  bom: BillOfMaterialsRecord,
  component: {
    componentSku: SKU;
    quantityPer: number;
    uom: UOMCode;
    scrapFactorPct?: number;
    sequenceNo?: number;
    isPhantom?: boolean;
    leadTimeOffsetDays?: number;
  },
): BillOfMaterialsRecord {
  if (component.quantityPer <= 0) {
    throw new Error('BillOfMaterials: quantityPer must be > 0');
  }
  if (component.componentSku === bom.parentSku) {
    throw new Error('BillOfMaterials: a component cannot be its own parent (self-reference)');
  }
  if (bom.components.some(c => c.componentSku === component.componentSku)) {
    throw new Error(`BillOfMaterials: duplicate componentSku ${component.componentSku}`);
  }
  const scrapFactorPct = component.scrapFactorPct ?? 0;
  if (scrapFactorPct < 0) {
    throw new Error('BillOfMaterials: scrapFactorPct must be >= 0');
  }
  const newComponent: BOMComponent = {
    componentSku: component.componentSku,
    quantityPer: component.quantityPer,
    uom: component.uom,
    scrapFactorPct,
    sequenceNo: component.sequenceNo ?? bom.components.length + 1,
    isPhantom: component.isPhantom ?? false,
    leadTimeOffsetDays: component.leadTimeOffsetDays ?? 0,
  };
  return {
    ...bom,
    components: [...bom.components, newComponent],
    updatedAt: nowUTC(),
  };
}

function removeComponent(bom: BillOfMaterialsRecord, componentSku: SKU): BillOfMaterialsRecord {
  return {
    ...bom,
    components: bom.components.filter(c => c.componentSku !== componentSku),
    updatedAt: nowUTC(),
  };
}

// ── Lifecycle ───────────────────────────────────────────────────────────────────

function activate(bom: BillOfMaterialsRecord): BillOfMaterialsRecord {
  if (bom.components.length === 0) {
    throw new Error('BillOfMaterials: cannot activate a BOM with no components');
  }
  if (bom.effectiveTo && bom.effectiveTo <= bom.effectiveFrom) {
    throw new Error('BillOfMaterials: effectiveTo must be after effectiveFrom');
  }
  return { ...bom, status: 'ACTIVE', updatedAt: nowUTC() };
}

function obsolete(bom: BillOfMaterialsRecord, effectiveTo?: ISODate): BillOfMaterialsRecord {
  const end = effectiveTo ?? nowUTC().substring(0, 10);
  if (end < bom.effectiveFrom) {
    throw new Error('BillOfMaterials: effectiveTo must be after effectiveFrom');
  }
  return { ...bom, status: 'OBSOLETE', effectiveTo: end, updatedAt: nowUTC() };
}

// ── Helpers ──────────────────────────────────────────────────────────────────────

/**
 * Gross requirement of a component to build `parentQty` units of the parent,
 * inflated for the component's scrap allowance.
 *
 *   gross = parentQty * quantityPer * (1 + scrapFactorPct / 100)
 */
function grossRequirement(
  bom: BillOfMaterialsRecord,
  parentQty: number,
  componentSku: SKU,
): number {
  const component = bom.components.find(c => c.componentSku === componentSku);
  if (!component) {
    throw new Error(`BillOfMaterials: component ${componentSku} not found on BOM ${bom.parentSku}`);
  }
  return parentQty * component.quantityPer * (1 + component.scrapFactorPct / 100);
}

/**
 * Detect a circular BOM reference, i.e. the parent SKU appears somewhere in
 * its own multi-level component tree. Throws if a cycle is found.
 *
 * @param bom     the BOM being validated.
 * @param allBoms the full set of BOMs (one or more per parent SKU) used to
 *                resolve child structures during the depth-first traversal.
 */
function validateNoCycle(
  bom: BillOfMaterialsRecord,
  allBoms: readonly BillOfMaterialsRecord[],
): void {
  // Index active, non-deleted BOMs by parent SKU for fast child lookup.
  const byParent = new Map<SKU, BillOfMaterialsRecord>();
  for (const b of allBoms) {
    if (b.isDeleted || b.status === 'OBSOLETE') continue;
    if (!byParent.has(b.parentSku)) byParent.set(b.parentSku, b);
  }
  // Ensure the BOM under test participates even if it is still a DRAFT.
  byParent.set(bom.parentSku, bom);

  const root = bom.parentSku;
  const visiting = new Set<SKU>();

  const dfs = (sku: SKU, path: SKU[]): void => {
    if (sku === root && path.length > 0) {
      throw new Error(
        `BillOfMaterials: circular reference detected — ${[...path, sku].join(' -> ')}`,
      );
    }
    if (visiting.has(sku)) return;        // already fully explored on this branch
    visiting.add(sku);
    const childBom = byParent.get(sku);
    if (childBom) {
      for (const c of childBom.components) {
        dfs(c.componentSku, [...path, sku]);
      }
    }
    visiting.delete(sku);
  };

  for (const c of bom.components) {
    dfs(c.componentSku, [root]);
  }
}

// ── Namespace export ───────────────────────────────────────────────────────────

export const BillOfMaterials = {
  create,
  addComponent,
  removeComponent,
  activate,
  obsolete,
  grossRequirement,
  validateNoCycle,
};
