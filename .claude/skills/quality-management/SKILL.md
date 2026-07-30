---
description: >
  Quality management domain expertise for Department 08. Use when reviewing incoming
  inspection (AQL), NCR lifecycle, DPMO, SPC, AQL sampling plans, or the concept nodes and rules of department 08 (quality-management).
---

# Quality Management — Department 08 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Enable (E4 — Manage Quality); Source (S1.3 Verify Product)

**AQL Sampling** (ISO 2859-1:1999 / ANSI/ASQ Z1.4)
- AQL = Acceptable Quality Level: max defective % considered acceptable
- Inspection levels: I (reduced), II (normal, default), III (tightened)
- Switching rules: 2 of 5 lots rejected → tightened; 5 consecutive accepted → reduced
- Common AQL values: 0.65% (critical); 1.0% (major); 4.0% (minor)

**AQL Sample Size Calculation**
```
1. Determine lot size → table mapping → sample size code letter (A–R)
2. Cross-reference code letter with AQL → sample size n, Acceptance number Ac, Rejection number Re
3. Inspect n units; count defectives d
4. Accept if d ≤ Ac; Reject if d ≥ Re
```

**Defect Classification**
| Class | Definition | AQL | Action on reject |
|-------|-----------|-----|------------------|
| Critical | Safety or regulatory risk | zero — not a project choice; the obligation is external | 100% inspection + hold |
| Major | Reduces usability for its purpose | project-chosen | Sort or return to supplier |
| Minor | Cosmetic, or deviates without affecting use | project-chosen, looser than Major | Concession or sort |

The **classes and their ordering** are standard practice, and once an AQL is chosen the
**sampling plan follows ISO 2859-1** mechanically (sample size code letter → sample size →
accept/reject numbers). The **AQL level itself is a term of the customer contract**, so this
context supplies none.

**NCR lifecycle — the stages are law, the state names are not.** ISO 9001:2015 §10.2 fixes the
*obligations*: react to the non-conformity, evaluate the need to eliminate its cause, implement
action, and **review the effectiveness** of what was done (QMS-R8 — a closed NCR whose
effectiveness was never verified is not closed). A chain such as
`OPEN → UNDER_INVESTIGATION → CORRECTIVE_ACTION_REQUIRED → ACTION_IN_PROGRESS → VERIFICATION → CLOSED`
is one reasonable encoding of those obligations; the names, the count and the transitions are the
project's. What must not be dropped is the verification step, which is the one teams skip.

**Quality metrics (ISO 9001:2015; APICS CPIM)**

**Metrics — definitions, not levels.** A skill states what a metric measures and what
constrains the answer; the level a project must clear is that project's decision (ADR-0037,
and the inclusion test in `CLAUDE.md`). The right-hand column names the constraint so the
question can be asked properly, and stops.

| Metric | Formula | What constrains the level |
|---|---|---|
| PPM | Defective parts / Total × 1,000,000 | **The customer contract.** An automotive PPM expectation is one industry's contracted requirement, not a standard — and it is the customer's number, so it is an input to the project, not a choice it makes freely. |
| DPMO | Defects / (Units × Opportunities) × 1,000,000 | **3.4 DPMO is definitional, not aspirational:** "six sigma" *means* that rate at 1.5σ shift. Cite it as the definition of the term (CPT-0053) and never as a bar this context sets. Counting "opportunities" consistently matters more than the level. |
| First-pass yield | Units passing first inspection / Total × 100 | Process capability, and where inspection sits. Moving the inspection point changes the number without changing the process. |
| Supplier defect rate | Defective units / Total received × 100 | The supply agreement, and the AQL level the project chose — **ISO 2859-1 fixes the sampling plan; the AQL is the project's decision** (SCM-R* §Project decisions). |
| Cost of poor quality | Prevention + Appraisal + Internal + External failure | What the project counts in each Juran category. The wide ranges quoted in the quality literature are observations of samples, not a bar (CPT-0054). |
| NCR closure rate | NCRs closed within N days / Total × 100 | Both the window and the rate are the project's escalation policy. ISO 9001:2015 §10.2 requires corrective action to be *effective* (QMS-R8) and fixes no clock. |

**Cost of Quality (PAF Model — Feigenbaum 1951)**
```
COPQ = Prevention Costs + Appraisal Costs + Internal Failure Costs + External Failure Costs
Target: Prevention >> Appraisal >> Internal >> External (shift left)
```

## Data Analytics

**Incoming Inspection Dashboard**
```sql
SELECT supplier_id, material_id,
       COUNT(*) AS inspection_lots,
       SUM(defective_units) AS total_defects,
       SUM(inspected_units) AS total_inspected,
       ROUND(SUM(defective_units)::float / NULLIF(SUM(inspected_units), 0) * 1e6, 0) AS ppm,
       SUM(CASE WHEN lot_disposition = 'ACCEPTED' THEN 1 ELSE 0 END)::float
         / NULLIF(COUNT(*), 0) * 100 AS acceptance_rate_pct
FROM incoming_inspections
WHERE inspection_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY supplier_id, material_id ORDER BY ppm DESC;
```

**SPC — Statistical Process Control (Shewhart)**
```sql
-- X-bar chart control limits (±3σ)
SELECT process_id,
       AVG(measurement) AS x_bar,
       STDDEV(measurement) AS sigma,
       AVG(measurement) + 3 * STDDEV(measurement) AS ucl,
       AVG(measurement) - 3 * STDDEV(measurement) AS lcl
FROM process_measurements
WHERE measurement_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY process_id;
```

**Pareto on Defect Types**
```sql
SELECT defect_code, defect_description,
       COUNT(*) AS occurrences,
       ROUND(COUNT(*)::float / SUM(COUNT(*)) OVER () * 100, 2) AS pct,
       ROUND(SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC)
             / SUM(COUNT(*)) OVER () * 100, 2) AS cumulative_pct
FROM ncr_defects GROUP BY defect_code, defect_description
ORDER BY occurrences DESC;
```

## Data Science

**Six Sigma DMAIC Framework**
| Phase | Activity | Statistical Tool |
|-------|---------|-----------------|
| Define | Project charter, CTQ tree | — |
| Measure | MSA, Gauge R&R | ANOVA, variance components |
| Analyze | Root cause, fishbone | Regression, hypothesis tests |
| Improve | DOE, pilot | ANOVA, t-test |
| Control | Control charts, SPC | X-bar/R, CUSUM, EWMA |

**Measurement System Analysis (Gauge R&R)**
```
%GRR = (GRR_variance / Total_variance) × 100
the bands that separate acceptable from marginal are a project decision
```

**Process Capability Indices**
```
Cp = (USL − LSL) / (6σ)         — potential capability
Cpk = min[(USL−μ)/3σ, (μ−LSL)/3σ] — actual capability
Cpk ≥ 1.33: capable; Cpk ≥ 1.67: highly capable (automotive)
```

## Machine Learning

**Defect Detection (Computer Vision — YOLOv8)**
```python
from ultralytics import YOLO
import cv2

def detect_surface_defects(image_path: str, model_path: str = 'yolov8n.pt') -> list[dict]:
    """
    Real-time surface defect detection on production line using YOLOv8.
    Classes: scratch, dent, contamination, discoloration, dimension_error.
    Ref: Ultralytics YOLOv8 (AGPL-3.0); Redmon et al. (2016), CVPR.
    """
    model = YOLO(model_path)
    results = model(image_path)
    defects = []
    for r in results:
        for box in r.boxes:
            defects.append({
                'class': model.names[int(box.cls)],
                'confidence': float(box.conf),
                'bbox': box.xyxy[0].tolist()
            })
    return defects
```

**Quality Prediction (Inline SPC)**
```python
from sklearn.svm import OneClassSVM
import numpy as np

def detect_process_anomaly(measurements: np.ndarray,
                            contamination: float = 0.05) -> np.ndarray:
    """
    One-Class SVM for detecting out-of-control process conditions.
    Input: measurements matrix (n_samples × n_features).
    Output: boolean array (True = anomaly = out-of-control).
    Ref: Schölkopf et al. (1999), Neural Computation 13(7).
    License: scikit-learn BSD-3.
    """
    clf = OneClassSVM(nu=contamination, kernel='rbf', gamma='scale')
    clf.fit(measurements)
    return clf.predict(measurements) == -1
```

**AQL Sampling Plan (Python)**
```python
import numpy as np
from scipy.stats import binom

def compute_aql_sample_size(lot_size: int, aql: float = 1.0,
                             inspection_level: str = 'II') -> dict:
    """
    ISO 2859-1 AQL sampling plan.
    Returns sample size n, acceptance number Ac, rejection number Re.
    Ref: ISO 2859-1:1999 (ANSI/ASQ Z1.4-2003 equivalent).
    """
    # Simplified: use probability-based approach for illustration
    # In production, use lookup tables from ISO 2859-1
    n = max(13, int(np.ceil(np.log(0.10) / np.log(1 - aql/100))))
    ac = int(np.floor(n * aql / 100))
    return {'sample_size': n, 'acceptance_number': ac, 'rejection_number': ac + 1}
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `scipy.stats` | Hypothesis tests, Cp/Cpk, normality | BSD-3 |
| `statsmodels` | ANOVA, regression, SPC charts | BSD-3 |
| `numpy` | PPM, DPMO calculations | BSD-3 |
| `pandas` | Inspection DataFrames, Pareto | BSD-3 |
| `scikit-learn` | Anomaly detection, classification | BSD-3 |
| `ultralytics` | YOLOv8 visual defect detection | AGPL-3.0 |
| `opencv-python` | Image preprocessing for inspection | Apache-2.0 |
| `pytesseract` | OCR for inspection report extraction | Apache-2.0 |

**Process Capability (Python)**
```python
import numpy as np
from scipy.stats import norm

def process_capability(measurements: np.ndarray, usl: float, lsl: float) -> dict:
    """
    Compute Cp, Cpk, sigma level, and PPM out-of-spec.
    Ref: Montgomery, D.C. (2019). Introduction to Statistical Quality Control, 8th ed. Wiley.
    """
    mu, sigma = np.mean(measurements), np.std(measurements, ddof=1)
    cp = (usl - lsl) / (6 * sigma)
    cpk = min((usl - mu) / (3 * sigma), (mu - lsl) / (3 * sigma))
    sigma_level = cpk * 3
    ppm_defective = (1 - norm.cdf(usl, mu, sigma) + norm.cdf(lsl, mu, sigma)) * 1e6
    return {'cp': round(cp, 4), 'cpk': round(cpk, 4),
            'sigma_level': round(sigma_level, 2), 'ppm_defective': round(ppm_defective, 0)}
```

## TypeScript

**Domain Objects**
- `domain/InspectionRecord.ts` — Inspection aggregate; AQL parameters; lot disposition
- `domain/NCR.ts` — NCR lifecycle; defect classification; corrective action
- `reports/QualityDashboard.ts` — PPM, DPMO, FPY, COPQ calculations
- `services/QualityService.ts` — Sampling plan lookup; SPC trigger; NCR creation

**AQL Disposition**
```typescript
type LotDisposition = 'ACCEPTED' | 'REJECTED' | 'CONDITIONAL_ACCEPT' | 'HOLD_FOR_REVIEW';

function disposeLot(defectiveCount: number, sampleSize: number,
                    acceptanceNumber: number): LotDisposition {
  if (defectiveCount <= acceptanceNumber) return 'ACCEPTED';
  if (defectiveCount <= acceptanceNumber + 2) return 'CONDITIONAL_ACCEPT';
  return 'REJECTED';
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Inspection records, NCR events |
| Apache Superset | Apache-2.0 | SPC charts, PPM dashboards |
| `ultralytics` | AGPL-3.0 | Visual defect detection |
| `opencv-python` | Apache-2.0 | Image processing pipeline |
| OpenSearch | Apache-2.0 | NCR document search |

**References**
- ISO 2859-1:1999 — Sampling procedures for inspection by attributes
- ISO 9001:2015 §8.4–8.7 — Quality control, traceability, nonconforming outputs
- Montgomery, D.C. (2019). *Introduction to Statistical Quality Control*, 8th ed. Wiley.
- Feigenbaum, A.V. (1951). *Total Quality Control*. McGraw-Hill.
- APICS/ASCM Dictionary, 17th ed. (2024) — *AQL*, *PPM*, *DPMO*, *NCR*, *COPQ*
- APICS CPIM 9.0 — Module 6: Quality Management
