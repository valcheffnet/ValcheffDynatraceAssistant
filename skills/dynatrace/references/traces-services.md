# Traces and services — spans, service detection, the Services app

Two related surfaces: **spans** in Grail, queried with DQL, and **services**, the
entities Dynatrace derives from those spans. Most confusion comes from asking a
service question and getting a span answer, or the reverse.

Corpus: `observe/application-observability` (92 files).

## Contents

- The Services app
- Service detection: v2 against v1
- Service naming
- Spans in Grail
- The Distributed Tracing app
- Sampling: why span counts do not match request counts
- Request attributes and calculated service metrics
- Failure and response-time analysis
- Profiling
- Live Debugger
- Classic

## The Services app

`observe/application-observability/services/services-app`. Views: Explorer,
Service Map (Early Access), Endpoints (Early Access), Messaging, Database
queries, Outbound calls, Failure analysis, Response time analysis.

> **Naming in flux.** As of 2026-08-03 the docs renamed the view to **Explorer
> (Early Access)** and there are now two: `Explorer view` and `New Explorer view
> Early Access`. The anchor `#explorer-early-access` exists on the live page but
> does not correspond to a heading of that text. Quote the current page, not
> memory. See `gotchas.md`.

Health monitoring and alert investigation: `services/managing-service-health`.
Concepts: `services/services-concepts`. Topology:
`services/service-map`, `services/services-smartscape`.

## Service detection: v2 against v1

| | Service Detection v2 | Service Detection v1 |
|---|---|---|
| Basis | a **single set of attribute-based rules**, built-in and user-defined, evaluated uniformly | classic detection for **OneAgent-instrumented processes** |
| Sources | OpenTelemetry **and** OneAgent | OneAgent only |
| Naming | service name **template** with placeholders such as `{k8s.workload.name}`, `{service.version}` | derived by detection heuristics |

The practical consequence: v2 gives one rule model across OTel and OneAgent
data, and names services from a template you control. A service appearing with
an unexpected name is usually a template question under v2 and a heuristic
question under v1.

Pages: `services/service-detection/service-detection-v2`,
`service-detection-v1`, `service-naming`. Enhanced endpoints under v1:
`service-detection/service-detection-v1/enhanced-endpoints-sdv1`.

Customising API definitions: `services/customize-api-definitions`.

## Spans in Grail

```dql
fetch spans, samplingRatio:100
| filter span.kind == "server"
| summarize c = count(), by:{code.namespace, code.function}
| fieldsAdd c = c*100
```

Core fields — `span.id`, `span.parent_id`, `span.name`, `span.kind`,
`span.status_code`, `span.events`, `span.links`, `span.timing.cpu` — are in
`semantic-fields.md`, with the full list in
`semantic-dictionary/model/trace.md` (18 060 words).

`span.kind` values: `server`, `client`, `producer`, `consumer`, `internal`
(default), `link`.

Permission: `storage:spans:read` plus a bucket permission. **Spans from one
trace can live in different buckets** — without permission on every relevant
bucket the user sees no trace at all. See `iam-grail-permissions.md`.

Field-level masking for spans uses the predefined fieldsets
`builtin-sensitive-spans` and `builtin-request-attributes-spans`, which apply to
spans, user.events and user.sessions but **not** to logs or events.

Storage and retention: `distributed-tracing/storage`,
`distributed-tracing/data-retention`. Ingesting traces from outside:
`distributed-tracing/ingest-traces`, and `ingest-otel.md` for OTLP.

## The Distributed Tracing app

`observe/application-observability/distributed-tracing/distributed-tracing-app`
— Explorer and Exceptions tabs, facet panel, waterfall span tree, per-span
attribute pane, and the logs attached to a trace.

Drilling from a trace to the frontend session
(`distributed-tracing-app/drill-down-to-frontend`) uses the **View user session**
button and an overflow menu with **View user error** and **View frontend
event**; both are greyed out on spans that carry no frontend link. Filter the
list to spans that do with `"Frontend link" = *`.

Analysis pages: `advanced-tracing-analytics`, `exception-analysis`,
`detect-performance-issues`, `tracking-transactions`,
`use-traces-and-dql-to-spot-patterns`. Permissions: `distributed-tracing/permissions`.

## Sampling: why span counts do not match request counts

**Adaptive Traffic Management** reduces the captured share of traces when volume
exceeds environment capacity, rather than dropping data unpredictably. On top of
that, `fetch spans, samplingRatio:N` returns roughly `1/N` of the raw records
and requires compensating arithmetic.

So a span count is not a request count unless both are accounted for. See
`oneagent.md` and `dql.md`.

## Request attributes and calculated service metrics

- `services/request-attributes` — capturing values from requests as attributes,
  which then become filterable and groupable. The
  `builtin-request-attributes-spans` fieldset exists to mask the sensitive ones.
- `services/calculated-service-metric` — deriving a metric from service traffic.
  Cheaper to query repeatedly than the underlying spans, and the documented
  advice when a span query runs often.

## Failure and response-time analysis

`services/failure-analysis`, `services/response-time-analysis`,
`services/monitor-service-message-processing`. Multidimensional analysis:
`observe/application-observability/multidimensional-analysis`.

## Profiling

`observe/application-observability/profiling-and-optimization`: CPU profiling,
memory profiling, continuous thread analysis, crash analysis, memory dump
analysis. Always-on profiling for services:
`services/always-on-app-profiling`.

Memory dumps need an ActiveGate with the **Memory dumps** module, which is
**not available on a containerized ActiveGate** — see `activegate.md`.

## Live Debugger

`observe/application-observability/live-debugger`. Requires **Observability for
Developers** to be enabled, scoped from environment level down to individual
entities, from either the Settings app or the Live Debugger app. Needs an
ActiveGate with the **Debugging** module.

> The enablement steps read oddly and it is not a conversion artifact: step 4
> navigates to *Enable Observability for Developers*, step 5 says *Turn off
> **Disable** Observability for Developers*. Verified against the live page.

## Classic

`observe/application-observability/services-classic` — the classic services
surface. Use it only for transition or comparison questions; see
`classic-vs-latest.md`.
