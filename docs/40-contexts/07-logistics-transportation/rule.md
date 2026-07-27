---
id: rule-logistics-transportation
title: "Rules — Logistics & Transportation (LOG-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-27
relations:
  - { type: part-of, target: index-contexts }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Logistics & Transportation

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `LOG`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **LOG-R1:** Every shipment carries an **Incoterms® 2020** rule, and that rule — not local
  habit — fixes where risk and cost transfer, who insures, and who clears customs. There are
  **eleven** rules; `DPU` replaced `DAT`; **four are usable only for sea or inland waterway**
  (`FAS`, `FOB`, `CFR`, `CIF`), so naming one of those for an air or road movement is an error, not
  a shorthand. *Source:* ICC Incoterms® 2020.
- **LOG-R3:** A shipment line of dangerous goods declares its **hazard class, UN number, packing
  group and proper shipping name** for the mode it travels. *Source:* IMDG Code (sea), ADR (road),
  IATA DGR / ICAO TI (air), RID (rail). Undeclared dangerous goods are a criminal offence in most
  jurisdictions, not a data-quality issue.
- **LOG-R4:** Chargeable weight is the **greater** of actual and volumetric weight — the carrier
  is paid for whichever the shipment consumes more of. *An identity of the tariff;* the volumetric
  divisor is set by the mode and the carrier agreement.

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **LOG-R2** | "On-time delivery is evaluated only against an actual delivery date" | Correct as far as it goes and worth stating in the OTD concept (CPT-0123), but it is a measurement definition rather than a departmental invariant — a shipment still in transit is *not yet* late, and treating it as either on-time or late is the error the concept node now names. |

## Project decisions (the questions this department must answer for itself)

- The **volumetric divisor** per mode and carrier, and whether a **minimum charge** floors the
  freight cost.
- Whether a surcharge applies to the base rate only or to accessorials as well.
- The **on-time window** — is a delivery on time if it arrives on the promised day, within an
  appointment slot, or early? Early delivery is a failure in some receiving operations.
- **Carrier selection criteria** and their weights.
- **Insurance** beyond what the chosen Incoterms rule obliges.

## Inherited rules (referenced, not restated)

- **SCM-R9** — dates and instants ISO 8601 / UTC; a delivery time without its time zone is
  ambiguous and cross-border shipments always cross zones.
- **SCM-R10** — weights and volumes carry their UN/ECE Rec 20 unit.
- **SCM-R14** — freight apportioned across lines sums exactly to the freight charged.
