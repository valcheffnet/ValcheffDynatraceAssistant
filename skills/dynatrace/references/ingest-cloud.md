# Cloud ingest — AWS, Azure, Google Cloud

All three providers follow the same shape: create a **connection**, then choose
which telemetry streams to pull. What differs is the mechanism per signal, and
that is where the questions land.

Corpus: `ingest-from/amazon-web-services` (179 files),
`microsoft-azure-services` (159), `google-cloud-platform` (69).

## Contents

- The common shape
- Creating a connection
- AWS
- Azure
- Google Cloud
- The Clouds app
- Permission fields
- Cost and volume control

## The common shape

```
Connection (auth + scope)  →  Telemetry streams  →  OpenPipeline  →  Grail
                              metrics · logs · topology · events
```

Four signal types per provider, each with its own mechanism and its own cost
behaviour. Metrics are polled, logs are pushed, topology is scanned, events are
subscribed.

Onboarding pages: `amazon-web-services/aws-onboarding`,
`microsoft-azure-services/azure-onboarding`,
`google-cloud-platform/gcp-onboarding`.

## Creating a connection

Each provider offers three routes, and they are not equivalent in what they can
express:

| Provider | UI | API | CLI |
|---|---|---|---|
| AWS | `create-an-aws-connection/aws-connection-app-settings` | `aws-connection-api` | `aws-connection-api-cli` |
| Azure | `create-an-azure-connection/azure-connection-app-settings` | `azure-connection-api` | `azure-connection-cli` |
| GCP | `create-a-gcp-connection` | — | `gcp-terraform-scripts` |

Managing existing connections: `manage-azure-connections`,
`manage-gcp-connections`. AWS multi-account is handled through
`amazon-web-services/aws-organizations`.

GCP ships **Terraform scripts** as a first-class onboarding path
(`gcp-terraform-scripts`), which is the cleanest option when the environment is
already IaC-managed. See `config-as-code` topics for the wider picture.

## AWS

### CloudWatch metrics

Any CloudWatch metric from any namespace can be polled. Three levers:

- **Metric groups** — curated collections per AWS service, the recommended
  starting point.
- **Auto discovery metric group** — pulls all key metrics, for
  business-critical services.
- **Region selection** — the poller only polls the regions selected.

Detail: `integrate-with-aws/cloudwatch-metrics`, `aws-metrics-ingest`. Full
per-service coverage: `integrate-with-aws/aws-all-services`.

> `integrate-with-aws/cloudwatch-metrics` is the single most cross-referenced
> page in the corpus — 205 anchored links point into it, and several of those
> anchors are dead upstream. Verify an anchor before quoting it. See
> `gotchas.md`.

### Logs

CloudWatch logs arrive through **Amazon Data Firehose**. Log groups are
subscribed to auto-generated Firehose streams; incoming logs are routed to
buckets through OpenPipeline. Supported sources (AWS Lambda CloudWatch Logs, for
example) are transformed and enriched with cloud metadata — AWS tags, account
ID.

Detail: `ingest-telemetry/cloudwatch-logs`, and
`cloudwatch-logs/amazon-data-firehose/aws-subscribe-log-groups` for the
subscription step.

### Topology

A topology service periodically scans the AWS environment and builds an
inventory of resources with metadata. Queryable in DQL — finding idle resources,
unattached EBS volumes and underused EC2 instances are the documented use cases.

Detail: `ingest-telemetry/aws-topology`.

### Events

**AWS EventBridge** with Dynatrace configured as an API destination. Event
sources are subscribed and published to EventBridge; `aws.health` events for EC2
are the worked example. Workflows can then trigger on event type or payload.

Detail: `ingest-telemetry/aws-events`.

### Deeper integration

`integrate-into-aws` and `aws-platform` cover running Dynatrace components
inside AWS rather than pointing at it from outside.

## Azure

The same four signals — topology, metrics, logs, events — documented at
`microsoft-azure-services/azure-onboarding` with per-signal detail under
`ingest-telemetry/`.

**Azure Native Integration** (`azure-native-integration`) is the distinct path:
Dynatrace as an Azure Marketplace resource, managed from the Azure portal, as
opposed to configuring a connection from the Dynatrace side.

Service-specific integration pages live under `azure-integrations`.

## Google Cloud

`google-cloud-platform/gcp-onboarding` is structured differently from the other
two, by concern rather than by signal:

| Section | Content |
|---|---|
| Authenticate | connection credentials |
| Topology | discovered resources, including **location and region fields** |
| Metrics | including **detecting scoping projects** |
| Logs | log ingest |
| Tags and labels | how GCP labels map to Dynatrace tags |
| Telemetry data in context | correlation, plus **enrichment timing considerations** |

**Enrichment timing** is worth reading before diagnosing "metadata is missing on
some records": enrichment is not instantaneous, and records ingested before
topology discovery completes can lack the cloud attributes that later records
carry.

Supported services: `dac-gcp-supported-services`. Integrations:
`gcp-integrations`.

## The Clouds app

All three providers surface in **Clouds**, where logs, topology and events are
shown in context — Lambda logs attached to the function, for instance. It is the
navigation layer, not a separate ingest path.

## Permission fields

Cloud identifiers are among the fourteen fields usable in IAM record-level
rules:

`aws.account.id` · `azure.subscription` · `azure.resource.group` ·
`gcp.project.id`

They work on events, security.events, bizevents, logs, metrics, spans and
smartscape. That makes per-account or per-subscription isolation possible
without setting `dt.security_context` — see `iam-grail-permissions.md` and
`semantic-fields.md`.

## Cost and volume control

- **Metric polling is the usual surprise.** Auto discovery across every region
  and namespace ingests a great deal. Cherry-pick metric groups and regions
  first, widen later.
- **Logs route through OpenPipeline like anything else**, so the Drop record
  processor applies before Ingest & Process is charged — see `openpipeline.md`.
- **Cloud tags become primary Grail tags** when configured, giving cost
  allocation and filtering without joins — see `semantic-fields.md`.
- An ActiveGate with the **AWS**, **Azure** or **Kubernetes** module does the
  polling; that workload sizes independently of OneAgent traffic. Note the AWS
  module is **not available on a containerized ActiveGate** — see
  `activegate.md`.
