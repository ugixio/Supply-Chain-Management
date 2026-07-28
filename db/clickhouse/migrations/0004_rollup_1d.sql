-- 0004 — the 1-day rollup, built from the 1-hour states. Final stage of the ADR-0036 cascade.
--
-- This is the table that carries long-term trend, so it has the longest retention and is the
-- cheapest per row. A supervision dashboard asking "how has this project trended over a year"
-- should land here and touch nothing else.

CREATE TABLE IF NOT EXISTS telemetry.samples_1d
(
    project_id  String                 CODEC(ZSTD(1)),
    metric      LowCardinality(String) CODEC(ZSTD(1)),
    bucket      Date                   CODEC(Delta, ZSTD(1)),

    count_state AggregateFunction(count),
    sum_state   AggregateFunction(sum, Float64),
    min_state   AggregateFunction(min, Float64),
    max_state   AggregateFunction(max, Float64),
    p95_state   AggregateFunction(quantileTDigest(0.95), Float64)
)
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(bucket)
ORDER BY (project_id, metric, bucket)
TTL bucket + INTERVAL 5 YEAR;

CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry.samples_1d_mv
TO telemetry.samples_1d
AS
SELECT
    project_id,
    metric,
    toDate(bucket) AS bucket,
    countMergeState(count_state) AS count_state,
    sumMergeState(sum_state)     AS sum_state,
    minMergeState(min_state)     AS min_state,
    maxMergeState(max_state)     AS max_state,
    quantileTDigestMergeState(0.95)(p95_state) AS p95_state
FROM telemetry.samples_1h
GROUP BY project_id, metric, bucket;
