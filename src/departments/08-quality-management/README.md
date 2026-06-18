# 08 — Quality Management System (QMS)

## Overview

The Quality Management department owns incoming inspection, statistical sampling, non-conformance tracking, and lot disposition — fully aligned with **ISO 9001:2015** (§8.4 control of external providers, §8.5.2 identification and traceability, §8.6 release of products, §8.7 control of nonconforming outputs).

Every incoming lot is inspected using **ISO 2859-1 AQL (Acceptance Quality Limit)** statistical sampling. The system auto-selects sample size from the AQL_SAMPLE_SIZES table based on lot size, inspection level, and AQL percentage. Lots are automatically dispositioned as `ACCEPT`, `REJECT`, `CONDITIONAL`, or `SORT_100PCT` based on defects found vs. the acceptance number (Ac) and rejection number (Re). Rejected lots automatically generate a **Non-Conformance Record (NCR)** with supplier notification.

**DPMO** (Defects Per Million Opportunities) and **PPM** (Parts Per Million defective) are calculated for every inspection and aggregated into the **Supplier Scorecard** (30% quality weight: 60% PPM score, 40% NCR rate). Quality performance drives the **Kraljic matrix** classification and supplier development programs.

SCOR mapping: **Source** (quality gate for inbound) and **Enable** (supplier quality management).

---

## KPIs

| KPI | Definition | World-Class Target |
|-----|------------|--------------------|
| **PPM — Parts Per Million** | (Defective units / Total inspected) × 1,000,000 | < 500 PPM (automotive/IATF 16949) |
| **DPMO — Defects Per Million Opportunities** | (Total defects / (Units × Opportunities)) × 1,000,000 | < 3.4 DPMO (Six Sigma) |
| **First Pass Yield (FPY)** | Units passing first inspection / Total inspected | > 99.5% |
| **NCR Closure Rate** | NCRs closed within SLA / Total NCRs raised | > 95% within 30 days |
| **COPQ — Cost of Poor Quality** | Internal failure + External failure + Appraisal + Prevention | < 5% of revenue (world-class) |
| **Cpk — Process Capability Index** | min((USL−μ)/3σ, (μ−LSL)/3σ) | ≥ 1.33 (standard); ≥ 1.67 (critical) |

---

## Standards

| Standard | Scope | Implementation |
|----------|-------|----------------|
| **ISO 9001:2015** | QMS requirements: §8.4 external providers, §8.6 product release, §8.7 nonconformities | `InspectionRecord.ts` — all inspection flows |
| **ISO 2859-1:1999** | Sampling procedures by attributes — AQL tables | `AQL_SAMPLE_SIZES` table; `getAQLSampleSize()` |
| **IATF 16949:2016** | Automotive QMS — PPM targets, APQP, PPAP, 8D | `InspectionRecord.defectClassification`; NCR 8D fields |
| **GMP (21 CFR Part 211)** | Pharma Good Manufacturing Practice — lot release | `LotDisposition.ACCEPT` gated by QA signature |
| **ISO 3951-1** | Sampling by variables (for measurement data) | Supplement to attribute sampling for Cpk |
| **IPC-A-610** | Acceptability of electronic assemblies | `acceptanceCriteria` on inspection record |

---

## Domain Files

### `domain/InspectionRecord.ts`

Central aggregate for all incoming quality inspections.

**AQL_SAMPLE_SIZES Table (excerpt — Normal Inspection Level II):**

| Lot Size Range | Sample Size Code | Sample Size (n) | Ac | Re |
|---------------|-----------------|-----------------|----|----|
| 2–8 | A | 2 | 0 | 1 |
| 9–15 | B | 3 | 0 | 1 |
| 16–25 | C | 5 | 0 | 1 |
| 26–50 | D | 8 | 0 | 1 |
| 51–90 | E | 13 | 1 | 2 |
| 91–150 | F | 20 | 1 | 2 |
| 151–280 | G | 32 | 2 | 3 |
| 281–500 | H | 50 | 3 | 4 |
| 501–1,200 | J | 80 | 5 | 6 |
| 1,201–3,200 | K | 125 | 7 | 8 |
| 3,201–10,000 | L | 200 | 10 | 11 |
| 10,001–35,000 | M | 315 | 14 | 15 |
| 35,001–150,000 | N | 500 | 21 | 22 |

*AQL 1.0% shown. Adjust Ac/Re per AQL level (0.1%, 0.25%, 0.4%, 0.65%, 1.0%, 1.5%, 2.5%, 4.0%, 6.5%).*

**Key Functions:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `getAQLSampleSize()` | `(lotSize, inspectionLevel, aqlPercent) → { n, Ac, Re }` | Looks up ISO 2859-1 table |
| `calculateDPMO()` | `(defects, units, opportunitiesPerUnit) → number` | Returns DPMO value |
| `createInspectionRecord()` | `(input) → InspectionRecord` | Factory with auto-disposition + auto-NCR on reject |

**LotDisposition values:**

| Value | Meaning |
|-------|---------|
| `ACCEPT` | defects_found ≤ Ac → lot released to stock |
| `REJECT` | defects_found ≥ Re → lot returned to supplier; NCR auto-created |
| `CONDITIONAL` | Ac < defects_found < Re → escalation required; QA manager disposition |
| `SORT_100PCT` | Full 100% inspection ordered; individual unit accept/reject |

**DefectFound fields:** `defectType`, `defectClass` (CRITICAL/MAJOR/MINOR), `quantity`, `dimension` (for variable data), `imageRef` (photo evidence URI).

---

## Business Rules

1. **AQL sampling is mandatory** for all incoming lots above the minimum lot size threshold (≥ 9 units).
2. **Auto-disposition** — `createInspectionRecord()` automatically sets disposition based on defects_found vs. Ac/Re; no manual override without QA manager approval.
3. **Auto-NCR** — any `REJECT` disposition triggers an automatic Non-Conformance Record with supplier notification and CAPA (Corrective and Preventive Action) request.
4. **Lot hold** — rejected and CONDITIONAL lots are automatically placed on `QUARANTINE` status in the inventory module; WMS cannot allocate quarantined lots.
5. **CRITICAL defects** — a single CRITICAL defect (safety, regulatory) results in immediate `REJECT` regardless of Ac number (zero-tolerance rule).
6. **Traceability** — every `InspectionRecord` links to: `supplierId`, `purchaseOrderId`, `lotId`, `inspectorId`, `warehouseLocationId`.
7. **Soft-delete** — NCR records are never deleted; closed NCRs retain full audit history.
8. **Document retention** — inspection records retained minimum **10 years** (IATF 16949); **5 years** minimum (ISO 9001:2015 §7.5.3).

---

## Modelos Matemáticos Aplicados

### 1. AQL Sampling — ISO 2859-1

Statistical acceptance sampling by attributes:

```
Step 1: Determine lot_size N
Step 2: Look up sample_size_code from ISO 2859-1 Table I (based on N and Inspection Level II)
Step 3: Look up n (sample size), Ac (acceptance number), Re (rejection number)
        from Table II-A at the specified AQL%

Decision rule:
    IF defects_found ≤ Ac  → ACCEPT lot
    IF defects_found ≥ Re  → REJECT lot
    IF Ac < defects_found < Re → CONDITIONAL (tightened inspection or 100% sort)

Switching rules:
    Normal → Tightened: 2 of 5 consecutive lots rejected
    Tightened → Normal: 5 consecutive lots accepted on tightened
    Normal → Reduced: 10 consecutive lots accepted + production stable
```

> Reference: ISO 2859-1:1999 — *Sampling procedures for inspection by attributes — Part 1: Sampling schemes indexed by acceptance quality limit (AQL) for lot-by-lot inspection*.

---

### 2. PPM — Parts Per Million

```
PPM = (Defective_Units / Total_Units_Inspected) × 1,000,000

Example: 3 defective in 10,000 inspected → PPM = 300
```

| Industry | PPM Benchmark |
|----------|--------------|
| Automotive (IATF 16949) | < 500 PPM |
| Food & Beverage | < 1,000 PPM |
| Consumer Electronics | < 1,000 PPM |
| Aerospace (AS9100) | < 50 PPM |
| Six Sigma (4.5σ with shift) | 3.4 PPM |
| Medical Devices (ISO 13485) | Near-zero (validated process) |

> Reference: Pyzdek, T. & Keller, P. — *The Six Sigma Handbook*, 4th Ed. (McGraw-Hill, 2014).

---

### 3. DPMO — Defects Per Million Opportunities

DPMO accounts for multiple defect opportunities per unit, enabling cross-product comparison:

```
DPMO = (Total_Defects / (Units_Inspected × Opportunities_per_Unit)) × 1,000,000

Six Sigma Level ↔ DPMO conversion (with 1.5σ mean shift):
    6σ = 3.4 DPMO
    5σ = 233 DPMO
    4σ = 6,210 DPMO
    3σ = 66,807 DPMO
    2σ = 308,537 DPMO
```

Example: 200 defects found inspecting 1,000 circuit boards, each with 50 solder joints:
```
DPMO = (200 / (1,000 × 50)) × 1,000,000 = 4,000 DPMO ≈ 4.1σ
```

> Reference: Harry, M. & Schroeder, R. — *Six Sigma: The Breakthrough Management Strategy* (Doubleday, 2000).

---

### 4. Cp / Cpk — Process Capability Indices

For variable (measurement) data, process capability quantifies how well the process fits within specification limits:

```
Cp = (USL − LSL) / (6σ)        [potential capability — centered process]

Cpk = min(
    (USL − μ) / (3σ),           [upper capability]
    (μ − LSL) / (3σ)            [lower capability]
)

where:
    USL = Upper Specification Limit
    LSL = Lower Specification Limit
    μ   = process mean (X-bar)
    σ   = process standard deviation (from R-chart or s-chart)
```

| Cpk | Performance | Recommended Use |
|-----|-------------|----------------|
| < 1.00 | Incapable | Process must be improved |
| 1.00–1.33 | Marginal | 3σ–4σ; monitor closely |
| ≥ 1.33 | Capable | 4σ; standard requirement (ISO 9001) |
| ≥ 1.67 | Highly capable | 5σ; automotive/aerospace |
| ≥ 2.00 | Six Sigma | Required for safety-critical parts |

> Reference: Montgomery, D.C. — *Introduction to Statistical Quality Control*, 7th Ed. (Wiley, 2013), Ch. 7.

---

### 5. COPQ — Cost of Poor Quality

```
COPQ = Internal_Failure_Cost + External_Failure_Cost + Appraisal_Cost + Prevention_Cost

Internal Failure:   rework, scrap, re-inspection, downtime
External Failure:   warranty claims, returns, recalls, customer penalties (OTD deductions)
Appraisal:          incoming inspection labor, equipment calibration, AQL sampling
Prevention:         supplier audits, APQP, training, process validation

COPQ as % of Revenue benchmark:
    World-class:   < 5%
    Good:          5–10%
    Industry avg:  10–20%
    Poor:          > 20%
```

COPQ provides the financial justification for quality investment: cost to prevent defects is always less than cost of failure.

> Reference: Juran, J.M. & Godfrey, A.B. — *Juran's Quality Handbook*, 5th Ed. (McGraw-Hill, 1999).

---

### 6. First Pass Yield (FPY) and Rolled Throughput Yield (RTY)

```
FPY = Units_passing_inspection_first_time / Total_units_inspected

For a multi-step process:
RTY = FPY_step1 × FPY_step2 × ... × FPY_stepN

Example (5-step process, each at 99% FPY):
    RTY = 0.99^5 = 0.951 = 95.1%
    Even though each step is 99%, the end-to-end yield is only 95.1%
```

RTY reveals the hidden factory — the rework and sorting occurring at each process step that FPY of the final step masks.

> Reference: Pyzdek, T. & Keller, P. — *The Six Sigma Handbook*, 4th Ed. (McGraw-Hill, 2014), Ch. 18.

---

## Modelos de Machine Learning Recomendados

### 1. Computer Vision / CNN para Inspección Visual Automatizada

**Problem:** Manual visual inspection is the most expensive and least consistent inspection method — inspector fatigue causes 10–30% miss rate after 2 hours.

**Architecture:** YOLOv8 or ResNet-50 trained on labeled defect images
- **Input:** High-resolution images captured on inspection line (multiple angles)
- **Defect classes:** scratch, crack, dimension_deviation, color_mismatch, contamination, missing_component
- **Output:** Defect type + bounding box + confidence score
- **Disposition trigger:** If confidence > threshold → auto-raise `DefectFound`; otherwise route to human inspector

**Training requirements:** Minimum 1,000 labeled images per defect class. Active learning loop — model-flagged uncertain cases go to human labeler.
**Accuracy benchmark:** >99% detection accuracy in automotive stamped parts applications.

**Libraries:** Ultralytics YOLOv8 (`ultralytics`), TensorFlow (`tf.keras.applications.ResNet50`).

> Reference: LeCun, Y., Bottou, L., Bengio, Y. & Haffner, P. — *Gradient-based learning applied to document recognition* (Proceedings of the IEEE, 86(11), 1998).

---

### 2. Gaussian Process para Control Estadístico de Procesos

**Problem:** Traditional SPC (Shewhart control charts) assumes stationarity and independence — both violated in modern automated production with drift and autocorrelation.

**Architecture:** Gaussian Process Regression (GPR) for online SPC
- **Input:** Time-ordered quality measurements (dimension, weight, torque)
- **GP prior:** Squared exponential (RBF) kernel captures smooth drift; Matérn 5/2 for rougher processes
- **Output:** Posterior mean μ(t) + uncertainty bounds (1.96σ)
- **Control rule:** Signal if observation falls outside posterior prediction interval (Bayesian Western Electric rule)

**Benefit:** Provides uncertainty-aware process monitoring; naturally handles autocorrelation and non-stationarity.

**Libraries:** GPy (`GPy.models.GPRegression`), scikit-learn (`GaussianProcessRegressor`).

---

### 3. One-Class SVM / Autoencoder para Pre-Screening de Lotes

**Problem:** AQL sampling has inherent statistical risk (producer's risk α, consumer's risk β). High-risk lots from known underperforming suppliers should receive intensified inspection before AQL sampling.

**Architecture:** One-Class SVM trained only on `ACCEPT` lot feature vectors
- **Features per lot:** supplier_id (encoded), material_code, shipment_origin, declared_quantity, invoice_value_vs_PO_variance, days_since_last_inspection, supplier_PPM_rolling_90d
- **Output:** Anomaly score — high score → pre-classify as HIGH_RISK → tighten inspection level (Level III AQL) before sampling
- **Alternative:** Undercomplete autoencoder (same input; high reconstruction error = anomalous lot)

**Benefit:** Concentrates inspection resources on highest-risk lots; reduces consumer's risk β.

**Libraries:** scikit-learn (`OneClassSVM`, `svm.OneClassSVM`), PyTorch (autoencoder).

---

### 4. Random Forest para Root Cause Analysis

**Problem:** When defect rates spike, root cause analysis (RCA) traditionally relies on fishbone diagrams and manual data review — slow and subjective.

**Architecture:** Random Forest classifier for automated RCA
- **Features:** supplier_id, material_batch, production_shift, machine_id, operator_id, ambient_temperature, humidity, incoming_inspection_date, transport_mode, transit_time_days
- **Target:** defect_type (multiclass)
- **Output:** Feature importance ranking → identifies the strongest predictors of each defect type
- **SHAP values:** Provide unit-level explanations ("this lot was rejected primarily because: supplier = XYZ + transit_time > 8 days")

**Benefit:** Reduces RCA cycle time from weeks to hours; removes confirmation bias.

**Libraries:** scikit-learn (`RandomForestClassifier`), SHAP (`shap.TreeExplainer`).

---

### 5. LSTM para Predicción de Calidad en Proceso (In-Process Quality)

**Problem:** Inspection at end-of-line discovers defects too late — rework cost is 10× prevention cost. In-process sensors can predict quality outcomes.

**Architecture:** LSTM reading multivariate sensor time series
- **Input:** Rolling window of sensor readings per production unit: temperature(t), pressure(t), vibration_rms(t), cycle_time(t), tool_wear_index(t)
- **Sequence length:** Last 60 sensor readings (e.g., 1 reading/second = last 60 seconds of production cycle)
- **Output:** P(defect) for this unit; if P > threshold → flag for immediate inspection or ejection

**Integration:** Real-time inference via ONNX Runtime deployed at edge PLC/OPC-UA gateway. InfluxDB for time-series sensor storage.

**Benefit:** Shift quality control from detection to prevention; reduces scrap and rework by 20–40%.

**Libraries:** TensorFlow/Keras (`LSTM`, `Dense`), ONNX Runtime (`onnxruntime`), InfluxDB client.

---

## References

1. Montgomery, D.C. — *Introduction to Statistical Quality Control*, 7th Ed. (Wiley, 2013)
2. Pyzdek, T. & Keller, P. — *The Six Sigma Handbook*, 4th Ed. (McGraw-Hill, 2014)
3. Juran, J.M. & Godfrey, A.B. — *Juran's Quality Handbook*, 5th Ed. (McGraw-Hill, 1999)
4. ISO 2859-1:1999 — *Sampling procedures for inspection by attributes — Part 1*
5. ISO 9001:2015 — *Quality management systems — Requirements*
6. IATF 16949:2016 — *Quality management system requirements for automotive production*
7. Harry, M. & Schroeder, R. — *Six Sigma: The Breakthrough Management Strategy* (Doubleday, 2000)
8. LeCun, Y. et al. — *Gradient-based learning applied to document recognition* (IEEE, 1998)
9. Rasmussen, C.E. & Williams, C.K.I. — *Gaussian Processes for Machine Learning* (MIT Press, 2006)
10. Lundberg, S.M. & Lee, S.I. — *A Unified Approach to Interpreting Model Predictions* (NeurIPS, 2017)
