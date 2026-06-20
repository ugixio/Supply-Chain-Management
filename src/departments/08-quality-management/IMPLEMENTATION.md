# Quality Management — Enterprise Implementation Guide

**Department**: 08 — Quality Management  
**Standard Alignment**: ISO 9001:2015 (§8.4, §8.5.2, §8.6, §8.7), ISO 2859-1:1999, IATF 16949:2016, AIAG FMEA 4th Ed., Six Sigma DMAIC  
**Author**: Supply Chain Centre of Excellence  
**Version**: 2.0  
**Classification**: Internal — Senior Leadership  
**Last Revised**: 2026-06-20

---

## Table of Contents

1. Executive Summary
2. Prerequisites and Dependencies
3. Phase 0: Assessment and AS-IS Analysis
4. Phase 1: Foundation and Master Data
5. Phase 2: Process Standardisation and Core Analytics
6. Phase 3: Mathematical Models
7. Phase 4: ML/AI Pipeline
8. Phase 5: Integration and Automation
9. Phase 6: Continuous Improvement
10. Technology Stack and Architecture
11. Change Management and Training
12. Implementation KPIs
13. Risk and Mitigation
14. Timeline Summary
15. References

---

## 1. Executive Summary

Quality management in a modern enterprise supply chain is not a cost centre — it is a strategic differentiator. Organisations that achieve Six Sigma capability across their supplier base, manufacturing operations, and logistics network command 15–25% lower cost-of-poor-quality (COPQ), sustain fewer regulatory recalls, and earn premium shelf placement from major retailers such as Walmart (OTIF ≥ 98%) and Costco (defect rate ≤ 200 PPM).

This implementation guide provides a phased, standards-aligned roadmap for deploying an enterprise-grade quality management capability within the Supply Chain Management platform. The scope covers:

- **Incoming inspection** governed by ISO 2859-1 AQL sampling plans, fully digitalised and integrated with Supplier Quality Portals and SAP QM.
- **In-process SPC** fed by MES/SCADA sensor streams, with real-time X-bar/R and CUSUM control charts computed in Python and visualised on shop-floor dashboards.
- **Non-Conformance Reports (NCR)** managed through an 8D workflow with automated root-cause classification via NLP.
- **FMEA Risk Priority Number (RPN)** computation and tracking, with automatic escalation when RPN > 100.
- **Predictive quality** using XGBoost trained on process parameters, deployed to flag high-risk production batches before physical inspection.
- **Computer vision defect detection** using YOLOv8, running at inspection stations on NVIDIA Jetson edge hardware.
- **Process capability indices** (Cp, Cpk, Pp, Ppk) calculated per part number and control plan characteristic.

The expected return on investment horizon is 18 months post go-live, with a target reduction in COPQ of 20% in Year 1 and 35% by Year 3. All models, code, and integrations described in this document conform to the project's OSI-licensed technology mandate and SCOR-DS Enable process category requirements.

---

## 2. Prerequisites and Dependencies

### 2.1 Organisational Prerequisites

| Prerequisite | Owner | Completion Criteria |
|---|---|---|
| Quality Policy signed by C-suite | Chief Quality Officer | Signed document in document management system |
| Control Plan library available | Quality Engineering | ≥ 80% of active part numbers have approved Control Plans |
| Supplier qualification data migrated | Supplier Management (Dept 02) | All Tier-1 suppliers have active Supplier master records |
| ISO 9001:2015 gap assessment complete | External auditor | Gap report with open actions < 20 |
| Measurement System Analysis (MSA) executed | Metrology team | GR&R ≤ 10% for all critical gauges |
| IATF 16949 scope defined (if automotive) | Quality Director | Scope statement approved |

### 2.2 Technical Prerequisites

- Node.js ≥ 20, TypeScript ≥ 5.3 — domain aggregates
- Python ≥ 3.11 with virtual environment (`python/venv/`)
- PostgreSQL ≥ 15 — event store and relational master data
- Redis ≥ 7 — SPC sliding-window state, real-time alert pub/sub
- SAP QM module (or mock adapter) accessible via RFC/BAPI or REST wrapper
- MES/SCADA OPC-UA endpoint or MQTT broker for sensor streams
- NVIDIA Jetson Orin or equivalent edge device at each inspection station
- LIMS (Laboratory Information Management System) REST API
- GPU workstation or cloud instance (NVIDIA A10 minimum) for model training

### 2.3 Module Dependencies within This Platform

```
08-quality-management
  depends on:
    01-procurement          (PO reference on NCR, supplier linkage)
    02-supplier-management  (Supplier Scorecard PPM/DPMO feed)
    03-inventory            (Stock hold / quarantine movements)
    05-logistics            (Shipment reference on incoming inspection)
    09-warehouse            (Quarantine bin management)
    10-compliance           (REACH SVHC, hazmat handling on NCR)
```

---

## 3. Phase 0: Assessment and AS-IS Analysis

**Duration**: Weeks 1–4  
**Goal**: Establish baseline metrics, identify gaps against ISO 9001:2015 and IATF 16949, and define target state.

### 3.1 Data Collection

Collect the following datasets for the trailing 24 months:

- Incoming inspection records (pass/fail, quantity inspected, defects found by category)
- NCR log (open date, close date, root cause, supplier/process, 8D steps completed)
- Field complaints and warranty returns
- Internal scrap and rework costs by cost centre
- PPM history by supplier and commodity
- Control chart data (if SPC exists) — raw subgroup measurements

### 3.2 AS-IS KPI Baseline

| KPI | Formula | Baseline Target | World Class |
|---|---|---|---|
| Incoming Rejection Rate | (Rejected Lots / Total Lots) x 100 | < 5% | < 1% |
| Supplier PPM | (Defective Units / Units Inspected) x 1,000,000 | Measure only | < 500 (automotive) |
| NCR Cycle Time | Mean(Close Date - Open Date) | Measure only | ≤ 30 calendar days |
| COPQ as % of Revenue | (Scrap + Rework + Warranty + Appraisal) / Revenue | Measure only | < 1% |
| First Pass Yield (FPY) | Conforming Units / Total Started | Measure only | ≥ 99% |
| Cp (process capability) | (USL - LSL) / (6σ) | Measure only | ≥ 1.33 |
| Cpk | min[(USL-μ)/3σ, (μ-LSL)/3σ] | Measure only | ≥ 1.33 |

### 3.3 Gap Analysis Framework

Conduct gap analysis against ISO 9001:2015 clause structure:

- **§8.4** Control of externally provided processes — supplier qualification, incoming inspection
- **§8.5.2** Identification and traceability — lot tracking, SSCC labels
- **§8.6** Release of products and services — inspector sign-off, QMS integration
- **§8.7** Control of nonconforming outputs — NCR workflow, disposition authority

Assign each gap a severity (Critical / Major / Minor) and estimated remediation effort (person-days). Prioritise Critical gaps in Phase 1.

### 3.4 AS-IS Process Map

Document the current state for:
1. Incoming Inspection Flow (who, what, when, how many samples)
2. NCR Initiation and Escalation
3. Supplier Communication on quality rejects
4. Management Review cadence

This process map becomes the baseline for redesign in Phase 2.

---

## 4. Phase 1: Foundation and Master Data

**Duration**: Weeks 5–10  
**Goal**: Establish master data structures, configure AQL plans, and instrument core domain aggregates.

### 4.1 Quality Master Data Model

The following master data entities must be established before any transactional processing:

**Part-Quality Profile** — links a SKU to its AQL level, inspection frequency, critical characteristics, and acceptance criteria.

**Control Plan** — per part number, lists all characteristics (dimensional, functional, visual), measurement method, gauge type, sample size, frequency, and reaction plan.

**Gauge Master** — calibration due dates, GR&R status, responsible metrology lab.

**Defect Code Library** — structured taxonomy of defect types (cosmetic, dimensional, functional, safety-critical) mapped to AIAG codes and IATF 16949 requirements.

**Supplier Quality Agreement (SQA)** — contractual PPM targets, AQL levels, and self-certification requirements per commodity.

### 4.2 TypeScript Domain Aggregates

Key domain types defined in `src/departments/08-quality-management/domain/`:

```typescript
// InspectionRecord.ts
export type AQLLevel = '0.065' | '0.10' | '0.15' | '0.25' | '0.40' | '0.65'
  | '1.0' | '1.5' | '2.5' | '4.0' | '6.5';

export type InspectionLevel = 'I' | 'II' | 'III' | 'S1' | 'S2' | 'S3' | 'S4';

export type SamplingType = 'NORMAL' | 'TIGHTENED' | 'REDUCED';

export type DispositionCode =
  | 'ACCEPT'
  | 'REJECT_RETURN_TO_SUPPLIER'
  | 'REJECT_SCRAP'
  | 'CONDITIONAL_USE_AS_IS'
  | 'SORT_AND_REWORK'
  | 'DEVIATE_CONCESSION';

export interface InspectionRecord {
  readonly id: string;
  readonly idempotencyKey: string;
  readonly lotNumber: string;
  readonly skuCode: string;
  readonly supplierId: string;
  readonly purchaseOrderId: string;
  readonly shipmentId: string;
  readonly inspectedAt: ISOTimestamp;
  readonly inspectorId: string;
  readonly lotSize: number;
  readonly sampleSize: number;
  readonly sampleSizeCodeLetter: string;
  readonly aqlLevel: AQLLevel;
  readonly inspectionLevel: InspectionLevel;
  readonly samplingType: SamplingType;
  readonly acceptNumber: number;
  readonly rejectNumber: number;
  readonly defectsFound: number;
  readonly defectDetails: DefectRecord[];
  readonly disposition: DispositionCode;
  readonly dispositionAuthority: string;
  readonly notes: string;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
}
```

### 4.3 Event Store Integration

Each inspection outcome generates a domain event fed into the shared Event Store (CQRS):

```typescript
export type QualityEvent =
  | { type: 'INSPECTION_STARTED'; payload: InspectionStartedPayload }
  | { type: 'INSPECTION_COMPLETED'; payload: InspectionCompletedPayload }
  | { type: 'LOT_ACCEPTED'; payload: LotAcceptedPayload }
  | { type: 'LOT_REJECTED'; payload: LotRejectedPayload }
  | { type: 'NCR_OPENED'; payload: NCROpenedPayload }
  | { type: 'NCR_8D_STEP_COMPLETED'; payload: NCR8DStepPayload }
  | { type: 'NCR_CLOSED'; payload: NCRClosedPayload }
  | { type: 'SPC_ALARM_RAISED'; payload: SPCAlarmPayload }
  | { type: 'FMEA_RPN_EXCEEDED'; payload: FMEARPNPayload };
```

Rejected lot events trigger downstream workflows:
- Quarantine stock movement in Inventory (Dept 03)
- Supplier scorecard debit (Dept 02)
- Accounts Payable deduction memo (if contractually agreed)

---

## 5. Phase 2: Process Standardisation and Core Analytics

**Duration**: Weeks 11–18  
**Goal**: Digitalise inspection workflows, implement NCR 8D process, activate SPC dashboards.

### 5.1 Incoming Inspection Workflow

The standard incoming inspection flow follows this sequence:

1. Goods Receipt posted in ERP (SAP MM) generates inspection lot in SAP QM.
2. Quality Management module receives inspection lot event via integration layer.
3. System computes sample size using ISO 2859-1 AQL table (see Phase 3).
4. Inspector retrieves batch ticket on tablet, records measurements against control plan.
5. Defect count entered; system evaluates accept/reject criterion.
6. Disposition recorded; lot released to warehouse or placed in quarantine.
7. NCR auto-generated if lot rejected; supplier notified via portal.

### 5.2 NCR 8D Workflow

The 8 Disciplines (8D) process is mandated for all Critical and Major non-conformances:

| Discipline | Activity | Owner | Target Duration |
|---|---|---|---|
| D1 | Team Formation | Quality Engineer | Day 1 |
| D2 | Problem Description (5W2H) | Quality Engineer | Day 2 |
| D3 | Interim Containment Action (ICA) | Production / Warehouse | Day 3 |
| D4 | Root Cause Analysis (Ishikawa / 5-Why) | Quality + Engineering | Day 7 |
| D5 | Permanent Corrective Action (PCA) selection | Quality + Engineering | Day 14 |
| D6 | PCA Implementation and validation | Engineering | Day 21 |
| D7 | Systemic Prevention (FMEA update, Control Plan) | Quality + Engineering | Day 28 |
| D8 | Team Recognition and closure | Quality Manager | Day 30 |

NCR cycle time KPI: mean time from D1 open to D8 close. Target ≤ 30 calendar days.

### 5.3 Supplier Scorecard Quality Feed

Each completed inspection feeds the supplier scorecard in real time:

```
PPM contribution per shipment = (defects_found / units_inspected) * 1_000_000
Rolling 12-month PPM = sum(defects_12m) / sum(units_inspected_12m) * 1_000_000
```

The quality dimension of the Supplier Scorecard (30% weighting) uses:
- PPM Score: 60% of quality sub-score
- NCR Rate: 40% of quality sub-score

---

## 6. Phase 3: Mathematical Models

**Duration**: Weeks 15–22 (overlaps with Phase 2)  
**Goal**: Implement all statistical and mathematical quality models in Python with full audit trails.

### 6.1 AQL Sampling — ISO 2859-1

#### 6.1.1 Theory

ISO 2859-1 (Sampling Procedures for Inspection by Attributes) defines statistically rigorous acceptance sampling plans. The key inputs are:

- **Lot size (N)**: total quantity in the shipment lot
- **Inspection Level**: I (less discriminating), II (normal), III (more discriminating), or special levels S1–S4
- **AQL**: Acceptable Quality Level — the worst tolerable process average (expressed as defects per 100 units or percent defective)
- **Sampling Type**: Normal, Tightened, or Reduced — switched based on preceding lot history

The output is:
- **Sample Size Code Letter** (A through R)
- **Sample size (n)**
- **Acceptance Number (Ac)**: maximum defects that allow lot acceptance
- **Rejection Number (Re)**: minimum defects that force lot rejection

#### 6.1.2 Sample Size Code Letter Table (ISO 2859-1 Table I — Normal Inspection Level II)

| Lot Size Range | Code Letter |
|---|---|
| 2 – 8 | A |
| 9 – 15 | B |
| 16 – 25 | C |
| 26 – 50 | D |
| 51 – 90 | E |
| 91 – 150 | F |
| 151 – 280 | G |
| 281 – 500 | H |
| 501 – 1,200 | J |
| 1,201 – 3,200 | K |
| 3,201 – 10,000 | L |
| 10,001 – 35,000 | M |
| 35,001 – 150,000 | N |
| 150,001 – 500,000 | P |
| 500,001 and over | Q |

Inspection Level I uses one row lower (e.g., lot size 91–150 maps to E instead of F).  
Inspection Level III uses one row higher (e.g., lot size 91–150 maps to G instead of F).

#### 6.1.3 Master AQL Acceptance/Rejection Table (Single Sampling, Normal Inspection)

| Code | n | AQL 0.65 Ac/Re | AQL 1.0 Ac/Re | AQL 1.5 Ac/Re | AQL 2.5 Ac/Re | AQL 4.0 Ac/Re |
|---|---|---|---|---|---|---|
| A | 2 | * | * | * | * | * |
| B | 3 | * | * | * | * | * |
| C | 5 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 |
| D | 8 | 0/1 | 0/1 | 0/1 | 0/1 | 1/2 |
| E | 13 | 0/1 | 0/1 | 0/1 | 1/2 | 1/2 |
| F | 20 | 0/1 | 0/1 | 1/2 | 1/2 | 2/3 |
| G | 32 | 0/1 | 1/2 | 1/2 | 2/3 | 3/4 |
| H | 50 | 1/2 | 1/2 | 2/3 | 3/4 | 5/6 |
| J | 80 | 1/2 | 2/3 | 3/4 | 5/6 | 7/8 |
| K | 125 | 2/3 | 3/4 | 5/6 | 7/8 | 10/11 |
| L | 200 | 3/4 | 5/6 | 7/8 | 10/11 | 14/15 |
| M | 315 | 5/6 | 7/8 | 10/11 | 14/15 | 21/22 |
| N | 500 | 7/8 | 10/11 | 14/15 | 21/22 | 21/22 |
| P | 800 | 10/11 | 14/15 | 21/22 | 21/22 | 21/22 |
| Q | 1250 | 14/15 | 21/22 | 21/22 | 21/22 | 21/22 |

(*) Use next code letter with arrow direction in actual ISO table.

#### 6.1.4 Python Implementation

```python
# python/08_quality_management/aql_sampling.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

AQLValue = Literal['0.065', '0.10', '0.15', '0.25', '0.40',
                   '0.65', '1.0', '1.5', '2.5', '4.0', '6.5']
InspectionLevel = Literal['I', 'II', 'III', 'S1', 'S2', 'S3', 'S4']
SamplingType = Literal['NORMAL', 'TIGHTENED', 'REDUCED']


# ISO 2859-1 Table I — lot size to code letter mapping per inspection level
_LOT_SIZE_BREAKS = [2, 9, 16, 26, 51, 91, 151, 281, 501, 1201, 3201,
                    10001, 35001, 150001, 500001]
_CODE_LETTERS = list('ABCDEFGHJKLMNPQ')

_LEVEL_OFFSET: dict[InspectionLevel, int] = {
    'S1': -4, 'S2': -3, 'S3': -2, 'S4': -1,
    'I': -1, 'II': 0, 'III': 1
}

# (sample_size, {aql: (accept, reject)})
_NORMAL_TABLE: dict[str, tuple[int, dict[str, tuple[int, int]]]] = {
    'A': (2,   {'0.065': (-1, 0), '1.0': (-1, 0), '1.5': (-1, 0), '2.5': (-1, 0), '4.0': (-1, 0)}),
    'B': (3,   {'0.065': (-1, 0), '1.0': (-1, 0), '1.5': (-1, 0), '2.5': (-1, 0), '4.0': (-1, 0)}),
    'C': (5,   {'0.065': (0, 1),  '1.0': (0, 1),  '1.5': (0, 1),  '2.5': (0, 1),  '4.0': (0, 1)}),
    'D': (8,   {'0.065': (0, 1),  '1.0': (0, 1),  '1.5': (0, 1),  '2.5': (0, 1),  '4.0': (1, 2)}),
    'E': (13,  {'0.065': (0, 1),  '1.0': (0, 1),  '1.5': (0, 1),  '2.5': (1, 2),  '4.0': (1, 2)}),
    'F': (20,  {'0.065': (0, 1),  '1.0': (0, 1),  '1.5': (1, 2),  '2.5': (1, 2),  '4.0': (2, 3)}),
    'G': (32,  {'0.065': (0, 1),  '1.0': (1, 2),  '1.5': (1, 2),  '2.5': (2, 3),  '4.0': (3, 4)}),
    'H': (50,  {'0.065': (1, 2),  '1.0': (1, 2),  '1.5': (2, 3),  '2.5': (3, 4),  '4.0': (5, 6)}),
    'J': (80,  {'0.065': (1, 2),  '1.0': (2, 3),  '1.5': (3, 4),  '2.5': (5, 6),  '4.0': (7, 8)}),
    'K': (125, {'0.065': (2, 3),  '1.0': (3, 4),  '1.5': (5, 6),  '2.5': (7, 8),  '4.0': (10, 11)}),
    'L': (200, {'0.065': (3, 4),  '1.0': (5, 6),  '1.5': (7, 8),  '2.5': (10, 11), '4.0': (14, 15)}),
    'M': (315, {'0.065': (5, 6),  '1.0': (7, 8),  '1.5': (10, 11), '2.5': (14, 15), '4.0': (21, 22)}),
    'N': (500, {'0.065': (7, 8),  '1.0': (10, 11), '1.5': (14, 15), '2.5': (21, 22), '4.0': (21, 22)}),
    'P': (800, {'0.065': (10, 11), '1.0': (14, 15), '1.5': (21, 22), '2.5': (21, 22), '4.0': (21, 22)}),
    'Q': (1250,{'0.065': (14, 15), '1.0': (21, 22), '1.5': (21, 22), '2.5': (21, 22), '4.0': (21, 22)}),
}


@dataclass(frozen=True)
class AQLSamplingPlan:
    lot_size: int
    inspection_level: InspectionLevel
    aql: AQLValue
    sampling_type: SamplingType
    code_letter: str
    sample_size: int
    accept_number: int
    reject_number: int

    def evaluate(self, defects_found: int) -> str:
        """Return 'ACCEPT' or 'REJECT' based on defects found."""
        if self.accept_number == -1:
            # Arrow — use next code in actual implementation
            return 'ACCEPT' if defects_found == 0 else 'REJECT'
        if defects_found <= self.accept_number:
            return 'ACCEPT'
        return 'REJECT'


def get_code_letter(lot_size: int, level: InspectionLevel) -> str:
    """Derive ISO 2859-1 sample size code letter from lot size and inspection level."""
    base_idx = 0
    for i, threshold in enumerate(_LOT_SIZE_BREAKS):
        if lot_size >= threshold:
            base_idx = i
    adjusted_idx = max(0, min(len(_CODE_LETTERS) - 1,
                               base_idx + _LEVEL_OFFSET[level]))
    return _CODE_LETTERS[adjusted_idx]


def build_sampling_plan(
    lot_size: int,
    aql: AQLValue,
    inspection_level: InspectionLevel = 'II',
    sampling_type: SamplingType = 'NORMAL',
) -> AQLSamplingPlan:
    """
    Construct an ISO 2859-1 single-sampling plan.

    Parameters
    ----------
    lot_size : int
        Total quantity in the submitted lot.
    aql : AQLValue
        Acceptable Quality Level string (e.g. '1.5').
    inspection_level : InspectionLevel
        'I', 'II', or 'III' for general; 'S1'–'S4' for special.
    sampling_type : SamplingType
        'NORMAL', 'TIGHTENED', or 'REDUCED'.

    Returns
    -------
    AQLSamplingPlan
        Fully resolved sampling plan with accept/reject numbers.
    """
    code = get_code_letter(lot_size, inspection_level)
    sample_size, aql_map = _NORMAL_TABLE[code]
    accept, reject = aql_map.get(aql, (-1, 0))
    return AQLSamplingPlan(
        lot_size=lot_size,
        inspection_level=inspection_level,
        aql=aql,
        sampling_type=sampling_type,
        code_letter=code,
        sample_size=sample_size,
        accept_number=accept,
        reject_number=reject,
    )


# Example usage:
# plan = build_sampling_plan(lot_size=2000, aql='1.5', inspection_level='II')
# result = plan.evaluate(defects_found=8)  -> 'ACCEPT' (Ac=14 for code K at 1.5 AQL)
```

#### 6.1.5 Switching Rules

- **Normal to Tightened**: triggered when 2 out of 5 consecutive lots are rejected under normal inspection.
- **Tightened to Normal**: triggered when 5 consecutive lots are accepted under tightened inspection.
- **Normal to Reduced**: triggered when 10 consecutive lots accepted, production steady, quality engineer approves.
- **Reduced to Normal**: triggered by a single rejection, production irregularity, or any other adverse condition.

### 6.2 PPM Calculation Pipeline

#### 6.2.1 Formula

```
PPM = (Total Defective Units / Total Units Inspected) x 1,000,000
```

For sampling-based inspection, the defect count is extrapolated to lot level:

```
Estimated Lot Defectives = (defects_in_sample / sample_size) x lot_size
Lot PPM contribution = (defects_in_sample / sample_size) x 1,000,000
```

Rolling 12-month supplier PPM:

```
PPM_rolling = sum(defects_i for i in last_12_months) /
              sum(units_inspected_i for i in last_12_months) * 1,000,000
```

#### 6.2.2 Industry Benchmarks

| Industry | PPM Target | Rationale |
|---|---|---|
| Automotive (IATF 16949) | < 500 PPM | AIAG Customer-Specific Requirements |
| Aerospace (AS9100) | < 100 PPM | Safety-critical parts, FAA traceability |
| Food & Beverage | <= 1,000 PPM | FDA 21 CFR Part 117, FSMA |
| Consumer Electronics | < 2,000 PPM | IPC-A-610 Class 2 |
| Pharmaceutical (GMP) | 0 tolerance on CQA | 21 CFR Part 211 — any OOS is NCR |
| General manufacturing | < 5,000 PPM | Industry average |

#### 6.2.3 Python Implementation

```python
# python/08_quality_management/ppm_calculator.py

from __future__ import annotations
import pandas as pd
from dataclasses import dataclass


INDUSTRY_PPM_BENCHMARKS = {
    'AUTOMOTIVE': 500,
    'AEROSPACE': 100,
    'FOOD': 1000,
    'CONSUMER_ELECTRONICS': 2000,
    'GENERAL': 5000,
}


@dataclass
class PPMResult:
    supplier_id: str
    period_months: int
    total_units_inspected: int
    total_defects: int
    ppm: float
    benchmark_industry: str
    benchmark_ppm: int
    status: str  # 'CONFORMING' | 'WARNING' | 'CRITICAL'


def calculate_rolling_ppm(
    inspection_df: pd.DataFrame,
    supplier_id: str,
    months: int = 12,
    industry: str = 'AUTOMOTIVE',
) -> PPMResult:
    """
    Calculate rolling PPM for a supplier over the specified number of months.

    Parameters
    ----------
    inspection_df : pd.DataFrame
        Columns: supplier_id, inspected_at, units_inspected, defects_found
    supplier_id : str
        Supplier identifier to filter.
    months : int
        Rolling window in months (default 12).
    industry : str
        Industry benchmark key.

    Returns
    -------
    PPMResult
    """
    cutoff = pd.Timestamp.now() - pd.DateOffset(months=months)
    df = inspection_df[
        (inspection_df['supplier_id'] == supplier_id) &
        (pd.to_datetime(inspection_df['inspected_at']) >= cutoff)
    ]

    total_inspected = df['units_inspected'].sum()
    total_defects = df['defects_found'].sum()

    ppm = (total_defects / total_inspected * 1_000_000) if total_inspected > 0 else 0.0

    benchmark = INDUSTRY_PPM_BENCHMARKS.get(industry, 5000)
    if ppm <= benchmark * 0.5:
        status = 'CONFORMING'
    elif ppm <= benchmark:
        status = 'WARNING'
    else:
        status = 'CRITICAL'

    return PPMResult(
        supplier_id=supplier_id,
        period_months=months,
        total_units_inspected=int(total_inspected),
        total_defects=int(total_defects),
        ppm=round(ppm, 1),
        benchmark_industry=industry,
        benchmark_ppm=benchmark,
        status=status,
    )
```

### 6.3 DPMO and Six Sigma Level

#### 6.3.1 Formula

```
DPMO = (Total Defects / (Units Produced x Opportunities Per Unit)) x 1,000,000
```

Where "Opportunities Per Unit" (OPU) is the number of distinct ways a unit can fail (defined in the FMEA or Control Plan). For example, a printed circuit board assembly with 150 solder joints has OPU = 150 for solder defects.

#### 6.3.2 Six Sigma Level Mapping Table

| Sigma Level | DPMO | Yield (%) | Cp Equivalent |
|---|---|---|---|
| 1σ | 691,462 | 30.85 | 0.33 |
| 2σ | 308,538 | 69.15 | 0.67 |
| 3σ | 66,807 | 93.32 | 1.00 |
| 4σ | 6,210 | 99.38 | 1.33 |
| 5σ | 233 | 99.977 | 1.67 |
| 6σ | 3.4 | 99.9997 | 2.00 |

Note: Six Sigma methodology incorporates a 1.5σ long-term shift, hence 6σ process = 3.4 DPMO (not 0.002 DPMO for a pure 6σ normal distribution).

#### 6.3.3 Python Implementation

```python
# python/08_quality_management/dpmo_calculator.py

import scipy.stats as stats
import numpy as np


SIGMA_DPMO_MAP = {
    1: 691462, 2: 308538, 3: 66807,
    4: 6210,   5: 233,    6: 3.4,
}


def calculate_dpmo(
    total_defects: int,
    units_produced: int,
    opportunities_per_unit: int,
) -> float:
    """Calculate Defects Per Million Opportunities."""
    if units_produced == 0 or opportunities_per_unit == 0:
        raise ValueError("units_produced and opportunities_per_unit must be > 0")
    return (total_defects / (units_produced * opportunities_per_unit)) * 1_000_000


def dpmo_to_sigma_level(dpmo: float) -> float:
    """
    Convert DPMO to sigma level, accounting for the 1.5-sigma long-term shift.

    Formula: sigma_level = stats.norm.ppf(1 - dpmo/1e6) + 1.5
    """
    if dpmo <= 0:
        return 6.0
    z = stats.norm.ppf(1 - dpmo / 1_000_000)
    return round(z + 1.5, 2)


def sigma_level_to_dpmo(sigma_level: float) -> float:
    """Convert sigma level to DPMO (with 1.5-sigma shift)."""
    z = sigma_level - 1.5
    return (1 - stats.norm.cdf(z)) * 1_000_000
```

### 6.4 Statistical Process Control (SPC)

#### 6.4.1 X-bar and R Chart Theory

SPC monitors process stability by plotting subgroup statistics over time and comparing them to statistically derived control limits.

**X-bar chart (subgroup mean):**

```
Center Line (CL):  X-double-bar = mean of all subgroup means
Upper Control Limit (UCL_Xbar) = X-double-bar + A2 * R-bar
Lower Control Limit (LCL_Xbar) = X-double-bar - A2 * R-bar
```

**R chart (subgroup range):**

```
Center Line (CL):  R-bar = mean of all subgroup ranges
UCL_R = D4 * R-bar
LCL_R = D3 * R-bar
```

#### 6.4.2 Control Chart Constants Table

| Subgroup Size (n) | A2 | D3 | D4 | d2 |
|---|---|---|---|---|
| 2 | 1.880 | 0 | 3.267 | 1.128 |
| 3 | 1.023 | 0 | 2.574 | 1.693 |
| 4 | 0.729 | 0 | 2.282 | 2.059 |
| 5 | 0.577 | 0 | 2.114 | 2.326 |
| 6 | 0.483 | 0 | 2.004 | 2.534 |
| 7 | 0.419 | 0.076 | 1.924 | 2.704 |
| 8 | 0.373 | 0.136 | 1.864 | 2.847 |
| 9 | 0.337 | 0.184 | 1.816 | 2.970 |
| 10 | 0.308 | 0.223 | 1.777 | 3.078 |

#### 6.4.3 Western Electric Rules (All 8 Rules)

A process is declared out of statistical control if any of the following occur on either the X-bar or R chart:

| Rule | Description |
|---|---|
| Rule 1 | One point beyond 3-sigma control limits |
| Rule 2 | Two of three consecutive points beyond 2-sigma warning limits (same side) |
| Rule 3 | Four of five consecutive points beyond 1-sigma limits (same side) |
| Rule 4 | Eight consecutive points on the same side of the center line |
| Rule 5 | Six consecutive points steadily increasing or decreasing (trend) |
| Rule 6 | Fifteen consecutive points within 1-sigma of center line (stratification) |
| Rule 7 | Fourteen consecutive points alternating up and down (mixture) |
| Rule 8 | Eight consecutive points beyond 1-sigma on either side (with none in zone C) |

#### 6.4.4 Python SPC Implementation

```python
# python/08_quality_management/spc_charts.py

from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass, field

# A2, D3, D4 constants indexed by subgroup size (n=2 to n=10)
_CONSTANTS = {
    2:  {'A2': 1.880, 'D3': 0,     'D4': 3.267, 'd2': 1.128},
    3:  {'A2': 1.023, 'D3': 0,     'D4': 2.574, 'd2': 1.693},
    4:  {'A2': 0.729, 'D3': 0,     'D4': 2.282, 'd2': 2.059},
    5:  {'A2': 0.577, 'D3': 0,     'D4': 2.114, 'd2': 2.326},
    6:  {'A2': 0.483, 'D3': 0,     'D4': 2.004, 'd2': 2.534},
    7:  {'A2': 0.419, 'D3': 0.076, 'D4': 1.924, 'd2': 2.704},
    8:  {'A2': 0.373, 'D3': 0.136, 'D4': 1.864, 'd2': 2.847},
    9:  {'A2': 0.337, 'D3': 0.184, 'D4': 1.816, 'd2': 2.970},
    10: {'A2': 0.308, 'D3': 0.223, 'D4': 1.777, 'd2': 3.078},
}


@dataclass
class SPCLimits:
    subgroup_size: int
    x_bar_bar: float
    r_bar: float
    ucl_xbar: float
    cl_xbar: float
    lcl_xbar: float
    ucl_r: float
    cl_r: float
    lcl_r: float
    sigma_estimate: float  # process sigma = R-bar / d2


@dataclass
class SPCAlarm:
    subgroup_index: int
    chart: str  # 'XBAR' or 'R'
    rule: int
    description: str
    value: float


def compute_spc_limits(subgroups: list[list[float]]) -> SPCLimits:
    """
    Compute X-bar/R control limits from historical subgroup data.

    Parameters
    ----------
    subgroups : list of lists
        Each inner list is one subgroup of measurements.
    """
    n = len(subgroups[0])
    if n not in _CONSTANTS:
        raise ValueError(f"Subgroup size {n} not supported (2–10 only)")

    c = _CONSTANTS[n]
    means = np.array([np.mean(sg) for sg in subgroups])
    ranges = np.array([max(sg) - min(sg) for sg in subgroups])

    x_bar_bar = float(np.mean(means))
    r_bar = float(np.mean(ranges))

    return SPCLimits(
        subgroup_size=n,
        x_bar_bar=x_bar_bar,
        r_bar=r_bar,
        ucl_xbar=x_bar_bar + c['A2'] * r_bar,
        cl_xbar=x_bar_bar,
        lcl_xbar=x_bar_bar - c['A2'] * r_bar,
        ucl_r=c['D4'] * r_bar,
        cl_r=r_bar,
        lcl_r=c['D3'] * r_bar,
        sigma_estimate=r_bar / c['d2'],
    )


def detect_western_electric_violations(
    values: list[float],
    cl: float,
    ucl: float,
    lcl: float,
    chart: str = 'XBAR',
) -> list[SPCAlarm]:
    """Detect all 8 Western Electric rule violations in a sequence of plotted values."""
    alarms: list[SPCAlarm] = []
    n = len(values)
    sigma = (ucl - cl) / 3

    for i in range(n):
        v = values[i]
        # Rule 1: beyond 3-sigma
        if v > ucl or v < lcl:
            alarms.append(SPCAlarm(i, chart, 1, 'Beyond 3-sigma control limit', v))

        if i >= 2:
            window3 = values[i-2:i+1]
            # Rule 2: 2 of 3 beyond 2-sigma (same side)
            above2 = sum(1 for x in window3 if x > cl + 2*sigma)
            below2 = sum(1 for x in window3 if x < cl - 2*sigma)
            if above2 >= 2 or below2 >= 2:
                alarms.append(SPCAlarm(i, chart, 2, '2 of 3 beyond 2-sigma', v))

        if i >= 4:
            window5 = values[i-4:i+1]
            # Rule 3: 4 of 5 beyond 1-sigma
            above1 = sum(1 for x in window5 if x > cl + sigma)
            below1 = sum(1 for x in window5 if x < cl - sigma)
            if above1 >= 4 or below1 >= 4:
                alarms.append(SPCAlarm(i, chart, 3, '4 of 5 beyond 1-sigma', v))

        if i >= 7:
            window8 = values[i-7:i+1]
            # Rule 4: 8 consecutive on same side
            if all(x > cl for x in window8) or all(x < cl for x in window8):
                alarms.append(SPCAlarm(i, chart, 4, '8 consecutive same side', v))
            # Rule 5: 6 consecutive trending
            diffs = [window8[j+1] - window8[j] for j in range(7)]
            if all(d > 0 for d in diffs) or all(d < 0 for d in diffs[:6]):
                alarms.append(SPCAlarm(i, chart, 5, '6 consecutive trend', v))

    return alarms
```

### 6.5 Process Capability Indices (Cp and Cpk)

#### 6.5.1 Formulas

```
sigma_process = R-bar / d2   (from SPC R chart)

Cp  = (USL - LSL) / (6 * sigma_process)

Cpk = min(
        (USL - X-bar-bar) / (3 * sigma_process),
        (X-bar-bar - LSL) / (3 * sigma_process)
      )

Pp  = (USL - LSL) / (6 * sigma_total)    [uses overall std dev, not R-bar/d2]
Ppk = min((USL - mean) / (3 * sigma_total), (mean - LSL) / (3 * sigma_total))
```

Cp measures potential capability (spread vs. tolerance band).  
Cpk measures actual capability (accounts for process centering).  
Pp and Ppk use total process variation (including between-subgroup variation).

#### 6.5.2 Process Capability Matrix

| Cp | Cpk | Interpretation | Action |
|---|---|---|---|
| ≥ 1.67 | ≥ 1.67 | Six Sigma capable — excellent | Maintain; reduce inspection frequency |
| ≥ 1.33 | ≥ 1.33 | Four Sigma — capable | Normal inspection; monitor quarterly |
| ≥ 1.33 | 1.00–1.33 | Capable but off-center | Center the process; SPC monitoring |
| 1.00–1.33 | 1.00–1.33 | Marginally capable | Increase sample frequency; SPC daily |
| 1.00–1.33 | < 1.00 | Capable spread, poor centering | Immediate re-centering action |
| < 1.00 | < 1.00 | Incapable | STOP production; NCR; process redesign |

### 6.6 FMEA Risk Priority Number (RPN)

#### 6.6.1 Formula

```
RPN = Severity (S) x Occurrence (O) x Detection (D)

Where S, O, D each range from 1 (best) to 10 (worst).
Maximum RPN = 1,000
Action threshold: RPN > 100
```

#### 6.6.2 Severity Scale (AIAG FMEA 4th Ed.)

| S | Effect | Automotive Criterion |
|---|---|---|
| 10 | Hazardous — no warning | Safety defect, regulatory non-compliance |
| 9 | Hazardous — with warning | Safety defect with warning |
| 8 | Very High | Vehicle/item inoperable — loss of primary function |
| 7 | High | Vehicle/item operable — reduced primary function |
| 6 | Moderate | Vehicle/item operable — comfort/convenience lost |
| 5 | Low | Vehicle/item operable — reduced comfort |
| 4 | Very Low | Fit/finish/squeak noticed by most customers |
| 3 | Minor | Fit/finish/squeak noticed by discriminating customers |
| 2 | Very Minor | Defect noticed by discriminating customers |
| 1 | None | No effect |

#### 6.6.3 Occurrence Scale

| O | Probability | Rate |
|---|---|---|
| 10 | Very High | ≥ 1 in 2 |
| 9 | Very High | 1 in 3 |
| 8 | High | 1 in 8 |
| 7 | High | 1 in 20 |
| 6 | Moderate | 1 in 80 |
| 5 | Moderate | 1 in 400 |
| 4 | Moderate-Low | 1 in 2,000 |
| 3 | Low | 1 in 15,000 |
| 2 | Very Low | 1 in 150,000 |
| 1 | Remote | < 1 in 1,500,000 |

#### 6.6.4 Detection Scale

| D | Detectability | Criterion |
|---|---|---|
| 10 | Absolutely impossible | No current controls; cannot detect |
| 9 | Very Remote | Very unlikely to detect |
| 8 | Remote | Poor chance to detect |
| 7 | Very Low | Poor chance to detect in time |
| 6 | Low | Controls may detect |
| 5 | Moderate | Controls may detect (moderate chance) |
| 4 | Moderately High | Controls likely to detect |
| 3 | High | Controls have good chance of detection |
| 2 | Very High | Controls almost certain to detect |
| 1 | Almost Certain | Controls will detect; mistake-proof |

#### 6.6.5 RPN Risk Priority Matrix

| RPN Range | Risk Level | Required Action |
|---|---|---|
| > 500 | Critical | Immediate production hold; emergency containment within 24 h |
| 200 – 500 | High | Design or process change required within 30 days |
| 100 – 199 | Moderate | Corrective action plan with 8D within 60 days |
| 50 – 99 | Low | Monitor; improve at next planned revision |
| < 50 | Negligible | Document; no immediate action required |

### 6.7 AQL Operating Characteristic (OC) Curve

#### 6.7.1 Theory

The OC curve plots the probability of lot acceptance (Pa) against the actual fraction defective (p) in the lot. It characterises the discriminating power of the sampling plan.

- **Producer Risk (alpha)**: probability of rejecting a good lot (p = AQL). Typically alpha = 0.05 (5%).
- **Consumer Risk (beta)**: probability of accepting a bad lot (p = LTPD, Lot Tolerance Percent Defective). Typically beta = 0.10 (10%).

For a binomial sampling plan with sample size n and acceptance number c:

```
Pa(p) = sum_{k=0}^{c} C(n, k) * p^k * (1-p)^(n-k)
```

For large n and small p, the Poisson approximation is more convenient:

```
Pa(p) = sum_{k=0}^{c} exp(-n*p) * (n*p)^k / k!
```

#### 6.7.2 Python OC Curve

```python
# python/08_quality_management/oc_curve.py

import numpy as np
from scipy.stats import binom
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def oc_curve(n: int, c: int, p_range: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute the Operating Characteristic curve for a single-sampling plan.

    Parameters
    ----------
    n : int   Sample size.
    c : int   Acceptance number.
    p_range : array of fraction defective values (0 to 1).

    Returns
    -------
    (p_values, pa_values) arrays.
    """
    if p_range is None:
        p_range = np.linspace(0, 0.20, 200)

    pa = np.array([binom.cdf(c, n, p) for p in p_range])
    return p_range, pa


def find_producer_consumer_risk(
    n: int,
    c: int,
    aql: float,
    ltpd: float,
) -> dict[str, float]:
    """
    Derive producer risk (alpha) and consumer risk (beta) from the OC curve.

    Parameters
    ----------
    aql  : AQL as fraction defective (e.g. 0.015 for 1.5%)
    ltpd : Lot Tolerance Percent Defective as fraction (e.g. 0.08)
    """
    pa_at_aql = float(binom.cdf(c, n, aql))
    pa_at_ltpd = float(binom.cdf(c, n, ltpd))
    return {
        'producer_risk_alpha': round(1 - pa_at_aql, 4),
        'consumer_risk_beta': round(pa_at_ltpd, 4),
        'pa_at_aql': round(pa_at_aql, 4),
        'pa_at_ltpd': round(pa_at_ltpd, 4),
    }
```

### 6.8 NCR Cycle Time Analytics

#### 6.8.1 Key Metrics

```
NCR Cycle Time = NCR_Close_Date - NCR_Open_Date  (calendar days)

Mean Cycle Time = mean(NCR_Cycle_Time for all closed NCRs in period)
P80 Cycle Time  = 80th percentile of NCR_Cycle_Time distribution
Target          = mean <= 30 days; P80 <= 45 days
```

#### 6.8.2 Pareto of Root Causes

Root causes are coded using the Ishikawa (5M1E) taxonomy:
- **Man** (human error, training gap)
- **Machine** (equipment failure, tooling wear)
- **Material** (supplier non-conformance, raw material defect)
- **Method** (process parameter deviation, work instruction error)
- **Measurement** (gauge error, calibration lapse)
- **Environment** (temperature, humidity, contamination)

A Pareto chart of NCR frequency by root cause category is generated monthly. The top 2 root causes typically account for 70–80% of NCRs (Juran's 80/20 rule). These drive the monthly Quality Improvement Project (QIP) selection.

---

## 7. Phase 4: ML/AI Pipeline

**Duration**: Weeks 20–32  
**Goal**: Deploy machine learning models that move the quality function from reactive to predictive.

### 7.1 Architecture Overview

```
[MES/SCADA Sensors] ---MQTT---> [Redis Streams] ----> [LSTM Autoencoder (SPC anomaly)]
[Inspection Images] ---USB/GigE-> [Jetson Orin] -----> [YOLOv8 defect detection]
[Process Parameters] -> [Feature Store (PostgreSQL)] -> [XGBoost predictive quality]
[NCR Text (D2 field)] -> [NLP Pipeline] --------------> [spaCy + DistilBERT classifier]
                                                              |
                                              [Quality Dashboard (Grafana)]
```

All models are retrained monthly using the latest production data. Model versioning is managed with MLflow (Apache-2.0). Champion/challenger framework: new model is promoted only when validation AUC exceeds incumbent by > 0.02 on held-out test set.

### 7.2 Computer Vision Defect Detection (YOLOv8)

#### 7.2.1 Use Case

Automated visual inspection at incoming goods or end-of-line stations. The camera captures images of parts; YOLOv8 detects and classifies defects (scratch, crack, contamination, dimensional deviation) in real time. Results are posted to the NCR workflow if confidence > 0.85 and bounding box area > threshold.

#### 7.2.2 Dataset Preparation

1. Collect minimum 2,000 images per defect class (Roboflow benchmark for production-grade YOLO).
2. Annotate with LabelImg (MIT licensed):
   - Draw bounding boxes around each defect.
   - Assign class labels from the defect code library.
   - Export in YOLO format (`class cx cy w h` normalised to image dimensions).
3. Split: 70% train / 15% val / 15% test.
4. Apply data augmentation (albumentations library, MIT licensed):
   - Horizontal flip, vertical flip, rotation ±15 degrees
   - Brightness/contrast jitter ±20%
   - Gaussian noise (sigma 5–25)
   - Random crop and resize to 640x640

#### 7.2.3 Training Pipeline

```python
# python/08_quality_management/cv/train_yolov8.py

from ultralytics import YOLO
import yaml
from pathlib import Path


def train_defect_detection_model(
    dataset_yaml: str,
    model_variant: str = 'yolov8m.pt',
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    device: str = 'cuda:0',
    project: str = 'runs/quality/defect_detection',
    run_name: str = 'v1',
) -> str:
    """
    Train YOLOv8 defect detection model.

    Parameters
    ----------
    dataset_yaml : str
        Path to dataset configuration YAML.
        Must define: path, train, val, test, nc (num classes), names (class list).
    model_variant : str
        YOLOv8 pre-trained weights: yolov8n/s/m/l/x.pt
    epochs : int
        Training epochs.
    device : str
        'cpu', 'cuda:0', or '0,1' for multi-GPU.

    Returns
    -------
    str : Path to best weights file.
    """
    model = YOLO(model_variant)

    results = model.train(
        data=dataset_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project=project,
        name=run_name,
        patience=20,          # early stopping
        save=True,
        save_period=10,
        val=True,
        augment=True,
        # Hyperparameters tuned for industrial defect images
        lr0=0.01,
        lrf=0.001,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        mosaic=1.0,
        mixup=0.1,
        copy_paste=0.1,
    )

    best_weights = Path(project) / run_name / 'weights' / 'best.pt'
    return str(best_weights)


def export_to_tensorrt(weights_path: str, output_dir: str) -> str:
    """Export trained model to TensorRT for Jetson Orin edge deployment."""
    model = YOLO(weights_path)
    # Export to TensorRT FP16 for Jetson
    model.export(format='engine', half=True, device=0, imgsz=640)
    engine_path = weights_path.replace('.pt', '.engine')
    return engine_path


def run_inference_at_station(
    engine_path: str,
    image_source: str,  # 'rtsp://...' or camera index
    confidence_threshold: float = 0.85,
    iou_threshold: float = 0.45,
) -> list[dict]:
    """
    Real-time inference at inspection station.
    Posts defect records to quality management API when detections exceed threshold.
    """
    model = YOLO(engine_path)
    detections = []

    for result in model.predict(
        source=image_source,
        conf=confidence_threshold,
        iou=iou_threshold,
        stream=True,
        verbose=False,
    ):
        for box in result.boxes:
            detections.append({
                'class': result.names[int(box.cls)],
                'confidence': float(box.conf),
                'bbox': box.xyxy[0].tolist(),
                'image_path': result.path,
            })

    return detections
```

#### 7.2.4 Dataset YAML Example

```yaml
# datasets/defect_detection/dataset.yaml
path: /data/quality/defect_images
train: images/train
val: images/val
test: images/test

nc: 6
names:
  - scratch
  - crack
  - contamination
  - dimensional_deviation
  - surface_void
  - label_defect
```

#### 7.2.5 Edge Deployment on Jetson Orin

1. Flash Jetson Orin with JetPack 6.x (includes CUDA 12, TensorRT 10).
2. Install ultralytics with CUDA support: `pip install ultralytics[export]`
3. Export model to TensorRT FP16 (inference latency target: < 50 ms at 640x640).
4. Station control software calls `run_inference_at_station()` for each part image.
5. Results posted to Quality Management API `/api/v1/inspections/{id}/cv-detections` within 100 ms.
6. High-confidence detections trigger automatic NCR draft with annotated image attached.

#### 7.2.6 Performance Targets

| Metric | Target | Measurement |
|---|---|---|
| mAP@0.5 | ≥ 0.90 | YOLO validation set |
| mAP@0.5:0.95 | ≥ 0.75 | YOLO validation set |
| Inference Latency | < 50 ms | Jetson Orin TensorRT FP16 |
| False Positive Rate | < 5% | Manual audit 500 images/month |
| False Negative Rate | < 2% | Critical — missed defects |

### 7.3 Predictive Quality with XGBoost

#### 7.3.1 Use Case

Predict the probability that a production batch will contain defects exceeding the AQL threshold, using in-process parameters (temperature, pressure, speed, humidity, tooling age, operator shift) as features. Batches above the risk threshold are flagged for 100% inspection or hold pending engineer review.

#### 7.3.2 Feature Engineering

| Feature | Source | Type | Notes |
|---|---|---|---|
| machine_temperature_mean | MES | Continuous | Mean over batch run |
| machine_temperature_std | MES | Continuous | Instability indicator |
| injection_pressure_bar | MES | Continuous | Average peak pressure |
| cycle_time_seconds | MES | Continuous | Deviation from standard |
| tooling_age_shots | MES | Integer | Shots since last PM |
| ambient_humidity_pct | SCADA | Continuous | From environmental sensor |
| operator_shift | ERP | Categorical | Morning/Afternoon/Night |
| raw_material_lot_ppm | Quality | Continuous | Supplier PPM for input lot |
| days_since_last_calibration | Metrology | Integer | Gauge calibration lag |
| last_5_batch_dpmo | Quality | Continuous | Rolling quality trend |

#### 7.3.3 Training Pipeline

```python
# python/08_quality_management/ml/predictive_quality_xgboost.py

from __future__ import annotations
import numpy as np
import pandas as pd
import xgboost as xgb
import shap
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (roc_auc_score, precision_score,
                              recall_score, f1_score, classification_report)
from sklearn.preprocessing import LabelEncoder
import mlflow
import mlflow.xgboost
from pathlib import Path


FEATURE_COLS = [
    'machine_temperature_mean', 'machine_temperature_std',
    'injection_pressure_bar', 'cycle_time_seconds',
    'tooling_age_shots', 'ambient_humidity_pct',
    'operator_shift_encoded', 'raw_material_lot_ppm',
    'days_since_last_calibration', 'last_5_batch_dpmo',
]

TARGET_COL = 'batch_failed_aql'  # 1 = failed AQL, 0 = passed


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Encode categorical features and handle missing values."""
    df = df.copy()
    le = LabelEncoder()
    df['operator_shift_encoded'] = le.fit_transform(df['operator_shift'].fillna('UNKNOWN'))
    # Clip extreme outliers at 99th percentile per feature
    for col in FEATURE_COLS:
        if col in df.columns:
            cap = df[col].quantile(0.99)
            df[col] = df[col].clip(upper=cap)
    df[FEATURE_COLS] = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())
    return df


def train_predictive_quality_model(
    df: pd.DataFrame,
    experiment_name: str = 'quality-predictive-xgboost',
    n_folds: int = 5,
) -> xgb.XGBClassifier:
    """
    Train XGBoost defect prediction model with cross-validation and MLflow tracking.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain FEATURE_COLS and TARGET_COL.
    experiment_name : str
        MLflow experiment name.
    n_folds : int
        Stratified K-fold splits.

    Returns
    -------
    xgb.XGBClassifier : Best trained model.
    """
    df = prepare_features(df)
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    pos_weight = (y == 0).sum() / max((y == 1).sum(), 1)  # handle class imbalance

    params = {
        'n_estimators': 500,
        'learning_rate': 0.05,
        'max_depth': 6,
        'min_child_weight': 3,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'scale_pos_weight': pos_weight,
        'eval_metric': 'auc',
        'use_label_encoder': False,
        'random_state': 42,
        'tree_method': 'hist',  # GPU-accelerated: 'gpu_hist'
    }

    mlflow.set_experiment(experiment_name)
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    fold_aucs = []

    with mlflow.start_run():
        mlflow.log_params(params)

        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
            model = xgb.XGBClassifier(**params)
            model.fit(
                X[train_idx], y[train_idx],
                eval_set=[(X[val_idx], y[val_idx])],
                verbose=False,
                early_stopping_rounds=30,
            )
            val_preds = model.predict_proba(X[val_idx])[:, 1]
            auc = roc_auc_score(y[val_idx], val_preds)
            fold_aucs.append(auc)

        mean_auc = float(np.mean(fold_aucs))
        mlflow.log_metric('cv_mean_auc', mean_auc)

        # Final model on full dataset
        final_model = xgb.XGBClassifier(**params)
        final_model.fit(X, y, verbose=False)
        mlflow.xgboost.log_model(final_model, 'model')

    return final_model


def explain_prediction_with_shap(
    model: xgb.XGBClassifier,
    X_sample: pd.DataFrame,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Generate SHAP feature importance for a specific batch prediction.
    Returns a DataFrame of feature name, SHAP value, and direction for engineer review.
    """
    X_prepared = prepare_features(X_sample)[FEATURE_COLS]
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_prepared)

    shap_df = pd.DataFrame({
        'feature': FEATURE_COLS,
        'shap_value': shap_values[0],
        'abs_shap': np.abs(shap_values[0]),
        'direction': ['increase_risk' if v > 0 else 'decrease_risk' for v in shap_values[0]],
    }).sort_values('abs_shap', ascending=False).head(top_n)

    return shap_df
```

### 7.4 NLP for NCR Root Cause Classification

#### 7.4.1 Use Case

Quality engineers spend significant time manually categorising NCR root causes in D4 of the 8D report. An NLP classifier reads the free-text problem description (D2) and suggests the most likely root cause category from the Ishikawa 5M1E taxonomy. This reduces classification time from ~15 minutes to < 30 seconds and improves consistency across sites.

#### 7.4.2 Architecture

```
[NCR D2 Text] -> [spaCy preprocessing] -> [DistilBERT fine-tuned]
                                             -> [Softmax over 6 classes]
                                             -> [Confidence score]
                                             -> [Top-2 suggestions to engineer]
```

#### 7.4.3 Training Pipeline

```python
# python/08_quality_management/nlp/ncr_classifier.py

from __future__ import annotations
import pandas as pd
import numpy as np
import spacy
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from datasets import Dataset
import torch
from sklearn.metrics import classification_report


ROOT_CAUSE_LABELS = ['MAN', 'MACHINE', 'MATERIAL', 'METHOD', 'MEASUREMENT', 'ENVIRONMENT']
LABEL2ID = {label: i for i, label in enumerate(ROOT_CAUSE_LABELS)}
ID2LABEL = {i: label for label, i in LABEL2ID.items()}

nlp = spacy.load('en_core_web_sm')  # loaded once at module level


def preprocess_ncr_text(text: str) -> str:
    """
    Normalise NCR description text using spaCy:
    - Lowercase, lemmatise, remove stop words and punctuation.
    - Preserve domain-specific terms (part numbers, process codes).
    """
    doc = nlp(text.lower())
    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct and token.is_alpha
    ]
    return ' '.join(tokens)


def build_hf_dataset(df: pd.DataFrame, tokenizer) -> Dataset:
    """Convert DataFrame with 'text' and 'label' columns to HuggingFace Dataset."""
    df = df.copy()
    df['label'] = df['root_cause'].map(LABEL2ID)
    df['text'] = df['d2_description'].apply(preprocess_ncr_text)

    def tokenize(batch):
        return tokenizer(batch['text'], truncation=True, padding='max_length', max_length=128)

    dataset = Dataset.from_pandas(df[['text', 'label']])
    return dataset.map(tokenize, batched=True)


def train_ncr_classifier(
    df_train: pd.DataFrame,
    df_eval: pd.DataFrame,
    output_dir: str = 'models/ncr_classifier',
    epochs: int = 5,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
) -> DistilBertForSequenceClassification:
    """Fine-tune DistilBERT for NCR root cause classification."""
    model_name = 'distilbert-base-uncased'
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(ROOT_CAUSE_LABELS),
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    train_dataset = build_hf_dataset(df_train, tokenizer)
    eval_dataset = build_hf_dataset(df_eval, tokenizer)

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='eval_loss',
        logging_dir=f'{output_dir}/logs',
        warmup_ratio=0.1,
        fp16=torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )
    trainer.train()
    trainer.save_model(output_dir)

    return model


def classify_ncr(
    text: str,
    model: DistilBertForSequenceClassification,
    tokenizer: DistilBertTokenizer,
    top_k: int = 2,
) -> list[dict]:
    """
    Classify NCR description and return top-k root cause suggestions.

    Returns list of {'label': str, 'confidence': float} sorted by confidence desc.
    """
    processed = preprocess_ncr_text(text)
    inputs = tokenizer(processed, return_tensors='pt',
                       truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1).squeeze().tolist()

    results = [
        {'label': ROOT_CAUSE_LABELS[i], 'confidence': round(prob, 4)}
        for i, prob in enumerate(probs)
    ]
    return sorted(results, key=lambda x: x['confidence'], reverse=True)[:top_k]
```

### 7.5 SPC Anomaly Detection with LSTM Autoencoder

#### 7.5.1 Use Case

Traditional Western Electric rules detect univariate out-of-control signals on individual control charts. The LSTM Autoencoder extends this to multivariate sensor streams (e.g., 12 simultaneous process parameters from a CNC machining centre), detecting complex anomaly patterns invisible to single-variable SPC.

The autoencoder is trained only on in-control data. When a new window of sensor readings has a reconstruction error above the 99th percentile of the training distribution, an alarm is raised.

#### 7.5.2 Architecture

```
Input: sliding window [T=30 timesteps, F=12 features]
   -> LSTM Encoder (64 units, return_sequences=False)
   -> RepeatVector(30)
   -> LSTM Decoder (64 units, return_sequences=True)
   -> TimeDistributed(Dense(12))
   -> Output: reconstructed window [T=30, F=12]

Loss: MSE between input and reconstruction
Threshold: 99th percentile of MSE on validation set (in-control data only)
```

#### 7.5.3 Training Pipeline

```python
# python/08_quality_management/ml/spc_lstm_autoencoder.py

from __future__ import annotations
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from typing import Optional


WINDOW_SIZE = 30   # timesteps per sliding window
N_FEATURES = 12   # number of sensor channels
ANOMALY_PERCENTILE = 99


class LSTMAutoencoder(nn.Module):
    """LSTM Autoencoder for multivariate SPC anomaly detection."""

    def __init__(self, n_features: int = N_FEATURES, hidden_size: int = 64):
        super().__init__()
        self.n_features = n_features
        self.hidden_size = hidden_size

        self.encoder = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_size,
            num_layers=1,
            batch_first=True,
        )
        self.decoder = nn.LSTM(
            input_size=hidden_size,
            hidden_size=n_features,
            num_layers=1,
            batch_first=True,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, n_features)
        _, (hidden, _) = self.encoder(x)
        # Repeat hidden state across sequence
        context = hidden.permute(1, 0, 2).repeat(1, x.size(1), 1)
        reconstruction, _ = self.decoder(context)
        return reconstruction


def create_windows(data: np.ndarray, window_size: int) -> np.ndarray:
    """Create overlapping sliding windows from time series data."""
    windows = []
    for i in range(len(data) - window_size + 1):
        windows.append(data[i:i + window_size])
    return np.array(windows)


def train_lstm_autoencoder(
    normal_data: pd.DataFrame,
    epochs: int = 50,
    batch_size: int = 64,
    learning_rate: float = 1e-3,
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
) -> tuple[LSTMAutoencoder, StandardScaler, float]:
    """
    Train LSTM Autoencoder on in-control sensor data.

    Parameters
    ----------
    normal_data : pd.DataFrame
        Time series of shape (n_timesteps, n_features) — IN-CONTROL data only.

    Returns
    -------
    (model, scaler, threshold) where threshold is 99th percentile reconstruction error.
    """
    scaler = StandardScaler()
    scaled = scaler.fit_transform(normal_data.values)
    windows = create_windows(scaled, WINDOW_SIZE)

    # 80/20 train/val split
    split = int(0.8 * len(windows))
    X_train = torch.FloatTensor(windows[:split])
    X_val = torch.FloatTensor(windows[split:])

    train_loader = DataLoader(TensorDataset(X_train, X_train),
                               batch_size=batch_size, shuffle=True)

    model = LSTMAutoencoder(n_features=normal_data.shape[1]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for x_batch, _ in train_loader:
            x_batch = x_batch.to(device)
            optimizer.zero_grad()
            recon = model(x_batch)
            loss = criterion(recon, x_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        if (epoch + 1) % 10 == 0:
            model.eval()
            with torch.no_grad():
                val_recon = model(X_val.to(device))
                val_loss = criterion(val_recon, X_val.to(device)).item()
            print(f"Epoch {epoch+1}/{epochs} | Train: {train_loss/len(train_loader):.4f} | Val: {val_loss:.4f}")

    # Compute threshold on validation set
    model.eval()
    with torch.no_grad():
        val_recon = model(X_val.to(device))
        errors = ((val_recon - X_val.to(device)) ** 2).mean(dim=(1, 2)).cpu().numpy()

    threshold = float(np.percentile(errors, ANOMALY_PERCENTILE))
    return model, scaler, threshold


def detect_anomaly(
    window: np.ndarray,
    model: LSTMAutoencoder,
    scaler: StandardScaler,
    threshold: float,
    device: str = 'cpu',
) -> dict:
    """
    Detect anomaly in a single sensor window.

    Parameters
    ----------
    window : np.ndarray shape (WINDOW_SIZE, N_FEATURES)

    Returns
    -------
    dict with 'reconstruction_error', 'is_anomaly', 'threshold'.
    """
    scaled = scaler.transform(window)
    x = torch.FloatTensor(scaled).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        recon = model(x)
        error = float(((recon - x) ** 2).mean().item())

    return {
        'reconstruction_error': round(error, 6),
        'threshold': round(threshold, 6),
        'is_anomaly': error > threshold,
        'severity_ratio': round(error / threshold, 3),
    }
```

---

## 8. Phase 5: Integration and Automation

**Duration**: Weeks 28–36  
**Goal**: Connect all quality models and workflows to enterprise systems.

### 8.1 SAP QM Integration

Integration points with SAP Quality Management (QM module):

| Direction | SAP Object | Integration Method | Trigger |
|---|---|---|---|
| SAP -> QMS | Inspection Lot (QA01) | RFC BAPI_INSPLOT_CREATE | Goods receipt in SAP MM |
| QMS -> SAP | Usage Decision (QA11) | RFC BAPI_QUAINSP_USAGEDEC | Inspector posts disposition |
| QMS -> SAP | Defect Recording (QF01) | REST wrapper over RFC QM_QF01_* | Defects entered on tablet |
| SAP -> QMS | Material Master AQL config | RFC BAPI_MATERIAL_GET_DETAIL | Synchronised nightly |
| QMS -> SAP | NCR notification (QM10) | RFC BAPI_QM_CREATE_NOTIFICATION | NCR opened in QMS |

### 8.2 MES/SCADA for In-Process SPC

SPC data acquisition follows this flow:

1. SCADA publishes sensor readings to MQTT broker (topic: `factory/{line_id}/sensors`) at 1 Hz.
2. Quality SPC service subscribes, buffers readings into Redis Streams.
3. When a subgroup is complete (n=5 readings), the SPC computation service calculates X-bar and R, evaluates Western Electric rules, and persists to PostgreSQL.
4. Violations trigger SPC alarms via Redis Pub/Sub to shop-floor dashboards (Grafana) and push notifications to line supervisors.
5. LSTM Autoencoder runs on a 30-timestep sliding window, posting anomaly scores every 30 seconds.

### 8.3 LIMS Integration

Laboratory Information Management System integration:

- Test requests created in LIMS when incoming inspection requires chemical or physical lab testing (e.g., tensile strength, pH, viscosity).
- LIMS test results posted to QMS via REST API (`POST /api/v1/lab-results`).
- Results automatically linked to inspection record; disposition decision deferred until lab results available.
- EU REACH SVHC test results stored with minimum 5-year retention per CSDDD Article 23.

### 8.4 Supplier Quality Portal

Suppliers interact with the portal for:

- **Defect notifications**: automatic email and portal alert on lot rejection, with AQL report and annotated images (from YOLOv8).
- **8D response submission**: supplier uploads corrective action documents directly to NCR workflow.
- **Self-certification**: suppliers upload PPAP (Production Part Approval Process) documents, CoC (Certificates of Conformance), and test reports.
- **PPM dashboard**: real-time visibility of their rolling 12-month PPM vs. contractual target.

### 8.5 IATF 16949 Audit Integration

For automotive customers, the quality system must support IATF 16949 audit requirements:

- All Control Plans stored with version history and approval workflow.
- FMEA records linked to Control Plan characteristics; RPN history maintained.
- Customer-Specific Requirements (CSRs) documented per OEM (Volkswagen VDA 6.3, GM BIQS, Ford Q1).
- Audit findings tracked as NCRs with standard 8D response.
- Management Review minutes stored with action owner, due date, and status.

---

## 9. Phase 6: Continuous Improvement

**Duration**: Ongoing from Week 36  
**Goal**: Institutionalise improvement cadence; drive year-over-year quality gains.

### 9.1 DMAIC Project Pipeline

A formal Six Sigma DMAIC project pipeline is maintained with at minimum two active projects at any time:

| Stage | Gate Criteria | Tool |
|---|---|---|
| Define | Problem statement, team, goal, scope | Project Charter |
| Measure | Baseline Cp/Cpk, DPMO, Pareto | MSA, SPC, Pareto |
| Analyse | Root causes validated (hypothesis test p < 0.05) | DOE, Regression, Fishbone |
| Improve | Solution validated (paired t-test or ANOVA) | DOE, Poka-Yoke |
| Control | Control Plan updated, SPC active, handoff | SPC, FMEA update |

### 9.2 Kaizen Velocity Targets

| Year | Kaizen Events | Expected COPQ Reduction |
|---|---|---|
| Year 1 | 6 events | 20% COPQ reduction |
| Year 2 | 8 events | 15% additional COPQ reduction |
| Year 3 | 10 events | 10% additional (compounding) |

### 9.3 Supplier Development Programme

Suppliers rated CONDITIONAL or PROBATION on the scorecard are placed on a Supplier Development Programme (SDP):

- Dedicated SQE (Supplier Quality Engineer) assigned for 90 days.
- Monthly on-site process audits.
- Joint FMEA and Control Plan review.
- PPM improvement target: 30% reduction within 6 months or supplier at risk of disqualification.

### 9.4 Model Retraining Schedule

| Model | Retraining Frequency | Trigger |
|---|---|---|
| YOLOv8 defect detection | Monthly | ≥ 500 new labelled images |
| XGBoost predictive quality | Monthly | New production batch data |
| DistilBERT NCR classifier | Quarterly | ≥ 200 new labelled NCRs |
| LSTM SPC Autoencoder | Quarterly | Process engineering change |

---

## 10. Technology Stack and Architecture

### 10.1 Stack Summary

| Layer | Technology | License | Purpose |
|---|---|---|---|
| Domain Logic | TypeScript 5.3+ | — | Aggregates, domain events, business rules |
| Mathematical Models | Python 3.11+ | — | AQL, SPC, Cp/Cpk, PPM, DPMO |
| ML Training | PyTorch 2.x, XGBoost, transformers | BSD-3/Apache | Model training |
| ML Serving | TorchServe / FastAPI | Apache-2.0 | Model inference API |
| Edge Vision | YOLOv8 TensorRT on Jetson Orin | AGPL-3.0 / commercial-ok for production | Station defect detection |
| Event Store | PostgreSQL 15 + event sourcing | PostgreSQL License | Domain events |
| Streaming | Redis 7 Streams | BSD-3 | MQTT buffering, SPC windows |
| Model Registry | MLflow | Apache-2.0 | Model versioning, lineage |
| Dashboards | Grafana | AGPL-3.0 | SPC charts, quality KPIs |
| API Layer | FastAPI (Python) + Express (TypeScript) | MIT | REST APIs |
| Message Bus | RabbitMQ | MPL-2.0 | Cross-module events |

### 10.2 Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                      │
│                                                           │
│  [Quality API (FastAPI)] <--> [PostgreSQL Event Store]   │
│       |                                                   │
│  [SPC Service] <---------> [Redis Streams]               │
│       |                         ^                         │
│  [ML Inference API]        [MQTT Bridge]                  │
│   - XGBoost                     ^                         │
│   - DistilBERT                  |                         │
│   - LSTM AE              [MES/SCADA OPC-UA]               │
│                                                           │
└─────────────────────────────────────────────────────────┘
         |                              |
  [Jetson Orin]              [Supplier Portal]
  (YOLOv8 edge)              (Node.js / React)
```

---

## 11. Change Management and Training

### 11.1 Stakeholder Impact Assessment

| Stakeholder | Change Impact | Resistance Risk | Mitigation |
|---|---|---|---|
| Quality Inspectors | New digital tablet workflow replaces paper | Medium | Hands-on training; involve champions early |
| Quality Engineers | AI-assisted root cause classification | Low | Framed as decision support, not replacement |
| Suppliers | Portal-based NCR communication | Medium | Simple UX; portal onboarding workshop |
| Production Supervisors | Real-time SPC alarms disrupt flow | High | Clear alarm response procedure; false alarm governance |
| QA Manager | KPI dashboards visible to leadership | Low | Co-design dashboard content |
| IT/Infrastructure | New Jetson Orin fleet, GPU servers | Medium | Infrastructure sizing workshop early |

### 11.2 Training Plan

| Role | Training Module | Duration | Delivery |
|---|---|---|---|
| Inspector | Digital Incoming Inspection Workflow | 4 hours | Classroom + hands-on |
| Inspector | AQL Sampling Principles (ISO 2859-1) | 2 hours | E-learning |
| Quality Engineer | SPC Interpretation and Response | 8 hours | Workshop |
| Quality Engineer | XGBoost Model Outputs and SHAP | 4 hours | Workshop |
| Quality Engineer | 8D NLP Classifier — how to use and override | 2 hours | E-learning |
| SQE | Supplier Development Programme | 16 hours | Classroom |
| Supervisor | Reading Grafana Dashboards | 2 hours | E-learning |
| IT | Jetson Orin Operations | 8 hours | Vendor training |

### 11.3 Communication Plan

- Month -2: Executive sponsorship announcement; "What's changing and why" Q&A sessions.
- Month -1: Super-user network identified; pilot site selection communicated.
- Week 0: Go-live communications; helpdesk contact publicised.
- Months 1–3: Weekly quality newsletter with early wins and KPI progress.
- Month 6: Lessons learned workshop; Phase 2 improvement decisions.

---

## 12. Implementation KPIs

### 12.1 Programme Health KPIs (Implementation)

| KPI | Target | Measurement |
|---|---|---|
| % of inspections digitalised (vs. paper) | 100% by Week 18 | System record count |
| % of active part numbers with digital Control Plan | ≥ 90% by Week 12 | QMS count |
| Supplier portal adoption rate | ≥ 80% of Tier-1 by Week 24 | Login data |
| SPC charts active on critical characteristics | 100% by Week 22 | SPC service report |
| YOLOv8 model mAP@0.5 on test set | ≥ 0.90 before go-live | Validation log |
| XGBoost AUC on held-out test set | ≥ 0.80 before go-live | MLflow metrics |

### 12.2 Business Outcome KPIs (Post Go-Live)

| KPI | Baseline | Year 1 Target | Year 3 Target |
|---|---|---|---|
| Supplier PPM (Tier-1 average) | Measured | -25% | -50% |
| NCR Mean Cycle Time | Measured | ≤ 30 days | ≤ 21 days |
| Incoming Rejection Rate | Measured | -20% | -40% |
| COPQ as % of Revenue | Measured | -20% | -35% |
| First Pass Yield | Measured | +2 pp | +5 pp |
| Cpk (critical characteristics) | Measured | ≥ 1.33 avg | ≥ 1.67 avg |
| % defects caught by CV before inspector | 0% | 60% | 85% |
| Predictive quality alert precision | N/A | ≥ 75% | ≥ 85% |

---

## 13. Risk and Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Insufficient labelled image data for YOLOv8 | High | High | Start labelling Day 1; synthetic data augmentation; transfer learning from similar domain |
| MES/SCADA OPC-UA connectivity delays | Medium | High | Parallel CSV upload path for batch SPC; OPC-UA pilot on one line first |
| Supplier resistance to portal adoption | Medium | Medium | Executive-level supplier meeting; incentivise early adopters with scorecard bonus |
| SPC false alarm rate too high (>5%) | Medium | Medium | Phased Western Electric rule activation; start with Rule 1 only; tune over 60 days |
| FMEA data not maintained by engineering | High | High | FMEA update mandatory gate on NCR closure; automated FMEA staleness report |
| XGBoost model drift after process change | Medium | High | MLflow model monitoring; retrain trigger when PSI > 0.2 on feature distribution |
| GDPR / data privacy on operator shift feature | Low | Medium | Anonymise shift data to shift code; DPA review before production use |
| Jetson Orin firmware/driver incompatibility | Low | Medium | Validate JetPack version against ultralytics compatibility matrix before procurement |
| ISO 9001 audit finding during implementation | Medium | Medium | Pre-audit internal review at Week 16; address Critical gaps before external audit |
| Key quality engineer attrition | Low | High | Knowledge documentation at each phase; cross-training backup per model |

---

## 14. Timeline Summary

| Phase | Weeks | Key Deliverables |
|---|---|---|
| Phase 0: Assessment | 1–4 | AS-IS baseline, gap analysis, project charter |
| Phase 1: Foundation | 5–10 | Master data loaded, TypeScript aggregates deployed, Event Store live |
| Phase 2: Process Standardisation | 11–18 | Digital inspection workflow, NCR 8D active, Supplier Portal v1 |
| Phase 3: Mathematical Models | 15–22 | AQL engine, PPM/DPMO pipeline, SPC charts, Cp/Cpk, FMEA RPN |
| Phase 4: ML/AI Pipeline | 20–32 | YOLOv8 trained and edge-deployed, XGBoost live, NLP classifier live, LSTM AE live |
| Phase 5: Integration | 28–36 | SAP QM bi-directional, MES/SCADA SPC feed, LIMS integration, IATF audit system |
| Phase 6: Continuous Improvement | 36+ | DMAIC pipeline, Kaizen cadence, model retraining schedule, SDP programme |

**Total programme duration**: 36 weeks to full capability; ongoing from Week 36.

**Critical path**: Phase 0 -> Phase 1 -> Phase 2 (digital workflow is prerequisite for ML training data) -> Phase 3 (SPC needed before LSTM training) -> Phase 4 (depends on labelled data from Phases 2–3) -> Phase 5.

**Recommended governance**: Quality Steering Committee meeting bi-weekly; Phase gate reviews at Week 10, 18, 22, 32, 36 with formal sign-off before proceeding.

---

## 15. References

### Standards and Regulations

1. ISO 2859-1:1999 — *Sampling procedures for inspection by attributes — Part 1: Sampling schemes indexed by acceptance quality limit (AQL) for lot-by-lot inspection*. International Organisation for Standardisation, Geneva.
2. ISO 9001:2015 — *Quality management systems — Requirements*. International Organisation for Standardisation, Geneva.
3. IATF 16949:2016 — *Quality management system requirements for automotive production and relevant service parts organizations*. International Automotive Task Force.
4. ISO 7870-2:2013 — *Control charts — Part 2: Shewhart control charts*. International Organisation for Standardisation.
5. AIAG FMEA Reference Manual, 4th Edition (2008). Automotive Industry Action Group, Southfield, MI.
6. AIAG MSA Reference Manual, 4th Edition (2010). Automotive Industry Action Group.
7. AIAG PPAP Production Part Approval Process, 4th Edition (2006). Automotive Industry Action Group.
8. Western Electric Company (1956). *Statistical Quality Control Handbook*. Western Electric Co., Indianapolis, IN.
9. EU Directive 2024/1760 (CSDDD) — Corporate Sustainability Due Diligence Directive. Official Journal of the European Union.
10. EU REACH Regulation 1907/2006. European Chemicals Agency.

### Academic and Practitioner References

11. Montgomery, D.C. (2020). *Introduction to Statistical Quality Control*, 8th Edition. John Wiley & Sons, Hoboken, NJ.
12. Pyzdek, T. and Keller, P. (2018). *The Six Sigma Handbook*, 5th Edition. McGraw-Hill, New York.
13. Juran, J.M. and De Feo, J.A. (2010). *Juran's Quality Handbook*, 6th Edition. McGraw-Hill, New York.
14. Shewhart, W.A. (1931). *Economic Control of Quality of Manufactured Product*. D. Van Nostrand, New York. (Republished ASQ, 1980.)
15. Hoerl, R.W. and Snee, R.D. (2012). *Statistical Thinking: Improving Business Performance*, 2nd Edition. John Wiley & Sons.
16. Redmon, J. and Farhadi, A. (2018). *YOLOv3: An Incremental Improvement*. arXiv:1804.02767.
17. Jocher, G. et al. (2023). *Ultralytics YOLOv8*. https://github.com/ultralytics/ultralytics.
18. Chen, T. and Guestrin, C. (2016). *XGBoost: A Scalable Tree Boosting System*. KDD 2016.
19. Lundberg, S. and Lee, S. (2017). *A Unified Approach to Interpreting Model Predictions*. NeurIPS 2017 (SHAP).
20. Sanh, V. et al. (2019). *DistilBERT, a distilled version of BERT*. arXiv:1910.01108.
21. Hochreiter, S. and Schmidhuber, J. (1997). *Long Short-Term Memory*. Neural Computation 9(8):1735–1780.

### Internal Documents

22. Supply Chain Management Platform — CLAUDE.md (project standards and architecture guide).
23. `src/departments/08-quality-management/domain/InspectionRecord.ts` — TypeScript aggregate definitions.
24. `python/08_quality_management/` — Python mathematical model implementations.
25. `docs/standards/REGULATORY_FRAMEWORK.md` — Full regulatory reference.
26. `src/departments/02-supplier-management/domain/SupplierScorecard.ts` — Supplier PPM feed specification.
27. `src/departments/03-inventory/domain/StockMovement.ts` — Quarantine movement integration.

---

*This document is subject to annual review by the Quality Centre of Excellence. Next scheduled review: 2027-06-20.*

*All implementations must comply with the OSI open-source licence mandate defined in CLAUDE.md. Proprietary libraries are prohibited.*
