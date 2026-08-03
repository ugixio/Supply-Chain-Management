-- 0006 — a metric declares its kind, and a level's sum is not addressable (M2b, risk #14).
--
-- THE DEFECT. `samples_1m` computed sumState for every metric. MSR-R2 says a level is never summed:
-- a backlog of 40 read every ten seconds sums to 240 in a one-minute bucket — six times reality, in
-- range, with nothing failing and no gate able to see it. No level metric is ingested today, so the
-- exposure was latent, and it would become live at the moment nobody was looking for it.
--
-- THE FIX IS DATA, NOT DOCUMENTATION. The kind is a column, stamped by the ingester from its
-- governed-metric registry and never taken from the sample — an emitter cannot relabel its own
-- metric. Then the correct aggregation is *added* and the incorrect one is made **unaddressable**:
-- `telemetry.levels_*` has no sum column at all. An invalid aggregation that is absent cannot be
-- used by mistake; one that is merely documented can.
--
-- argMax, NOT anyLast — and this corrects the risk register's own wording, which named them as
-- alternatives. `anyLast` returns whichever row the engine processed last, which under parallel
-- inserts and background merges is not the latest reading; it is a nondeterministic pick that
-- *usually* looks right. `argMax(value, ts)` returns the value at the greatest timestamp in the
-- bucket, which is what "the last reading" means. For a level the two differ exactly when it
-- matters: under load, when rows arrive out of order.
--
-- Columns are APPENDED, never inserted with AFTER. A materialized view with `TO <table>` maps its
-- SELECT to the destination **by position**, so a column inserted mid-table silently shifts every
-- later value into the wrong column. Appending keeps the mapping stable and the SELECT lists below
-- are written in exact table order for the same reason.
--
-- Forward-only and idempotent (ADR-0036): every statement is IF NOT EXISTS or OR REPLACE, and the
-- views are dropped before recreation because a materialized view's SELECT cannot be altered.

-- ---------------------------------------------------------------------------- raw

-- '' is the ADR-0036 convention for absence on a hot column (no Nullable). It can only appear on
-- rows written before this migration; the ingester rejects an unknown metric, and every governed
-- metric has a kind, so every row written after this carries one.
ALTER TABLE telemetry.samples
    ADD COLUMN IF NOT EXISTS kind LowCardinality(String) DEFAULT '' CODEC(ZSTD(1));

-- ---------------------------------------------------------------------------- 1 minute

ALTER TABLE telemetry.samples_1m
    ADD COLUMN IF NOT EXISTS kind SimpleAggregateFunction(any, LowCardinality(String)) DEFAULT '';

-- SimpleAggregateFunction(any, …) rather than an AggregateFunction state: the kind is functionally
-- determined by the metric name, so every candidate value in a group is identical and "any" is
-- deterministic in effect. That is the one place `any` is safe — and it is why `value` may not use it.
ALTER TABLE telemetry.samples_1m
    ADD COLUMN IF NOT EXISTS last_state AggregateFunction(argMax, Float64, DateTime64(3, 'UTC'));

DROP VIEW IF EXISTS telemetry.samples_1m_mv;

CREATE MATERIALIZED VIEW telemetry.samples_1m_mv
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
    quantileTDigestState(0.95)(value)   AS p95_state,
    any(kind)                           AS kind,
    argMaxState(value, ts)              AS last_state
FROM telemetry.samples
GROUP BY project_id, metric, bucket;

-- ---------------------------------------------------------------------------- 1 hour

ALTER TABLE telemetry.samples_1h
    ADD COLUMN IF NOT EXISTS kind SimpleAggregateFunction(any, LowCardinality(String)) DEFAULT '';

ALTER TABLE telemetry.samples_1h
    ADD COLUMN IF NOT EXISTS last_state AggregateFunction(argMax, Float64, DateTime64(3, 'UTC'));

DROP VIEW IF EXISTS telemetry.samples_1h_mv;

CREATE MATERIALIZED VIEW telemetry.samples_1h_mv
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
    quantileTDigestMergeState(0.95)(p95_state) AS p95_state,
    any(kind)                    AS kind,
    argMaxMergeState(last_state) AS last_state
FROM telemetry.samples_1m
GROUP BY project_id, metric, bucket;

-- ---------------------------------------------------------------------------- 1 day

ALTER TABLE telemetry.samples_1d
    ADD COLUMN IF NOT EXISTS kind SimpleAggregateFunction(any, LowCardinality(String)) DEFAULT '';

ALTER TABLE telemetry.samples_1d
    ADD COLUMN IF NOT EXISTS last_state AggregateFunction(argMax, Float64, DateTime64(3, 'UTC'));

DROP VIEW IF EXISTS telemetry.samples_1d_mv;

CREATE MATERIALIZED VIEW telemetry.samples_1d_mv
TO telemetry.samples_1d
AS
SELECT
    project_id,
    metric,
    toStartOfDay(bucket) AS bucket,
    countMergeState(count_state) AS count_state,
    sumMergeState(sum_state)     AS sum_state,
    minMergeState(min_state)     AS min_state,
    maxMergeState(max_state)     AS max_state,
    quantileTDigestMergeState(0.95)(p95_state) AS p95_state,
    any(kind)                    AS kind,
    argMaxMergeState(last_state) AS last_state
FROM telemetry.samples_1h
GROUP BY project_id, metric, bucket;

-- ---------------------------------------------------------- the read surface: kind decides shape
--
-- These are the tables a dashboard reads. The enforcement is structural: `levels_*` exposes no sum
-- and no count-derived total, so MSR-R2's forbidden aggregation is not a column anyone can select.
-- `flows_*` exposes no last_value, because "the last reading" of a flow is a single interval's
-- count and reading it as a level would understate the period.

CREATE OR REPLACE VIEW telemetry.flows_1m AS
SELECT
    project_id, metric, bucket,
    countMerge(count_state)                 AS samples,
    sumMerge(sum_state)                     AS total,
    minMerge(min_state)                     AS minimum,
    maxMerge(max_state)                     AS maximum,
    quantileTDigestMerge(0.95)(p95_state)   AS p95
FROM telemetry.samples_1m
WHERE kind IN ('flow', 'event_count')
GROUP BY project_id, metric, bucket;

CREATE OR REPLACE VIEW telemetry.levels_1m AS
SELECT
    project_id, metric, bucket,
    argMaxMerge(last_state) AS last_value,
    minMerge(min_state)     AS minimum,
    maxMerge(max_state)     AS maximum,
    countMerge(count_state) AS readings
FROM telemetry.samples_1m
WHERE kind = 'level'
GROUP BY project_id, metric, bucket;

-- `readings` is the number of samples in the bucket, not a quantity of anything measured. It is
-- exposed because a level read twice in a minute and a level read six hundred times are different
-- evidence for the same last_value, and MSR-R2's time-weighted average cannot be reconstructed
-- without knowing how often it was read.

GRANT SELECT ON telemetry.flows_1m  TO telemetry_reader;
GRANT SELECT ON telemetry.levels_1m TO telemetry_reader;
