# Logs — ingest, processing, the Logs app

Logs are the highest-volume data type in most environments, so almost every logs
question is really a cost, limit or routing question wearing a different hat.

Corpus: `analyze-explore-automate/logs` (93 files, latest) and
`analyze-explore-automate/log-monitoring` (43 files, Classic).

## Contents

- Latest against Classic
- Ingest paths
- Ingest limits — the ones that silently drop data
- Processing: the three places it happens
- Bucket assignment and security context
- Enrichment
- Alerting on logs
- Cost control
- Troubleshooting

## Latest against Classic

| | Logs app (latest) | Log Monitoring Classic |
|---|---|---|
| Corpus path | `analyze-explore-automate/logs` | `analyze-explore-automate/log-monitoring` |
| Query | DQL | log search syntax |
| Processing | OpenPipeline | classic log processing pipeline |
| Storage | Grail buckets | classic log storage |

Migration: `logs/logs-upgrade`, plus
`platform/openpipeline/migration-classic-pipeline`.

## Ingest paths

`analyze-explore-automate/logs/lma-log-ingestion`:

| Path | Page |
|---|---|
| OneAgent | `lma-log-ingestion-via-oa` |
| Log Monitoring API v2 | `lma-log-ingestion-via-api` |
| Syslog | `lma-log-ingestion-syslog` (needs an ActiveGate with the **Extensions** module, host-based x86-64 only) |
| Cloud provider forwarding | `lma-cloud-provider-log-forwarding` |
| OpenTelemetry | `lma-stream-logs-with-opentelemetry` |
| Fluent Bit / Fluentd / Logstash / Cribl | `lma-stream-logs-with-*`, `lma-stream-logs-fluentd-k8s` |
| AWS Fargate | `lma-aws-fargate` |
| Cloudflare | `lma-push-logs-with-cloudflare` |
| NetFlow via Fluentd | `lma-send-netflow-via-fluentd` |

Delivery guarantees: `lma-delivery-reliability`. Onboarding walk-through:
`lma-onboarding-flow`. Advanced OneAgent settings: `advanced-log-settings`.

## Ingest limits — the ones that silently drop data

`analyze-explore-automate/logs/lma-limits`:

| Limit | Value |
|---|---|
| Log entry body (content) | 10 MB |
| Attribute key | 100 bytes |
| Attribute value length | 32 kB |
| Attributes per log record | 500 |
| Values per attribute | 32 |
| Nested object depth | 5 levels |
| Request payload | 10 MB |
| Log records per request | 50 000 |
| Log events per minute | no limit |
| Extracted log attribute in an event template | truncated to 4 096 bytes |

**Timestamp windows — this is where records vanish:**

| Record timestamp | Result |
|---|---|
| older than **current time minus 24 hours** | the log event is **dropped** |
| older than **current time minus 2 hours** for log **metrics and events** | the data point is **dropped** |
| more than 10 minutes in the future | timestamp is **reset to current time** |

The two-hour window for log-derived metrics is tighter than the 24-hour window
for the logs themselves, so a backfill can land the logs and lose their metrics.

**OneAgent-side buffering:** storage capacity 2 GB of compressed logs including
metadata; log processing rate 500 MB/min, raisable to 1 GB/min where resources
allow.

## Processing: the three places it happens

`analyze-explore-automate/logs/lma-log-processing` names them in order:

1. **Automatic log processing on ingest** — built-in parsing Dynatrace applies
   without configuration.
2. **Pre-processing with OpenPipeline** — only available on **custom ingest
   sources**; see `openpipeline.md`.
3. **Log processing with OpenPipeline** — the processing stage proper: DQL,
   Add/Remove/Rename fields, Drop record, technology bundles.

Classic equivalent: `lma-classic-log-processing`.

Patterns are DPL, not regex — see `dpl-patterns.md`. A `parse` that has
stabilised in a query belongs in a pipeline processor, where it runs once per
record instead of once per query.

## Bucket assignment and security context

- `lma-bucket-assignment` — which bucket a log lands in. Remember the Storage
  stage takes **first match only**, so processor order decides.
- `lma-security-context` — setting `dt.security_context` for record-level IAM.
  `log.source` is also a permission field in its own right; see
  `iam-grail-permissions.md`.

## Enrichment

`lma-log-enrichment` — attaching entity, Kubernetes and cloud metadata so logs
correlate with the rest of the telemetry. Without it, logs arrive as text with
no topology attached and cannot be filtered by entity.

## Alerting on logs

`alerting-on-logs`. The latest path is a DQL custom alert in the **Anomaly
Detection** app; log metrics can also be extracted in OpenPipeline's metric
extraction stage and alerted as metrics. Worked example:
`lma-use-cases/lma-alert-log-based-events`.

## Cost control

Logs are charged on Ingest & Process, Retain and Query. In descending order of
effect:

1. **Drop record in OpenPipeline** — removes the record before Ingest & Process
   is charged. The only lever that cuts all three dimensions.
2. **Bucket with a short retention** — cuts Retain.
3. **Tight `fetch` with `bucket:` and a bounded timeframe** — cuts Query. See
   `dql.md`.
4. **`INCLUDED` query consumption** in the IAM policy for the broad user base —
   see `iam-grail-permissions.md`.

`lma-best-practices` and `logs-on-grail-examples` carry the worked queries.

## Troubleshooting

`lma-troubleshooting`. The usual order: is the record arriving at all (check the
default buckets — anything there means routing missed it), is it inside the
timestamp window, did a Drop record processor match it, does the user have both
bucket and table permission.
