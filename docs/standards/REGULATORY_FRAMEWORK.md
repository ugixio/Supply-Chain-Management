# Regulatory & Standards Framework

> **What this document is.** The reference list behind the standards table in `CLAUDE.md`: every
> external source this context relies on, what it fixes, and **when it was last verified**. Nothing
> here is implemented — this repository holds knowledge, not a supply-chain application (ADR-0037).
>
> **Half-life matters.** The ISO and GS1 entries change on a multi-year cycle. The EU entries have
> changed **three times in eighteen months**, and this document was wrong about CSDDD on three
> separate points until 2026-07-27. Treat any entry older than a year as unverified, and re-read the
> instrument rather than a summary of it.

**Last full review: 2026-07-27.**

---

## Standards

### ISO 28000:2022 — Supply-chain security management
Published 15 March 2022, replacing ISO 28000:2007. A management-system standard for security in any
supply chain, applicable to organisations of any type or size. Certification is per organisation and
**expires** — a certificate without a validity check is decoration.
*Verified 2026-07-27.*

### ISO 9001:2015 — Quality management systems
The clauses this context leans on: **§8.4** control of externally provided processes and products ·
**§8.5.2** identification and traceability · **§8.6** release of products and services · **§8.7**
control of nonconforming outputs · **§9.1.3** analysis and evaluation · **§10.2** nonconformity and
corrective action, whose §10.2.1 effectiveness-review requirement is **QMS-R8**.
A revision (ISO 9001:2026) has been in preparation with a customary three-year transition; **confirm
its publication status before relying on either edition**, and note that a transition period means
both editions are live for certified organisations.
*Verified 2026-07-27.*

### ISO 2859-1 — Sampling procedures for inspection by attributes
The single-sampling plans, inspection levels and switching rules. The **plan is fixed** by the
standard's tables (lot size × inspection level → code letter → sample size, `Ac`, `Re`); the **AQL is
a contract term** the project supplies. Plans are read, never interpolated (**QMS-R5**).
*Verified 2026-07-27.*

### GS1 General Specifications v23.0
**GTIN** (14 digits) · **GLN** (13) · **SSCC** (18) · **GSIN**, all sharing the mod-10 check digit
with weights 3 and 1. Application identifiers used here include **AI(17)** expiry date.
GS1 has a **2027 "Sunrise"** for 2D barcodes (Digital Link / QR) at retail point of sale — a
migration date, not a compliance deadline; verify the current scope with GS1 directly.
*Verified 2026-07-27.*

### UN/ECE Recommendation 20 — Units of measure
The unit codes GS1 and UN/EDIFACT both reference: `KGM`, `LTR`, `MTR`, `MTK`, `MTQ`, `EA`, `BX`,
`PL`, `DZN`, `HUR`. **Not** `KG`, `L`, `M` — that shorthand looks plausible and fails conformance
silently, which is why it is named as an anti-pattern in `CLAUDE.md`.
*Verified 2026-07-27.*

### ISO 8601-1:2019 · ISO 4217 · ISO 3166-1
Dates and instants (`YYYY-MM-DD`, UTC instants — **SCM-R9**); currency codes and their **minor
units**, which decide where money rounds; country codes, which every trade and due-diligence
instrument below is expressed in.
*Verified 2026-07-27.*

### UN/EDIFACT — message semantics
**ORDERS** purchase order · **ORDRSP** order response · **DESADV** despatch advice · **RECADV**
receiving advice · **INVOIC** invoice. What the context takes from these is the *semantics* of each
document and the fact that a receiving advice is a distinct document from an invoice — not a
transport binding.
*Verified 2026-07-27.*

### Incoterms® 2020 (ICC, effective 1 January 2020)
Eleven rules. **DPU replaced DAT** (delivery at any place, not only a terminal), and security-related
costs are explicitly allocated. **Four are sea-and-inland-waterway only — `FAS`, `FOB`, `CFR`,
`CIF`** — so naming one for air or road freight is an error, not a shorthand (**LOG-R1**).
Incoterms are revised roughly once a decade; the 2020 edition is current.
*Verified 2026-07-27.*

### IEEE 754-2019 §4.3.3 — `roundTiesToEven`
The tie-breaking rule for monetary rounding (**SCM-R14**). Sum-preserving apportionment is an
arithmetic identity, not a preference.
*Verified 2026-07-27.*

### IAS 2 — Inventories
Cost is the **lower of cost and net realisable value** (§§9–11, 25); **LIFO is not permitted**; only
**non-recoverable** taxes capitalize into inventory cost (§11). FIFO and weighted average are both
permitted, so which one applies is a project's accounting policy — but it must be disclosed with any
valuation figure (**FIN-R4/R5**).
*Verified 2026-07-27.*

### SCOR Digital Standard (ASCM, 2019)
Six level-1 processes: **Plan · Source · Make · Deliver · Return · Enable**, with level-2
configurations (P1–P5, S1–S3, D1–D4, R1–R5, E1–E8) and level-3 activities. Level 4 is
company-specific and therefore outside this context by definition. SCOR supplies a **process
taxonomy and metric definitions**; the benchmark values published alongside it are illustrations, not
requirements.
*Verified 2026-07-27.*

---

## Law

> Dates below are the ones that bind. Where an instrument has been amended, **the amending
> instrument is named** — citing only the original is how a superseded threshold survives.

### EU Corporate Sustainability Due Diligence Directive (CSDDD)
**Directive (EU) 2024/1760**, as amended by **Directive (EU) 2026/470** ("Omnibus I", OJ 26 February
2026, in force 18 March 2026).

The amendment **replaced the original three-phase scope with a single band**:

| | Threshold | Applies from |
|---|---|---|
| EU undertakings | **> 5,000 employees *and* > €1,500m net worldwide turnover** (both tests) | **26 July 2029** |
| Non-EU undertakings | **> €1,500m net turnover generated in the EU** | **26 July 2029** |

- **Member State transposition** of the amended provisions: **26 July 2028**.
- Scope narrowed from roughly 13,000 undertakings to roughly **6,000**.
- **Penalties: capped at 3%** of net worldwide turnover (reduced from the original 5% floor on the
  maximum). Under the risk-based prioritisation the directive requires, failing to address a *less
  significant* adverse impact does not itself attract a penalty.
- **The harmonised EU-wide civil liability regime was deleted.** Whether non-compliance creates civil
  liability is now a Member State question — so exposure genuinely differs by jurisdiction.
- **Documentation retention: at least 5 years** (Art. 23) — **SCM-R7**. Longer is a project's choice;
  shorter is unlawful.

> The earlier 2027 / 2028 / 2029 phase-in at 5,000 / 3,000 / 1,000 employees is **superseded law**.
> This document asserted it until 2026-07-27.

*Verified 2026-07-27.*

### EU Corporate Sustainability Reporting Directive (CSRD)
**Directive (EU) 2022/2464**, also amended by **Directive (EU) 2026/470**, which narrowed scope and
adjusted timing. Relevant here because a due-diligence disclosure and a sustainability report draw on
the same supplier evidence. **Check the amended scope before assuming a company reports at all.**
*Verified 2026-07-27.*

### EU Deforestation Regulation (EUDR)
**Regulation (EU) 2023/1115**, as revised (postponement and simplification agreed December 2025).

- Applies from **30 December 2026** for large and medium operators, and for micro and small operators
  already covered by the EU Timber Regulation; from **30 June 2027** for other micro and small
  operators.
- Country risk classification is **read from the Commission's benchmarking**, never hardcoded — it is
  revised, and a stale list is wrong in the direction of under-diligence (**SDV-R6**).
- The Commission adopted further measures on **13 July 2026**: a delegated act updating the product
  scope, and an implementing act on the information system for due-diligence statements. **Re-check
  the product scope against the current annex** — it has moved.

*Verified 2026-07-27.*

### EU Carbon Border Adjustment Mechanism (CBAM)
**Regulation (EU) 2023/956**, as amended by the 2025 simplification package (OJ 17 October 2025, in
force 20 October 2025).

- **Definitive regime from 1 January 2026.**
- **De minimis: 50 tonnes per importer per year**, replacing the former €150-per-consignment trigger.
- **Quarterly minimum certificate holding: 50%** of cumulative embedded emissions (reduced from the
  original 80%) — and this obligation bites **from 2027**, because certificate **sales begin February
  2027** for 2026 imports.
- Annual declaration and surrender: **30 September** of the following year. 2026 liability therefore
  accrues before any certificate can be bought — it is a cost to accrue, not to pay.

*Verified 2026-07-27.*

### US Uyghur Forced Labor Prevention Act (UFLPA)
**Pub. L. 117-78**, signed 23 December 2021, enforcement from 21 June 2022. A **rebuttable
presumption** that goods mined, produced or manufactured wholly or in part in the XUAR — or by listed
entities — are made with forced labour and are barred from entry. **No de minimis**: trace content
triggers it. Rebuttal requires **clear and convincing** evidence (**SCM-R6**).
Because the presumption reaches *any input*, tier-1-only visibility is a decision to accept exposure.
The UFLPA Entity List is revised; read it, do not cache it.
*Verified 2026-07-27.*

### EU REACH — Regulation (EC) No 1907/2006
Registration from **1 tonne/year** per substance per registrant. For substances of very high concern
in articles: **above 0.1% w/w** triggers the Art. 33 communication duty and Art. 7(2) ECHA
notification (**CMP-R3**). The **Candidate List is updated about twice a year**, so a one-time screen
expires — the re-screening cadence is the project's, the duty is not.
*Verified 2026-07-27.*

### German Supply Chain Act (LkSG)
In force 1 January 2023; **≥ 1,000 employees** in Germany since January 2024. It does not disappear
when the CSDDD applies: national law and the directive coexist, and the amended CSDDD timing means
LkSG obligations bind **years earlier** than CSDDD compliance for most companies.
*Verified 2026-07-27.*

### UK Modern Slavery Act 2015 — Section 54
Turnover **≥ £36m** and carrying on business in the UK → an annual transparency statement, approved
by the board and signed by a director. A statement saying "we took no steps" is compliant; the
obligation is to publish, not to act.
*Verified 2026-07-27.*

### US Uniform Commercial Code, Article 2
A **quantity term must be stated** for an enforceable agreement to buy (§2-201) — **PRC-R1**; other
terms may be supplied by the code. §2-615 excuse by failure of presupposed conditions is the
force-majeure analogue.
*Verified 2026-07-27.*

### Basel Convention — transboundary movement of hazardous wastes
Applies to hazardous waste crossing borders: **Prior Informed Consent** before shipment, with the
notification and movement documents. Distinct from the transport-mode dangerous-goods regimes below.
*Verified 2026-07-27.*

### Dangerous-goods regimes by mode
**IMDG** (sea) · **ADR** (road) · **RID** (rail) · **IATA DGR** (air). Each requires the hazard
class, UN number, packing group and proper shipping name on the declaration for its mode
(**LOG-R3**). A mis-declaration is a criminal matter, not a data-quality issue.
*Verified 2026-07-27.*

### WTO Trade Facilitation Agreement
In force **22 February 2017**. Art. 7 pre-arrival processing and authorised-operator schemes,
Art. 10 formalities and HS classification. The trusted-trader programmes it enables —
**AEO** in the EU (AEO-C customs simplifications, AEO-S security), **C-TPAT** in the US — are
**voluntary**: they buy facilitation, they do not change an obligation.
*Verified 2026-07-27.*

---

## References (definitions only, never target values)

| Author(s) | Work | Year |
|---|---|---|
| ASCM | APICS Dictionary, 16th Ed. — terminology | 2024 |
| ASCM | SCOR Digital Standard — process taxonomy | 2019 |
| ICC | Incoterms® 2020 | 2019 |
| GS1 | General Specifications v23.0 | 2023 |
| Chopra & Meindl | Supply Chain Management: Strategy, Planning and Operation, 6th Ed. | 2016 |
| Christopher, M. | Logistics and Supply Chain Management, 6th Ed. | 2022 |
| Ballou, R.H. | Business Logistics / Supply Chain Management, 5th Ed. | 2004 |
| Orlicky / Ptak & Smith | Material Requirements Planning, 3rd Ed. | 2011 |
| Silver, Pyke & Peterson | Inventory Management and Production Planning and Scheduling | 1998 |
| Holt, C.C. | Forecasting trends and seasonals by exponentially weighted averages | 1957 |
| Winters, P.R. | Forecasting sales by exponentially weighted moving averages | 1960 |
| Croston, J.D. | Forecasting and stock control for intermittent demands | 1972 |
| Syntetos & Boylan | The accuracy of intermittent demand estimates | 2005 |
| Harris, F.W. | How many parts to make at once (EOQ) | 1913 |
| Wagner & Whitin | Dynamic version of the economic lot size model | 1958 |
| Kraljic, P. | Purchasing Must Become Supply Management (HBR) | 1983 |
| Lee, Padmanabhan & Whang | The Bullwhip Effect in Supply Chains (MIT Sloan) | 1997 |
| Chen et al. | Quantifying the bullwhip effect (Management Science) | 2000 |
| Hyndman & Koehler | Another look at measures of forecast accuracy (IJF) | 2006 |
| Hyndman & Athanasopoulos | Forecasting: Principles and Practice, 3rd Ed. | 2021 |
| Montgomery, D.C. | Introduction to Statistical Quality Control | 2013 |
| Frazelle, E. | World-Class Warehousing and Material Handling | 2002 |
| Wallace, T.F. | Sales and Operations Planning | 2004 |
| Gilliland, M. | The Business Forecasting Deal (origin of FVA) | 2010 |

A consultancy maturity model or a published vendor ranking is **not** a standard and does not belong
in this document: an organisation can reasonably decline to use one, which by the inclusion test puts
it outside this context.
