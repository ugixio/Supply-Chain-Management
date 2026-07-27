---
id: concept-certification-and-contract-validity
title: "Certification & Contract Validity (CPT-0035)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Certification & Contract Validity (CPT-0035)

> Two date predicates that keep procurement compliant: is a supplier's security
> certification still valid, and is a contract about to expire and need renewal.

## Formula

    certValid       ⇔  cert.expiresAt  >  now
    expiringSoon    ⇔  0 < (expiryDate − today) in days  ≤  daysThreshold   (default 90)

| Symbol | Meaning | Unit |
|---|---|---|
| expiresAt / expiryDate | certification / contract end | ISO 8601 date |
| daysThreshold | renewal lead-time window | days (default 90) |

## Inputs and outputs

- **`isCertificationValid(cert)`** → `boolean`: strictly `expiresAt > now` (an expiry
  exactly now is invalid).
- **`isExpiringSoon(contract, daysThreshold=90)`** → `boolean`: true only in the window
  **(0, threshold]** — an already-expired contract (`daysLeft ≤ 0`) is **not** "expiring
  soon", it has expired; renewal alerting must handle that state separately.

## Assumptions and limits

- **Timezone:** compares against the runtime clock via `Date`. Dates are ISO 8601/UTC
  (SCM-R9); a naive local-time boundary can be off by a day near midnight — prefer a
  UTC-normalized comparison when this drives a hard cutoff.
- `isExpiringSoon` is a **half-open** window: it excludes already-expired contracts by
  design, so a dashboard needs both "expiring soon" and "expired" buckets — one predicate
  does not cover both.
- No grace period is modelled — expiry is a hard boundary. Certifications required by
  ISO 28000 / C-TPAT that lapse should block, not warn (a policy the caller enforces).
- **Does not apply when:** a certification has no expiry (perpetual) — `expiresAt` must
  still be a valid date for the comparison.

## Worked example

Today 2026-07-20, contract expiry 2026-09-30 → `daysLeft ≈ 72` → within (0, 90] →
`expiringSoon = true` (start the renewal). A cert with `expiresAt = 2026-07-01` → past →
`isCertificationValid = false` (block use until renewed).

## Governing rules

- **SCM-R9** — dates are ISO 8601, timestamps UTC; these predicates depend on that.
- **PRC-R8** — a contract's expiry is strictly after its effective date; validity assumes
  that invariant holds.

## Related

- CPT-0034 Price escalation — applies only within the valid contract window.
- ISO 28000 supplier certifications (dept 02/09) — what `isCertificationValid` gates.

## References

- ISO 28000:2022 (supply-chain security); APICS/ASCM Dictionary — *contract management*.
