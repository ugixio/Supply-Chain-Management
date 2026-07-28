-- 0003 — the 1-hour rollup, built from the 1-minute states, not from raw.
--
-- `-MergeState` combines existing states into a coarser state. Re-reading raw here would work and
-- would also make every stage scan the largest table, which is the cost the cascade exists to avoid.

CREATE TABLE IF NOT EXISTS telemetry.samples_1h
(
    project_id  String                 CODEC(ZSTD(1)),
    metric      LowCardinality(String) CODEC(ZSTD(1)),
    bucket      DateTime('UTC')        CODEC(Delta, ZSTD(1)),

    count_state AggregateFunction(count),
    sum_state   AggregateFunction(sum, Float64),
    min_state   AggregateFunction(min, Float64),
    max_state   AggregateFunction(max, Float64),
    p95_state   AggregateFunction(quantileTDigest(0.95), Float64)
)
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(bucket)
ORDER BY (project_id, metric, bucket)
TTL bucket + INTERVAL 1 YEAR;

CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry.samples_1h_mv
TO telemetry.samples_1h
AS
SELECT
    project_id,
    metric,
    toStartOfHour(bucket) AS bucket,
    countMergeState(count_state) AS count_state,
    sumMergeState(sum_state)     AS sum_state,
    minMergeState(min_state)     AS min_state,
    maxMergeState(max_state)     AS max_state,
    quantileTDigestMergeState(0.95)(p95_state) AS p95_state
FROM telemetry.samples_1m
GROUP BY project_id, metric, bucket;
