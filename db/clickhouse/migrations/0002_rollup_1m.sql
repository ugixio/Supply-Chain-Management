-- 0002 — the 1-minute rollup, first stage of the ADR-0036 cascade (raw → 1m → 1h → 1d).
--
-- Aggregation happens at INSERT time so dashboard cost is paid on write, not on read. The stored
-- columns are aggregate *states*, not finished numbers: a state can be merged again by the next
-- stage, which is what makes the cascade exact rather than an average of averages.

CREATE TABLE IF NOT EXISTS telemetry.samples_1m
(
    project_id  String                 CODEC(ZSTD(1)),
    metric      LowCardinality(String) CODEC(ZSTD(1)),
    bucket      DateTime('UTC')        CODEC(Delta, ZSTD(1)),

    count_state AggregateFunction(count),
    sum_state   AggregateFunction(sum, Float64),
    min_state   AggregateFunction(min, Float64),
    max_state   AggregateFunction(max, Float64),
    -- A quantile state, so percentiles survive the cascade. Averaging percentiles is meaningless;
    -- merging t-digest states is not.
    p95_state   AggregateFunction(quantileTDigest(0.95), Float64)
)
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(bucket)
ORDER BY (project_id, metric, bucket)
TTL bucket + INTERVAL 90 DAY;

CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry.samples_1m_mv
TO telemetry.samples_1m
AS
SELECT
    project_id,
    metric,
    toStartOfMinute(ts) AS bucket,
    countState()                        AS count_state,
    sumState(value)                     AS sum_state,
    minState(value)                     AS min_state,
    maxState(value)                     AS max_state,
    quantileTDigestState(0.95)(value)   AS p95_state
FROM telemetry.samples
GROUP BY project_id, metric, bucket;
