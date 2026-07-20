---
id: out-of-scope
title: "Out-of-Scope Register"
type: governance
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-governance }
  - { type: governed-by, target: knowledge-architecture }
---
# Out-of-Scope Register

> What was **deliberately excluded**, so it is not re-proposed forever and "missing" is
> distinguishable from "rejected". An exclusion is lifted only by a new decision.

## Exclusion register

| # | Excluded capability / tool | Why (short) | Decided by | Revisit trigger |
|---|---|---|---|---|
| 1 | AWS Textract | proprietary SaaS; OSI substitute `pytesseract` + `pdfplumber` | ADR-0002 | never (policy) |
| 2 | Google Earth Engine | commercial; substitute `rasterio` + Copernicus open API | ADR-0002 | never (policy) |
| 3 | AnyLogic | commercial; substitute `simpy` | ADR-0002 | never (policy) |
| 4 | Neo4j v4+ | SSPL (non-OSI); substitute `networkx` + `torch-geometric` | ADR-0002 | never (policy) |
| 5 | Elasticsearch ≥ 7.11 | SSPL; substitute `opensearch-py` | ADR-0002 | never (policy) |
| 6 | AWS SageMaker | proprietary SaaS; substitute local PyTorch/TensorFlow | ADR-0002 | never (policy) |
| 7 | Non-English content in repo artifacts | single working language | ADR-0003 | never (policy) |

> Product-scope exclusions (features deliberately not built) are added here as the owner
> decides them — none recorded yet.
