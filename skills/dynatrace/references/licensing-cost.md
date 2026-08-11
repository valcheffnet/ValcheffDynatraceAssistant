# DPS licensing and cost management

Dynatrace Platform Subscription is consumption-based across many capabilities.
Two separate corpus areas: `license` (67 files) is what you are charged for,
`manage-your-costs` (17 files) is how to see and control it.

## Contents

- The three Grail dimensions
- Capabilities on the rate card
- Where the cost actually comes from
- Viewing consumption
- Allocating cost
- Controlling cost
- Predicting cost
- Included queries
- Classic licensing

## The three Grail dimensions

| Dimension | Unit | Measured |
|---|---|---|
| **Ingest & Process** | GiB | raw bytes, **before** enrichment and transformation |
| **Retain** | GiB-day | after parsing, enrichment, transformation and filtering, **before compression** |
| **Query** | GiB scanned | on **every** DQL execution |

Reporting is hourly; the budget updates daily.

For some data types, queried data is **included** in Ingest & Process and Retain
rather than charged separately. Some apps consume no query budget when
displaying their initial state — a custom dashboard is not one of them.

## Capabilities on the rate card

`license/capabilities` (47 files), one area each:

Application & Infrastructure Observability · Container Observability ·
Application Security · Real User and Synthetic Monitoring · Log Analytics ·
Data · Traces powered by Grail · Events powered by Grail · Metrics powered by
Grail · Automation · AppEngine Functions · Platform extensions

Each has its own unit and its own rate. Two worth knowing because they are not
byte-based:

- **Database Monitoring** is charged in **database-instance-hours**: an instance
  monitored at any point in a 15-minute interval costs 0.25 h for that interval.
  Two instances across four intervals can total 1.25 database-instance-hours.
- **Host-based capabilities** are charged per host unit, which is why OneAgent
  monitoring mode is a licensing decision as much as a technical one — see
  `oneagent.md`.

Consumption is queryable:

```dql
fetch dt.system.events, from: now() - 24h
| filter event.kind == "BILLING_USAGE_EVENT" and event.type == "Database Monitoring"
| summarize `Last 24h consuming Database-instances` = countDistinct(dt.smartscape_source.id)
```

```dql
fetch dt.system.events
| filter event.kind == "BILLING_USAGE_EVENT" and event.type == "Database Monitoring"
| makeTimeseries { `Total database-instance-hours` = sum(`database-instance-hours`, default:0) }
, time:usage.start, interval:24h
```

`event.kind == "BILLING_USAGE_EVENT"` is the entry point for any consumption
query; `event.type` selects the capability; `usage.start` is the timestamp
field. Reading these requires `storage:system:read` plus a bucket permission on
`dt_*` — the **Read all system data** predefined policy. See
`iam-grail-permissions.md`.

## Where the cost actually comes from

In descending order of how often it is the answer:

1. **Query on dashboards.** Every open re-queries. A broad `fetch logs` with no
   `bucket:` and a wide timeframe, on a wall-mounted dashboard, is a standing
   charge. See `dashboards-notebooks.md`.
2. **Ingest of data nobody reads.** The only fix that cuts all three dimensions
   is dropping it in OpenPipeline before it is charged. See `openpipeline.md`.
3. **Retention on high-volume buckets.** Retain is GiB-day, so 365-day retention
   on a 2 TB/day bucket is a different product from 30-day retention.
4. **Metric cardinality**, which multiplies data points without multiplying
   information. See `metrics.md`.
5. **Cloud metric polling** with auto-discovery across every region and
   namespace. See `ingest-cloud.md`.

Datawarping means an early `filter` reduces scanned bytes directly. And note
that **a query still scans records the user is not permitted to see** — so
bucket-level DENY cuts cost as well as access, while record-level filtering does
not.

## Viewing consumption

`manage-your-costs/view`:

| Page | What it gives |
|---|---|
| `where-to-look` | the starting point |
| `billing-report` | the authoritative report |
| `usage-dashboards` | consumption dashboards |
| `export-via-api` | pulling usage out programmatically |

The **Capability cost and usage analysis** view filters by environment,
capability, timeframe and resolution, and offers *Open details with Notebooks*
to take the query further.

## Allocating cost

`manage-your-costs/allocate`: `plan-and-set-up`, `analyze`.

Allocation happens in two places:

- **OpenPipeline** has dedicated **Cost allocation** and **Product allocation**
  stages, assigning cost center and product per matching record.
- **Lookup data** can tag uploaded data with `dt.cost.costcenter` and
  `dt.cost.product` host properties.

Primary Grail tags carry ownership metadata onto every signal including derived
Davis events, which is what makes allocation work without joins. See
`segments-tags.md`.

## Controlling cost

`manage-your-costs/control`: `budgets`, `cost-monitors`, `investigate-a-spike`.

`investigate-a-spike` is the runbook worth knowing before the spike happens.

## Predicting cost

`manage-your-costs/predict`: `built-in-forecast`, `estimate-new-workloads`,
`project-run-rate`. Plus `manage-your-costs/optimize`.

## Included queries

For logs only, when **Log Management & Analytics – Retain with Included
Queries** is on the rate card, the IAM condition `storage:query-consumption`
takes `INCLUDED` or `ON_DEMAND`:

```sql
-- broad user base: no additional Query consumption
ALLOW storage:buckets:read WHERE storage:query-consumption="INCLUDED";
-- deep divers: full retained access in one bucket
ALLOW storage:buckets:read WHERE storage:bucket-name="common_logs"
                             AND storage:query-consumption="ON_DEMAND";
```

`ON_DEMAND` is the default when unspecified. This is the one cost control that
lives in the permission model rather than in the pipeline.

## Classic licensing

`license/classic-licensing` (11 files) — host units, DDUs and the rest. Also
`license/dps-for-hybrid`, `license/dps-permissions`, `license/concepts`,
`license/faq`, `license/proof-of-concept`, `license/your-first-year`.
