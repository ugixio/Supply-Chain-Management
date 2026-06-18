# /supplier-check — Supplier Integration Reviewer

Reviews supplier integration code for reliability, security, and EDI/API compliance.

## Usage
`/supplier-check [file or supplier name]`

---

Review the supplier integration in: $ARGUMENTS

Verify:
1. **Auth security** — credentials stored in env vars / secrets manager, never hardcoded
2. **Retry logic** — exponential backoff with jitter for transient failures
3. **Idempotency** — duplicate acknowledgements/orders handled gracefully
4. **Timeout handling** — all HTTP calls have explicit timeouts (recommended: 30s connect, 60s read)
5. **Error classification** — transient vs permanent errors distinguished (4xx vs 5xx)
6. **EDI compliance** — if EDI, verify ISA/GS/ST envelope structure and segment terminators
7. **Data validation** — supplier data validated against schema before persisting
8. **Audit logging** — all inbound/outbound messages logged with timestamp and correlation ID
9. **Supplier scorecard impact** — does this integration feed OTD/OTIF metrics?

Flag any issue that could cause silent data loss or double-ordering.
