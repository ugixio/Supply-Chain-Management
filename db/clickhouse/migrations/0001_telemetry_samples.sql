-- 0001 — the raw telemetry table (ADR-0036).
--
-- Shape, sort key, partitioning and codecs are all fixed by ADR-0036; the retention value is this
-- application's own decision (owner-selected 2026-07-28) and is stated in db/clickhouse/README.md
-- with its reason.
--
-- No column is Nullable: ADR-0036 forbids it on hot columns because it costs a second column and
-- blocks optimizations. Absence is the empty string, which is why `environment` and `unit` carry
-- explicit DEFAULT ''.

CREATE DATABASE IF NOT EXISTS telemetry;

CREATE TABLE IF NOT EXISTS telemetry.samples
(
    -- Leading sort-key column. Deliberately NOT LowCardinality: the dictionary encoding degrades
    -- past roughly ten thousand distinct values, and the project count is expected to grow.
    project_id   String                 CODEC(ZSTD(1)),

    -- A bounded vocabulary (the CPT-* delivery metrics), so LowCardinality is correct here.
    metric       LowCardinality(String) CODEC(ZSTD(1)),

    -- Millisecond UTC instants (SCM-R9). Delta before ZSTD because ingest is near-monotonic.
    ts           DateTime64(3, 'UTC')   CODEC(Delta, ZSTD(1)),

    -- Gorilla is built for slowly-varying float series, which is what supervision telemetry is.
    value        Float64                CODEC(Gorilla, ZSTD(1)),

    environment  LowCardinality(String) DEFAULT ''  CODEC(ZSTD(1)),
    unit         LowCardinality(String) DEFAULT ''  CODEC(ZSTD(1)),

    -- Arrival time, kept separate from `ts`: a late-arriving sample must stay diagnosable.
    ingested_at  DateTime64(3, 'UTC')   DEFAULT now64(3) CODEC(Delta, ZSTD(1))
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (project_id, metric, ts)
TTL toDateTime(ts) + INTERVAL 14 DAY
SETTINGS index_granularity = 8192;
