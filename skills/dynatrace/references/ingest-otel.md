# OpenTelemetry ingest

Three ways to get OTLP into Dynatrace, one API surface underneath all of them.
Most failures here are URL, protocol or token-scope mistakes rather than
instrumentation problems.

Corpus: `ingest-from/opentelemetry` (71 files).

## Contents

- The three ingest methods
- The OTLP API
- Base URLs — and the one that looks right but is not
- Signal paths
- Authentication and token scopes
- API limitations
- The Collector
- Semantic mapping
- Security context
- Licensing
- Choosing a method

## The three ingest methods

```
App ──────────────────────── OTLP ─────────────────────────┐
App ── OTLP ─→ Standard OTel Collector ── OTLP API ────────┼──→ Dynatrace
App ── OTLP ─→ Dynatrace OTel Collector ── OTLP API ───────┘
```

| Method | Best when |
|---|---|
| **Direct export to the Dynatrace API** | minimal complexity and no extra infrastructure; simple deployments |
| **Standard OTel Collector** | the organisation has already standardised on OTel Collectors and has the expertise |
| **Dynatrace OTel Collector** *(recommended)* | most Dynatrace deployments needing processing, with a supported distribution |

## The OTLP API

`ingest-from/opentelemetry/otlp-api`. Sub-pages for `ingest-traces`,
`ingest-logs`, `ingest-otlp-metrics` and `otel-semantic-mapping`.

## Base URLs — and the one that looks right but is not

| Target | Base URL |
|---|---|
| Dynatrace SaaS | `https://{environment-id}.live.dynatrace.com/api/v2/otlp` |
| Environment ActiveGate | `https://{activegate-domain}:9999/e/{environment-id}/api/v2/otlp` |
| Containerized Environment ActiveGate | `https://{activegate-domain}/e/{environment-id}/api/v2/otlp` |

**The apps domain is not the ingest domain.** This is the single most common
mistake:

```
WRONG   https://{environment-id}.live.apps.dynatrace.com/api/v2/otlp
RIGHT   https://{environment-id}.live.dynatrace.com/api/v2/otlp
```

The failure it produces names the wrong culprit:

```
not retryable error: Permanent error: rpc error: code = Unimplemented
desc = error exporting items, request to https://<environment>.live.apps.dynatrace.com/...
```

`Unimplemented` reads like a protocol problem. It is a hostname problem.

Note the containerized ActiveGate drops the `:9999` port that the host-based one
requires.

## Signal paths

Append to the base URL:

| Signal | Path |
|---|---|
| Traces | `/v1/traces` |
| Metrics | `/v1/metrics` |
| Logs | `/v1/logs` |

So SaaS traces land at
`https://{environment-id}.live.dynatrace.com/api/v2/otlp/v1/traces`.

## Authentication and token scopes

An API access token in the `Authorization` header, one scope per signal. Scopes
can be combined in a single token or added to an existing one:

| Signal | Scope |
|---|---|
| Traces | `openTelemetryTrace.ingest` |
| Metrics | `metrics.ingest` |
| Logs | `logs.ingest` |

Environment variables for an SDK exporter:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=[YOUR_BASE_URL]
OTEL_EXPORTER_OTLP_HEADERS="Authorization=Api-Token [YOUR_TOKEN]"
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
```

The `Api-Token ` prefix inside the header value is part of the value, not
decoration.

## API limitations

Two hard ones, and both are easy to trip over because the OTel defaults go the
other way:

- **gRPC is not supported.** Calls must use HTTP. A Collector can transform OTLP
  gRPC into HTTP — see `collector/use-cases`.
- **JSON is not supported for Protocol Buffers.** Binary format only, hence
  `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`.

An ActiveGate needs the **OTLP Ingest** module for metrics and traces, and the
**Log Monitoring** module for logs — see `activegate.md`.

## The Collector

`ingest-from/opentelemetry/collector` — deployment, configuration, scaling,
resiliency, self-monitoring, system requirements, references and use cases.

Standard Collector anatomy applies: **receivers** take data in, **processors**
(optional) transform it, **exporters** send it on, and **services** wire them
into pipelines.

Two distributions are documented: the **Dynatrace OTel Collector**, which is
supported, and the upstream **OpenTelemetry distributions**.

## Semantic mapping

`otlp-api/otel-semantic-mapping` — how OTel semantic conventions map onto
Dynatrace fields. The Semantic Dictionary carries OTel semconv names alongside
`dt.*` names; when a user quotes an OTel attribute, check
`semantic-fields.md` before assuming it survives ingest under the same name.

## Security context

`ingest-from/opentelemetry/opentelemetry-security-context` — setting
`dt.security_context` on OTLP data so record-level IAM applies. Without it,
OTLP records fall back to whatever OpenPipeline assigns. See
`iam-grail-permissions.md`.

## Licensing

`ingest-from/opentelemetry/opentelemetry-licensing`. OTLP data is charged on the
same DPS dimensions as everything else — Ingest & Process, Retain, Query — so
Collector-side filtering directly reduces the bill. See
`grail-and-data-organization.md`.

## Choosing a method

- **Direct export** when there is no Collector already and the telemetry is
  simple. The cost is that every application needs the endpoint and token, and
  there is nowhere to filter before ingest.
- **A Collector** when data needs shaping, batching or filtering before it is
  charged, when gRPC has to be translated to HTTP, or when applications should
  not hold Dynatrace tokens.
- **The Dynatrace distribution** unless there is a reason to run the upstream
  one; it is the supported path.

Instrumentation walkthroughs per language: `ingest-from/opentelemetry/walkthroughs`.
Integrations: `ingest-from/opentelemetry/integrations`.
Troubleshooting: `ingest-from/opentelemetry/troubleshooting`.
