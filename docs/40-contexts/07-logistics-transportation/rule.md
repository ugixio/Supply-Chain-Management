---
id: rule-logistics-transportation
title: "Rules — Logistics & Transportation (LOG-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-contexts }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Logistics & Transportation

> Invariants for `src/departments/07-logistics-transportation/` (Incoterms 2020, IMDG
> hazmat, customs). Know-how lives in the allowlisted homes (`README.md`,
> `IMPLEMENTATION.md`, `.claude/skills/logistics-transportation/`). IDs append-only
> (family `LOG`). Inherited `SCM-R*` referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **LOG-R1:** Every shipment carries an Incoterms® 2020 term that fixes the risk- and
  cost-transfer point between buyer and seller (`Shipment.incoterm`, required).
- **LOG-R2:** On-time delivery is evaluated only against an actual delivery date; an
  undelivered shipment has undefined OTD, never a false one (`isOnTimeDelivery`).

## Mandatory validations

- **LOG-R3:** A hazardous shipment line declares its IMDG/ADR hazmat class (and, per the
  README, UN number, proper shipping name and packing group). **Enforcement gap:** the
  domain currently types `hazmatClass` as optional and does not reject an `isHazmat` line
  missing it — closing this is a HOW-lane follow-up (see `program/WORKFLOW.md`).

## Anti-states (the system must never allow)

- A shipment without a declared Incoterm (LOG-R1).
- A hazardous line moving without its hazmat classification (LOG-R3, once enforced).

## Inherited rules (referenced, not restated)

- **SCM-R3** — shipments are financial/operational records: soft-delete only.
- **SCM-R9** — dates ISO 8601; delivery timestamps UTC.
