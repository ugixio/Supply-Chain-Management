# api  (scaffold — NestJS + GraphQL)

**The only counterpart the frontend has** (ENG-R8): Next.js talks to this and to nothing else.
Code-first GraphQL (ADR-0025). It calls the Rust core and reads the ClickHouse telemetry tier
through a SELECT-only identity; it computes no business result itself.

No code yet — this is **Phase M4**. What lands here first is the monitoring gateway: the delivery
metrics defined as concept nodes (CPT-0155..0160) served over the telemetry written by
`crates/scm-ingest` into the schema in `db/clickhouse`.

**One module per department (ADR-0023) does not apply to this application.** That shape was for the
supply-chain application ADR-0037 deleted; this service has one bounded context, monitoring.

**Open decision affecting this directory.** ADR-0024/0025 also specify a Postgres read model over
`docs/` and a GraphQL surface for it (backlog P3). Whether that is built alongside the monitoring
gateway is an owner decision, recorded as ⚠ in `docs/program/WORKFLOW.md` §Triage.
