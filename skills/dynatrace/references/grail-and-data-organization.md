# Grail — data lakehouse, buckets, partitioning, cost

## Contents

- What Grail is
- Data model: bucket → table → view
- Partitioning strategy
- Cost model (DPS)
- Finding partitioning candidates
- Retention
- Certifications
- The next step after designing buckets

Sources: `/docs/platform/grail/dynatrace-grail/concepts`,
`/docs/platform/grail/organize-data/partition-data`,
`/docs/manage/upgrade-guide-landing-page/upgrade-guide-concepts`
(harvested 2026-07-30).

## What Grail is

A data lakehouse — the reliability and performance of a data warehouse combined
with the flexibility and scale of a data lake. All data in latest Dynatrace
lives here: **logs, metrics, traces/spans, events, business events, entities,
user sessions and events, smartscape**.

**Schema-on-read** — the schema is defined at **read** time, not at ingest.
Nothing has to be declared before data is sent. Parsing happens at query time
through **DPL** (the `parse` command) or at ingest time through OpenPipeline
processors.

## Data model: bucket → table → view

| Level | What it is |
|---|---|
| **Bucket** | The physical and logical storage unit, like a folder. Always bound to **one record type** (logs, events, spans, user events, user sessions …). Carries retention, cost allocation and the access boundary |
| **Table** | Groups records by type. `fetch logs` returns records from **every** bucket the caller can access |
| **View** | The third level of the data model |

**Critical:** every record lives in **exactly one** bucket and **cannot be moved
between buckets after ingest**. Plan before sending.

### Default buckets

When OpenPipeline names no bucket, everything lands in the defaults — log lines
go to `default_logs`, for instance. Others: `default_user_events`,
`default_user_sessions`, `dt_system_events` (system, audit, billing).

Practical advice from the docs: configure routing so the default buckets stay
**empty**. Data in a default bucket is then a signal that routing is wrong, or
that something new is arriving that the setup does not cover yet. The fix is to
correct the routing, grant permissions, or drop the data.

> Enterprise pattern: restrict access to the default buckets to the central
> monitoring team, so confidential information cannot leak to an unexpected
> audience.

### Custom buckets — limits

- **80 custom buckets** per environment by default. Default buckets do not
  count.
- More are granted on request, based on actual daily log ingest: **1 extra
  bucket per 10 GB of daily ingest**. Example: 50 000 GB/day → up to 5 000
  buckets.
- Above **1 000 buckets**, contact Dynatrace support directly; it needs
  additional review.

Checking eligibility: *Account Management > Subscription > Cost and usage
details > Ingest & Process > Usage summary* → sum the "Last 0-30 days" usage for
Ingest & Process capabilities, divide by 30 for the average daily ingest, then
by 10 GB for the number of extra buckets.

Creation: the **Storage Management** app, or the API (`Manage custom Grail
buckets`).

## Partitioning strategy

The docs recommend that a **central team** define the overall partitioning
strategy and revisit it periodically. Before designing, answer:

- Who owns which data?
- Who depends on that data?
- Who is accountable for retention decisions?

In many organisations the team sending the data is **not** the team paying for
retention or setting the retention periods. Without clear ownership: routing
problems, unexpected storage growth, and permissions that do not match actual
responsibility.

### Recommended steps

1. **By record type** — a dedicated set of buckets per record type, with a
   consistent naming scheme. **Avoid `default` in a custom bucket's name**
   (`logs_default` gets confused with the built-in `default_logs`). The docs
   example uses a `_shared` suffix.
2. **By cost center** — one bucket per cost center for cost allocation and
   cross-charging. Example: `shared`, `delivery`, `accounting`,
   `infrastructure`, each times every record type. Routing via OpenPipeline.
3. **By retention** — retention is configured **per bucket**. Example name:
   `logs_delivery_90d` (record type, purpose, retention).
4. **For query performance** — see below.
5. **For access control** — only as a supplement to IAM, never as the primary
   mechanism.

### Naming pattern from a real enterprise example

The docs table shows names such as:
```
custom_sen_low_logs_grail_shared              (90d)
custom_sen_high_kubernetes_istio_network_logs (365d)
custom_sen_low_logs_platform_service_shared   (90d)
custom_sen_low_logs_classic_server_feature_shared (30d)
```
That is `custom_<sensitivity>_<recordtype>_<domain>_<scope>`, with the
sensitivity classification baked into the name — a useful pattern in a regulated
environment.

### When a custom bucket is worth it, and when it is not

- **Low volumes** → the default setup is often enough.
- The deciding measure is the bucket's **fill rate**. A bucket taking 12 TB/day
  for a year will time out queries and dashboards.
- The docs recommend **splitting above 2 TB daily ingest** per bucket.
- Where queries always use narrow timeframes, **above 15 TB/day** in one bucket
  can be fine. Long timeframes over high-volume buckets are the problem.
- **The query timeout for apps (Dashboards, Notebooks) and workflows is 5
  minutes.** Bucket size has to allow a result inside that limit.
- The more often data is queried, the more a dedicated bucket pays off — many
  queries against a small volume also add up in cost.

### Anti-patterns

- **One bucket per Kubernetes cluster** → many underused buckets, more
  maintenance, more buckets scanned per query. Better: 1:1 only for the most
  significant clusters, the rest grouped into one or a few.
- **Copying the structure from the previous tool** (Splunk indexes, say) — Grail
  buckets have different constraints. A migration is a chance to rethink, not to
  replicate.
- **Over-engineering at the start** — better to begin small and correct once the
  need is proven. Short retention makes strategy changes easier, because the old
  structure expires on its own.
- **Hundreds of buckets by hand** — use the API and automation with a
  well-defined naming convention.

### A real example from the docs

A customer with thousands of applications and **250 TB/day** of ingest
considered a bucket per application; many would have been underused. Looking one
level up instead revealed about **50 business units**. The decision:
- one dedicated bucket per business unit
- dedicated buckets only for applications exceeding the recommended 2 TB/day

## Cost model (DPS)

**Dynatrace Platform Subscription** — consumption-based, with hourly usage
reporting and daily budget updates.

| Dimension | Unit | When it is measured |
|---|---|---|
| **Ingest & Process** | GiB | raw bytes, before enrichment and transformation |
| **Retain** | GiB-day | after parsing, enrichment, transformation and filtering, **before compression** |
| **Query** | GiB scanned | on every DQL execution |

DPS covers log data, events, business events, traces powered by Grail, and
metrics. For some data types, queried data is **included** in Ingest & Process
and Retain. Some apps consume no query budget when displaying their initial
state.

### Scanned data and datawarping

On execution Grail processes all relevant data in the timeframe.
**Datawarping** retrieves only the records matching the query's filters, cutting
scanned bytes. Scanned data is a function of matching records plus the bytes
scanned in the requested buckets.

The consequence: an early `filter` in the pipeline is not style, it is a direct
reduction of the bill. See `dql.md` for the full best practices.

**Important:** even when the user is **not permitted** to see a record, the
query still scans the data in the bucket. A bucket-level DENY — rather than
record-level — therefore cuts cost and improves performance at the same time.

## Finding partitioning candidates

Querying `dt.system.buckets` gives current volume and retention for every
bucket:

```dql
fetch dt.system.buckets
| filter dt.system.table == 'logs'
| fieldsAdd est_avgDailyIngest = estimated_uncompressed_bytes / retention_days
| fieldsRemove display_name, dt.system.table
| sort est_avgDailyIngest desc
```

> This is a **rough estimate**, not billable ingest.

Further advice from the docs:
- Do not optimise on the basis of one query or one record — confirm the effect
  holds across large data sets.
- Consider whether frequently queried log, event or span content is worth
  extracting into **dedicated metrics**; metrics need fewer resources and adapt
  more easily than new buckets do.
- Review bucket usage periodically.

## Retention

Configured **per bucket**. Different legal, compliance and business requirements
mean different buckets. Real values from the example table: 30d, 35d (default),
90d, 365d.

Managing logs specifically → `/docs/analyze-explore-automate/logs` →
"Configure data storage and retention for logs".
Deleting specific records →
`/docs/platform/grail/organize-data/record-deletion-in-grail`.

## Certifications

The platform holds SOC 2 Type II, ISO 27001, HIPAA, FedRAMP, IRAP and CCPA.
Detail → the Dynatrace Trust Center.
Data privacy → `/docs/manage/data-privacy-and-security` (26 pages).

## The next step after designing buckets

Bucket definitions are **empty shells** without routing. OpenPipeline has to
direct the data:
- Data flow in OpenPipeline
- Processing in OpenPipeline
- Configure data storage and retention for logs
