# Metrics — Grail metrics, `timeseries`, cardinality and cost

Metrics are the one Grail table not queried with `fetch`. They are also the data
type where cost is driven by **cardinality** rather than volume, which changes
what "reduce the bill" means.

Corpus: `analyze-explore-automate/metrics` (15 files, latest) plus
`metrics-classic` (3).

## Contents

- Metrics powered by Grail against Metrics Classic
- Querying: `timeseries`, not `fetch`
- Built-in metrics
- Histograms and percentiles
- Cardinality
- Cost control
- Security context
- Migration
- Limits and troubleshooting

## Metrics powered by Grail against Metrics Classic

| | Metrics powered by Grail | Metrics Classic |
|---|---|---|
| Query language | **DQL** | metric selector |
| Ingest limits | limitless dimensions (excluding highly volatile ones); **custom metric keys capped at 100 000** | built-in limits |
| Query limits | **500 million data points** | 20 million data points |
| Granularity | **1 minute over the entire history** | 1 minute for the first 14 days, then coarser |
| Retention | **15 months by default, up to 10 years** | 5 years, not configurable |

The granularity difference is the one that matters for long-range analysis:
Classic degrades resolution after 14 days, Grail does not.

## Querying: `timeseries`, not `fetch`

```dql
timeseries avg(dt.host.cpu.usage), by:{dt.entity.host}, interval:5m
```

`fetch metrics` is not the path — `timeseries` loads, filters and aggregates in
one command. `storage:metrics:read` is the permission it needs, and
`storage:buckets:read` alongside it. See `dql.md` and
`iam-grail-permissions.md`.

To build a timeseries from **records** rather than metrics, use
`makeTimeseries` on a `fetch`. That is a different operation with a different
cost: it scans records.

Worked queries: `analyze-explore-automate/metrics/dql-examples`.

## Built-in metrics

`built-in-metrics-on-grail` is the catalogue, organised by source: Billing,
Cloud (AWS, Azure, Cloud Foundry, VMware), Containers, Infrastructure and more.
Grep it for a metric key before assuming one has to be created — most
infrastructure and cloud signals already exist.

`metric.key` is a permission field, on the `metrics` table only, so per-metric
access control is possible without a security context.

## Histograms and percentiles

`analyze-explore-automate/metrics/histograms` — ingesting histogram metrics and
querying percentiles from them in DQL. The page carries a **visualisation
warnings** section worth reading before charting percentiles, and its own
licensing and billing section.

Percentiles computed from a histogram are not the same as `percentile()` over
raw records; the histogram is bucketed at ingest and the answer inherits those
bucket boundaries.

## Cardinality

Dimensions are effectively unlimited, **except for highly volatile ones**, and
custom metric keys are capped at **100 000**. High cardinality is the usual
cause of both cost and slow queries.

`best-practices-metrics` walks the diagnosis:

1. Find high-cardinality cost centers, cost products or metric sources.
2. Drill into metric keys.
3. Analyse one specific metric key.

It also covers understanding ingest through the OTel Collector — Dynatrace
self-monitoring metrics, the Collector's internal telemetry, and the Collector
debug exporter.

## Cost control

Two levels, and the docs treat them as equivalent choices rather than a
hierarchy:

- **In Dynatrace, with OpenPipeline** — the centralised option. Drop metrics in
  the **Processing** stage with a **Drop record** processor: by name, by
  resource attribute, or by metric point attribute. Route the target metrics to
  a pipeline first (*Settings > Process and contextualize > OpenPipeline >
  Metrics*).
- **At the source, for example in the OTel Collector** — when volume has to drop
  before it leaves the network.

**Dropped metrics are not billed for Metrics Ingest & Process**, whether dropped
by an OpenPipeline rule or upstream. They are also **never persisted and not
recoverable**, which is the trade: no cost, no second chance.

The second lever is **reducing cardinality**, which cuts data points without
losing the signal entirely.

Remember the backdating window: metrics are rejected beyond **ingest time minus
1 hour**, against 24 hours for logs — see `openpipeline.md`.

## Security context

`metrics-security-context` — setting `dt.security_context` on metrics. Combined
with `metric.key`, this gives two independent axes for record-level metric
permissions.

## Migration

`analyze-explore-automate/metrics/upgrade` holds per-domain guides:
`kubernetes-metric-migration`, `rum-metric-migration`,
`runtime-metric-migration`, `service-metric-migration`. Metric selectors become
`timeseries`; `classicEntitySelector()` bridges the entity-selector syntax.

Timeseries API v1 → Metrics API v2 → DQL:
`dynatrace-api/basics/deprecation-migration-guides/timeseries-to-metrics`.

## Limits and troubleshooting

`analyze-explore-automate/metrics/limits`, `troubleshooting` and `faq`. When a
metric "does not exist", check in order: the exact key (case-sensitive, see
`semantic-fields.md`), whether a Drop record processor matched it, whether the
data point fell outside the one-hour backdating window, and whether the user has
`storage:metrics:read` plus a bucket permission.
