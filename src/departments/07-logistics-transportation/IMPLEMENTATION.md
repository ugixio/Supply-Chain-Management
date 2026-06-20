# Logistics & Transportation — Implementation Guide

**Department**: 07 — Logistics & Transportation
**Standard alignment**: Incoterms 2020, IATA, IMO/IMDG, WCO HS Nomenclature 2022,
EU CBAM Regulation 2023/956, ISO 28000:2022, C-TPAT, AEO, WTO TFA Art. 7
**Author**: Supply Chain Centre of Excellence
**Version**: 2.0 — 2026-06-20
**Status**: Approved for implementation

---

## Table of Contents

1. Executive Summary
2. Prerequisites & Dependencies
3. Phase 0: Assessment & AS-IS Analysis
4. Phase 1: Foundation & Master Data
5. Phase 2: Process Standardisation & Core Analytics
6. Phase 3: Mathematical Models
7. Phase 4: ML/AI Pipeline
8. Phase 5: Integration & Automation
9. Phase 6: Continuous Improvement
10. Technology Stack & Architecture
11. Change Management & Training
12. Implementation KPIs
13. Risk & Mitigation
14. Timeline Summary
15. References

---

## 1. Executive Summary

The Logistics & Transportation module governs the end-to-end physical movement of goods
from origin supplier facilities to final delivery destinations, spanning ocean freight,
air cargo, road transport, rail, and multimodal intermodal movements. This implementation
guide provides the complete technical and operational blueprint for deploying a
best-in-class Transportation Management capability aligned with SCOR-DS Deliver processes
(D1–D4) and Enable processes (EP.6 — Manage Transportation).

### Strategic objectives

- Achieve carrier OTD of 95 percent or above across all lanes within 18 months
- Reduce blended freight cost per kg-km by 12 percent year-one through lane consolidation
  and carrier optimisation
- Attain full Incoterms 2020 compliance on all international purchase orders, eliminating
  DDP mis-classification errors that expose the company to customs liability
- Implement real-time visibility on 100 percent of active shipments via GPS/AIS integration
  with project44 and FourKites
- Comply with EU CBAM carbon reporting requirements for all imports of covered goods
  effective from the 2026 definitive phase
- Automate HS code classification for 80 percent of new SKUs through BERT-based NLP,
  reducing customs broker dependency and mis-declaration risk

### Value at stake

Based on industry benchmarks (Gartner 2025, McKinsey Global Institute 2024), a
mid-size manufacturer with USD 500 million in annual procurement spend can expect:

| Lever | Annual Saving (USD) | Confidence |
|---|---|---|
| Freight modal shift optimisation | 3.5 M | High |
| Carrier consolidation & RFQ leverage | 2.1 M | High |
| Demurrage & detention elimination | 1.4 M | Medium |
| HS mis-classification duty recovery | 0.9 M | Medium |
| CBAM avoidance through supplier carbon data | 0.6 M | Low-Medium |
| **Total** | **8.5 M** | — |

---

## 2. Prerequisites & Dependencies

### 2.1 Upstream module dependencies

| Module | Dependency | Criticality |
|---|---|---|
| 01-procurement | Confirmed PO with Incoterms, supplier GLN, ship-from address | Blocking |
| 02-supplier-management | Supplier AEO/C-TPAT status, UFLPA clearance flags | Blocking |
| 03-inventory | Lot numbers, FEFO expiry dates, REACH SVHC flags | High |
| 04-demand-planning | Replenishment triggers, safety stock alerts | High |
| 06-warehouse | Dock scheduling, inbound appointment management | Medium |
| 10-compliance | CSDDD country risk, UFLPA supplier flags | High |

### 2.2 Infrastructure prerequisites

- Event Store operational (shared/EventStore.ts) — all shipment state transitions
  must be event-sourced
- Money type enforced: all freight costs in integer cents (USD or EUR base currency)
- ISO 8601 timestamps in UTC for all ETA/ATD/ATA fields
- Carrier master data loaded (SCAC codes, service contracts, rate cards)
- HS code tariff database loaded from WCO 2022 Harmonised System nomenclature

### 2.3 External API accounts & credentials

- project44 Movement API (real-time multimodal visibility)
- FourKites (ocean + road GPS tracking)
- CargoWise One (freight forwarding TMS)
- Customs broker API (e.g., Flexport, Expeditors, Kuehne+Nagel Digital)
- Port Community Systems: DAKOSY (Hamburg), Portbase (Rotterdam), PortXchange
- Carrier EDI gateway (Stedi, SPS Commerce, or direct VAN)

---

## 3. Phase 0: Assessment & AS-IS Analysis

**Duration**: Weeks 1–4
**Owner**: Logistics Centre of Excellence + external consulting partner

### 3.1 Current-state data collection

Collect the following datasets for baseline analysis:

```
Minimum 24 months of:
- Shipment history (origin, destination, carrier, mode, weight, volume,
  cost, requested delivery date, actual delivery date)
- Freight invoice data (carrier, lane, base rate, surcharges, accessorials)
- Customs entry data (HS codes used, duty paid, broker fees, exam holds)
- Carrier performance scorecards (if any)
- Claims history (damage, loss, shortage by carrier and lane)
```

### 3.2 AS-IS maturity assessment

Score each capability on Gartner's Supply Chain Technology Maturity Model (1–5):

| Capability | Target Score | Typical AS-IS |
|---|---|---|
| Shipment visibility | 4 (predictive ETAs) | 2 (milestone updates) |
| Freight cost management | 4 (dynamic benchmarking) | 2 (static rate cards) |
| Carrier performance management | 4 (automated scorecards) | 1 (manual reviews) |
| Customs compliance | 4 (automated classification) | 2 (broker-dependent) |
| Carbon footprint tracking | 3 (CBAM reporting) | 1 (none) |
| Route optimisation | 4 (AI-driven VRP) | 1 (manual routing) |

### 3.3 Gap analysis outputs

Deliverables from Phase 0:

1. Carrier spend cube (carrier x lane x mode x month)
2. OTD by carrier by lane (24-month trend)
3. Freight cost per kg-km by mode
4. HS code error rate from customs audits
5. Demurrage & detention spend by port and carrier
6. Carbon emissions inventory (tonne CO2e by shipment)

---

## 4. Phase 1: Foundation & Master Data

**Duration**: Weeks 5–10
**Owner**: Data Management team + IT

### 4.1 Carrier master data

Every carrier record must contain:

```typescript
interface CarrierMaster {
  carrierId: string;           // internal UUID
  scacCode: string;            // Standard Carrier Alpha Code (4-char)
  name: string;
  modes: TransportMode[];      // OCEAN | AIR | ROAD | RAIL | MULTIMODAL
  serviceContracts: ServiceContract[];
  aeoStatus: AEOStatus;        // EU AEO-C, AEO-S, AEO-F, or NONE
  ctpatStatus: boolean;        // US C-TPAT certified
  iataCode?: string;           // IATA 2-letter airline code (air carriers)
  ediCapabilities: EDIMessage[]; // DESADV, IFTMBC, IFTSTA
  isDeleted: boolean;          // soft-delete only
}
```

### 4.2 Lane master data

```typescript
interface LaneMaster {
  laneId: string;
  originGLN: string;           // GS1 GLN of origin facility
  destinationGLN: string;      // GS1 GLN of destination facility
  originPortLocode: string;    // UN/LOCODE
  destinationPortLocode: string;
  incoterms2020: Incoterms2020Rule;
  primaryMode: TransportMode;
  transitTimeDays: number;     // contractual transit time
  rateCents: number;           // base rate per UOM in integer cents
  rateUOM: 'PER_KG' | 'PER_CBM' | 'PER_TEU' | 'PER_FEU' | 'PER_UNIT';
  fuelSurchargePercent: number; // BAF/YAS/FSC as decimal (e.g. 0.18 for 18%)
  thcOriginCents: number;      // Terminal Handling Charge origin
  thcDestinationCents: number; // Terminal Handling Charge destination
  lastUpdated: ISOTimestamp;
}
```

### 4.3 HS code tariff database

Load the WCO 2022 HS nomenclature (98 chapters, ~5,000 headings, ~21,000 subheadings).
Augment with country-level extensions to 8-digit (EU Combined Nomenclature) and
10-digit (US HTS, CN Tariff).

```sql
-- Schema for tariff database
CREATE TABLE hs_codes (
  hs_code        VARCHAR(10) PRIMARY KEY,
  level          SMALLINT CHECK (level IN (2,4,6,8,10)),
  description    TEXT NOT NULL,
  parent_hs_code VARCHAR(10),
  chapter        CHAR(2),
  heading        CHAR(4),
  subheading     CHAR(6)
);

CREATE TABLE duty_rates (
  id              UUID PRIMARY KEY,
  hs_code         VARCHAR(10) REFERENCES hs_codes(hs_code),
  country_origin  CHAR(2),   -- ISO 3166-1 alpha-2
  country_import  CHAR(2),
  rate_type       VARCHAR(20), -- MFN | GSP | FTA | PREFERENTIAL | ANTIDUMPING
  ad_valorem_rate NUMERIC(6,4), -- e.g. 0.065 for 6.5%
  specific_rate_per_unit NUMERIC(12,4),
  unit_of_measure VARCHAR(10),
  effective_from  DATE,
  effective_to    DATE
);
```

### 4.4 Incoterms 2020 rule master

All 11 Incoterms 2020 rules must be loaded with their risk/cost transfer points:

```typescript
const INCOTERMS_2020_RULES = {
  EXW: { riskTransfer: 'AT_SELLERS_PREMISES', costCoveredBySeller: [] },
  FCA: { riskTransfer: 'NAMED_PLACE_DELIVERY_TO_CARRIER',
         costCoveredBySeller: ['EXPORT_CLEARANCE'] },
  CPT: { riskTransfer: 'NAMED_PLACE_DELIVERY_TO_CARRIER',
         costCoveredBySeller: ['EXPORT_CLEARANCE', 'MAIN_CARRIAGE'] },
  CIP: { riskTransfer: 'NAMED_PLACE_DELIVERY_TO_CARRIER',
         costCoveredBySeller: ['EXPORT_CLEARANCE', 'MAIN_CARRIAGE', 'INSURANCE_ICC_A'] },
  DAP: { riskTransfer: 'NAMED_DESTINATION',
         costCoveredBySeller: ['EXPORT_CLEARANCE', 'MAIN_CARRIAGE', 'DELIVERY'] },
  DPU: { riskTransfer: 'NAMED_DESTINATION_UNLOADED',
         costCoveredBySeller: ['EXPORT_CLEARANCE', 'MAIN_CARRIAGE', 'DELIVERY', 'UNLOADING'] },
  DDP: { riskTransfer: 'NAMED_DESTINATION',
         costCoveredBySeller: ['EXPORT_CLEARANCE', 'MAIN_CARRIAGE',
                               'DELIVERY', 'IMPORT_DUTY', 'IMPORT_VAT'] },
  FAS: { riskTransfer: 'ALONGSIDE_VESSEL_ORIGIN_PORT',
         costCoveredBySeller: ['EXPORT_CLEARANCE'] },
  FOB: { riskTransfer: 'ON_BOARD_VESSEL_ORIGIN_PORT',
         costCoveredBySeller: ['EXPORT_CLEARANCE', 'LOADING'] },
  CFR: { riskTransfer: 'ON_BOARD_VESSEL_ORIGIN_PORT',
         costCoveredBySeller: ['EXPORT_CLEARANCE', 'LOADING', 'MAIN_CARRIAGE_SEA'] },
  CIF: { riskTransfer: 'ON_BOARD_VESSEL_ORIGIN_PORT',
         costCoveredBySeller: ['EXPORT_CLEARANCE', 'LOADING',
                               'MAIN_CARRIAGE_SEA', 'INSURANCE_ICC_C'] },
} as const;
```

---

## 5. Phase 2: Process Standardisation & Core Analytics

**Duration**: Weeks 11–18
**Owner**: Logistics Operations + Business Process team

### 5.1 Shipment lifecycle process

Define standard state machine for all shipments:

```
DRAFT -> BOOKING_REQUESTED -> BOOKING_CONFIRMED -> IN_TRANSIT
      -> PORT_OF_LOADING -> CUSTOMS_CLEARANCE_EXPORT
      -> MAIN_CARRIAGE -> PORT_OF_DISCHARGE
      -> CUSTOMS_CLEARANCE_IMPORT -> LAST_MILE
      -> DELIVERED | EXCEPTION | CANCELLED
```

Every state transition emits a domain event to the Event Store:
`ShipmentBooked`, `ShipmentDeparted`, `ShipmentArrived`, `CustomsClearedExport`,
`CustomsClearedImport`, `ShipmentDelivered`, `ShipmentExceptionRaised`.

### 5.2 Carrier performance baseline

Establish automated weekly carrier scorecards from day one of Phase 2.
Do not wait for ML models. Simple SQL aggregations are sufficient for baseline:

```sql
SELECT
  carrier_id,
  COUNT(*) AS total_shipments,
  SUM(CASE WHEN actual_delivery_date <= requested_delivery_date THEN 1 ELSE 0 END)
    * 100.0 / COUNT(*) AS otd_percent,
  AVG(actual_transit_days - contracted_transit_days) AS avg_transit_variance_days,
  SUM(claims_amount_cents) * 1.0 / SUM(freight_cost_cents) AS damage_loss_ratio,
  SUM(freight_cost_cents) * 1.0 / SUM(gross_weight_kg * distance_km)
    AS cost_per_kg_km_cents
FROM shipments
WHERE shipment_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY carrier_id;
```

### 5.3 Freight invoice audit process

Automate matching of carrier invoices against contracted rates. Flag exceptions:

- Rate applied differs from contracted rate by more than 2 percent
- Fuel surcharge percentage exceeds agreed BAF index cap
- Accessorial charges not pre-authorised (detention, re-delivery, address correction)
- Invoice received more than 30 days after delivery (statute of limitations risk)

Target: 100 percent automated matching on standard charges; exceptions routed to
logistics analyst queue within 24 hours.

---

## 6. Phase 3: Mathematical Models

**Duration**: Weeks 15–24
**Owner**: Analytics & Data Science team

### 6.1 Incoterms 2020 Cost Allocation Model

#### 6.1.1 Risk and cost transfer points (all 11 rules)

| Rule | Risk Transfers At | Seller Pays | Buyer Pays | Insurance |
|---|---|---|---|---|
| EXW | Seller's premises | Nothing | Everything | Buyer arranges |
| FCA | Named place / On board (FCA+B/L) | Export clearance | Main carriage, import | Buyer arranges |
| FAS | Alongside vessel, origin port | Export clearance | Loading, main carriage, import | Buyer arranges |
| FOB | On board vessel, origin port | Export clearance, loading | Main carriage, import | Buyer arranges |
| CFR | On board vessel, origin port | Export clearance, loading, sea freight | Import, unloading | Buyer arranges |
| CIF | On board vessel, origin port | Export clearance, loading, sea freight, ICC-C insurance | Import, unloading | Seller — minimum ICC-C |
| CPT | Delivery to first carrier | Export clearance, main carriage | Import, last mile | Buyer arranges |
| CIP | Delivery to first carrier | Export clearance, main carriage, ICC-A insurance | Import, last mile | Seller — full ICC-A |
| DAP | Named destination, uncleared | Export clearance, main carriage, last mile | Import duty, VAT, unloading | Seller's risk from origin |
| DPU | Named destination, unloaded | Export clearance, main carriage, last mile, unloading | Import duty, VAT | Seller's risk |
| DDP | Named destination | Everything including import duty and VAT | Nothing | Seller's risk |

**Critical note on CIF vs CIP insurance**: CIF requires only Institute Cargo Clauses (C)
— minimum cover. CIP requires ICC (A) — all-risk cover. This is a common negotiation
trap: sellers prefer CIF, buyers should push for CIP when seller arranges insurance.

#### 6.1.2 CIF vs DDP landed cost comparison

```typescript
interface LandedCostCalculation {
  goodsValueCents: number;       // FOB value in cents
  oceanFreightCents: number;
  insuranceCents: number;        // 0.5-1.5% of CIF value typical
  originTHCCents: number;        // Terminal Handling Charge at loading port
  destinationTHCCents: number;
  customsDutyRateBps: number;    // basis points (e.g. 650 = 6.5%)
  customsBrokerFeeCents: number;
  importVatRateBps: number;      // e.g. 2000 = 20% (EU standard rate)
  demurrageCents: number;        // if container not returned within free time
  lastMileFreightCents: number;
}

function computeLandedCost(input: LandedCostCalculation): {
  cifValueCents: number;
  dutiableValueCents: number;
  customsDutyCents: number;
  importVatCents: number;
  totalLandedCostCents: number;
} {
  const cifValueCents =
    input.goodsValueCents +
    input.oceanFreightCents +
    input.insuranceCents;

  // WTO Customs Valuation Agreement Art.1: dutiable value = CIF at port of import
  const dutiableValueCents = cifValueCents + input.destinationTHCCents;

  const customsDutyCents = Math.round(
    (dutiableValueCents * input.customsDutyRateBps) / 10000
  );

  // EU VAT base = CIF + duty + THC (Article 86 UCC)
  const vatBaseCents = dutiableValueCents + customsDutyCents;
  const importVatCents = Math.round(
    (vatBaseCents * input.importVatRateBps) / 10000
  );

  const totalLandedCostCents =
    cifValueCents +
    input.originTHCCents +
    input.destinationTHCCents +
    customsDutyCents +
    input.customsBrokerFeeCents +
    importVatCents +
    input.demurrageCents +
    input.lastMileFreightCents;

  return {
    cifValueCents,
    dutiableValueCents,
    customsDutyCents,
    importVatCents,
    totalLandedCostCents,
  };
}
```

**CIF vs DDP decision table** (buyer perspective):

| Scenario | Prefer CIF | Prefer DDP |
|---|---|---|
| Buyer has AEO status | Yes — lower duty cost, AEO fast lane | No |
| Supplier in UFLPA-risk country | Yes — buyer controls clearance | Never — supplier controls, risk of seizure |
| High-value goods with damage risk | Avoid (ICC-C only) | N/A (buyer arranges ICC-A under DAP/DDP variant) |
| Buyer lacks import license | No | Yes — seller handles |
| VAT-registered at destination | Yes — reclaim import VAT | Yes — but seller may not recover VAT |

### 6.2 Freight Cost Calculation

#### 6.2.1 IATA volumetric weight formula (air cargo)

The International Air Transport Association defines chargeable weight as the greater
of actual gross weight and volumetric weight:

```
Volumetric Weight (kg) = (L_cm x W_cm x H_cm) / 6000

Equivalently:
1 cubic metre = 166.67 kg (commonly rounded to 167 kg)

Chargeable Weight = max(Gross Weight, Volumetric Weight)
```

```python
def compute_chargeable_weight_air(
    gross_weight_kg: float,
    length_cm: float,
    width_cm: float,
    height_cm: float,
) -> dict:
    """
    Compute IATA chargeable weight for air freight.

    Returns dict with volumetric_kg, chargeable_kg, and basis.
    Reference: IATA Cargo Services Conference Resolution 123.
    """
    volumetric_kg = (length_cm * width_cm * height_cm) / 6000.0
    chargeable_kg = max(gross_weight_kg, volumetric_kg)
    basis = "VOLUMETRIC" if volumetric_kg > gross_weight_kg else "ACTUAL"
    return {
        "gross_weight_kg": gross_weight_kg,
        "volumetric_kg": round(volumetric_kg, 2),
        "chargeable_kg": round(chargeable_kg, 2),
        "basis": basis,
    }
```

#### 6.2.2 Fuel surcharge (BAF / YAS / FSC)

Bunker Adjustment Factor (ocean) and Fuel Surcharge (air) are contractually linked
to published indices. Calculate as follows:

```python
def compute_freight_cost_cents(
    base_rate_cents_per_kg: int,
    chargeable_kg: float,
    fuel_surcharge_rate: float,   # e.g. 0.18 for 18%
    security_surcharge_cents: int,
    war_risk_surcharge_cents: int,
    peak_season_surcharge_cents: int,
) -> int:
    """
    Compute total air/ocean freight cost in integer cents.
    All monetary inputs and outputs are integer cents.
    """
    base_cost_cents = round(base_rate_cents_per_kg * chargeable_kg)
    fuel_surcharge_cents = round(base_cost_cents * fuel_surcharge_rate)
    total_cents = (
        base_cost_cents
        + fuel_surcharge_cents
        + security_surcharge_cents
        + war_risk_surcharge_cents
        + peak_season_surcharge_cents
    )
    return total_cents
```

#### 6.2.3 Terminal Handling Charge (THC)

THC is assessed per TEU or per cargo unit by the ocean carrier at origin and destination.
It is NOT included in the ocean freight rate under Incoterms 2020:

```
THC Total = THC_Origin (charged to shipper) + THC_Destination (charged to consignee)

For FCL:
  THC_Origin per TEU:  USD 165–280 (Shanghai), USD 195–310 (Rotterdam)
  THC_Destination per TEU: USD 200–350 (Los Angeles), USD 165–240 (Hamburg)

For LCL (charged per CBM or per W/M — weight/measurement ton, whichever greater):
  W/M ton = max(weight_kg / 1000, volume_cbm)  [1 revenue ton = 1 tonne or 1 CBM]
```

```python
def compute_lcl_revenue_tons(weight_kg: float, volume_cbm: float) -> float:
    """
    Compute LCL revenue tons (W/M — weight or measurement, whichever greater).
    Used for LCL ocean freight and THC calculation.
    """
    weight_tons = weight_kg / 1000.0
    return max(weight_tons, volume_cbm)
```

### 6.3 Landed Cost Model

The complete landed cost formula integrating all cost elements:

```
Landed Cost = Goods Value (EXW)
            + Origin Charges (export clearance + origin THC + stuffing)
            + Main Carriage (ocean/air/road freight)
            + Insurance Premium
            + Destination THC
            + Customs Duty (ad valorem or specific)
            + Anti-Dumping / Countervailing Duty (if applicable)
            + Customs Broker Fee
            + Import VAT / GST (where non-recoverable)
            + Port Demurrage (if free time exceeded)
            + Detention (container usage beyond free time)
            + Last Mile Delivery
            + CBAM Carbon Cost (EU imports of covered goods from 2026)
```

```python
from dataclasses import dataclass

@dataclass
class LandedCostInputs:
    goods_value_cents: int          # EXW value in integer cents
    export_clearance_cents: int
    origin_thc_cents: int
    ocean_freight_cents: int
    insurance_cents: int
    destination_thc_cents: int
    customs_duty_rate_bps: int      # basis points (10000 = 100%)
    antidumping_duty_rate_bps: int  # 0 if not applicable
    customs_broker_fee_cents: int
    import_vat_rate_bps: int
    vat_recoverable: bool           # False for B2C, often True for B2B
    demurrage_cents: int
    detention_cents: int
    last_mile_cents: int
    cbam_cost_cents: int            # 0 if non-EU or non-covered goods

def compute_full_landed_cost(inp: LandedCostInputs) -> dict:
    """
    Compute full landed cost with all cost components.
    All values in integer cents. Returns breakdown dict.
    """
    cif_value_cents = (
        inp.goods_value_cents
        + inp.origin_thc_cents
        + inp.ocean_freight_cents
        + inp.insurance_cents
    )

    # WTO Customs Valuation Agreement: transaction value = CIF at port of import
    dutiable_value_cents = cif_value_cents + inp.destination_thc_cents

    customs_duty_cents = round(dutiable_value_cents * inp.customs_duty_rate_bps / 10000)
    antidumping_cents = round(dutiable_value_cents * inp.antidumping_duty_rate_bps / 10000)
    total_duty_cents = customs_duty_cents + antidumping_cents

    vat_base_cents = dutiable_value_cents + total_duty_cents
    import_vat_gross_cents = round(vat_base_cents * inp.import_vat_rate_bps / 10000)
    import_vat_net_cents = 0 if inp.vat_recoverable else import_vat_gross_cents

    total_landed_cost_cents = (
        inp.goods_value_cents
        + inp.export_clearance_cents
        + inp.origin_thc_cents
        + inp.ocean_freight_cents
        + inp.insurance_cents
        + inp.destination_thc_cents
        + total_duty_cents
        + inp.customs_broker_fee_cents
        + import_vat_net_cents
        + inp.demurrage_cents
        + inp.detention_cents
        + inp.last_mile_cents
        + inp.cbam_cost_cents
    )

    return {
        "goods_value_cents": inp.goods_value_cents,
        "cif_value_cents": cif_value_cents,
        "dutiable_value_cents": dutiable_value_cents,
        "customs_duty_cents": customs_duty_cents,
        "antidumping_duty_cents": antidumping_cents,
        "import_vat_gross_cents": import_vat_gross_cents,
        "import_vat_net_cents": import_vat_net_cents,
        "total_landed_cost_cents": total_landed_cost_cents,
    }
```

### 6.4 HS Code Classification Pipeline

#### 6.4.1 HS code hierarchy

```
Level 1: Chapter (2 digits)       e.g. 84 — Nuclear reactors, boilers, machinery
Level 2: Heading (4 digits)       e.g. 8471 — Automatic data processing machines
Level 3: Subheading (6 digits)    e.g. 847130 — Portable ADP machines, weight <= 10 kg
Level 4: Tariff line (8 digits)   e.g. 84713000 — EU CN 8-digit
Level 5: Statistical (10 digits)  e.g. 8471300000 — US HTS / national extensions
```

#### 6.4.2 Duty rate lookup pipeline

```python
def lookup_duty_rate(
    hs_code_6: str,
    country_of_origin: str,
    country_of_import: str,
    db_session,
) -> dict:
    """
    Look up applicable duty rate for HS code + trade lane combination.
    Preferential rates take precedence over MFN where RoO are met.

    Returns dict with rate_type, ad_valorem_rate, notes.
    """
    # Priority: FTA > GSP > MFN > Antidumping
    rates = db_session.query(DutyRate).filter(
        DutyRate.hs_code.startswith(hs_code_6),
        DutyRate.country_origin == country_of_origin,
        DutyRate.country_import == country_of_import,
        DutyRate.effective_from <= date.today(),
        (DutyRate.effective_to == None) | (DutyRate.effective_to >= date.today()),
    ).order_by(DutyRate.ad_valorem_rate.asc()).all()

    if not rates:
        raise ValueError(f"No duty rate found for HS {hs_code_6} "
                         f"{country_of_origin}->{country_of_import}")

    preferred = next((r for r in rates if r.rate_type in ('FTA', 'GSP')), None)
    mfn = next((r for r in rates if r.rate_type == 'MFN'), None)
    antidumping = next((r for r in rates if r.rate_type == 'ANTIDUMPING'), None)

    applicable = preferred or mfn
    return {
        "rate_type": applicable.rate_type if applicable else "UNKNOWN",
        "ad_valorem_rate": applicable.ad_valorem_rate if applicable else None,
        "antidumping_rate": antidumping.ad_valorem_rate if antidumping else 0,
        "mfn_rate": mfn.ad_valorem_rate if mfn else None,
        "saving_vs_mfn_bps": round(
            (mfn.ad_valorem_rate - preferred.ad_valorem_rate) * 10000
        ) if (preferred and mfn) else 0,
    }
```

#### 6.4.3 Rules of origin determination

Two primary tests apply under most FTAs:

| Test | Description | Triggers |
|---|---|---|
| Wholly Obtained (WO) | Product entirely produced in one country (minerals, agricultural goods) | Chapter 1-24 primary goods |
| Substantial Transformation (ST) | Change of HS chapter/heading/subheading, or RVC threshold met | Manufactured goods |
| Regional Value Content (RVC) | Value added in FTA territory meets percentage threshold | USMCA: 60-75% depending on method |
| Specific Process Rule | Must undergo defined manufacturing process | Textiles, chemicals |

```python
def assess_rules_of_origin(
    hs_code_input: str,    # HS code of input materials
    hs_code_output: str,   # HS code of finished good
    input_value_cents: int,
    output_value_cents: int,
    fta_agreement: str,    # e.g. 'EU-KOREA', 'USMCA', 'CPTPP'
) -> dict:
    """
    Assess whether substantial transformation test is met for FTA preferential rate.
    Returns eligibility assessment and confidence score.
    """
    chapter_change = hs_code_input[:2] != hs_code_output[:2]
    heading_change = hs_code_input[:4] != hs_code_output[:4]
    subheading_change = hs_code_input[:6] != hs_code_output[:6]

    # Simplified RVC (build-down method)
    non_originating_value = input_value_cents
    rvc_percent = (output_value_cents - non_originating_value) / output_value_cents * 100

    return {
        "chapter_change": chapter_change,
        "heading_change": heading_change,
        "subheading_change": subheading_change,
        "rvc_percent": round(rvc_percent, 1),
        "fta_agreement": fta_agreement,
        "preliminary_eligible": chapter_change or (rvc_percent >= 40),
        "requires_legal_review": not chapter_change and rvc_percent < 40,
    }
```

### 6.5 Carrier Performance Scorecard Model

```python
import numpy as np

def compute_carrier_scorecard(
    shipment_records: list[dict],
    weights: dict = None,
) -> dict:
    """
    Compute weighted carrier KPI scorecard.

    Formula for cost per kg*km (efficiency index):
    cost_index = sum(freight_cost_cents) / sum(weight_kg * distance_km)

    OTD = on-time deliveries / total deliveries
    Transit time variance = std(actual_transit - contracted_transit)
    Damage rate = damaged shipments / total shipments
    """
    if weights is None:
        weights = {
            "otd": 0.40,
            "transit_variance": 0.25,
            "damage_rate": 0.20,
            "cost_efficiency": 0.15,
        }

    total = len(shipment_records)
    if total == 0:
        raise ValueError("No shipment records provided")

    on_time = sum(1 for s in shipment_records
                  if s["actual_delivery_date"] <= s["requested_delivery_date"])
    otd_score = on_time / total

    transit_variances = [
        s["actual_transit_days"] - s["contracted_transit_days"]
        for s in shipment_records
    ]
    transit_variance_days = float(np.std(transit_variances))
    # Normalise: 0 variance = 1.0 score, 3-day std = 0.0 score
    transit_score = max(0.0, 1.0 - (transit_variance_days / 3.0))

    damaged = sum(1 for s in shipment_records if s.get("has_damage_claim", False))
    damage_rate = damaged / total
    damage_score = max(0.0, 1.0 - (damage_rate / 0.05))  # 5% damage rate = 0 score

    total_cost = sum(s["freight_cost_cents"] for s in shipment_records)
    total_tkm = sum(s["weight_kg"] * s["distance_km"] for s in shipment_records)
    cost_per_tkm = total_cost / total_tkm if total_tkm > 0 else 0
    # Normalised against benchmark: lower is better
    benchmark_cents_per_tkm = 5.0  # adjust per mode/lane
    cost_score = min(1.0, benchmark_cents_per_tkm / cost_per_tkm) if cost_per_tkm else 0

    composite_score = (
        weights["otd"] * otd_score
        + weights["transit_variance"] * transit_score
        + weights["damage_rate"] * damage_score
        + weights["cost_efficiency"] * cost_score
    ) * 100

    return {
        "otd_percent": round(otd_score * 100, 1),
        "transit_variance_days": round(transit_variance_days, 2),
        "damage_rate_percent": round(damage_rate * 100, 2),
        "cost_per_tkm_cents": round(cost_per_tkm, 4),
        "composite_score": round(composite_score, 1),
        "rating": (
            "PREFERRED" if composite_score >= 90 else
            "APPROVED" if composite_score >= 75 else
            "CONDITIONAL" if composite_score >= 60 else
            "PROBATION" if composite_score >= 45 else
            "DISQUALIFIED"
        ),
    }
```

### 6.6 Route Optimisation — Vehicle Routing Problem (VRP)

#### 6.6.1 VRP mathematical formulation

The Capacitated Vehicle Routing Problem with Time Windows (CVRPTW) is formulated as:

```
Minimise:  sum_{k in K} sum_{i in V} sum_{j in V} c_ij * x_ijk

Subject to:
  (1) sum_{k in K} sum_{j in V} x_ijk = 1        for all i in C  [each customer visited once]
  (2) sum_{i in V} x_ijk = sum_{i in V} x_jik    for all j in C, k in K  [flow conservation]
  (3) sum_{i in C} d_i * sum_{j in V} x_ijk <= Q_k  for all k in K  [capacity constraint]
  (4) s_ik + t_ij - M(1 - x_ijk) <= s_jk        for all i,j in V, k in K  [time propagation]
  (5) a_i <= s_ik <= b_i                          for all i in C, k in K  [time windows]

Where:
  K = set of vehicles
  V = set of all nodes (depot + customers)
  C = set of customer nodes
  c_ij = cost of arc (i,j) [distance or time]
  x_ijk = 1 if vehicle k travels from i to j, else 0
  d_i = demand at customer i
  Q_k = capacity of vehicle k
  s_ik = service start time at node i by vehicle k
  t_ij = travel time from i to j
  [a_i, b_i] = time window at node i
  M = large constant (big-M method)
```

#### 6.6.2 OR-Tools CVRPTW implementation

```python
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np

def solve_vrptw(
    distance_matrix: list[list[int]],  # in metres, integer
    demands: list[int],                # in kg, integer
    vehicle_capacities: list[int],     # in kg, integer
    time_windows: list[tuple[int,int]], # (earliest, latest) in minutes from depot open
    depot_index: int = 0,
    time_limit_seconds: int = 30,
) -> dict:
    """
    Solve CVRPTW using Google OR-Tools.
    Returns optimised routes, total distance, and total load per vehicle.

    Reference: OR-Tools CVRPTW example — Google Operations Research (2024).
    """
    num_vehicles = len(vehicle_capacities)
    manager = pywrapcp.RoutingIndexManager(
        len(distance_matrix), num_vehicles, depot_index
    )
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Capacity constraint
    def demand_callback(from_idx):
        from_node = manager.IndexToNode(from_idx)
        return demands[from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, vehicle_capacities, True, "Capacity"
    )

    # Time window constraint (assume speed = 50 km/h avg; distance in m -> time in min)
    def time_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return int(distance_matrix[from_node][to_node] / 1000 / 50 * 60)

    time_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.AddDimension(time_callback_index, 30, 480, False, "Time")
    time_dimension = routing.GetDimensionOrDie("Time")
    for node_idx, (tw_start, tw_end) in enumerate(time_windows):
        index = manager.NodeToIndex(node_idx)
        time_dimension.CumulVar(index).SetRange(tw_start, tw_end)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.seconds = time_limit_seconds

    solution = routing.SolveWithParameters(search_params)

    if not solution:
        return {"status": "NO_SOLUTION", "routes": [], "total_distance_m": 0}

    routes = []
    total_distance = 0
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route = []
        route_distance = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            prev_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(prev_index, index, vehicle_id)
        routes.append({"vehicle_id": vehicle_id, "route": route, "distance_m": route_distance})
        total_distance += route_distance

    return {
        "status": "OPTIMAL" if solution.ObjectiveValue() > 0 else "FEASIBLE",
        "routes": routes,
        "total_distance_m": total_distance,
        "objective_value": solution.ObjectiveValue(),
    }
```

### 6.7 CBAM Carbon Cost in Freight

EU Carbon Border Adjustment Mechanism (Regulation 2023/956) applies to imports of
iron/steel, aluminium, cement, fertilisers, electricity, and hydrogen from 2026.
Embedded emissions in freight must be reported and certificates purchased.

#### 6.7.1 Emission intensity by transport mode (tonne CO2e per tonne-km)

| Mode | CO2e per tonne-km (g) | Source | Notes |
|---|---|---|---|
| Air freight | 500–800 | ICAO Carbon Calculator | Includes uplift factor 1.9 (non-CO2 effects) |
| Ocean (container) | 10–16 | IMO 4th GHG Study 2020 | Per MEPC.342(78) CII rating |
| Road (diesel HGV) | 60–100 | GLEC Framework v3.0 | EU average Euro VI fleet |
| Road (electric HGV) | 10–25 | GLEC Framework v3.0 | Depends on grid intensity |
| Rail (electrified) | 5–15 | EEA 2024 | EU average grid mix |
| Rail (diesel) | 25–40 | GLEC Framework v3.0 | |
| Inland waterway | 25–35 | GLEC Framework v3.0 | |

#### 6.7.2 CBAM carbon cost calculation

```python
def compute_cbam_freight_carbon_cost_cents(
    weight_kg: float,
    distance_km: float,
    mode: str,                    # 'AIR' | 'OCEAN' | 'ROAD' | 'RAIL'
    cbam_allowance_price_eur_cents: int,  # EU ETS price per tonne CO2e in cents
    emission_factor_g_per_tkm: float = None,
) -> dict:
    """
    Compute CBAM carbon cost for freight movements into the EU.
    Uses GLEC Framework v3.0 emission factors.

    cbam_allowance_price_eur_cents: current EU ETS price (e.g. 6500 = EUR 65.00)
    Returns cost in EUR cents (integer).
    """
    DEFAULT_FACTORS = {
        "AIR": 600.0,    # g CO2e per tonne-km (with RFI uplift)
        "OCEAN": 12.0,
        "ROAD": 75.0,
        "RAIL": 10.0,
    }
    factor = emission_factor_g_per_tkm or DEFAULT_FACTORS[mode]

    tonne_km = (weight_kg / 1000.0) * distance_km
    emissions_g = factor * tonne_km
    emissions_tonnes = emissions_g / 1_000_000.0

    # CBAM certificate cost = emissions (tCO2e) x ETS price (EUR/tonne)
    cost_eur_cents = round(emissions_tonnes * cbam_allowance_price_eur_cents)

    return {
        "tonne_km": round(tonne_km, 2),
        "emissions_g_co2e": round(emissions_g, 2),
        "emissions_tonnes_co2e": round(emissions_tonnes, 6),
        "cbam_cost_eur_cents": cost_eur_cents,
        "mode": mode,
        "emission_factor_g_per_tkm": factor,
    }
```

### 6.8 Customs Duty Calculation with MFN vs Preferential Rates

```python
def compute_customs_duty_cents(
    dutiable_value_cents: int,
    hs_code_6: str,
    country_of_origin: str,
    country_of_import: str,
    has_eur1_certificate: bool,
    has_form_a_gsp: bool,
    db_session,
) -> dict:
    """
    Compute customs duty applying correct rate (MFN, GSP, FTA).
    Preferential rates require documentary proof (EUR.1, Form A, REX).
    Returns duty breakdown in integer cents.
    """
    rates = lookup_duty_rate(hs_code_6, country_of_origin, country_of_import, db_session)

    mfn_rate = rates["mfn_rate"] or 0.0
    preferred_rate = None
    rate_type = "MFN"

    if has_eur1_certificate and rates["rate_type"] == "FTA":
        preferred_rate = rates["ad_valorem_rate"]
        rate_type = "FTA"
    elif has_form_a_gsp and rates["rate_type"] == "GSP":
        preferred_rate = rates["ad_valorem_rate"]
        rate_type = "GSP"

    applied_rate = preferred_rate if preferred_rate is not None else mfn_rate

    duty_cents = round(dutiable_value_cents * applied_rate)
    mfn_duty_cents = round(dutiable_value_cents * mfn_rate)
    antidumping_cents = round(dutiable_value_cents * rates["antidumping_rate"])

    return {
        "applied_rate_type": rate_type,
        "applied_rate": applied_rate,
        "duty_cents": duty_cents,
        "mfn_duty_cents": mfn_duty_cents,
        "antidumping_duty_cents": antidumping_cents,
        "total_duty_cents": duty_cents + antidumping_cents,
        "duty_saving_vs_mfn_cents": mfn_duty_cents - duty_cents,
        "documentary_proof_required": rate_type in ("FTA", "GSP"),
    }
```

---

## 7. Phase 4: ML/AI Pipeline

**Duration**: Weeks 20–36
**Owner**: Data Science team + Logistics Analytics

### 7.1 XGBoost Delivery Delay Prediction

#### 7.1.1 Feature engineering

| Feature | Type | Source | Notes |
|---|---|---|---|
| carrier_id | Categorical (OHE) | Carrier master | SCAC code encoded |
| origin_locode | Categorical (OHE) | Shipment | UN/LOCODE |
| destination_locode | Categorical (OHE) | Shipment | UN/LOCODE |
| transport_mode | Categorical | Shipment | OCEAN/AIR/ROAD/RAIL |
| contracted_transit_days | Numeric | Lane master | |
| booking_lead_days | Numeric | Computed | Days between booking and ETD |
| shipment_weight_kg | Numeric | Shipment | |
| shipment_volume_cbm | Numeric | Shipment | |
| incoterms_rule | Categorical | PO | FOB/CIF/DDP etc. |
| week_of_year | Numeric | ETD | Seasonality (peak season = weeks 36-42) |
| month | Numeric | ETD | |
| origin_port_congestion_index | Numeric | External API | 0-100 scale |
| destination_port_congestion_index | Numeric | External API | 0-100 scale |
| weather_risk_origin | Numeric | Weather API | 0-1 probability of disruption |
| carrier_90d_otd | Numeric | Computed rolling | Historical OTD on lane |
| lane_avg_delay_days_90d | Numeric | Computed rolling | |

#### 7.1.2 Training pipeline

```python
import xgboost as xgb
import shap
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.preprocessing import OrdinalEncoder

def train_delay_prediction_model(
    df: pd.DataFrame,
    target_col: str = "delay_days",
    binary_target_col: str = "is_delayed",
    n_splits: int = 5,
) -> dict:
    """
    Train XGBoost model to predict delivery delays.
    Uses time-series cross-validation to prevent data leakage.
    Returns trained model, feature importance, and SHAP explainer.

    Features must be pre-computed as described in Section 7.1.1.
    Target: delay_days (regression) or is_delayed (classification).
    """
    categorical_cols = [
        "carrier_id", "origin_locode", "destination_locode",
        "transport_mode", "incoterms_rule"
    ]
    numeric_cols = [
        "contracted_transit_days", "booking_lead_days", "shipment_weight_kg",
        "shipment_volume_cbm", "week_of_year", "month",
        "origin_port_congestion_index", "destination_port_congestion_index",
        "weather_risk_origin", "carrier_90d_otd", "lane_avg_delay_days_90d"
    ]

    encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    df[categorical_cols] = encoder.fit_transform(df[categorical_cols])

    feature_cols = categorical_cols + numeric_cols
    X = df[feature_cols]
    y_binary = df[binary_target_col]

    tscv = TimeSeriesSplit(n_splits=n_splits)
    auc_scores = []

    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=10,
        scale_pos_weight=(y_binary == 0).sum() / (y_binary == 1).sum(),
        use_label_encoder=False,
        eval_metric="auc",
        early_stopping_rounds=50,
        random_state=42,
        enable_categorical=True,
    )

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y_binary.iloc[train_idx], y_binary.iloc[val_idx]
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        preds = model.predict_proba(X_val)[:, 1]
        auc_scores.append(roc_auc_score(y_val, preds))

    # Retrain on full dataset
    model.fit(X, y_binary, verbose=False)

    # SHAP explainability
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X.sample(min(1000, len(X)), random_state=42))

    feature_importance = pd.DataFrame({
        "feature": feature_cols,
        "shap_mean_abs": abs(shap_values).mean(axis=0),
    }).sort_values("shap_mean_abs", ascending=False)

    return {
        "model": model,
        "encoder": encoder,
        "explainer": explainer,
        "cv_auc_mean": round(sum(auc_scores) / len(auc_scores), 4),
        "cv_auc_scores": auc_scores,
        "feature_importance": feature_importance,
        "feature_cols": feature_cols,
        "categorical_cols": categorical_cols,
    }
```

#### 7.1.3 Inference and alerting

```python
def predict_delay_risk(
    model_artifacts: dict,
    shipment_features: pd.DataFrame,
    alert_threshold: float = 0.60,
) -> pd.DataFrame:
    """
    Run inference on new shipments and flag high-risk deliveries.
    Returns DataFrame with delay_probability and risk_tier columns.
    """
    encoder = model_artifacts["encoder"]
    model = model_artifacts["model"]
    cat_cols = model_artifacts["categorical_cols"]
    feature_cols = model_artifacts["feature_cols"]

    df = shipment_features.copy()
    df[cat_cols] = encoder.transform(df[cat_cols])

    delay_proba = model.predict_proba(df[feature_cols])[:, 1]
    df["delay_probability"] = delay_proba
    df["risk_tier"] = pd.cut(
        delay_proba,
        bins=[0, 0.30, 0.60, 1.0],
        labels=["LOW", "MEDIUM", "HIGH"],
    )
    df["alert"] = delay_proba >= alert_threshold
    return df[["shipment_id", "delay_probability", "risk_tier", "alert"]]
```

### 7.2 NLP for Customs Document Classification (HS Code Suggestion)

#### 7.2.1 Model architecture

Use a fine-tuned DistilBERT model (66 million parameters, 40 percent faster than BERT-base)
for multi-class classification of HS codes at 4-digit heading level (~1,200 classes).

```
Input: Invoice line description (free text, up to 128 tokens)
       + optional: commodity description, unit of measure, country of origin
Architecture: DistilBERT-base-uncased -> [CLS] pooler -> Dropout(0.3) -> Linear(768, 1200)
Output: Softmax probabilities over HS 4-digit headings
Confidence threshold: >= 0.80 auto-classify; < 0.80 route to customs broker
```

#### 7.2.2 Training pipeline

```python
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from datasets import Dataset
import torch
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

def train_hs_classifier(
    descriptions: list[str],
    hs_heading_labels: list[int],  # integer class indices (0 to num_classes-1)
    num_classes: int,
    output_dir: str = "./models/hs_classifier",
    num_epochs: int = 5,
    batch_size: int = 32,
) -> dict:
    """
    Fine-tune DistilBERT for HS 4-digit heading classification.
    Training data: minimum 10,000 labelled invoice descriptions recommended.
    GPU required for training (CPU inference is feasible for batch <100).
    """
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    def tokenize(batch):
        return tokenizer(batch["text"], padding="max_length",
                         truncation=True, max_length=128)

    dataset = Dataset.from_dict({"text": descriptions, "label": hs_heading_labels})
    dataset = dataset.map(tokenize, batched=True)
    split = dataset.train_test_split(test_size=0.15, seed=42)

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=num_classes
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=1)
        return {
            "accuracy": accuracy_score(labels, preds),
            "f1_macro": f1_score(labels, preds, average="macro"),
        }

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        evaluation_strategy="epoch",
        save_strategy="best",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        warmup_steps=200,
        weight_decay=0.01,
        logging_dir=f"{output_dir}/logs",
        fp16=torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=split["train"],
        eval_dataset=split["test"],
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    return {
        "model_dir": output_dir,
        "eval_results": trainer.evaluate(),
    }
```

#### 7.2.3 Inference with confidence routing

```python
def classify_hs_code(
    description: str,
    model_dir: str,
    hs_heading_index: dict,  # {class_index: hs_4digit_code}
    confidence_threshold: float = 0.80,
) -> dict:
    """
    Classify invoice description into HS 4-digit heading.
    Descriptions below confidence threshold are flagged for manual review.
    """
    from transformers import pipeline

    classifier = pipeline(
        "text-classification",
        model=model_dir,
        return_all_scores=False,
        top_k=3,
    )
    results = classifier(description)[0]
    top = max(results, key=lambda x: x["score"])
    class_idx = int(top["label"].replace("LABEL_", ""))
    hs_heading = hs_heading_index.get(class_idx, "UNKNOWN")

    return {
        "description": description,
        "predicted_hs_heading": hs_heading,
        "confidence": round(top["score"], 4),
        "auto_classify": top["score"] >= confidence_threshold,
        "route_to_broker": top["score"] < confidence_threshold,
        "top_3": [
            {"hs_heading": hs_heading_index.get(int(r["label"].replace("LABEL_","")), "?"),
             "confidence": round(r["score"], 4)}
            for r in sorted(results, key=lambda x: x["score"], reverse=True)[:3]
        ],
    }
```

### 7.3 Satellite/GPS ETA Prediction

#### 7.3.1 Data sources

| Source | Data | Update Frequency |
|---|---|---|
| AIS (MarineTraffic / exactEarth) | Vessel position, speed, heading | Every 2–5 minutes |
| Sentinel-2 (ESA Copernicus) | Port satellite imagery for congestion | Daily (cloud permitting) |
| Port Community Systems | Gate-in/gate-out, berth availability | Real-time |
| Weather APIs (ECMWF / NOAA) | Wind, swell, visibility | 6-hourly forecast |
| project44 / FourKites | Road GPS telematics | Every 30 seconds |

#### 7.3.2 ETA prediction model

```python
import torch
import torch.nn as nn
import numpy as np

class VesselETALSTM(nn.Module):
    """
    LSTM model for ocean vessel ETA prediction.
    Input: sequence of AIS position + weather + port congestion observations.
    Output: predicted hours to destination port.

    Architecture:
        Input (seq_len, batch, features=16) -> LSTM(hidden=128, layers=2)
        -> Dropout(0.2) -> Linear(128, 64) -> ReLU -> Linear(64, 1)
    """

    def __init__(self, input_size: int = 16, hidden_size: int = 128,
                 num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True,
        )
        self.head = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, features)
        lstm_out, _ = self.lstm(x)
        last_step = lstm_out[:, -1, :]  # use final time step
        return self.head(last_step).squeeze(-1)


def build_ais_feature_sequence(
    ais_observations: list[dict],
    port_congestion_index: float,
    weather_forecast: list[dict],
    sequence_length: int = 24,  # last 24 hours of observations
) -> np.ndarray:
    """
    Build feature matrix from AIS + contextual data for LSTM input.
    Returns array of shape (sequence_length, 16).

    Features per time step:
      0: latitude (normalised)
      1: longitude (normalised)
      2: speed_over_ground_knots
      3: course_over_ground_deg (sin)
      4: course_over_ground_deg (cos)
      5: distance_to_destination_nm
      6: time_elapsed_hours
      7: origin_port_congestion_index
      8: destination_port_congestion_index
      9: wind_speed_knots
      10: significant_wave_height_m
      11: visibility_km
      12: hour_of_day (sin)
      13: hour_of_day (cos)
      14: day_of_week (sin)
      15: day_of_week (cos)
    """
    obs = ais_observations[-sequence_length:]
    features = np.zeros((sequence_length, 16), dtype=np.float32)

    for i, obs_row in enumerate(obs):
        h = obs_row.get("hour_of_day", 12)
        d = obs_row.get("day_of_week", 0)
        cog = obs_row.get("course_over_ground_deg", 0)
        features[i] = [
            obs_row.get("latitude", 0) / 90.0,
            obs_row.get("longitude", 0) / 180.0,
            obs_row.get("sog_knots", 0) / 25.0,
            np.sin(np.radians(cog)),
            np.cos(np.radians(cog)),
            obs_row.get("distance_to_dest_nm", 0) / 10000.0,
            obs_row.get("time_elapsed_hours", 0) / 720.0,
            port_congestion_index / 100.0,
            obs_row.get("dest_congestion", 50) / 100.0,
            obs_row.get("wind_knots", 0) / 60.0,
            obs_row.get("wave_height_m", 0) / 10.0,
            obs_row.get("visibility_km", 10) / 50.0,
            np.sin(2 * np.pi * h / 24),
            np.cos(2 * np.pi * h / 24),
            np.sin(2 * np.pi * d / 7),
            np.cos(2 * np.pi * d / 7),
        ]
    return features
```

### 7.4 GNN for Logistics Network Optimisation

#### 7.4.1 Problem formulation

The logistics network is modelled as a directed graph G = (V, E) where:
- V = nodes (suppliers, DCs, ports, customer locations)
- E = edges (transport lanes with cost, capacity, lead time attributes)
- Node features: throughput capacity, operating cost, location coordinates
- Edge features: freight cost per unit, transit time, reliability score

The GNN learns optimal DC location selection and flow allocation by minimising
total network cost subject to service level constraints.

#### 7.4.2 GNN architecture with torch-geometric

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GATConv, global_mean_pool
from torch_geometric.data import Data, DataLoader

class LogisticsNetworkGNN(nn.Module):
    """
    Graph Neural Network for logistics network optimisation.
    Uses Graph Attention Network (GAT) layers to learn node embeddings
    that capture network topology and flow patterns.

    Node features (7):
      [throughput_capacity_norm, operating_cost_norm, lat_norm, lon_norm,
       is_dc, is_supplier, is_customer]

    Edge features (4):
      [freight_cost_norm, transit_time_norm, reliability_score, lane_volume_norm]

    Output: per-node score (higher = better DC location candidate)
    """

    def __init__(
        self,
        node_features: int = 7,
        edge_features: int = 4,
        hidden_dim: int = 64,
        num_heads: int = 4,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.gat1 = GATConv(node_features, hidden_dim, heads=num_heads,
                            dropout=dropout, edge_dim=edge_features)
        self.gat2 = GATConv(hidden_dim * num_heads, hidden_dim, heads=1,
                            dropout=dropout, edge_dim=edge_features)
        self.node_scorer = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )
        self.flow_predictor = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, data: Data):
        x, edge_index, edge_attr = data.x, data.edge_index, data.edge_attr

        # GAT layer 1
        x = F.elu(self.gat1(x, edge_index, edge_attr))
        x = F.dropout(x, p=0.3, training=self.training)

        # GAT layer 2
        x = F.elu(self.gat2(x, edge_index, edge_attr))

        # Node-level DC location score
        node_scores = self.node_scorer(x).squeeze(-1)

        # Edge-level flow allocation
        src_emb = x[edge_index[0]]
        dst_emb = x[edge_index[1]]
        edge_emb = torch.cat([src_emb, dst_emb], dim=-1)
        flow_allocation = self.flow_predictor(edge_emb).squeeze(-1)

        return node_scores, flow_allocation


def build_network_graph(
    nodes: list[dict],
    edges: list[dict],
) -> Data:
    """
    Convert logistics network to PyG Data object.

    nodes: list of dicts with keys:
        id, throughput_capacity, operating_cost_cents, latitude, longitude,
        is_dc, is_supplier, is_customer
    edges: list of dicts with keys:
        source_id, target_id, freight_cost_cents, transit_days, reliability_score,
        annual_volume_units
    """
    node_id_map = {n["id"]: i for i, n in enumerate(nodes)}

    # Normalise node features
    cap_max = max(n["throughput_capacity"] for n in nodes) or 1
    cost_max = max(n["operating_cost_cents"] for n in nodes) or 1
    x = torch.tensor([
        [
            n["throughput_capacity"] / cap_max,
            n["operating_cost_cents"] / cost_max,
            (n["latitude"] + 90) / 180,
            (n["longitude"] + 180) / 360,
            float(n["is_dc"]),
            float(n["is_supplier"]),
            float(n["is_customer"]),
        ]
        for n in nodes
    ], dtype=torch.float)

    edge_index = torch.tensor(
        [[node_id_map[e["source_id"]], node_id_map[e["target_id"]]] for e in edges],
        dtype=torch.long,
    ).t().contiguous()

    freq_max = max(e.get("annual_volume_units", 1) for e in edges) or 1
    cost_e_max = max(e.get("freight_cost_cents", 1) for e in edges) or 1
    edge_attr = torch.tensor([
        [
            e.get("freight_cost_cents", 0) / cost_e_max,
            e.get("transit_days", 0) / 30.0,
            e.get("reliability_score", 0.95),
            e.get("annual_volume_units", 0) / freq_max,
        ]
        for e in edges
    ], dtype=torch.float)

    return Data(x=x, edge_index=edge_index, edge_attr=edge_attr)
```

---

## 8. Phase 5: Integration & Automation

**Duration**: Weeks 28–40
**Owner**: IT Integration team + Logistics Operations

### 8.1 TMS integrations

#### SAP Transportation Management (SAP TM)

Integrate via SAP TM Web Services (SOAP/REST). Key integration points:
- Freight Order creation from confirmed POs (RFC_FO_CREATE)
- Carrier tendering (electronic spot and contract)
- Freight settlement (invoice matching, GR/IR clearing)
- Shipment tracking status push to SAP EWM

```typescript
// SAP TM adapter — create freight order from PO
async function createSAPFreightOrder(
  poId: string,
  carrierId: string,
  laneMaster: LaneMaster,
  authToken: string,
): Promise<{ freightOrderId: string; status: string }> {
  const payload = {
    PurchaseOrderID: poId,
    CarrierID: carrierId,
    TransportMode: laneMaster.primaryMode,
    RequestedDeliveryDate: laneMaster.lastUpdated, // replace with actual RDD
    Incoterms: laneMaster.incoterms2020,
  };
  const response = await fetchWithRetry(
    `${SAP_TM_BASE_URL}/api/v1/freight-orders`,
    { method: 'POST', headers: { Authorization: `Bearer ${authToken}`,
        'Content-Type': 'application/json' },
      body: JSON.stringify(payload) },
    { maxRetries: 3, backoffMs: 1000 },
  );
  return response.json();
}
```

#### Oracle Transportation Management (Oracle TMS / GTM)

Integrate via Oracle Integration Cloud (OIC) or direct REST API:
- Shipment order creation from ERP sales orders
- Global Trade Management: denied party screening, export licence check
- Rate engine API: real-time carrier rate comparison

#### project44 Movement API

```typescript
// project44 shipment tracking webhook handler
async function handleProject44TrackingEvent(
  event: Project44TrackingEvent,
  eventStore: EventStore,
): Promise<void> {
  const domainEvent: ShipmentTrackingUpdated = {
    eventId: generateUUID(),
    eventType: 'SHIPMENT_TRACKING_UPDATED',
    shipmentId: event.trackingNumber,
    source: 'PROJECT44',
    timestamp: event.eventTimestamp,
    location: {
      locode: event.locationCode,
      latitude: event.latitude,
      longitude: event.longitude,
    },
    statusCode: mapProject44Status(event.statusCode),
    predictedETA: event.predictedArrivalTime,
    etaConfidencePercent: event.confidenceScore,
  };
  await eventStore.append('shipment', event.trackingNumber, domainEvent);
}
```

#### CargoWise One

Integrate via CargoWise eAdaptor (XML-based) for:
- Customs entry creation and amendment
- Freight invoice import and matching
- Document management (B/L, AWB, packing list, COO)

#### Carrier EDI Integration

Standard UN/EDIFACT messages for carrier communication:

| Message | Direction | Purpose |
|---|---|---|
| IFTMBF | Outbound (to carrier) | Firm booking request |
| IFTMBC | Inbound (from carrier) | Booking confirmation |
| IFTSTA | Inbound (from carrier) | Status update / tracking |
| DESADV | Inbound (from supplier) | Despatch advice / ASN |
| IFCSUM | Inbound (from forwarder) | Consolidation summary |
| CUSCAR | Outbound (to customs) | Cargo declaration |

```typescript
// EDI DESADV parser — despatch advice inbound
function parseDESADV(ediMessage: string): DespatchAdvice {
  const segments = parseEDIFACTSegments(ediMessage);
  const bgmSegment = segments.find(s => s.tag === 'BGM');
  const dtmSegments = segments.filter(s => s.tag === 'DTM');
  const linSegments = segments.filter(s => s.tag === 'LIN');

  return {
    documentNumber: bgmSegment?.elements[1],
    despatchDate: parseDTM(dtmSegments.find(s => s.elements[0] === '11')),
    estimatedDeliveryDate: parseDTM(dtmSegments.find(s => s.elements[0] === '17')),
    lines: linSegments.map(parseLINSegment),
  };
}
```

### 8.2 Port Community System integration

Connect to port community systems for pre-arrival processing (WTO TFA Art. 7):
- DAKOSY (Port of Hamburg): CARIX container tracking, Atlas customs
- Portbase (Port of Rotterdam): Port Call Optimisation, EDI container notification
- PortXchange: Port Call Optimisation for berth scheduling and vessel planning

Pre-arrival processing reduces customs dwell time by 60–80 percent for AEO shippers.

### 8.3 Customs broker API integration

Implement standardised broker API adapter with:
- Entry filing (ICS2 EU, ACE US, CHIEF/CDS UK)
- Automated HS code suggestion from ML model (Section 7.2)
- Duty drawback management
- Denied party screening (OFAC, EU consolidated list, UN sanctions)

```typescript
interface CustomsBrokerAdapter {
  fileEntry(entry: CustomsEntry): Promise<{ entryNumber: string; status: string }>;
  getEntryStatus(entryNumber: string): Promise<CustomsEntryStatus>;
  screenDeniedParties(party: DeniedPartyQuery): Promise<DeniedPartyScreeningResult>;
  lookupDutyRate(hsCode: string, originCountry: string): Promise<DutyRateLookup>;
}
```

---

## 9. Phase 6: Continuous Improvement

**Duration**: Ongoing from Week 36
**Owner**: Logistics Centre of Excellence

### 9.1 Weekly cadence

- Automated carrier scorecards distributed every Monday (previous week data)
- Freight invoice exception queue reviewed Tuesday/Thursday
- Delay-risk alert review: daily at 08:00 (ML model inference on active shipments)
- Port congestion index update: every 6 hours from API feeds

### 9.2 Monthly cadence

- Lane optimisation review: compare actual vs VRP-optimised route costs
- Carrier tender trigger: if OTD < 90 percent on a lane for two consecutive months,
  issue RFQ to alternative carriers
- HS code model retraining: monthly refresh with new classification decisions

### 9.3 Quarterly cadence

- Full landed cost model recalibration (duty rates change quarterly for some FTAs)
- GNN network optimisation re-run: annual DC network review triggered if demand
  pattern shifts >15 percent or new sourcing countries onboarded
- CBAM embedded emissions data collection: quarterly supplier survey per
  Implementing Regulation 2023/1773

### 9.4 Model monitoring

Track the following ML model KPIs in production:

| Model | KPI | Alert Threshold |
|---|---|---|
| XGBoost delay prediction | AUC-ROC (weekly validation) | < 0.72 triggers retraining |
| DistilBERT HS classifier | Auto-classify accuracy | < 0.85 triggers retraining |
| LSTM ETA | MAE vs actual ETA (hours) | > 12 hours mean error |
| GNN network opt | Cost vs benchmark | > 5% above VRP baseline |

---

## 10. Technology Stack & Architecture

### 10.1 Core technology decisions

| Layer | Technology | Rationale |
|---|---|---|
| Domain logic | TypeScript | Type-safe aggregates, event sourcing |
| Mathematical models | Python 3.11+ | NumPy, SciPy, OR-Tools |
| ML training | PyTorch 2.x + HuggingFace | DistilBERT, LSTM |
| Graph ML | torch-geometric | GNN for network optimisation |
| Boosting | XGBoost | Delay prediction |
| Route optimisation | Google OR-Tools | CVRPTW solver |
| Graph analysis | NetworkX | Network topology metrics |
| Satellite imagery | rasterio + GeoPandas | Port congestion from Sentinel-2 |
| Event Store | PostgreSQL + custom EventStore.ts | CQRS, audit trail |
| TMS integration | SAP TM REST / Oracle OIC | Enterprise ERP |
| Visibility | project44 + FourKites | Multimodal real-time tracking |
| Freight audit | CargoWise One eAdaptor | Invoice matching |
| EDI | Stedi / SPS Commerce | DESADV, IFTMBC, CUSCAR |

### 10.2 Architecture principles

- All shipment state transitions are event-sourced: no direct DB updates
- Idempotency keys on all carrier API calls — safe to retry on timeout
- Soft-delete only: cancelled shipments retain full audit trail
- Money values: always integer cents, never floating point
- Dates: ISO 8601 UTC throughout; no timezone-naive timestamps
- Secrets: carrier API credentials in environment variables or vault, never in source

### 10.3 Data flow diagram

```
PO Confirmed
    |
    v
Shipment Booking Request
    |-> Carrier EDI (IFTMBF)
    |-> SAP TM Freight Order
    v
Booking Confirmed (IFTMBC)
    |
    v
ASN Received (DESADV)
    |
    v
In-Transit Tracking
    |-> project44 / FourKites webhook
    |-> AIS vessel positions
    |-> LSTM ETA prediction (6-hourly)
    |-> XGBoost delay risk (daily)
    v
Port of Discharge
    |-> Port Community System (DAKOSY / Portbase)
    |-> Customs entry filing (CargoWise / broker API)
    |-> HS code ML classification
    |-> Duty calculation (Section 6.8)
    v
Customs Released
    |
    v
Last Mile Delivery
    |-> VRP route optimisation (OR-Tools)
    v
Delivered — POD received
    |-> Carrier scorecard update
    |-> Freight invoice matching
    |-> CBAM carbon cost posting
```

---

## 11. Change Management & Training

### 11.1 Stakeholder map

| Stakeholder | Impact | Engagement | Key Concern |
|---|---|---|---|
| Logistics Manager | High | Co-owner | Carrier relationships, visibility |
| Customs Compliance | High | Co-owner | HS code accuracy, CBAM |
| Procurement | High | Consulted | Incoterms on POs, landed cost |
| Finance | Medium | Informed | Freight cost allocation, CBAM accruals |
| IT Integration | High | Co-owner | TMS connectivity, EDI |
| Customs Brokers | Medium | Managed | ML model replacing manual classification |
| Carriers | Low | Informed | EDI mandate, scorecard sharing |

### 11.2 Training programme

| Role | Training Module | Duration | Delivery |
|---|---|---|---|
| Logistics coordinators | Incoterms 2020 fundamentals | 4 hours | Instructor-led |
| Logistics coordinators | TMS navigation & shipment lifecycle | 8 hours | Instructor-led |
| Customs team | HS classification process + ML tool | 6 hours | Instructor-led |
| Customs team | CBAM reporting requirements | 4 hours | E-learning |
| Logistics analysts | Carrier scorecard interpretation | 3 hours | E-learning |
| Data science team | ML model monitoring & retraining | 8 hours | Workshop |
| Finance | CBAM accrual accounting | 2 hours | E-learning |

### 11.3 Benefits realisation

Assign a benefits owner for each value lever identified in Section 1.
Review actuals vs target quarterly. Escalate to Supply Chain Director if any lever
is tracking below 50 percent of target by month 12.

---

## 12. Implementation KPIs

Track the following KPIs from go-live. Report monthly to Supply Chain Director.

### 12.1 Operational KPIs

| KPI | Baseline | 6-Month Target | 12-Month Target | World-Class |
|---|---|---|---|---|
| Carrier OTD (%) | Measure in Phase 0 | + 5 pp | + 10 pp | >= 95% |
| OTIF (%) | Measure in Phase 0 | + 4 pp | + 8 pp | >= 92% |
| Freight cost per kg-km (index) | 100 | 95 | 88 | 70 |
| Customs dwell time (days) | Measure | -1 day | -2 days | <= 1 day AEO |
| Demurrage & detention (USD/shipment) | Measure | -20% | -45% | < USD 150 |
| HS mis-classification rate (%) | Measure | -30% | -60% | < 0.5% |
| Shipment visibility coverage (%) | Measure | 80% | 100% | 100% |
| CBAM reporting completeness (%) | 0% | 100% from 2026 | 100% | 100% |

### 12.2 ML model KPIs

| Model | Metric | Go-Live Target | Steady-State Target |
|---|---|---|---|
| XGBoost delay | AUC-ROC | >= 0.75 | >= 0.82 |
| DistilBERT HS | Auto-classify accuracy | >= 0.78 | >= 0.88 |
| LSTM ETA | MAE (hours) | <= 18 | <= 10 |
| GNN network | Cost reduction vs baseline | >= 3% | >= 8% |

### 12.3 Integration KPIs

| Integration | KPI | Target |
|---|---|---|
| project44 / FourKites | Shipments with real-time tracking | 100% |
| Carrier EDI | Bookings via EDI vs manual | >= 80% |
| Freight invoice auto-match | Rate | >= 90% |
| Customs HS auto-classify | Rate (>= 0.80 confidence) | >= 80% of SKUs |

---

## 13. Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Carrier EDI adoption resistance | High | Medium | Mandate EDI in carrier contracts; provide Stedi portal as fallback |
| HS code ML model accuracy below threshold | Medium | High | Maintain customs broker SLA for manual classification; track miss rate weekly |
| AIS data gaps for inland/road | High | Medium | Supplement with FourKites road GPS; accept lower confidence on road legs |
| CBAM regulation uncertainty | Low | High | Monitor European Commission guidance; build flexible emission factor table |
| SAP TM integration delay | Medium | High | Phase integration: manual workaround for first 3 months; prioritise EDI |
| Data quality — historical shipment records | High | High | Data cleansing sprint in Phase 0; accept partial ML training on clean subset |
| Customs seizure UFLPA | Low | Critical | Mandatory UFLPA screening at supplier onboarding; DDP prohibited for XUAR suppliers |
| Ocean congestion spike (peak season) | Medium | Medium | LSTM model monitors congestion index; pre-book capacity 8 weeks ahead in Q3 |
| CBAM allowance price spike | Low | Medium | Budget contingency 20% above baseline ETS price; hedge via financial instruments |
| Carrier rate card expiry mid-implementation | High | Low | Automate rate card refresh; monitor contract renewal dates in carrier master |

---

## 14. Timeline Summary

| Phase | Weeks | Key Deliverables | Owner |
|---|---|---|---|
| Phase 0: Assessment | 1–4 | Baseline KPIs, data gaps, carrier spend cube | CoE + Consulting |
| Phase 1: Foundation | 5–10 | Carrier master, lane master, HS tariff DB, Incoterms rules | Data Mgmt + IT |
| Phase 2: Standardisation | 11–18 | Shipment lifecycle events, carrier scorecards, invoice audit | Logistics Ops |
| Phase 3: Math Models | 15–24 | Landed cost engine, VRP solver, CBAM calculator, duty engine | Analytics |
| Phase 4: ML/AI | 20–36 | XGBoost delay model, DistilBERT HS classifier, LSTM ETA, GNN | Data Science |
| Phase 5: Integration | 28–40 | SAP TM, project44, FourKites, CargoWise, carrier EDI live | IT Integration |
| Phase 6: CImp | 36+ | Model monitoring, quarterly retraining, carrier tenders | CoE ongoing |

**Go-live (core TMS + visibility)**: Week 28
**Go-live (ML models + full automation)**: Week 40
**Benefits realisation review**: Month 18

---

## 15. References

### Regulatory & Standards

1. International Chamber of Commerce. *Incoterms 2020 Rules*. ICC Publication 723E.
   Paris: ICC, 2019.
2. World Customs Organization. *Harmonised System Nomenclature 2022*.
   Brussels: WCO, 2021.
3. International Air Transport Association. *IATA Cargo Services Conference Resolution 123:
   Volumetric Weight*. Montreal: IATA, 2023.
4. International Maritime Organization. *Fourth IMO GHG Study 2020*. MEPC.323(74).
   London: IMO, 2020.
5. European Parliament. *Regulation (EU) 2023/956 — Carbon Border Adjustment Mechanism*.
   Official Journal of the European Union, May 2023.
6. European Commission. *Implementing Regulation (EU) 2023/1773 — CBAM Reporting*.
   Official Journal of the European Union, September 2023.
7. US Customs and Border Protection. *Uyghur Forced Labor Prevention Act (UFLPA)
   Entity List and Enforcement Guidance*. Washington DC: CBP, 2022.
8. ISO. *ISO 28000:2022 — Security and Resilience — Supply Chain Security Management
   Systems — Requirements*. Geneva: ISO, 2022.
9. WTO. *Agreement on Trade Facilitation (TFA), Article 7 — Pre-Arrival Processing*.
   Geneva: WTO, 2014.

### Textbooks & Academic

10. Chopra, S. & Meindl, P. *Supply Chain Management: Strategy, Planning, and Operation*,
    6th ed. Hoboken NJ: Pearson, 2016. Chapters 13–15 (Transportation).
11. Ballou, R.H. *Business Logistics/Supply Chain Management*, 5th ed.
    Hoboken NJ: Pearson, 2004.
12. Christopher, M. *Logistics and Supply Chain Management*, 6th ed.
    Harlow: Pearson FT Publishing, 2022.
13. Toth, P. & Vigo, D. *Vehicle Routing: Problems, Methods, and Applications*, 2nd ed.
    Philadelphia: SIAM MOS-SIAM Series on Optimization, 2014.
14. Vaswani, A. et al. "Attention Is All You Need." *NeurIPS 2017*. arXiv:1706.03762.
15. Chen, T. & Guestrin, C. "XGBoost: A Scalable Tree Boosting System."
    *KDD 2016*. arXiv:1603.02754.
16. Scarselli, F. et al. "The Graph Neural Network Model."
    *IEEE Transactions on Neural Networks*, 20(1), 61–80, 2009.

### Industry Reports & Frameworks

17. Gartner. *Magic Quadrant for Transportation Management Systems* (TMS). 2025.
18. McKinsey Global Institute. *Delivering on the Promise of Supply Chain
    Technology*. McKinsey & Company, February 2024.
19. ASCM. *SCOR Digital Standard — Deliver Process Reference*. Chicago: ASCM, 2019.
20. Smart Freight Centre. *GLEC Framework for Logistics Emissions Accounting*, v3.0.
    Amsterdam: SFC, 2023.
21. Google. *OR-Tools Vehicle Routing Problem Documentation*.
    developers.google.com/optimization/routing, 2024.
22. Hugging Face. *DistilBERT: a distilled version of BERT*. arXiv:1910.01108. 2019.
23. APICS. *APICS Dictionary*, 16th ed. Chicago: ASCM, 2024.
24. ICC. *ICC Guide to Incoterms 2020*. ICC Publication 785E. Paris: ICC, 2019.
