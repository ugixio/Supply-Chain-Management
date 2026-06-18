# 08 — Quality Management (QMS / ISO 9001:2015)

## Overview

Sistema de gestión de calidad alineado con ISO 9001:2015. Responsable de la inspección de entrada (AQL ISO 2859-1), cálculo de PPM/DPMO, disposición de lotes, Registros de No-Conformidad (NCR), y métricas de capacidad de proceso (Cp/Cpk). Mide el costo de la mala calidad (COPQ) y las métricas Six Sigma.

---

## KPIs del Departamento

| KPI | Benchmark | Ref. |
|-----|-----------|------|
| PPM | < 500 (automotive IATF 16949) | ISO 9001 |
| PPM | < 1,000 (food/FMCG) | GMP |
| DPMO | < 3.4 (Six Sigma 6σ) | Pyzdek (2014) |
| First Pass Yield (FPY) | > 99% | Juran (1999) |
| Cpk | ≥ 1.33 (4σ) normal; ≥ 1.67 (5σ) crítico | Montgomery (2013) |
| NCR Closure Rate (días) | < 30 días | ISO 9001:2015 §8.7 |
| COPQ / Revenue % | < 5% | Juran (1999) |

---

## Estándares

| Estándar | Alcance |
|----------|---------|
| ISO 9001:2015 | §8.4 proveedores, §8.5.2 trazabilidad, §8.6 liberación, §8.7 no conformidad |
| ISO 2859-1 | AQL sampling — Normal Inspection Level II |
| IATF 16949:2016 | Automoción: PPAP, FMEA, SPC, MSA |
| ISO/IEC 17025 | Laboratorios de calibración |
| GMP (FDA 21 CFR) | Farmacéutica / alimentos |

---

## Archivos del Departamento

| Archivo | Responsabilidad |
|---------|----------------|
| `domain/InspectionRecord.ts` | AQL_SAMPLE_SIZES table, getAQLSampleSize(), DefectFound, LotDisposition (ACCEPT/REJECT/CONDITIONAL/SORT_100PCT), calculateDPMO(), createInspectionRecord() |

---

## Modelos Matemáticos Aplicados

### 1. AQL Sampling — ISO 2859-1

```
Paso 1: Determinar letra de código de tamaño (por lote y nivel de inspección)
Paso 2: n = sample_size(lot_size, InspectionLevel, AQL)
Paso 3: Inspeccionar n unidades
Paso 4: if defects_found ≤ Ac → ACCEPT
        if defects_found ≥ Re → REJECT
        (Ac = acceptance number, Re = rejection number)

Normal Inspection Level II es el estándar por defecto.
AQL típicos: 0.65% (críticos), 1.0% (mayores), 2.5% (menores)
```

Ref: ISO 2859-1:1999.

### 2. PPM — Parts Per Million

```
PPM = (Defective_units / Total_units_inspected) × 1,000,000

Benchmarks:
  Six Sigma (6σ):  3.4 PPM
  Automotive:    < 500 PPM  (IATF 16949)
  Food/FMCG:    < 1,000 PPM
  General mfg:  < 5,000 PPM
```

### 3. DPMO — Defects Per Million Opportunities

```
DPMO = (Total_defects / (Units_inspected × Opportunities_per_unit)) × 1,000,000

Sigma level vs DPMO:
  3σ = 66,807 DPMO
  4σ =  6,210 DPMO
  5σ =    233 DPMO
  6σ =    3.4 DPMO
```

Ref: Pyzdek & Keller (2014) *The Six Sigma Handbook*.

### 4. Cp / Cpk — Capacidad de Proceso

```
Cp  = (USL − LSL) / (6σ_process)         [potencial]
Cpk = min((USL−μ)/3σ, (μ−LSL)/3σ)       [real, considera centrado]

Objetivo:
  Cpk ≥ 1.33  → proceso capaz (4σ)
  Cpk ≥ 1.67  → proceso capaz (5σ) para dimensiones críticas
  Cpk < 1.00  → proceso NO capaz → acción correctiva
```

Ref: Montgomery (2013) *Introduction to Statistical Quality Control*, 7th Ed.

### 5. COPQ — Costo de la Mala Calidad

```
COPQ = Prevention_costs + Appraisal_costs + Internal_failure + External_failure

Típico: 5-30% de los ingresos
Optimización: invertir en prevención para reducir fallas externas
```

Ref: Juran & Godfrey (1999) *Juran's Quality Handbook*.

### 6. First Pass Yield y Rolled Throughput Yield

```
FPY_i  = Units_passing_inspection_i / Total_units_i

RTY    = Π FPY_i  (producto de FPY en todos los pasos del proceso)

Ejemplo: 3 pasos con FPY 99%, 98%, 97% → RTY = 0.99×0.98×0.97 = 94.1%
```

---

## Modelos de Machine Learning Recomendados

### 1. YOLOv8 — Inspección Visual Automatizada

**Tipo**: Detección de objetos (Computer Vision)  
**Funcionamiento**: Modelo YOLOv8 entrenado con imágenes etiquetadas de defectos (scratch, crack, dimensión fuera de tolerancia, contaminación). Desplegado en línea de producción o estación de entrada. Clasifica defectos en tiempo real a velocidad de línea.  
**Output**: `{unit_id, defect_type, confidence, bounding_box}`. Dispara REJECT automático.  
**Precisión**: > 99% en automoción (comparable a inspector humano experto).  
**Librería**: Ultralytics YOLOv8, OpenCV  
**Ref**: Redmon et al. (2016) CVPR; LeCun, Bengio & Hinton (2015) Nature.

### 2. Gaussian Process — SPC Bayesiano

**Tipo**: Regresión probabilística bayesiana  
**Funcionamiento**: Aprende distribución del proceso (media y varianza) como función del tiempo. Detecta shifts (reglas Western Electric) y predice deriva de Cpk. Proporciona intervalos de confianza, reduciendo falsas alarmas vs. Shewhart clásico.  
**Output**: `{mean_estimate, variance_estimate, drift_probability, action_required}`  
**Librería**: GPy, `sklearn.gaussian_process`  
**Ref**: Rasmussen & Williams (2006) *Gaussian Processes for Machine Learning*, MIT Press.

### 3. One-Class SVM / Autoencoder — Pre-Screening de Lotes

**Tipo**: Detección de anomalías  
**Funcionamiento**: Entrenado exclusivamente con lotes ACCEPT históricos. Alta puntuación de anomalía = lote con características atípicas → inspección AQL intensificada antes de liberar.  
**Output**: `anomaly_score` por lote. Priorización del plan de inspección.  
**Librería**: scikit-learn `OneClassSVM`, PyTorch Autoencoder  
**Ref**: Schölkopf et al. (2001) *Neural Computation*.

### 4. Random Forest — Root Cause Analysis

**Tipo**: Clasificación + importancia de features  
**Funcionamiento**: Features: proveedor, material, turno, máquina, temperatura, operario, mes. Target: tipo de defecto. Feature importance = probable causa raíz. Reemplaza análisis manual de diagrama Ishikawa para defectos recurrentes.  
**Output**: ranking de causas raíz con probabilidad; acción correctiva sugerida.  
**Librería**: scikit-learn `RandomForestClassifier`  
**Ref**: Breiman (2001) *Machine Learning* 45(1): 5-32.

### 5. LSTM + Sensores IoT — Calidad Predictiva en Proceso

**Tipo**: Serie temporal supervisada  
**Funcionamiento**: Lee datos de sensores (temperatura, presión, vibración, torque) de equipos de producción. Predice la probabilidad de defecto en la pieza actual antes de llegar a inspección. Permite intervención inmediata.  
**Output**: `P(defect)` en tiempo real. Alarma si > umbral configurable.  
**Librería**: TensorFlow, InfluxDB (almacenamiento IoT), Grafana (dashboard)  
**Ref**: Lee, Kao & Yang (2014) *Manufacturing Letters*.

---

## Referencias

- Montgomery, D.C. (2013) *Introduction to Statistical Quality Control*, 7th Ed. Wiley
- Pyzdek, T. & Keller, P. (2014) *The Six Sigma Handbook*, 4th Ed. McGraw-Hill
- Juran, J.M. & Godfrey, A.B. (1999) *Juran's Quality Handbook*, 5th Ed. McGraw-Hill
- ISO 2859-1:1999 *Sampling procedures for inspection by attributes*
- ISO 9001:2015 *Quality management systems — Requirements*
