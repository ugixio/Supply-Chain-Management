# /supplier-check — Supplier Integration Reviewer

Reviews a supplier integration **in a project's own repository** for reliability, security and
EDI/API conformance, against the standards this context carries and the SUP/PRC rule families.

## Usage
`/supplier-check [file, integration name, or repository path]`

---

Review the supplier integration in: $ARGUMENTS

Verify:
1. **Credential handling** — secrets from an environment or a secrets manager, never in the
   repository, never in a log line, never in an error message returned to a caller.
2. **Retry safety** — exponential backoff with jitter for transient failures, and an idempotency
   key so a retry cannot double-post. Retry safety is an engineering concern (`ENG` family), and it
   is the one that turns a network blip into a duplicate purchase order.
3. **Message conformance** — the **UN/EDIFACT** semantics for what is being exchanged: ORDERS,
   ORDRSP, DESADV, INVOIC, RECADV. A field that carries something the message does not mean is
   a conformance failure even when both ends agree.
4. **Identifier validity** — GS1 keys check-digit-validated on the way in: GTIN, GLN, SSCC, GSIN
   (SCM-R10). Rejecting a bad key at the boundary costs nothing; finding it downstream costs a lot.
5. **Trade terms** — Incoterms® 2020 used as the eleven rules actually are: DPU replaced DAT, and
   four are sea-only (FAS, FOB, CFR, CIF). Applying a sea-only rule to an air shipment is a
   real-world error with cost consequences.
6. **Dates and instants** — ISO 8601-1:2019, UTC, unambiguous (SCM-R9). A local-time timestamp
   across a supplier boundary is a defect waiting for a daylight-saving transition.
7. **Money** — minor units, exact arithmetic, quantized only at defined boundaries (SCM-R14,
   ENG-R4/R5). Never a float over a wire.
8. **Failure surface** — what the caller sees when the supplier is down, slow, or returns garbage.
   A partial success that reports as success is worse than a clean failure.

Report findings with severity and line references. Where the correct behaviour depends on the
supply agreement — tolerances, lead times, service levels — say so explicitly and name the term
rather than assuming one.
