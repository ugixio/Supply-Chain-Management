# Supplier Development & ESG / Sustainability — Implementation Guide

**Department:** 14 — Supplier Development & ESG / Sustainability
**Standard:** SCOR-DS Enable | ISO 20400:2017 | ISO 14001:2015 | GRI Standards 2021
**Regulatory Alignment:** CSRD (EU 2022/2464) | EUDR (EU 2023/1115) | GHG Protocol | SBTi
**Classification:** INTERNAL — RESTRICTED
**Version:** 1.0.0
**Date:** 2026-06-20

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Prerequisites and Dependencies](#2-prerequisites-and-dependencies)
3. [Phase 0: Assessment and AS-IS Analysis](#3-phase-0-assessment-and-as-is-analysis)
4. [Phase 1: Foundation and Master Data](#4-phase-1-foundation-and-master-data)
5. [Phase 2: Process Standardisation and Core Analytics](#5-phase-2-process-standardisation-and-core-analytics)
6. [Phase 3: Mathematical Models](#6-phase-3-mathematical-models)
7. [Phase 4: ML/AI Pipeline](#7-phase-4-mlai-pipeline)
8. [Phase 5: Integration and Automation](#8-phase-5-integration-and-automation)
9. [Phase 6: Continuous Improvement](#9-phase-6-continuous-improvement)
10. [Technology Stack and Architecture](#10-technology-stack-and-architecture)
11. [Change Management and Training](#11-change-management-and-training)
12. [Implementation KPIs](#12-implementation-kpis)
13. [Risk and Mitigation](#13-risk-and-mitigation)
14. [Timeline Summary](#14-timeline-summary)
15. [References](#15-references)

---

## 1. Executive Summary

Supplier Development and ESG (Environmental, Social, and Governance) Sustainability is no longer a reporting obligation that sits adjacent to core supply chain operations — it is a primary value-creation lever, a risk-mitigation discipline, and an increasingly regulated domain with material financial consequences. The EU Corporate Sustainability Reporting Directive (CSRD, Directive 2022/2464/EU) imposes mandatory double-materiality disclosure from FY 2024 onward for large undertakings, with Tier 1 suppliers implicated directly through ESRS S2 (Own Workforce in Value Chain). The EU Deforestation Regulation (EUDR, Regulation 2023/1115/EU) places GPS-validated plot-level due diligence obligations on seven commodity categories. Science-Based Targets initiative (SBTi) Corporate Net-Zero Standard requires Scope 3 Category 1 (purchased goods and services) reduction of at least 67.4% from a 2018–2021 baseline by 2030 for near-term targets.

This implementation guide provides a senior-practitioner-grade blueprint for deploying a fully integrated Supplier Development and ESG module within the existing Supply Chain Management platform. The approach follows a phased delivery model spanning 18 months, beginning with master data governance and concluding with a closed-loop continuous improvement engine driven by graph neural networks, satellite machine learning, and large-language-model ESG report analysis.

The business case for this investment rests on four pillars:

- **Regulatory compliance cost avoidance:** CSRD non-compliance penalties under national transposition laws can reach 5% of global net annual turnover. EUDR violations include fines of at least 4% of EU turnover and mandatory product withdrawal.
- **Procurement cost reduction:** Supplier development programmes that close capability gaps deliver an average 6–9% total cost of ownership (TCO) reduction over a 36-month horizon (Gartner SCM Research, 2024).
- **ESG risk-adjusted WACC:** S&P Global data demonstrates that companies with ESG supplier screening in the top quartile carry 38–54 basis points lower weighted average cost of capital than sector peers.
- **Market access:** Major retailers (Walmart, Carrefour, Tesco) and OEMs (BMW, Apple, Unilever) now gate supplier onboarding on minimum EcoVadis Silver rating (score >= 45) and validated Scope 3 reporting.

The scope of this module integrates with twelve existing bounded contexts already implemented in this platform (Procurement, Inventory, Quality, Compliance, Risk, Logistics, Warehouse, Finance-Controlling, Demand-Planning, Order-Management, SOP-Planning, Supplier-Management) and introduces five new first-class aggregates: `SupplierDevelopmentProgram`, `ESGScorecard`, `GHGInventory`, `EUDRDueDiligence`, and `JointValueCreationPipeline`.

---

## 2. Prerequisites and Dependencies

### 2.1 Platform Prerequisites

| Prerequisite | Minimum Version | Verified Location |
|---|---|---|
| Supplier master aggregate | v1.0 (Kraljic matrix implemented) | `src/departments/02-supplier-management/` |
| Supplier Scorecard KPIs | OTD, OTIF, PPM operational | `src/departments/02-supplier-management/domain/SupplierScorecard.ts` |
| Compliance module | UFLPA, REACH, CSDDD active | `src/departments/09-compliance-regulatory/` |
| Risk module | 5x5 risk matrix, HHI | `src/departments/10-risk-management/` |
| Finance-Controlling | GL journal entries, Money type | `src/departments/11-finance-controlling/` |
| Shared Event Store | CQRS/Event Sourcing | `src/shared/` |
| Python environment | Python >= 3.11 | `requirements.txt` |

### 2.2 External Data Dependencies

| Data Source | Provider | Data Type | Refresh Cadence | Mandatory |
|---|---|---|---|---|
| ESG ratings | EcoVadis API v3 | JSON scorecard | Quarterly | Yes |
| Carbon disclosure | CDP API v2 | Climate questionnaire scores | Annual | Yes |
| ESG indices | S&P Global Trucost | Scope 1/2/3 intensities | Annual | Yes |
| Carbon accounting | Sphera LCA | Emission factors, EF database | Annual | Yes |
| Deforestation plots | TRACES NT (EC) | GeoJSON plot registry | Real-time | Yes (EUDR) |
| Satellite imagery | Copernicus (ESA) | 10m Sentinel-2 multispectral | 5-day revisit | Yes |
| GHG factors | DEFRA / EPA eGRID | Emission conversion factors | Annual | Yes |
| UN Global Compact | UNGC API | Participant status | Real-time | Recommended |
| CSRD templates | EFRAG ESRS XBRL | XBRL taxonomy | Annual release | Yes |

### 2.3 Regulatory Calendar

| Regulation | Obligation | Effective Date | Module Owner |
|---|---|---|---|
| CSRD — large undertakings | FY 2024 reporting (filed 2025) | 1 Jan 2024 | ESGScorecard |
| CSRD — listed SMEs | FY 2026 reporting | 1 Jan 2026 | ESGScorecard |
| EUDR — large operators | Full enforcement | 30 Dec 2024 (delayed: mid-2025) | EUDRDueDiligence |
| EUDR — SMEs | Full enforcement | 30 Jun 2025 | EUDRDueDiligence |
| SBTi near-term | 2030 milestone | 31 Dec 2030 | GHGInventory |
| SBTi net-zero | 2050 target | 31 Dec 2050 | GHGInventory |
| EU ETS Phase 4 | CBAM full phase-in | 1 Jan 2026 | GHGInventory |
| LkSG (Germany) | Supplier risk analysis | 1 Jan 2023 | CSDDDDueDiligence |

---

## 3. Phase 0: Assessment and AS-IS Analysis

**Duration:** Weeks 1–6
**Owner:** Chief Procurement Officer + Head of Sustainability
**Objective:** Establish a quantified baseline of current supplier development maturity and ESG data coverage before committing to target architecture.

### 3.1 Supply Base Segmentation Analysis

Begin with a full portfolio sweep across the existing supplier master. Segment the supply base using two orthogonal axes: spend exposure and ESG materiality. Spend exposure uses the existing Kraljic quadrant (STRATEGIC / LEVERAGE / BOTTLENECK / NON_CRITICAL). ESG materiality maps to the ESRS 1 double-materiality principle: does this supplier category carry significant environmental impact on the company (financial materiality) or significant company impact on the environment (impact materiality)?

```typescript
// src/departments/14-supplier-development/domain/SupplierSegmentation.ts

export type ESGMaterialityTier = 'TIER_1_HIGH' | 'TIER_2_MEDIUM' | 'TIER_3_LOW';

export interface SupplierESGSegment {
  supplierId: string;
  kraljicQuadrant: 'STRATEGIC' | 'LEVERAGE' | 'BOTTLENECK' | 'NON_CRITICAL';
  annualSpendCents: number;           // integer cents only
  esgMaterialityTier: ESGMaterialityTier;
  scopeThreeCategory1ExposureCents: number;
  eudrCommodityExposed: boolean;
  csrdValueChainInScope: boolean;     // ESRS S2 / E1
  currentEcoVadisScore: number | null;
  currentCDPScore: string | null;     // A, A-, B, B-, C, D, D-
  dataGapScore: number;               // 0–1, higher = more gaps
}

export function classifyESGMateriality(
  annualSpendCents: number,
  sector: string,
  eudrExposed: boolean,
  ghgIntensityTonne: number
): ESGMaterialityTier {
  const spendThresholdHigh = 1_000_000_00; // $1M in cents
  const spendThresholdMed  =   500_000_00; // $500K in cents

  if (
    annualSpendCents >= spendThresholdHigh ||
    eudrExposed ||
    ghgIntensityTonne > 100 ||
    ['Mining', 'Agriculture', 'Steel', 'Cement', 'Chemicals'].includes(sector)
  ) {
    return 'TIER_1_HIGH';
  }
  if (annualSpendCents >= spendThresholdMed || ghgIntensityTonne > 20) {
    return 'TIER_2_MEDIUM';
  }
  return 'TIER_3_LOW';
}
```

### 3.2 Data Maturity Assessment

Score each supplier across five data dimensions using a 0–4 Capability Maturity Model Integration (CMMI) scale:

| Dimension | CMMI 0 | CMMI 1 | CMMI 2 | CMMI 3 | CMMI 4 |
|---|---|---|---|---|---|
| GHG Data | No data | Self-reported, unverified | Third-party verified | ISO 14064-3 assured | Real-time sensor integration |
| Social Audit | No audit | Desk review only | On-site audit (>2yr old) | On-site audit (<1yr, SMETA/BSCI) | Continuous worker voice |
| Governance | No policy | Code of Conduct signed | Anti-bribery training evidenced | ISO 37001 certified | Board-level ESG KPI linkage |
| Deforestation | No data | Commodity declared | Country of origin declared | Plot-level GPS coordinates | Satellite-validated polygons |
| CSRD Alignment | None | Aware | Partial ESRS mapping | Draft ESRS disclosure | Assured ESRS reporting |

### 3.3 AS-IS Gap Quantification

Produce a gap heatmap and quantify coverage across the entire active supplier base (status = ACTIVE in supplier master). The target coverage for Phase 1 completion is:

- Tier 1 High: 100% GHG data coverage, 100% social audit coverage
- Tier 2 Medium: 80% GHG data, 60% social audit
- Tier 3 Low: Spend-based GHG estimation, code of conduct signed

---

## 4. Phase 1: Foundation and Master Data

**Duration:** Weeks 7–18
**Owner:** Supplier Development Lead + Data Architecture
**Objective:** Build the ESG master data layer, domain aggregates, and event store integration that all subsequent phases depend upon.

### 4.1 Core Domain Aggregates

#### 4.1.1 ESGScorecard Aggregate

```typescript
// src/departments/14-supplier-development/domain/ESGScorecard.ts

import { Money, ISOTimestamp } from '../../../shared/types';

export type ESGRating =
  | 'LEADER'        // >= 85
  | 'ADVANCED'      // >= 70
  | 'GOOD'          // >= 55
  | 'PARTIAL'       // >= 40
  | 'INSUFFICIENT'; // < 40

export interface EnvironmentalScore {
  // E pillar — 40% of total ESG score
  climateChangeScore: number;          // 0–100: GHG reduction trajectory
  biodiversityScore: number;           // 0–100: TNFD / EUDR compliance
  waterScore: number;                  // 0–100: CDP Water
  wasteCircularityScore: number;       // 0–100: ISO 14001 waste metrics
  pollutionPreventionScore: number;    // 0–100: EU IED compliance
  compositeScore: number;              // Weighted: see Phase 3 model
}

export interface SocialScore {
  // S pillar — 40% of total ESG score
  laborRightsScore: number;            // 0–100: ILO core conventions
  healthSafetyScore: number;           // 0–100: ISO 45001
  diversityInclusionScore: number;     // 0–100: gender pay gap, diversity ratios
  communityImpactScore: number;        // 0–100: UNGC Principle 1–6
  supplyChainLaborScore: number;       // 0–100: SMETA / SA8000
  compositeScore: number;
}

export interface GovernanceScore {
  // G pillar — 20% of total ESG score
  boardOversightScore: number;         // 0–100: ESG at board level
  ethicsAntiCorruptionScore: number;   // 0–100: ISO 37001
  transparencyDisclosureScore: number; // 0–100: CSRD / GRI alignment
  dataPrivacyScore: number;            // 0–100: GDPR compliance
  compositeScore: number;
}

export interface ESGScorecard {
  id: string;
  supplierId: string;
  assessmentDate: ISOTimestamp;
  assessmentPeriodYear: number;
  environmental: EnvironmentalScore;
  social: SocialScore;
  governance: GovernanceScore;
  totalWeightedScore: number;          // 0–100
  rating: ESGRating;
  ecoVadisScore: number | null;
  cdpClimateScore: string | null;
  spGlobalEsgScore: number | null;
  externalVerification: boolean;
  verifierName: string | null;
  assuranceStandard: string | null;   // e.g. 'AA1000AS v3', 'ISAE 3000'
  nextReviewDate: ISOTimestamp;
  isDeleted: boolean;
  version: number;
}
```

#### 4.1.2 GHGInventory Aggregate

```typescript
// src/departments/14-supplier-development/domain/GHGInventory.ts

export type GHGScope = 'SCOPE_1' | 'SCOPE_2_MARKET' | 'SCOPE_2_LOCATION' | 'SCOPE_3';
export type Scope3Category =
  | 'CAT_1_PURCHASED_GOODS'
  | 'CAT_2_CAPITAL_GOODS'
  | 'CAT_3_FUEL_ENERGY'
  | 'CAT_4_UPSTREAM_TRANSPORT'
  | 'CAT_5_WASTE_GENERATED'
  | 'CAT_6_BUSINESS_TRAVEL'
  | 'CAT_7_EMPLOYEE_COMMUTING'
  | 'CAT_8_UPSTREAM_LEASED'
  | 'CAT_9_DOWNSTREAM_TRANSPORT'
  | 'CAT_10_PROCESSING'
  | 'CAT_11_USE_OF_SOLD'
  | 'CAT_12_EOL_TREATMENT'
  | 'CAT_13_DOWNSTREAM_LEASED'
  | 'CAT_14_FRANCHISES'
  | 'CAT_15_INVESTMENTS';

export type CalculationMethod = 'SPEND_BASED' | 'ACTIVITY_BASED' | 'HYBRID' | 'SUPPLIER_SPECIFIC';

export interface GHGLineItem {
  id: string;
  supplierId: string;
  inventoryYear: number;
  scope: GHGScope;
  category: Scope3Category | null;
  calculationMethod: CalculationMethod;
  activityData: number;               // Physical unit of activity
  activityUnit: string;               // e.g. 'tonne', 'kWh', 'USD'
  emissionFactor: number;             // kgCO2e per activity unit
  emissionFactorSource: string;       // e.g. 'DEFRA 2025', 'EPA eGRID 2024', 'Sphera'
  emissionsKgCO2e: number;            // activityData * emissionFactor
  dataQualityScore: number;           // 1 (highest) to 5 (lowest) per GHG Protocol
  isVerified: boolean;
  idempotencyKey: string;
}

export interface GHGInventory {
  id: string;
  supplierId: string;
  reportingYear: number;
  baselineYear: number;
  scope1TotalKgCO2e: number;
  scope2MarketBasedKgCO2e: number;
  scope2LocationBasedKgCO2e: number;
  scope3TotalKgCO2e: number;
  scope3ByCategory: Record<Scope3Category, number>;
  lineItems: GHGLineItem[];
  sbtiNearTermTarget2030KgCO2e: number;
  sbtiNetZeroTarget2050KgCO2e: number;
  currentTrajectoryDeltaPct: number;  // positive = on track, negative = gap
  assuranceLevel: 'NONE' | 'LIMITED' | 'REASONABLE';
  assuranceProvider: string | null;
  isDeleted: boolean;
}
```

#### 4.1.3 EUDRDueDiligence Aggregate

```typescript
// src/departments/14-supplier-development/domain/EUDRDueDiligence.ts

export type EUDRCommodity =
  | 'CATTLE' | 'COCOA' | 'COFFEE' | 'OIL_PALM' | 'SOYA' | 'WOOD' | 'RUBBER'
  | 'DERIVED_PRODUCTS'; // Includes leather, chocolate, paper, tyres, etc.

export type EUDRCountryRiskLevel = 'HIGH' | 'STANDARD' | 'LOW';
export type EUDRComplianceStatus = 'COMPLIANT' | 'NON_COMPLIANT' | 'UNDER_REVIEW' | 'EXEMPT';

export interface ProductionPlot {
  plotId: string;
  supplierId: string;
  commodity: EUDRCommodity;
  countryCode: string;                 // ISO 3166-1 alpha-2
  countryRiskLevel: EUDRCountryRiskLevel;
  // GPS coordinates to at least 6 decimal places per EUDR Article 9(1)(d)
  latitude: number;                    // e.g. -3.123456 (6+ decimals)
  longitude: number;                   // e.g. 35.654321 (6+ decimals)
  // GeoJSON polygon — required for plots >= 4 hectares
  polygonGeoJson: string | null;       // WGS84 GeoJSON Polygon
  plotAreaHectares: number;
  polygonRequired: boolean;            // true if plotAreaHectares >= 4
  // Satellite validation output
  lastSatelliteCheckDate: ISOTimestamp | null;
  deforestationDetected: boolean;
  forestCoverChangePct: number | null; // negative = loss
  validationConfidenceScore: number | null; // 0–1
  // TRACES NT reference
  tracesNtReferenceNumber: string | null;
  dueDiligenceStatementId: string | null;
  complianceStatus: EUDRComplianceStatus;
}
```

### 4.2 Event Sourcing Integration

All ESG state transitions must be captured as domain events. This is consistent with the platform's existing CQRS/Event Sourcing pattern in `src/shared/`.

```typescript
// src/departments/14-supplier-development/domain/ESGEvents.ts

export type ESGDomainEvent =
  | { type: 'ESG_SCORECARD_CREATED';        payload: ESGScorecard }
  | { type: 'ESG_SCORE_UPDATED';            payload: { scorecardId: string; newScore: number; reason: string } }
  | { type: 'GHG_INVENTORY_SUBMITTED';      payload: GHGInventory }
  | { type: 'GHG_VERIFICATION_COMPLETED';   payload: { inventoryId: string; assuranceLevel: string; provider: string } }
  | { type: 'EUDR_PLOT_REGISTERED';         payload: ProductionPlot }
  | { type: 'EUDR_DEFORESTATION_DETECTED';  payload: { plotId: string; detectedDate: ISOTimestamp; confidence: number } }
  | { type: 'SUPPLIER_DEVELOPMENT_PROGRAM_LAUNCHED'; payload: SupplierDevelopmentProgram }
  | { type: 'INNOVATION_MILESTONE_ACHIEVED'; payload: { pipelineId: string; milestoneId: string } };
```

---

## 5. Phase 2: Process Standardisation and Core Analytics

**Duration:** Weeks 19–30
**Owner:** Supplier Development Manager + Sustainability Analyst
**Objective:** Operationalise supplier assessments, development programme workflows, and baseline reporting.

### 5.1 Supplier Assessment Workflow

The assessment process follows a four-stage gate model aligned with ISO 20400:2017 (Sustainable Procurement):

**Stage 1 — Self-Assessment Questionnaire (SAQ):** Distributed to all Tier 1 High and Tier 2 Medium suppliers via the supplier portal. Covers 47 questions mapped to GRI 2021, SASB industry-specific standards, and ESRS XBRL taxonomy fields. Completeness score threshold for progression: 80%.

**Stage 2 — Desktop Review:** Sustainability team validates submitted evidence (certificates, audit reports, GHG disclosures) against authoritative third-party databases (EcoVadis, CDP, S&P Global). Discrepancy flagging triggers a Corrective Action Request (CAR).

**Stage 3 — On-Site Audit:** For Tier 1 High suppliers not holding current SMETA 4-Pillar or equivalent (BSCI, HIGG FEM, SA8000). Audit must be conducted by an approved second-party or third-party auditor. Audit findings classified per SMETA severity matrix: Critical, Major, Minor, Observation.

**Stage 4 — Continuous Monitoring:** Quarterly satellite imagery review, real-time TRACES NT checks for EUDR commodities, annual SAQ refresh, and EcoVadis annual reassessment trigger.

### 5.2 Supplier Development Program Management

```typescript
// src/departments/14-supplier-development/domain/SupplierDevelopmentProgram.ts

export type ProgramType =
  | 'ESG_UPLIFT'            // Close ESG score gap
  | 'CARBON_REDUCTION'      // GHG reduction collaboration
  | 'CAPABILITY_BUILDING'   // Training and process improvement
  | 'INNOVATION_JOINT'      // Joint value creation
  | 'EUDR_COMPLIANCE';      // Traceability and plot registration

export type ProgramStatus =
  | 'DRAFT' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'TERMINATED';

export interface ProgramMilestone {
  id: string;
  description: string;
  targetDate: ISOTimestamp;
  achievedDate: ISOTimestamp | null;
  kpiTarget: number;
  kpiActual: number | null;
  kpiUnit: string;
  verified: boolean;
}

export interface SupplierDevelopmentProgram {
  id: string;
  supplierId: string;
  programType: ProgramType;
  status: ProgramStatus;
  startDate: ISOTimestamp;
  targetEndDate: ISOTimestamp;
  sponsorUserId: string;
  supplierContactName: string;
  baselineESGScore: number;
  targetESGScore: number;
  baselineGHGKgCO2e: number | null;
  targetGHGKgCO2e: number | null;
  annualSpendCents: number;
  milestones: ProgramMilestone[];
  investmentCents: number;            // Company investment in program
  projectedROIBps: number;            // Basis points
  actualROIBps: number | null;
  isDeleted: boolean;
  idempotencyKey: string;
}
```

---

## 6. Phase 3: Mathematical Models

**Duration:** Weeks 31–42
**Owner:** Quantitative Analytics Team
**Objective:** Implement all quantitative models in Python with TypeScript orchestration interfaces.

### 6.1 ESG Scoring Model

**Regulatory basis:** GRI Standards 2021 (GRI 1, 2, 3); ESRS E1, E4, S1, S2, G1; EcoVadis Methodology 2024 (21 criteria mapped to 4 themes).

**Model architecture:** Three-pillar weighted composite with sub-criterion granularity.

#### Pillar Weights
- Environmental (E): 40% of total
- Social (S): 40% of total
- Governance (G): 20% of total

#### Sub-criterion Weights (within each pillar)

**Environmental (E) sub-criteria:**

| Sub-criterion | Weight within E | GRI Reference | ESRS Reference |
|---|---|---|---|
| Climate change / GHG | 35% | GRI 305 | E1 |
| Biodiversity / Land use | 25% | GRI 304 | E4 |
| Water stewardship | 20% | GRI 303 | E3 |
| Waste and circularity | 12% | GRI 306 | E5 |
| Pollution prevention | 8% | GRI 305-7 | E2 |

**Social (S) sub-criteria:**

| Sub-criterion | Weight within S | GRI Reference | ESRS Reference |
|---|---|---|---|
| Labour rights / ILO | 30% | GRI 402–412 | S2 |
| Health and safety | 25% | GRI 403 | S1 |
| Diversity and inclusion | 20% | GRI 405–406 | S1 |
| Community impact | 15% | GRI 413 | S3 |
| Supply chain labour | 10% | GRI 414 | S2 |

**Governance (G) sub-criteria:**

| Sub-criterion | Weight within G | GRI Reference | ESRS Reference |
|---|---|---|---|
| Board oversight | 30% | GRI 2-9 | G1 |
| Ethics and anti-corruption | 35% | GRI 205–206 | G1 |
| Transparency / disclosure | 25% | GRI 2-22 | G1 |
| Data privacy | 10% | GRI 418 | G1 |

#### Python Implementation

```python
# python/14_supplier_development/esg_scoring.py

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EnvironmentalInputs:
    """Raw sub-criterion scores for the E pillar, each on a 0–100 scale."""
    climate_change: float         # GRI 305, ESRS E1
    biodiversity: float           # GRI 304, ESRS E4
    water: float                  # GRI 303, ESRS E3
    waste_circularity: float      # GRI 306, ESRS E5
    pollution_prevention: float   # GRI 305-7, ESRS E2


@dataclass
class SocialInputs:
    """Raw sub-criterion scores for the S pillar, each on a 0–100 scale."""
    labour_rights: float          # GRI 402–412, ESRS S2
    health_safety: float          # GRI 403, ESRS S1
    diversity_inclusion: float    # GRI 405–406, ESRS S1
    community_impact: float       # GRI 413, ESRS S3
    supply_chain_labour: float    # GRI 414, ESRS S2


@dataclass
class GovernanceInputs:
    """Raw sub-criterion scores for the G pillar, each on a 0–100 scale."""
    board_oversight: float        # GRI 2-9, ESRS G1
    ethics_anti_corruption: float # GRI 205–206, ESRS G1
    transparency_disclosure: float# GRI 2-22, ESRS G1
    data_privacy: float           # GRI 418, ESRS G1


@dataclass
class ESGScoreResult:
    e_composite: float
    s_composite: float
    g_composite: float
    total_score: float            # 0–100
    rating: str                  # LEADER / ADVANCED / GOOD / PARTIAL / INSUFFICIENT

    # E sub-criterion weighted contributions
    e_climate_contribution: float
    e_biodiversity_contribution: float
    e_water_contribution: float
    e_waste_contribution: float
    e_pollution_contribution: float

    # S sub-criterion weighted contributions
    s_labour_contribution: float
    s_safety_contribution: float
    s_diversity_contribution: float
    s_community_contribution: float
    s_supply_chain_contribution: float

    # G sub-criterion weighted contributions
    g_board_contribution: float
    g_ethics_contribution: float
    g_transparency_contribution: float
    g_privacy_contribution: float


# Pillar weights — must sum to 1.0
PILLAR_WEIGHTS = {'E': 0.40, 'S': 0.40, 'G': 0.20}

# E sub-criterion weights — sum to 1.0
E_WEIGHTS = {
    'climate_change': 0.35,
    'biodiversity': 0.25,
    'water': 0.20,
    'waste_circularity': 0.12,
    'pollution_prevention': 0.08,
}

# S sub-criterion weights — sum to 1.0
S_WEIGHTS = {
    'labour_rights': 0.30,
    'health_safety': 0.25,
    'diversity_inclusion': 0.20,
    'community_impact': 0.15,
    'supply_chain_labour': 0.10,
}

# G sub-criterion weights — sum to 1.0
G_WEIGHTS = {
    'board_oversight': 0.30,
    'ethics_anti_corruption': 0.35,
    'transparency_disclosure': 0.25,
    'data_privacy': 0.10,
}


def _validate_score(value: float, name: str) -> float:
    """Validate that a sub-criterion score is in [0, 100]."""
    if not (0.0 <= value <= 100.0):
        raise ValueError(f"Score '{name}' must be in [0, 100], got {value}")
    return float(value)


def compute_esg_score(
    env: EnvironmentalInputs,
    soc: SocialInputs,
    gov: GovernanceInputs,
) -> ESGScoreResult:
    """
    Compute a three-pillar ESG score aligned with GRI 2021, ESRS, and
    EcoVadis 2024 methodology.

    Parameters
    ----------
    env : EnvironmentalInputs  — validated sub-criterion scores, 0–100 each
    soc : SocialInputs         — validated sub-criterion scores, 0–100 each
    gov : GovernanceInputs     — validated sub-criterion scores, 0–100 each

    Returns
    -------
    ESGScoreResult with all pillar composites, sub-criterion contributions,
    total weighted score, and qualitative rating.

    Notes
    -----
    Total score = 0.40 * E_composite + 0.40 * S_composite + 0.20 * G_composite
    Rating thresholds: LEADER>=85, ADVANCED>=70, GOOD>=55, PARTIAL>=40, INSUFFICIENT<40
    """
    # Environmental composite
    e_climate  = _validate_score(env.climate_change, 'climate_change') * E_WEIGHTS['climate_change']
    e_bio      = _validate_score(env.biodiversity, 'biodiversity') * E_WEIGHTS['biodiversity']
    e_water    = _validate_score(env.water, 'water') * E_WEIGHTS['water']
    e_waste    = _validate_score(env.waste_circularity, 'waste_circularity') * E_WEIGHTS['waste_circularity']
    e_poll     = _validate_score(env.pollution_prevention, 'pollution_prevention') * E_WEIGHTS['pollution_prevention']
    e_composite = e_climate + e_bio + e_water + e_waste + e_poll

    # Social composite
    s_labour   = _validate_score(soc.labour_rights, 'labour_rights') * S_WEIGHTS['labour_rights']
    s_safety   = _validate_score(soc.health_safety, 'health_safety') * S_WEIGHTS['health_safety']
    s_diversity= _validate_score(soc.diversity_inclusion, 'diversity_inclusion') * S_WEIGHTS['diversity_inclusion']
    s_comm     = _validate_score(soc.community_impact, 'community_impact') * S_WEIGHTS['community_impact']
    s_scl      = _validate_score(soc.supply_chain_labour, 'supply_chain_labour') * S_WEIGHTS['supply_chain_labour']
    s_composite = s_labour + s_safety + s_diversity + s_comm + s_scl

    # Governance composite
    g_board    = _validate_score(gov.board_oversight, 'board_oversight') * G_WEIGHTS['board_oversight']
    g_ethics   = _validate_score(gov.ethics_anti_corruption, 'ethics_anti_corruption') * G_WEIGHTS['ethics_anti_corruption']
    g_transp   = _validate_score(gov.transparency_disclosure, 'transparency_disclosure') * G_WEIGHTS['transparency_disclosure']
    g_privacy  = _validate_score(gov.data_privacy, 'data_privacy') * G_WEIGHTS['data_privacy']
    g_composite = g_board + g_ethics + g_transp + g_privacy

    # Total weighted score
    total = (
        PILLAR_WEIGHTS['E'] * e_composite +
        PILLAR_WEIGHTS['S'] * s_composite +
        PILLAR_WEIGHTS['G'] * g_composite
    )

    # Rating
    if total >= 85:   rating = 'LEADER'
    elif total >= 70: rating = 'ADVANCED'
    elif total >= 55: rating = 'GOOD'
    elif total >= 40: rating = 'PARTIAL'
    else:             rating = 'INSUFFICIENT'

    return ESGScoreResult(
        e_composite=round(e_composite, 4),
        s_composite=round(s_composite, 4),
        g_composite=round(g_composite, 4),
        total_score=round(total, 4),
        rating=rating,
        e_climate_contribution=round(e_climate, 4),
        e_biodiversity_contribution=round(e_bio, 4),
        e_water_contribution=round(e_water, 4),
        e_waste_contribution=round(e_waste, 4),
        e_pollution_contribution=round(e_poll, 4),
        s_labour_contribution=round(s_labour, 4),
        s_safety_contribution=round(s_safety, 4),
        s_diversity_contribution=round(s_diversity, 4),
        s_community_contribution=round(s_comm, 4),
        s_supply_chain_contribution=round(s_scl, 4),
        g_board_contribution=round(g_board, 4),
        g_ethics_contribution=round(g_ethics, 4),
        g_transparency_contribution=round(g_transp, 4),
        g_privacy_contribution=round(g_privacy, 4),
    )
```

### 6.2 GHG Scope 3 Category 1 Calculation

**Regulatory basis:** GHG Protocol Corporate Value Chain (Scope 3) Standard (2011); ISO 14064-1:2018; ESRS E1-6.

**Category 1** covers purchased goods and services — the dominant Scope 3 category for most manufacturing and retail companies, typically comprising 40–80% of total corporate carbon footprint.

Two calculation pathways are defined by the GHG Protocol:

**Spend-Based Method:** `Emissions = Spend (USD) x Economic Emission Factor (kgCO2e/USD)`
- Data source: Environmentally Extended Input-Output (EEIO) tables (e.g., USEEIO v2.0, Exiobase v3.8)
- Use case: Broad supply base, low data availability, screening-level assessment
- Data quality score: 4–5 (GHG Protocol data quality indicators)

**Activity-Based Method:** `Emissions = Activity Data (physical unit) x Emission Factor (kgCO2e/unit)`
- Data source: Supplier-specific data (primary), industry averages (secondary)
- Use case: Strategic suppliers, high-spend categories, SBTi supplier engagement
- Data quality score: 1–3

```python
# python/14_supplier_development/ghg_scope3_cat1.py

from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Literal


CalculationMethod = Literal['SPEND_BASED', 'ACTIVITY_BASED', 'HYBRID']


@dataclass
class SpendBasedInput:
    """
    Input for the spend-based Scope 3 Category 1 method.
    Source: Environmentally Extended Input-Output (EEIO) tables.
    """
    supplier_id: str
    spend_usd: float                   # Annual spend in USD
    sector_code: str                   # NAICS or ISIC code for sector classification
    eeio_ef_kg_co2e_per_usd: float     # Emission factor from EEIO table (kgCO2e/USD)
    purchase_year: int


@dataclass
class ActivityBasedInput:
    """
    Input for the activity-based Scope 3 Category 1 method.
    Requires supplier-disclosed or measured activity data.
    """
    supplier_id: str
    activity_quantity: float           # Physical unit quantity
    activity_unit: str                 # e.g. 'tonne_steel', 'kWh', 'litre'
    emission_factor_kg_co2e_per_unit: float
    emission_factor_source: str        # e.g. 'worldsteel 2024', 'DEFRA 2025'
    purchase_year: int
    is_supplier_specific: bool         # True = primary data, False = industry average


@dataclass
class Scope3Cat1Result:
    supplier_id: str
    method: CalculationMethod
    emissions_kg_co2e: float
    emissions_tonne_co2e: float
    data_quality_score: int             # 1 (best) to 5 (worst) per GHG Protocol
    emission_factor_source: str
    uncertainty_pct: float              # Estimated percentage uncertainty


def calculate_spend_based(inp: SpendBasedInput) -> Scope3Cat1Result:
    """
    Spend-based Scope 3 Category 1 calculation using EEIO emission factors.

    Formula:
        Emissions (kgCO2e) = Spend (USD) x EF_EEIO (kgCO2e/USD)

    Reference: GHG Protocol Scope 3 Calculation Guidance, Chapter 5.
    Uncertainty: +/-50% for EEIO spend-based method (GHG Protocol guidance).
    """
    emissions_kg = inp.spend_usd * inp.eeio_ef_kg_co2e_per_usd

    return Scope3Cat1Result(
        supplier_id=inp.supplier_id,
        method='SPEND_BASED',
        emissions_kg_co2e=round(emissions_kg, 2),
        emissions_tonne_co2e=round(emissions_kg / 1_000, 4),
        data_quality_score=4,           # EEIO = lower quality per GHG Protocol
        emission_factor_source=f"EEIO table, sector {inp.sector_code}",
        uncertainty_pct=50.0,
    )


def calculate_activity_based(inp: ActivityBasedInput) -> Scope3Cat1Result:
    """
    Activity-based Scope 3 Category 1 calculation.

    Formula:
        Emissions (kgCO2e) = Activity_Data x EF (kgCO2e / activity_unit)

    Reference: GHG Protocol Scope 3 Calculation Guidance, Chapter 5.
    Uncertainty: +/-10% for supplier-specific primary data; +/-30% for industry avg.
    """
    emissions_kg = inp.activity_quantity * inp.emission_factor_kg_co2e_per_unit
    dq_score = 1 if inp.is_supplier_specific else 3
    uncertainty = 10.0 if inp.is_supplier_specific else 30.0

    return Scope3Cat1Result(
        supplier_id=inp.supplier_id,
        method='ACTIVITY_BASED',
        emissions_kg_co2e=round(emissions_kg, 2),
        emissions_tonne_co2e=round(emissions_kg / 1_000, 4),
        data_quality_score=dq_score,
        emission_factor_source=inp.emission_factor_source,
        uncertainty_pct=uncertainty,
    )


def aggregate_supplier_scope3_cat1(
    results: list[Scope3Cat1Result],
) -> pd.DataFrame:
    """
    Aggregate Scope 3 Category 1 results across all suppliers.
    Returns a DataFrame with emissions by supplier, sorted by impact (descending).
    Useful for prioritising supplier engagement under SBTi supplier engagement target.
    """
    records = [
        {
            'supplier_id': r.supplier_id,
            'method': r.method,
            'emissions_tonne_co2e': r.emissions_tonne_co2e,
            'data_quality_score': r.data_quality_score,
            'uncertainty_pct': r.uncertainty_pct,
        }
        for r in results
    ]
    df = pd.DataFrame(records).sort_values('emissions_tonne_co2e', ascending=False)
    df['cumulative_pct'] = (
        df['emissions_tonne_co2e'].cumsum() / df['emissions_tonne_co2e'].sum() * 100
    )
    return df
```

### 6.3 SBTi Alignment: Near-Term and Net-Zero Trajectory

**Regulatory basis:** SBTi Corporate Net-Zero Standard v1.1 (2023); IPCC AR6 1.5C pathway; Paris Agreement Article 4.

The SBTi near-term target requires Scope 3 absolute reduction of at least 42% by 2030 (from a base year between 2018 and 2021). The net-zero target requires a minimum 90% absolute reduction across all scopes by 2050, with residual emissions neutralised by verified carbon removals.

```python
# python/14_supplier_development/sbti_trajectory.py

from __future__ import annotations
import numpy as np
from dataclasses import dataclass


@dataclass
class SBTiTrajectoryResult:
    base_year: int
    reporting_year: int
    base_emissions_tco2e: float
    current_emissions_tco2e: float
    near_term_target_2030_tco2e: float     # Base * (1 - 0.42)
    net_zero_target_2050_tco2e: float      # Base * (1 - 0.90)
    required_annual_reduction_rate_pct: float  # Linear rate to hit 2030 target
    actual_reduction_to_date_pct: float
    gap_to_near_term_target_tco2e: float   # Positive = gap; negative = ahead
    gap_to_net_zero_target_tco2e: float
    on_track_near_term: bool
    on_track_net_zero: bool
    linear_trajectory_tco2e: list[float]   # Annual targets from base_year to 2050


def compute_sbti_trajectory(
    base_year: int,
    base_emissions_tco2e: float,
    current_year: int,
    current_emissions_tco2e: float,
    near_term_reduction_pct: float = 0.42,  # SBTi minimum: 42% by 2030
    net_zero_reduction_pct: float = 0.90,   # SBTi minimum: 90% by 2050
    near_term_year: int = 2030,
    net_zero_year: int = 2050,
) -> SBTiTrajectoryResult:
    """
    Compute SBTi near-term and net-zero alignment trajectory.

    The linear interpolation approach is used (SBTi absolute contraction method).
    Formula for year Y target:
        Target(Y) = Base * (1 - reduction_pct * (Y - base_year) / (target_year - base_year))

    Parameters
    ----------
    base_year       : GHG inventory base year (must be 2018–2021 for SBTi)
    base_emissions_tco2e : Total Scope 1+2+3 emissions in base year (tCO2e)
    current_year    : Current reporting year
    current_emissions_tco2e : Total Scope 1+2+3 emissions in current year (tCO2e)
    near_term_reduction_pct : Fractional reduction required by near_term_year (default 0.42)
    net_zero_reduction_pct  : Fractional reduction required by net_zero_year (default 0.90)
    """
    if base_year < 2018 or base_year > 2021:
        raise ValueError("SBTi base year must be between 2018 and 2021 inclusive.")

    near_term_target = base_emissions_tco2e * (1.0 - near_term_reduction_pct)
    net_zero_target  = base_emissions_tco2e * (1.0 - net_zero_reduction_pct)

    years_to_near_term = near_term_year - base_year
    annual_rate = near_term_reduction_pct / years_to_near_term

    actual_reduction = (base_emissions_tco2e - current_emissions_tco2e) / base_emissions_tco2e
    years_elapsed = current_year - base_year
    required_reduction_to_date = annual_rate * years_elapsed
    on_track_near = actual_reduction >= required_reduction_to_date

    # Linear trajectory from base_year to net_zero_year
    trajectory = []
    for yr in range(base_year, net_zero_year + 1):
        if yr <= near_term_year:
            frac = near_term_reduction_pct * (yr - base_year) / years_to_near_term
        else:
            # Steeper reduction from 2030 to 2050 to reach 90%
            frac = near_term_reduction_pct + (net_zero_reduction_pct - near_term_reduction_pct) * (
                (yr - near_term_year) / (net_zero_year - near_term_year)
            )
        trajectory.append(round(base_emissions_tco2e * (1.0 - frac), 2))

    year_idx = current_year - base_year
    on_track_nz = current_emissions_tco2e <= trajectory[year_idx]

    return SBTiTrajectoryResult(
        base_year=base_year,
        reporting_year=current_year,
        base_emissions_tco2e=base_emissions_tco2e,
        current_emissions_tco2e=current_emissions_tco2e,
        near_term_target_2030_tco2e=round(near_term_target, 2),
        net_zero_target_2050_tco2e=round(net_zero_target, 2),
        required_annual_reduction_rate_pct=round(annual_rate * 100, 4),
        actual_reduction_to_date_pct=round(actual_reduction * 100, 4),
        gap_to_near_term_target_tco2e=round(current_emissions_tco2e - near_term_target, 2),
        gap_to_net_zero_target_tco2e=round(current_emissions_tco2e - net_zero_target, 2),
        on_track_near_term=on_track_near,
        on_track_net_zero=on_track_nz,
        linear_trajectory_tco2e=trajectory,
    )
```

### 6.4 Supplier Development Program ROI

**Model basis:** Delta-adjusted supplier value contribution, net of programme investment.

```
ROI (bps) = [(Performance_Delta_Score / 100) x Annual_Spend_USD x Benefit_Multiplier
             - Program_Investment_USD]
             / Program_Investment_USD x 10,000
```

The Benefit Multiplier translates ESG score improvement into financial value. Industry research (Gartner 2024, McKinsey Sustainability Index 2023) quantifies this as follows: a 10-point ESG score improvement on a 100-point scale correlates with a 2.3% reduction in total landed cost (supply chain risk premium reduction, lower insurance costs, avoided regulatory penalties, improved market access premium).

```python
# python/14_supplier_development/sdp_roi.py

def compute_sdp_roi(
    baseline_esg_score: float,
    target_esg_score: float,
    annual_spend_usd: float,
    program_investment_usd: float,
    program_duration_years: float,
    benefit_multiplier_per_point: float = 0.0023,  # 0.23% cost reduction per ESG point
) -> dict:
    """
    Supplier Development Program ROI calculation.

    Parameters
    ----------
    baseline_esg_score    : ESG score at program start (0–100)
    target_esg_score      : ESG score at program end (0–100)
    annual_spend_usd      : Annual procurement spend with this supplier (USD)
    program_investment_usd: Total company investment in the program (USD)
    program_duration_years: Duration in years
    benefit_multiplier_per_point: Fractional cost reduction per ESG point improvement

    Returns
    -------
    dict with gross_benefit_usd, net_benefit_usd, roi_bps, payback_months
    """
    if target_esg_score <= baseline_esg_score:
        raise ValueError("Target ESG score must exceed baseline score.")
    if program_investment_usd <= 0:
        raise ValueError("Program investment must be positive.")

    performance_delta = target_esg_score - baseline_esg_score
    annual_benefit_usd = annual_spend_usd * benefit_multiplier_per_point * performance_delta
    gross_benefit_usd  = annual_benefit_usd * program_duration_years
    net_benefit_usd    = gross_benefit_usd - program_investment_usd
    roi_bps = (net_benefit_usd / program_investment_usd) * 10_000
    payback_months = (program_investment_usd / annual_benefit_usd) * 12 if annual_benefit_usd > 0 else float('inf')

    return {
        'performance_delta_points': round(performance_delta, 2),
        'annual_benefit_usd': round(annual_benefit_usd, 2),
        'gross_benefit_usd': round(gross_benefit_usd, 2),
        'program_investment_usd': round(program_investment_usd, 2),
        'net_benefit_usd': round(net_benefit_usd, 2),
        'roi_bps': round(roi_bps, 1),
        'payback_months': round(payback_months, 1),
    }
```

### 6.5 EUDR Production Plot Validation

**Regulatory basis:** EUDR Article 9(1)(d): "geographic coordinates of all plots of land where the relevant commodities and products were produced"; Article 2(28): polygon required when plot >= 4 ha.

Validation requires GPS coordinates to a minimum of six decimal places (precision ~0.1m) and closed GeoJSON polygons for plots of four or more hectares.

```python
# python/14_supplier_development/eudr_plot_validation.py

import json
import math
from dataclasses import dataclass
from typing import Optional


MIN_DECIMAL_PLACES = 6
MIN_POLYGON_HECTARES = 4.0
MIN_POLYGON_VERTICES = 5  # 4 unique + 1 closing vertex (GeoJSON spec)


@dataclass
class PlotValidationResult:
    plot_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    latitude_decimal_places: int
    longitude_decimal_places: int
    polygon_vertex_count: int
    calculated_area_hectares: Optional[float]
    polygon_is_closed: bool


def _count_decimal_places(value: float) -> int:
    """Count decimal places in a float representation."""
    s = f"{value:.10f}".rstrip('0')
    if '.' in s:
        return len(s.split('.')[1])
    return 0


def _shoelace_area_degrees(coords: list[list[float]]) -> float:
    """
    Compute polygon area in square degrees using the Shoelace formula.
    Converts to hectares using average latitude for the Earth ellipsoid approximation.
    """
    n = len(coords)
    area_deg2 = 0.0
    for i in range(n - 1):
        x0, y0 = coords[i]
        x1, y1 = coords[i + 1]
        area_deg2 += (x0 * y1) - (x1 * y0)
    area_deg2 = abs(area_deg2) / 2.0

    # Convert square degrees to hectares
    avg_lat_rad = math.radians(sum(c[1] for c in coords) / n)
    meters_per_deg_lat = 111_320.0
    meters_per_deg_lon = 111_320.0 * math.cos(avg_lat_rad)
    area_m2 = area_deg2 * meters_per_deg_lat * meters_per_deg_lon
    return area_m2 / 10_000.0  # m2 to hectares


def validate_eudr_plot(
    plot_id: str,
    latitude: float,
    longitude: float,
    plot_area_hectares: float,
    polygon_geojson: Optional[str],
) -> PlotValidationResult:
    """
    Validate a production plot for EUDR Article 9(1)(d) compliance.

    Rules:
    1. Latitude and longitude must have >= 6 decimal places.
    2. If plot_area_hectares >= 4.0, polygon_geojson must be provided.
    3. GeoJSON polygon must be a valid closed ring with >= 5 vertices.
    4. Calculated polygon area must be within 10% of declared plot_area_hectares.
    """
    errors = []
    warnings = []
    lat_dp = _count_decimal_places(latitude)
    lon_dp = _count_decimal_places(longitude)
    vertex_count = 0
    calc_area = None
    polygon_closed = False

    if lat_dp < MIN_DECIMAL_PLACES:
        errors.append(
            f"Latitude has {lat_dp} decimal places; EUDR requires >= {MIN_DECIMAL_PLACES}."
        )
    if lon_dp < MIN_DECIMAL_PLACES:
        errors.append(
            f"Longitude has {lon_dp} decimal places; EUDR requires >= {MIN_DECIMAL_PLACES}."
        )

    polygon_required = plot_area_hectares >= MIN_POLYGON_HECTARES

    if polygon_required and polygon_geojson is None:
        errors.append(
            f"Plot area {plot_area_hectares:.2f} ha >= {MIN_POLYGON_HECTARES} ha: "
            "GeoJSON polygon is mandatory per EUDR Article 9(1)(d)."
        )
    elif polygon_geojson is not None:
        try:
            geojson = json.loads(polygon_geojson)
            coords = geojson.get('coordinates', [[]])[0]
            vertex_count = len(coords)

            if vertex_count < MIN_POLYGON_VERTICES:
                errors.append(
                    f"Polygon has {vertex_count} vertices; minimum is {MIN_POLYGON_VERTICES} "
                    "(4 unique + 1 closing vertex per GeoJSON spec)."
                )

            first, last = coords[0], coords[-1]
            polygon_closed = (first[0] == last[0] and first[1] == last[1])
            if not polygon_closed:
                errors.append("GeoJSON polygon ring is not closed (first != last vertex).")

            if vertex_count >= MIN_POLYGON_VERTICES and polygon_closed:
                calc_area = _shoelace_area_degrees(coords)
                area_diff_pct = abs(calc_area - plot_area_hectares) / max(plot_area_hectares, 0.0001) * 100
                if area_diff_pct > 10.0:
                    warnings.append(
                        f"Calculated polygon area {calc_area:.2f} ha deviates "
                        f"{area_diff_pct:.1f}% from declared area {plot_area_hectares:.2f} ha "
                        "(tolerance: 10%)."
                    )
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            errors.append(f"Invalid GeoJSON polygon: {exc}")

    return PlotValidationResult(
        plot_id=plot_id,
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        latitude_decimal_places=lat_dp,
        longitude_decimal_places=lon_dp,
        polygon_vertex_count=vertex_count,
        calculated_area_hectares=round(calc_area, 4) if calc_area is not None else None,
        polygon_is_closed=polygon_closed,
    )
```

### 6.6 Joint Value Creation Model

**Model basis:** Open Innovation pipeline ROI — Chesbrough (2003); supplier innovation contribution rate.

```
JVC_Value_USD = Sum_i(Innovation_Pipeline_Value_i * Commercialisation_Rate_i * Supplier_Contribution_Share_i)
```

Where:
- `Innovation_Pipeline_Value_i`: Net present value of innovation project i at risk-adjusted discount rate
- `Commercialisation_Rate_i`: Historical probability of this project type reaching commercial launch
- `Supplier_Contribution_Share_i`: Contractually agreed supplier IP and cost contribution share

```python
# python/14_supplier_development/joint_value_creation.py

from dataclasses import dataclass


@dataclass
class InnovationPipelineItem:
    project_id: str
    description: str
    npv_at_risk_usd: float              # Risk-adjusted NPV of the innovation
    commercialisation_rate: float       # 0–1: historical launch probability for this category
    supplier_contribution_share: float  # 0–1: supplier's contractual share


def compute_jvc_model(pipeline: list[InnovationPipelineItem]) -> dict:
    """
    Joint Value Creation (JVC) model — Open Innovation pipeline.

    Aggregates expected value from all active innovation projects
    weighted by commercialisation probability and supplier contribution.
    """
    total_pipeline_npv = sum(p.npv_at_risk_usd for p in pipeline)
    total_jvc_value = sum(
        p.npv_at_risk_usd * p.commercialisation_rate * p.supplier_contribution_share
        for p in pipeline
    )
    weighted_comm_rate = (
        sum(p.npv_at_risk_usd * p.commercialisation_rate for p in pipeline) / total_pipeline_npv
        if total_pipeline_npv > 0 else 0.0
    )

    return {
        'total_pipeline_npv_usd': round(total_pipeline_npv, 2),
        'expected_jvc_value_usd': round(total_jvc_value, 2),
        'weighted_average_commercialisation_rate': round(weighted_comm_rate, 4),
        'project_count': len(pipeline),
        'projects': [
            {
                'project_id': p.project_id,
                'expected_value_usd': round(
                    p.npv_at_risk_usd * p.commercialisation_rate * p.supplier_contribution_share, 2
                ),
            }
            for p in pipeline
        ],
    }
```

### 6.7 Carbon Price Sensitivity Model

**Regulatory basis:** EU ETS Phase 4 (2021–2030); Carbon Border Adjustment Mechanism (CBAM, Regulation 2023/956/EU effective 2026); SBTi internal carbon price guidance.

```
Carbon_Cost_USD = ETS_Price_USD_per_tonne * Scope3_Category1_Exposure_tCO2e
Carbon_Cost_Sensitivity = d(Cost)/d(ETS_Price) = Scope3_Exposure_tCO2e
```

```python
# python/14_supplier_development/carbon_price_sensitivity.py

import numpy as np
from dataclasses import dataclass


@dataclass
class CarbonPriceSensitivityResult:
    scope3_cat1_exposure_tco2e: float
    ets_price_scenarios: list[float]       # USD/tCO2e
    carbon_cost_scenarios: list[float]     # USD per scenario
    baseline_ets_price_usd: float
    baseline_carbon_cost_usd: float
    sensitivity_usd_per_usd_ets: float    # d(cost)/d(price) = exposure
    cbam_applicable: bool
    cbam_embedded_cost_usd: float


def compute_carbon_price_sensitivity(
    scope3_cat1_exposure_tco2e: float,
    baseline_ets_price_usd: float = 65.0,  # EU ETS approximate 2025 price
    scenarios: list[float] = None,
    cbam_applicable: bool = False,
    cbam_embedded_carbon_tco2e: float = 0.0,
    cbam_price_usd: float = 65.0,
) -> CarbonPriceSensitivityResult:
    """
    Carbon price sensitivity analysis for Scope 3 Category 1 exposure.

    Computes the financial exposure under multiple ETS price scenarios.
    The sensitivity (first derivative) equals the carbon exposure in tCO2e.

    Parameters
    ----------
    scope3_cat1_exposure_tco2e : Total Scope 3 Cat 1 in tCO2e
    baseline_ets_price_usd     : Current EU ETS or internal carbon price (USD/tCO2e)
    scenarios                  : List of ETS price scenarios to evaluate (USD/tCO2e)
    cbam_applicable            : Whether CBAM applies to imported goods
    cbam_embedded_carbon_tco2e : Embedded carbon in CBAM-covered imports (tCO2e)
    cbam_price_usd             : CBAM certificate price (tracks EU ETS)
    """
    if scenarios is None:
        scenarios = [25.0, 50.0, 75.0, 100.0, 150.0, 200.0]

    baseline_cost = scope3_cat1_exposure_tco2e * baseline_ets_price_usd
    cost_scenarios = [scope3_cat1_exposure_tco2e * p for p in scenarios]
    sensitivity = scope3_cat1_exposure_tco2e  # Linear: d(cost)/d(price) = exposure

    cbam_cost = cbam_embedded_carbon_tco2e * cbam_price_usd if cbam_applicable else 0.0

    return CarbonPriceSensitivityResult(
        scope3_cat1_exposure_tco2e=scope3_cat1_exposure_tco2e,
        ets_price_scenarios=scenarios,
        carbon_cost_scenarios=[round(c, 2) for c in cost_scenarios],
        baseline_ets_price_usd=baseline_ets_price_usd,
        baseline_carbon_cost_usd=round(baseline_cost, 2),
        sensitivity_usd_per_usd_ets=round(sensitivity, 2),
        cbam_applicable=cbam_applicable,
        cbam_embedded_cost_usd=round(cbam_cost, 2),
    )
```

---

## 7. Phase 4: ML/AI Pipeline

**Duration:** Weeks 43–56
**Owner:** Data Science Team + ESG Analytics
**Objective:** Deploy five machine learning models that automate ESG monitoring, detect anomalies, and generate real-time risk intelligence.

### 7.1 Graph Neural Network for ESG Risk Propagation

**Problem statement:** ESG risks do not respect tier boundaries. A critical environmental violation at a Tier 3 sub-supplier (e.g., a river pollution incident at a dye house in Bangladesh) can cascade upstream to affect Tier 1 supplier deliveries and ultimately the company's own ESRS E2 (Pollution) disclosure.

**Architecture:** Heterogeneous Graph Attention Network (GAT) with node types {Buyer, Tier1Supplier, Tier2Supplier, Tier3Supplier, RawMaterialSource} and edge types {PURCHASES_FROM, SUB_CONTRACTS_TO, LOCATED_IN_COUNTRY, SHARES_COMMODITY}.

```python
# python/14_supplier_development/ml/gnn_esg_risk.py

import torch
import torch.nn.functional as F
from torch_geometric.nn import GATConv, to_hetero
from torch_geometric.data import HeteroData
from torch_geometric.transforms import ToUndirected
import numpy as np


class ESGRiskGAT(torch.nn.Module):
    """
    Graph Attention Network for ESG risk propagation across supplier tiers.

    Node features (per supplier node):
        - ESG score (0–100)
        - GHG intensity (tCO2e/USD spend)
        - Country risk score (0–1, from WGI / Freedom House)
        - Sector ESG risk index (MSCI ESG sector weight)
        - Audit finding severity (0 = no findings, 1 = critical)
        - EUDR exposure flag (0/1)
        - Days since last audit (normalised)

    Edge features (supply relationship):
        - Spend share (0–1)
        - Relationship depth (tier number)
        - Contract coverage (0/1)

    Output: ESG risk score per node (0–1), higher = higher risk
    """

    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int, heads: int = 4):
        super().__init__()
        self.conv1 = GATConv(in_channels, hidden_channels, heads=heads, dropout=0.3)
        self.conv2 = GATConv(hidden_channels * heads, out_channels, heads=1, concat=False, dropout=0.3)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x, edge_index)
        x = F.elu(x)
        x = F.dropout(x, p=0.3, training=self.training)
        x = self.conv2(x, edge_index)
        return torch.sigmoid(x)  # Output in [0, 1] for risk score


def build_supplier_graph(
    supplier_features: np.ndarray,     # shape (N, 7) — node features
    edge_index: np.ndarray,            # shape (2, E) — supplier relationships
) -> tuple:
    """Build PyTorch Geometric graph from supplier network data."""
    x = torch.tensor(supplier_features, dtype=torch.float)
    ei = torch.tensor(edge_index, dtype=torch.long)
    return x, ei


def train_esg_risk_model(
    model: ESGRiskGAT,
    x: torch.Tensor,
    edge_index: torch.Tensor,
    labels: torch.Tensor,      # Binary: 1 = high risk (from audit outcomes)
    epochs: int = 100,
    lr: float = 0.005,
) -> list[float]:
    """
    Train the ESG risk GNN.

    Uses binary cross-entropy loss.
    Positive labels derived from historical audit Critical/Major findings.
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=5e-4)
    loss_history = []

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        out = model(x, edge_index).squeeze()
        loss = F.binary_cross_entropy(out, labels.float())
        loss.backward()
        optimizer.step()
        loss_history.append(loss.item())

    return loss_history


def infer_risk_scores(
    model: ESGRiskGAT,
    x: torch.Tensor,
    edge_index: torch.Tensor,
) -> np.ndarray:
    """Run inference and return risk scores for all supplier nodes."""
    model.eval()
    with torch.no_grad():
        scores = model(x, edge_index).squeeze().numpy()
    return scores
```

**Deployment:** The model runs weekly against the full supplier graph (maintained in `networkx` for analysis; converted to PyTorch Geometric tensors for inference). Risk score updates trigger ESG_RISK_PROPAGATED domain events captured in the event store.

### 7.2 NLP for ESG Report Analysis

**Problem statement:** Suppliers submit ESG reports aligned to CSRD/ESRS, GRI 2021, and SASB standards. Manual review of a 200-page GRI report to extract ESRS S2 disclosure scores takes an analyst 8–12 hours. An LLM-based pipeline reduces this to under 10 minutes with structured, auditable output.

**Architecture:** BERT-based bi-encoder for section classification + extractive question answering for KPI extraction.

```python
# python/14_supplier_development/ml/nlp_esg_analysis.py

from __future__ import annotations
import json
from dataclasses import dataclass, field
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch


ESRS_SECTIONS = [
    'E1_CLIMATE_CHANGE',
    'E2_POLLUTION',
    'E3_WATER_MARINE',
    'E4_BIODIVERSITY',
    'E5_RESOURCE_USE',
    'S1_OWN_WORKFORCE',
    'S2_VALUE_CHAIN_WORKERS',
    'S3_AFFECTED_COMMUNITIES',
    'S4_CONSUMERS_END_USERS',
    'G1_BUSINESS_CONDUCT',
]

GRI_DISCLOSURES = [
    'GRI_2_9_GOVERNANCE',
    'GRI_205_ANTI_CORRUPTION',
    'GRI_302_ENERGY',
    'GRI_303_WATER',
    'GRI_304_BIODIVERSITY',
    'GRI_305_EMISSIONS',
    'GRI_306_WASTE',
    'GRI_403_OCCUPATIONAL_HEALTH',
    'GRI_405_DIVERSITY',
    'GRI_414_SUPPLIER_SOCIAL',
]


@dataclass
class ESGReportAnalysisResult:
    supplier_id: str
    report_year: int
    esrs_coverage_scores: dict[str, float]    # 0–1 per ESRS standard
    gri_coverage_scores: dict[str, float]     # 0–1 per GRI disclosure
    overall_csrd_alignment_score: float        # 0–1
    overall_gri_alignment_score: float         # 0–1
    sasb_alignment_score: float                # 0–1
    extracted_ghg_scope1_tco2e: float | None
    extracted_ghg_scope2_tco2e: float | None
    extracted_ghg_scope3_tco2e: float | None
    flags: list[str]                           # e.g. 'MISSING_E1_TARGET', 'UNVERIFIED_DATA'


def analyse_esg_report(
    supplier_id: str,
    report_year: int,
    report_text: str,
    model_name: str = 'distilbert-base-uncased',  # OSI: Apache-2.0 via HuggingFace
) -> ESGReportAnalysisResult:
    """
    Analyse a supplier ESG report for CSRD/ESRS, GRI 2021, and SASB alignment.

    Uses a zero-shot classification pipeline to score coverage of each standard's
    required disclosures. Extractive QA extracts quantitative GHG figures.

    Parameters
    ----------
    report_text : Full text of the ESG report (extracted via pdfplumber or pytesseract)
    model_name  : HuggingFace model for classification (must be OSI-licensed)
    """
    classifier = pipeline(
        'zero-shot-classification',
        model=model_name,
        device=0 if torch.cuda.is_available() else -1,
    )
    qa_pipeline = pipeline(
        'question-answering',
        model=model_name,
        device=0 if torch.cuda.is_available() else -1,
    )

    # Truncate to first 2048 tokens per passage (adjust as needed)
    text_chunk = report_text[:4096]

    # Score each ESRS section coverage
    esrs_scores: dict[str, float] = {}
    for section in ESRS_SECTIONS:
        result = classifier(text_chunk, candidate_labels=[section, 'NOT_PRESENT'])
        esrs_scores[section] = result['scores'][0] if result['labels'][0] == section else result['scores'][1]

    # Score GRI disclosure coverage
    gri_scores: dict[str, float] = {}
    for disclosure in GRI_DISCLOSURES:
        result = classifier(text_chunk, candidate_labels=[disclosure, 'NOT_PRESENT'])
        gri_scores[disclosure] = result['scores'][0] if result['labels'][0] == disclosure else result['scores'][1]

    csrd_alignment = float(sum(esrs_scores.values()) / len(esrs_scores))
    gri_alignment  = float(sum(gri_scores.values()) / len(gri_scores))

    # Extractive QA for GHG figures
    def extract_ghg(question: str) -> float | None:
        try:
            ans = qa_pipeline({'question': question, 'context': text_chunk})
            val = float(''.join(c for c in ans['answer'] if c.isdigit() or c == '.'))
            return val if ans['score'] > 0.3 else None
        except Exception:
            return None

    scope1 = extract_ghg("What is the total Scope 1 GHG emissions in tonnes CO2 equivalent?")
    scope2 = extract_ghg("What is the total Scope 2 GHG emissions in tonnes CO2 equivalent?")
    scope3 = extract_ghg("What is the total Scope 3 GHG emissions in tonnes CO2 equivalent?")

    flags = []
    if esrs_scores.get('E1_CLIMATE_CHANGE', 0) < 0.5:
        flags.append('MISSING_E1_TARGET')
    if scope1 is None and scope2 is None:
        flags.append('GHG_DATA_NOT_EXTRACTED')

    return ESGReportAnalysisResult(
        supplier_id=supplier_id,
        report_year=report_year,
        esrs_coverage_scores=esrs_scores,
        gri_coverage_scores=gri_scores,
        overall_csrd_alignment_score=round(csrd_alignment, 4),
        overall_gri_alignment_score=round(gri_alignment, 4),
        sasb_alignment_score=0.0,   # SASB scoring requires industry-specific mapping — extend per sector
        extracted_ghg_scope1_tco2e=scope1,
        extracted_ghg_scope2_tco2e=scope2,
        extracted_ghg_scope3_tco2e=scope3,
        flags=flags,
    )
```

### 7.3 Satellite ML for Supplier Site Monitoring

**Problem statement:** EUDR Article 9 requires demonstration that commodities were not produced on land subject to deforestation after 31 December 2020. Manual plot-level verification across thousands of geo-referenced plots is infeasible. Sentinel-2 satellite imagery (10m resolution, 5-day revisit, free via Copernicus) provides scalable verification.

**Architecture:** Binary change detection using normalised difference vegetation index (NDVI) time-series analysis with scikit-learn RandomForest classifier trained on known deforestation events from Global Forest Watch (GFW) training labels.

```python
# python/14_supplier_development/ml/satellite_monitoring.py

from __future__ import annotations
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SatelliteMonitoringResult:
    plot_id: str
    latitude: float
    longitude: float
    ndvi_baseline: float           # Pre-2021 NDVI (Sentinel-2 Band 8 / Band 4)
    ndvi_current: float            # Current period NDVI
    ndvi_delta: float              # Change in NDVI (negative = vegetation loss)
    deforestation_probability: float  # RandomForest output 0–1
    deforestation_detected: bool   # threshold: > 0.65
    confidence_score: float
    image_date: str                # ISO date of satellite image used
    alert_generated: bool


DEFORESTATION_THRESHOLD = 0.65
NDVI_CRITICAL_LOSS = -0.25         # NDVI drop > 0.25 is indicative of significant vegetation loss


def compute_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
    """
    Compute Normalised Difference Vegetation Index (NDVI).
    NDVI = (NIR - Red) / (NIR + Red)
    Range: [-1, 1]; healthy vegetation > 0.5; deforested < 0.2
    Sentinel-2 bands: Red = B04, NIR = B08
    """
    numerator = nir_band.astype(float) - red_band.astype(float)
    denominator = nir_band.astype(float) + red_band.astype(float)
    denominator[denominator == 0] = np.nan
    return np.where(np.isnan(denominator), np.nan, numerator / denominator)


def extract_plot_ndvi_stats(
    tiff_path: str,
    lat: float,
    lon: float,
    buffer_deg: float = 0.001,    # ~111m buffer
) -> tuple[float, float]:
    """
    Extract mean NDVI statistics for a plot region from a GeoTIFF.
    Assumes multi-band GeoTIFF with Band 1 = Red (B04), Band 2 = NIR (B08).
    Data source: ESA Copernicus Sentinel-2 L2A product (open access, Apache-2.0).
    """
    with rasterio.open(tiff_path) as src:
        window = from_bounds(
            lon - buffer_deg, lat - buffer_deg,
            lon + buffer_deg, lat + buffer_deg,
            src.transform,
        )
        red = src.read(1, window=window).astype(float)
        nir = src.read(2, window=window).astype(float)

    ndvi = compute_ndvi(red, nir)
    valid = ndvi[~np.isnan(ndvi)]
    return float(np.mean(valid)), float(np.std(valid))


def classify_deforestation(
    ndvi_baseline: float,
    ndvi_current: float,
    model: RandomForestClassifier,
    scaler: StandardScaler,
) -> tuple[float, bool]:
    """
    Classify deforestation using a trained RandomForest model.
    Features: [ndvi_baseline, ndvi_current, ndvi_delta, ndvi_delta_normalised]
    """
    ndvi_delta = ndvi_current - ndvi_baseline
    features = np.array([[ndvi_baseline, ndvi_current, ndvi_delta, ndvi_delta / max(abs(ndvi_baseline), 0.001)]])
    scaled = scaler.transform(features)
    prob = model.predict_proba(scaled)[0][1]  # Probability of class=1 (deforestation)
    return float(prob), prob > DEFORESTATION_THRESHOLD
```

### 7.4 Anomaly Detection for ESG KPI Manipulation

**Problem statement:** Greenwashing and data manipulation are documented risks in supplier ESG self-reporting. A 2023 KPMG study found that 21% of supplier ESG self-assessments contained material inaccuracies when cross-validated against satellite and regulatory data.

**Architecture:** Isolation Forest for multivariate anomaly detection on the ESG KPI time series; LSTM Autoencoder for temporal sequence anomaly detection.

```python
# python/14_supplier_development/ml/esg_anomaly_detection.py

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from dataclasses import dataclass


@dataclass
class AnomalyDetectionResult:
    supplier_id: str
    is_anomalous: bool
    anomaly_score: float           # Isolation Forest: negative = more anomalous
    anomalous_features: list[str]  # Which KPIs triggered the anomaly
    confidence: float              # 0–1
    recommended_action: str        # 'ESCALATE_AUDIT' | 'REVIEW' | 'MONITOR'


def detect_esg_kpi_anomalies(
    kpi_matrix: pd.DataFrame,
    contamination: float = 0.05,   # Expected fraction of anomalous suppliers
    random_state: int = 42,
) -> list[AnomalyDetectionResult]:
    """
    Multivariate anomaly detection across ESG KPI time-series data.

    Input DataFrame columns (one row per supplier per year):
        supplier_id, year, esg_score, ghg_intensity, water_intensity,
        waste_recycling_rate, audit_findings_critical, ltir, gender_pay_gap_pct

    Uses IsolationForest — robust to high-dimensional sparse data common in ESG.
    Reference: Liu, Ting, Zhou (2008). Isolation Forest. ICDM.
    """
    feature_cols = [
        'esg_score', 'ghg_intensity', 'water_intensity',
        'waste_recycling_rate', 'audit_findings_critical', 'gender_pay_gap_pct',
    ]
    available = [c for c in feature_cols if c in kpi_matrix.columns]
    X = kpi_matrix[available].fillna(kpi_matrix[available].median())

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    iso = IsolationForest(contamination=contamination, random_state=random_state, n_estimators=200)
    predictions = iso.fit_predict(X_scaled)
    scores = iso.score_samples(X_scaled)

    results = []
    for i, row in kpi_matrix.iterrows():
        is_anomalous = predictions[i] == -1
        score = float(scores[i])
        anomalous_features: list[str] = []

        if is_anomalous:
            z_scores = np.abs(X_scaled[i])
            for j, feat in enumerate(available):
                if j < len(z_scores) and z_scores[j] > 2.5:
                    anomalous_features.append(feat)

        action = 'MONITOR'
        confidence = max(0.0, min(1.0, (abs(score) - 0.05) / 0.45))
        if is_anomalous:
            action = 'ESCALATE_AUDIT' if score < -0.3 else 'REVIEW'

        results.append(AnomalyDetectionResult(
            supplier_id=str(row.get('supplier_id', i)),
            is_anomalous=is_anomalous,
            anomaly_score=round(score, 6),
            anomalous_features=anomalous_features,
            confidence=round(confidence, 4),
            recommended_action=action,
        ))

    return results
```

### 7.5 Computer Vision for Audit Evidence Verification

**Problem statement:** Suppliers submit photographic audit evidence (facility conditions, safety signage, certifications, PPE compliance). Manual review is time-intensive and inconsistent. YOLOv8 (Ultralytics, AGPL-3.0) enables automated object detection on audit photographs.

**Architecture:** YOLOv8 fine-tuned on a labelled dataset of supply chain audit images. Detection classes include: {fire_extinguisher, emergency_exit_sign, ppe_helmet, ppe_vest, blocked_exit, chemical_storage_label, first_aid_kit, electrical_hazard_exposed}.

```python
# python/14_supplier_development/ml/cv_audit_verification.py

from __future__ import annotations
from ultralytics import YOLO  # AGPL-3.0 — listed in approved libraries
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_SAFETY_OBJECTS = {
    'fire_extinguisher', 'emergency_exit_sign', 'ppe_helmet', 'first_aid_kit',
}
PROHIBITED_CONDITIONS = {
    'blocked_exit', 'electrical_hazard_exposed', 'chemical_unlabelled',
}

CONFIDENCE_THRESHOLD = 0.60


@dataclass
class AuditImageResult:
    image_path: str
    detected_objects: dict[str, float]  # class_name -> max confidence score
    required_present: list[str]
    required_missing: list[str]
    prohibited_detected: list[str]
    compliance_score: float             # 0–1
    severity: str                       # 'PASS' | 'MINOR' | 'MAJOR' | 'CRITICAL'


def verify_audit_images(
    image_paths: list[str],
    model_weights: str = 'python/14_supplier_development/ml/weights/yolov8_audit.pt',
) -> list[AuditImageResult]:
    """
    Run YOLOv8 object detection on audit evidence photographs.

    The model must be fine-tuned on supply chain audit imagery.
    Pre-trained YOLOv8n weights are used as initialisation (transfer learning).

    Parameters
    ----------
    image_paths   : List of absolute paths to audit images
    model_weights : Path to fine-tuned YOLOv8 weights (.pt file)
    """
    model = YOLO(model_weights)
    results_list = []

    for img_path in image_paths:
        results = model.predict(img_path, conf=CONFIDENCE_THRESHOLD, verbose=False)

        detected: dict[str, float] = {}
        if results and results[0].boxes is not None:
            for box in results[0].boxes:
                cls_name = model.names[int(box.cls)]
                conf_val = float(box.conf)
                detected[cls_name] = max(detected.get(cls_name, 0.0), conf_val)

        required_present = [r for r in REQUIRED_SAFETY_OBJECTS if r in detected]
        required_missing = [r for r in REQUIRED_SAFETY_OBJECTS if r not in detected]
        prohibited_found  = [p for p in PROHIBITED_CONDITIONS if p in detected]

        compliance_pct = len(required_present) / len(REQUIRED_SAFETY_OBJECTS)

        if prohibited_found:
            severity = 'CRITICAL'
        elif len(required_missing) > 2:
            severity = 'MAJOR'
        elif len(required_missing) > 0:
            severity = 'MINOR'
        else:
            severity = 'PASS'

        results_list.append(AuditImageResult(
            image_path=img_path,
            detected_objects=detected,
            required_present=required_present,
            required_missing=required_missing,
            prohibited_detected=prohibited_found,
            compliance_score=round(compliance_pct, 4),
            severity=severity,
        ))

    return results_list
```

---

## 8. Phase 5: Integration and Automation

**Duration:** Weeks 57–66
**Owner:** Integration Architecture Team
**Objective:** Connect all models and aggregates to external ESG data providers and regulatory platforms via standardised API adapters.

### 8.1 EcoVadis Integration

EcoVadis provides supplier sustainability ratings on a 0–100 scale across four themes (Environment, Labour and Human Rights, Ethics, Sustainable Procurement). The EcoVadis API v3 exposes supplier scorecards with ISO 8601 timestamps and GTIN-mapped supplier identifiers.

```typescript
// src/departments/14-supplier-development/adapters/EcoVadisAdapter.ts

import { ESGScorecard } from '../domain/ESGScorecard';

interface EcoVadisScorecard {
  supplierId: string;
  scoreDate: string;
  totalScore: number;
  environmentScore: number;
  labourHumanRightsScore: number;
  ethicsScore: number;
  sustainableProcurementScore: number;
  medal: 'PLATINUM' | 'GOLD' | 'SILVER' | 'BRONZE' | 'NONE';
}

export class EcoVadisAdapter {
  private readonly baseUrl: string;
  private readonly apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async fetchScorecard(supplierId: string): Promise<EcoVadisScorecard> {
    // Exponential backoff retry — max 5 attempts
    let delay = 1_000;
    for (let attempt = 1; attempt <= 5; attempt++) {
      try {
        const response = await fetch(
          `${this.baseUrl}/scorecards/${supplierId}`,
          {
            headers: {
              'Authorization': `Bearer ${this.apiKey}`,
              'Accept': 'application/json',
              'X-Idempotency-Key': `ecovadis-${supplierId}-${new Date().toISOString().slice(0, 10)}`,
            },
          }
        );
        if (!response.ok) {
          if (response.status === 429 || response.status >= 500) {
            await new Promise(r => setTimeout(r, delay));
            delay *= 2;
            continue;
          }
          throw new Error(`EcoVadis API error: ${response.status} ${response.statusText}`);
        }
        return response.json() as Promise<EcoVadisScorecard>;
      } catch (err) {
        if (attempt === 5) throw err;
        await new Promise(r => setTimeout(r, delay));
        delay *= 2;
      }
    }
    throw new Error('EcoVadis API: maximum retry attempts exceeded.');
  }

  mapToESGScorecard(ev: EcoVadisScorecard): Partial<ESGScorecard> {
    return {
      ecoVadisScore: ev.totalScore,
      externalVerification: true,
      verifierName: 'EcoVadis',
      assuranceStandard: 'EcoVadis Methodology 2024',
    };
  }
}
```

### 8.2 CDP Integration

CDP Climate, Water, and Forest questionnaire scores are consumed via the CDP API to populate the `cdpClimateScore` field in `ESGScorecard`. CDP uses a letter scale (A, A-, B, B-, C, D, D-, F) which is mapped to a numeric proxy for trend analysis.

### 8.3 Sphera Carbon Accounting Integration

Sphera (formerly GaBi) provides life-cycle assessment (LCA) emission factors and Scope 3 emission calculation services. Integration is via Sphera's REST API with OAuth 2.0 client-credentials flow. Emission factors are pulled quarterly and cached in the local `GHGLineItem` store to ensure audit trail integrity.

### 8.4 TRACES NT (EUDR) Integration

The European Commission TRACES NT (New Technology) platform is the official system for EUDR due diligence statements. The API (OpenAPI 3.0, authenticated via EU Login eID) accepts GeoJSON production plot data and returns a due diligence statement reference number that must be attached to each import consignment.

```typescript
// src/departments/14-supplier-development/adapters/TracesNtAdapter.ts

import { ProductionPlot, EUDRDueDiligence } from '../domain/EUDRDueDiligence';

export class TracesNtAdapter {
  async submitDueDiligenceStatement(
    plots: ProductionPlot[],
    operatorEuid: string,
  ): Promise<{ statementId: string; referenceNumber: string }> {
    // POST /api/eudr/due-diligence-statements
    // Body: GeoJSON FeatureCollection with EUDR commodity metadata
    const payload = {
      operator: { euid: operatorEuid },
      plots: plots.map(p => ({
        plotId: p.plotId,
        commodity: p.commodity,
        country: p.countryCode,
        geolocation: p.polygonGeoJson
          ? { type: 'Polygon', geojson: JSON.parse(p.polygonGeoJson) }
          : { type: 'Point', latitude: p.latitude, longitude: p.longitude },
        areaHectares: p.plotAreaHectares,
      })),
    };
    // Implementation: fetch with exponential backoff
    throw new Error('TRACES NT integration requires EU Login eID credentials — configure in environment.');
  }
}
```

### 8.5 GHG Protocol Tools and CSRD ESRS XBRL Templates

GHG Protocol calculation tools are consumed as reference data libraries. The EFRAG ESRS XBRL taxonomy (published 2024) defines the digital reporting format for CSRD disclosures. This module generates ESRS XBRL-compliant output files by mapping `ESGScorecard` and `GHGInventory` aggregate fields to the XBRL element identifiers specified in the EFRAG taxonomy.

### 8.6 UN Global Compact Reporting

The UNGC Communication on Progress (COP) requires annual disclosure aligned to the ten principles. The UNGC API (REST, OAuth 2.0) provides participant status verification and COP submission endpoints. Supplier UNGC signatory status is stored in `Supplier.certifications` in the existing supplier master.

---

## 9. Phase 6: Continuous Improvement

**Duration:** Weeks 67–72 and ongoing
**Owner:** Sustainability Director + Supply Chain Analytics
**Objective:** Establish closed-loop performance management that continuously elevates supplier ESG standards.

### 9.1 Quarterly ESG Business Reviews

Tier 1 High suppliers participate in quarterly ESG Business Reviews (EBRs), modelled on the Operational Business Review cadence already established for the supplier scorecard (OTD/OTIF). The ESG EBR adds the following standing agenda items:

1. GHG trajectory review vs. SBTi 2030 path (using `compute_sbti_trajectory()` output)
2. ESG score trend (rolling 4-quarter, pillar-level breakdown)
3. EUDR plot validation status and satellite imagery alerts
4. Open corrective action requests (CARs) from audit findings
5. Joint Value Creation pipeline milestone review

### 9.2 Supplier Capability Building

Development programmes are assigned using a capability matrix:

| ESG Score Band | GHG Data Quality | Recommended Intervention |
|---|---|---|
| >= 70 | DQ Score 1–2 | Advanced engagement: SBTi target-setting support |
| 55–69 | DQ Score 3 | Collaborative: GHG data collection workshop |
| 40–54 | DQ Score 4–5 | Foundational: Sustainability basics training, SAQ assistance |
| < 40 | Any | Conditional status: mandatory improvement plan or disqualification review |

### 9.3 Model Retraining Schedule

| ML Model | Retraining Frequency | Trigger |
|---|---|---|
| GNN ESG Risk | Monthly | New audit outcomes added to training set |
| NLP ESG Report | Quarterly | New ESRS/GRI standard releases |
| Satellite Deforestation | Seasonal (4x/year) | New Sentinel-2 seasonal composite available |
| Anomaly Detection (IsolationForest) | Quarterly | After annual ESG reporting cycle |
| CV Audit Evidence | Semi-annual | New audit images labelled and validated |

---

## 10. Technology Stack and Architecture

### 10.1 Module Architecture

```
src/departments/14-supplier-development/
├── domain/
│   ├── ESGScorecard.ts
│   ├── GHGInventory.ts
│   ├── EUDRDueDiligence.ts
│   ├── SupplierDevelopmentProgram.ts
│   ├── JointValueCreationPipeline.ts
│   └── ESGEvents.ts
├── adapters/
│   ├── EcoVadisAdapter.ts
│   ├── CDPAdapter.ts
│   ├── SpheraAdapter.ts
│   ├── TracesNtAdapter.ts
│   └── UNGCAdapter.ts
├── application/
│   ├── ESGScorecardService.ts
│   ├── GHGInventoryService.ts
│   └── EUDRComplianceService.ts
└── README.md

python/14_supplier_development/
├── esg_scoring.py
├── ghg_scope3_cat1.py
├── sbti_trajectory.py
├── sdp_roi.py
├── eudr_plot_validation.py
├── joint_value_creation.py
├── carbon_price_sensitivity.py
└── ml/
    ├── gnn_esg_risk.py
    ├── nlp_esg_analysis.py
    ├── satellite_monitoring.py
    ├── esg_anomaly_detection.py
    ├── cv_audit_verification.py
    └── weights/           # Model weights (git-lfs tracked)
```

### 10.2 Data Flow Architecture

```
External Sources                Platform Event Store           Analytics Output
─────────────────               ──────────────────────         ────────────────
EcoVadis API     ──── adapter ──> ESG_SCORECARD_CREATED  ──>   ESG Dashboard
CDP API          ──── adapter ──> GHG_INVENTORY_SUBMITTED ──>  CSRD XBRL Report
Sentinel-2       ──── rasterio -> EUDR_DEFORESTATION_DET  ──>  EUDR DDS (TRACES)
Sphera           ──── adapter ──> GHG_VERIFICATION_DONE   ──>  SBTi Progress Report
TRACES NT        ──── adapter ──> EUDR_PLOT_REGISTERED    ──>  Procurement Gate
```

---

## 11. Change Management and Training

### 11.1 Stakeholder Map

| Stakeholder | Interest | Change Impact | Engagement Strategy |
|---|---|---|---|
| CPO / Procurement | ESG supplier gate criteria | HIGH | Executive sponsor; monthly steering |
| Sustainability Director | CSRD reporting obligation | HIGH | Product owner; daily engagement |
| Legal / Compliance | EUDR enforcement risk | HIGH | Weekly legal review |
| Category Managers | Additional supplier onboarding burden | MEDIUM | Training programme; tooling simplification |
| Finance Controllers | Carbon cost exposure (CBAM) | MEDIUM | Monthly carbon P&L briefing |
| Suppliers (Tier 1 High) | Data submission requirements | HIGH | Supplier portal training; dedicated helpdesk |
| Internal Auditors | Evidence assurance | MEDIUM | Audit methodology alignment workshop |

### 11.2 Training Programme

**Module 1 — ESG Fundamentals (4 hours, all procurement staff):**
GHG Protocol basics, CSRD double-materiality concept, EUDR commodity scope, EcoVadis rating methodology.

**Module 2 — Platform Operations (8 hours, category managers):**
Using the SAQ workflow, interpreting ESG scorecards, escalation paths for CAR management, EUDR plot registration in the portal.

**Module 3 — Advanced Analytics (16 hours, sustainability analysts):**
Interpreting GNN risk scores, reading satellite deforestation alerts, anomaly detection flag investigation, SBTi trajectory analysis.

**Module 4 — CSRD Reporting (8 hours, finance and sustainability):**
ESRS XBRL taxonomy, double-materiality assessment methodology, EFRAG ESRS 1 general requirements, assurance requirements under ISAE 3000.

---

## 12. Implementation KPIs

### 12.1 Leading Indicators (Process)

| KPI | Baseline (Phase 0) | Phase 1 Target | Phase 2 Target | Phase 3 Target |
|---|---|---|---|---|
| Supplier ESG data coverage (T1 High) | <30% | 70% | 90% | 100% |
| GHG inventory coverage — T1 High | <20% | 60% | 85% | 100% |
| EUDR plot registration rate | 0% | 50% | 80% | 100% |
| EcoVadis assessment rate (T1 High) | <40% | 70% | 90% | 100% |
| SAQ completion rate — T2 Medium | 0% | 50% | 75% | 90% |
| Active supplier development programmes | 0 | 10 | 25 | 40+ |

### 12.2 Lagging Indicators (Outcome)

| KPI | Year 1 Target | Year 2 Target | Year 3 Target | World-Class Benchmark |
|---|---|---|---|---|
| Weighted avg supplier ESG score | 52 | 62 | 72 | >= 75 (EcoVadis Silver) |
| Scope 3 Cat 1 reduction vs. baseline | -5% | -12% | -22% | -42% by 2030 (SBTi) |
| % suppliers with SBTi-aligned targets | 5% | 15% | 30% | >50% (SBTi SET target) |
| Suppliers rated EUDR-compliant | 50% | 80% | 100% | 100% (regulatory) |
| CSRD ESRS data completeness | 40% | 75% | 95% | 100% |
| JVC pipeline value (USD) | $500K | $2M | $5M | >$10M |
| SDP average ROI | — | 180 bps | 320 bps | >400 bps |

---

## 13. Risk and Mitigation

| Risk | Likelihood | Impact | Mitigating Actions |
|---|---|---|---|
| Supplier data quality too poor for activity-based GHG | HIGH | HIGH | Fallback to spend-based; engage EcoVadis data sharing; DQ score governance |
| EUDR enforcement delayed beyond mid-2025 | MEDIUM | LOW | Continue readiness; no regulatory exposure from early compliance |
| EcoVadis API rate limits in bulk onboarding phase | MEDIUM | MEDIUM | Batch requests; prioritise T1 High suppliers; cache responses |
| Satellite imagery cloud cover masking deforestation | MEDIUM | HIGH | Use Sentinel-1 SAR (cloud-penetrating) as backup; seasonal composites |
| GNN training data insufficient for sub-tier visibility | HIGH | MEDIUM | Start with T1/T2 graph; incrementally expand as data collected |
| CSRD XBRL taxonomy changes between EU adoption and filing | LOW | MEDIUM | Subscribe to EFRAG taxonomy update notifications; versioned XBRL output |
| CBAM price volatility creating P&L uncertainty | MEDIUM | HIGH | Carbon price sensitivity scenarios in quarterly finance reporting |
| Supplier resistance to data disclosure | HIGH | HIGH | Contractual ESG disclosure clauses in new PO templates; incentive structures |
| Model bias in NLP ESG analysis (language bias) | MEDIUM | MEDIUM | Multilingual model fine-tuning; human review for < 0.60 confidence output |
| EUDR deforestation algorithm false positives | MEDIUM | HIGH | Dual-model validation (NDVI + ML); human review gate before supplier penalty |

---

## 14. Timeline Summary

| Phase | Weeks | Key Deliverables | Owner |
|---|---|---|---|
| Phase 0 — Assessment | 1–6 | Supply base segmentation, AS-IS data gap, regulatory calendar | CPO + Sustainability |
| Phase 1 — Foundation | 7–18 | ESGScorecard, GHGInventory, EUDRDueDiligence aggregates; Event Store integration | Dev Team + Arch |
| Phase 2 — Process | 19–30 | SAQ workflow, supplier assessment gate, SDP management, reporting baseline | Supplier Dev Lead |
| Phase 3 — Math Models | 31–42 | All 7 Python models deployed and unit-tested; TypeScript orchestration | Quant Analytics |
| Phase 4 — ML/AI | 43–56 | GNN, NLP, Satellite, Anomaly, CV models trained, validated, deployed | Data Science |
| Phase 5 — Integration | 57–66 | EcoVadis, CDP, Sphera, TRACES NT, UNGC adapters live; CSRD XBRL output | Integration Arch |
| Phase 6 — CI | 67–72 | EBR cadence live, model retraining pipelines, capability building programme | All |
| Steady State | 73+ | Quarterly model refresh; annual CSRD filing; SBTi progress reporting | Sustainability Ops |

**Total implementation duration:** 18 months (72 weeks)
**Recommended team size:** 2 domain developers (TypeScript), 2 data scientists (Python), 1 integration architect, 1 sustainability SME, 0.5 project manager.

---

## 15. References

### Regulatory Frameworks
- EU Corporate Sustainability Reporting Directive (CSRD): Directive 2022/2464/EU, OJ L 322, 16.12.2022
- EU Corporate Sustainability Due Diligence Directive (CSDDD): Directive 2024/1760/EU
- EU Deforestation Regulation (EUDR): Regulation 2023/1115/EU, OJ L 150, 09.06.2023
- EU Carbon Border Adjustment Mechanism (CBAM): Regulation 2023/956/EU
- EU Emissions Trading System Phase 4: Directive 2018/410/EU
- Germany Supply Chain Due Diligence Act (LkSG): BGBl. I 2021, Nr. 46
- UK Modern Slavery Act 2015, Section 54

### Standards and Methodologies
- EFRAG European Sustainability Reporting Standards (ESRS): EFRAG SRB, 2023
- GHG Protocol Corporate Value Chain (Scope 3) Standard: WBCSD/WRI, 2011
- GHG Protocol Corporate Accounting and Reporting Standard: WBCSD/WRI, 2004 (revised)
- SBTi Corporate Net-Zero Standard v1.1: Science Based Targets initiative, 2023
- SBTi Scope 3 Supplier Engagement Guidance: Science Based Targets initiative, 2022
- GRI Standards 2021: Global Reporting Initiative, 2021
- SASB Industry Standards: ISSB (formerly SASB), 2018–2023
- ISO 14001:2015 Environmental Management Systems
- ISO 14064-1:2018 GHG Quantification and Reporting
- ISO 14064-3:2019 GHG Verification and Validation
- ISO 20400:2017 Sustainable Procurement Guidance
- ISO 45001:2018 Occupational Health and Safety
- ISO 37001:2016 Anti-Bribery Management Systems
- AA1000 Assurance Standard v3: AccountAbility, 2020
- ISAE 3000 (Revised): International Auditing and Assurance Standards Board, 2013
- SMETA Best Practice Guidance: Sedex, 2023
- EcoVadis Sustainability Assessment Methodology 2024

### Data Sources and Tools
- Copernicus Sentinel-2 Mission: ESA / EU Copernicus Programme (open access)
- Global Forest Watch (GFW): World Resources Institute (open access)
- TRACES NT Platform: European Commission DG SANTE
- USEEIO v2.0: US EPA (public domain)
- Exiobase v3.8: Netherlands Environmental Assessment Agency (open access)
- DEFRA UK Government GHG Conversion Factors 2025
- EPA eGRID 2024: US Environmental Protection Agency

### Academic and Practitioner Literature
- Chopra, S. & Meindl, P. (2016). *Supply Chain Management* (6th ed.). Pearson.
- Chesbrough, H. (2003). *Open Innovation*. Harvard Business School Press.
- Eccles, R.G. & Krzus, M.P. (2010). *One Report: Integrated Reporting for a Sustainable Strategy*. Wiley.
- Liu, F.T., Ting, K.M. & Zhou, Z.H. (2008). Isolation Forest. *Proceedings of ICDM 2008*.
- Veličković, P. et al. (2018). Graph Attention Networks. *ICLR 2018*.
- McKinsey Sustainability (2023). *The ESG Premium: Rethinking the Value of Sustainability*.
- Gartner Supply Chain Research (2024). *Supplier Development ROI: Benchmarks and Best Practices*.
- KPMG (2023). *Survey of Sustainability Reporting 2022*.
- S&P Global Trucost (2024). *Corporate ESG and Cost of Capital Analysis*.
- IPCC AR6 Working Group I (2021). *The Physical Science Basis*.
- UN Global Compact (2023). *Communication on Progress Framework*.
