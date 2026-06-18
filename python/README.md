# Python — SCM Mathematical Models & ML

All mathematical models and ML algorithms for the Supply Chain Management system.

## Tech Stack (OSI open source only)

| Layer | Language | Purpose |
|-------|----------|---------|
| Domain logic | **TypeScript** | Aggregates, business rules, event sourcing (`src/departments/`) |
| Math & ML | **Python ≥ 3.11** | Algorithms, optimization, forecasting, ML models (`python/`) |

## Setup

```bash
pip install -r requirements.txt
```

## Run Tests

```bash
pytest python/ -v --cov=python --cov-report=term-missing
```

## Module Map

```
python/
├── shared/                    # Common types and utilities
│   ├── types.py               # Money, UOM, Incoterms (mirrors TypeScript)
│   └── utils.py               # Math helpers
├── 01_procurement/
│   └── kraljic.py             # Kraljic Matrix, RFQ scoring, TCO
├── 02_supplier_management/
│   └── scorecard.py           # OTD/OTIF/PPM/DPMO scorecard
├── 03_demand_planning/
│   ├── forecasting.py         # SMA, SES, Holt, Holt-Winters, metrics
│   └── safety_stock.py        # 4 SS methods, EOQ, ROP, XYZ
├── 04_supply_planning/
│   └── mrp.py                 # MRP netting, lot sizing (L4L/EOQ/PPB)
├── 05_inventory_management/
│   └── stock_balance.py       # Event replay, ABC/XYZ classification
├── 06_warehouse_management/
│   └── slotting.py            # FEFO, CPOI, ABC velocity, S-shape routing
├── 07_logistics_transportation/
│   └── logistics.py           # CO2, freight cost, Clarke-Wright VRP, OTD
├── 08_quality_management/
│   └── quality.py             # AQL ISO 2859-1, PPM, DPMO, Cp/Cpk, COPQ
├── 09_compliance_regulatory/
│   └── compliance.py          # CSDDD phases, UFLPA risk, REACH SVHC
├── 10_risk_management/
│   └── risk_model.py          # Risk matrix 5x5, EAL, HHI, Bullwhip, Monte Carlo
├── 11_finance_controlling/
│   └── finance.py             # 3-way match, C2C cycle, working capital
├── 12_sop_planning/
│   └── sop.py                 # Consensus forecast, RCCP, Monte Carlo scenarios
├── 13_order_management/
│   └── order_metrics.py       # OTIF, Perfect Order Rate, ATP, fill rate
└── 14_supplier_development/
    └── esg_scoring.py         # ESG E+S+G scoring, Scope 3, LTIFR, deforestation
```

## Key OSI Libraries

| Library | License | Use |
|---------|---------|-----|
| `numpy` | BSD-3 | Numerics, arrays |
| `scipy` | BSD-3 | Stats, optimization |
| `pandas` | BSD-3 | DataFrames, time series |
| `statsmodels` | BSD-3 | ETS, ARIMA, regression |
| `prophet` | MIT | Time-series forecasting |
| `scikit-learn` | BSD-3 | ML: classification, clustering, anomaly |
| `xgboost` | Apache-2.0 | Gradient boosting |
| `lightgbm` | MIT | Gradient boosting (fast) |
| `torch` | BSD-3 | Deep learning (LSTM, GNN) |
| `transformers` | Apache-2.0 | BERT/NLP (HuggingFace) |
| `stable-baselines3` | MIT | Reinforcement Learning |
| `ortools` | Apache-2.0 | VRP, scheduling |
| `networkx` | BSD-3 | Graph analysis |
| `simpy` | MIT | Discrete event simulation |
| `ultralytics` | AGPL-3.0 | YOLOv8 computer vision |
| `rasterio` | BSD-3 | Satellite imagery |
| `pulp` | MIT | Linear programming |

## Non-OSI Libraries — PROHIBITED

| Prohibited | OSI Replacement |
|-----------|----------------|
| AWS Textract | `pytesseract` + `pdfplumber` |
| Google Earth Engine (commercial) | `rasterio` + Copernicus Open API |
| AnyLogic (commercial) | `simpy` |
| Neo4j v4+ (SSPL) | `networkx` + `torch-geometric` |
| Elasticsearch v7.11+ (SSPL) | `opensearch-py` (Apache-2.0) |
| SageMaker (proprietary) | local PyTorch / TensorFlow |
