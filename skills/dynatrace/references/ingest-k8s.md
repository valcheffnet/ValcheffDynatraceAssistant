# Kubernetes ingest — the Dynatrace Operator and its deployment modes

Kubernetes monitoring is not the host installer running in a pod. It is the
**Dynatrace Operator** reconciling a `DynaKube` custom resource, and the first
question on any Kubernetes issue is which **deployment mode** is in use — the
modes differ in what gets instrumented, what runs privileged, and what is
charged.

Corpus: `ingest-from/setup-on-k8s` (110 files).

## Contents

- Deployment modes
- The Dynatrace Operator
- Tokens and scopes
- Log monitoring
- Security posture management
- Security context
- Cost allocation
- Migration paths
- Where to look for the rest

## Deployment modes

| Mode | What it monitors | Code-level instrumentation |
|---|---|---|
| **Kubernetes platform monitoring** | the cluster itself — nodes, workloads, events, the API server | no |
| **Application observability** | applications in pods | yes, via init container |
| **Full-stack observability** (cloud-native) | cluster plus nodes plus applications | yes |
| **Classic Full-Stack** *(other)* | the older node-agent-per-host model | yes |
| **Host monitoring** *(other)* | nodes only, no application instrumentation | no |

`how-it-works/kubernetes-monitoring`, `how-it-works/application-monitoring`,
`how-it-works/cloud-native-fullstack`,
`how-it-works/other-deployment-modes/{classic-fullstack,host-monitoring}`.

Classic Full-Stack and host monitoring are documented under "other" because they
are the legacy shapes. New deployments use cloud-native full-stack or
application observability.

**The commonest confusion:** platform monitoring gives cluster and workload
visibility with no traces. When someone reports "Kubernetes is monitored but I
see no services", the mode is the answer.

## The Dynatrace Operator

`how-it-works/components/dynatrace-operator` — the operator owns the lifecycle
of OneAgent and ActiveGate inside the cluster, driven by the `DynaKube` CR.

Release notes are their own section: `whats-new/dynatrace-operator` (24 pages),
which is where the API version changes and breaking behaviour are announced.

## Tokens and scopes

`deployment/tokens-permissions`. Two tokens, and giving one the other's scopes
is a routine cause of a half-working install.

**Operator token** — manages the components:

| Scope | Purpose |
|---|---|
| PaaS — Installer (`Installer download`) | OneAgent and ActiveGate lifecycle |
| API v1 `DataExport` | notifies the cluster of graceful shutdown |
| API v2 `settings.read`, `settings.write` | manages the ActiveGate object for Kubernetes API monitoring — optional from Operator 1.7.0+ |
| API v2 `entities.read` | checks whether the ActiveGate object exists — 0.4.0 to <1.7.0 only, **no longer required from 1.7.0+** |
| API v2 `activeGateTokenManagement.create` | creates the ActiveGate authentication token |

> The ActiveGate authentication token is **rotated every 30 days**, and rotation
> deletes and recreates the affected ActiveGate. A monitoring gap on a 30-day
> cadence is this, not a fault.

**Data Ingest token** — carries the telemetry:

| Scope | Purpose |
|---|---|
| API v2 `metrics.ingest` | metadata enrichment for custom metrics |
| API v2 `logs.ingest` | logs through Log Monitoring API v2 |
| API v2 `openTelemetryTrace.ingest` | OpenTelemetry traces |

Newer platform-token scopes appear alongside the classic ones:
`fleet-management:activegate.connection-info:read`,
`fleet-management:activegate.tokens:create`,
`fleet-management:container-images:read`,
`fleet-management:oneagent.connection-info:read`,
`fleet-management:oneagents:download`,
`settings:objects:read`, `settings:objects:write`,
`openpipeline:logs:ingest`, `openpipeline:metrics:ingest`,
`openpipeline:traces:ingest`, `storage:metrics:write`.

Onboarding is done by a **service user** with platform tokens rather than a
personal token — see the "Create a service user" and "Create platform tokens"
sections of the same page.

## Log monitoring

`deployment/k8s-log-monitoring` — streaming container logs. Configured through
settings objects, which is why the operator token needs `settings:objects:read`
and `write`.

## Security posture management

`deployment/security-posture-management` — KSPM. Also settings-object driven.

## Security context

`setup-on-k8s/k8-security-context` — setting `dt.security_context` on Kubernetes
telemetry. Worth doing at this layer: `k8s.namespace.name` and
`k8s.cluster.name` are already permission fields (see `semantic-fields.md`), so
namespace-scoped IAM works without extra context, but anything cutting across
namespaces needs the explicit field.

## Cost allocation

`setup-on-k8s/kubernetes-cost-allocation` — attributing consumption per cluster
and namespace.

## Migration paths

`guides/migration/` covers the transitions that break things:

- classic full-stack → cloud-native full-stack
- classic full-stack → application monitoring
- CSI driver → ephemeral volumes
- DynaKube API versions

A DynaKube API version bump is a CR schema change — read the operator release
notes before applying one.

## Where to look for the rest

| Topic | Path |
|---|---|
| Quickstart | `setup-on-k8s/quickstart` |
| Supported technologies | `deployment/supported-technologies` |
| Application observability setup | `deployment/application-observability` |
| Full-stack setup | `deployment/full-stack-observability` |
| Platform observability setup | `deployment/platform-observability` |
| Marketplace installs | `deployment/marketplaces` |
| Troubleshooting | `deployment/troubleshooting` |
| Integrations | `extend-observability-k8s` |
| Reference | `setup-on-k8s/reference` |
| Container registries, public registry | `guides/container-registries` |
| Non-Kubernetes container platforms | `ingest-from/setup-on-container-platforms` |

An ActiveGate with the **Kubernetes** module is what monitors the cluster API —
see `activegate.md`. Memory limits need raising when deep monitoring is enabled,
because code modules increase RSS and the limit applies to RSS — see
`oneagent.md`.
