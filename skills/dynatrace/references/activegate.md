# ActiveGate — proxy, collector and remote monitor

An ActiveGate does two unrelated jobs, and conflating them causes most sizing
and placement mistakes:

1. **A secure proxy** between OneAgents and the Dynatrace cluster, giving one
   local egress point instead of every host talking outbound.
2. **A monitoring engine in its own right**, polling cloud APIs, databases,
   SNMP and Prometheus, and terminating ingest endpoints (OTLP, metrics, logs,
   syslog, RUM beacons).

Corpus: `ingest-from/dynatrace-activegate` (39 files).

## Contents

- Types: Environment and Cluster
- Deployment shapes
- Modules and what they enable
- Connectivity schemes
- Configuration
- The `agctl` CLI
- Security
- Diagnostics and self-monitoring
- Placement guidance

## Types: Environment and Cluster

| Type | When |
|---|---|
| **Environment ActiveGate** | SaaS — the only type needed |
| **Cluster ActiveGate** | Managed deployments, in front of the cluster |

On SaaS, install an Environment ActiveGate. Which functionality it offers is
determined by its **modules**, not by its type.

An Environment ActiveGate can serve several environments — see
`configuration/configure-an-environment-activegate-for-multi-environment-support`.

## Deployment shapes

- **Host-based** — on a physical or virtual machine, Linux or Windows.
- **Containerized** — the ActiveGate packaged as a container.
  `activegate-in-container` covers the differences, persistence requirements and
  configuration. Not every module is available in a container.

**Grouping:** ActiveGates can be organised into groups (`activegate-group`) so
OneAgents fail over between members of the same group.

## Modules and what they enable

Functionality comes from modules. Availability differs across host-based x86-64,
other architectures and containerized deployments — the table in
`ingest-from/dynatrace-activegate/capabilities.md` is the authority. The mapping:

| Functionality | Module |
|---|---|
| Message routing, buffering and compression, authentication, access to sealed networks | OneAgent routing |
| Memory dumps | Memory dumps |
| AWS monitoring | AWS |
| Azure monitoring | Azure |
| Cloud Foundry monitoring | Cloud Foundry |
| Kubernetes / OpenShift monitoring | Kubernetes |
| ActiveGate extensions | Extensions |
| Oracle database insights | Database insights |
| VMware / virtualized infrastructure | VMware |
| Dynatrace API access | REST API |
| Log Monitoring | Log Monitoring |
| Metric ingestion | HTTP Metric API |
| OpenTelemetry metric and trace ingestion | OTLP Ingest |
| OpenTelemetry log ingestion | Log Monitoring |
| Real User Monitoring beacons | Beacon forwarder |
| Live Debugging | Debugging |
| Syslog ingestion | Extensions |

Two placement traps live in that table:

- **Extensions and syslog ingestion are host-based x86-64 only.** A containerized
  ActiveGate cannot terminate syslog or run ActiveGate extensions.
- **AWS monitoring and memory dumps are not available in containers either.**

Synthetic monitoring runs on a **synthetic-enabled ActiveGate**, which is a
different capability set with its own hardware requirements
(`capabilities/synthetic-purpose`). z/OS traffic routing uses **zremote**
(`capabilities/zremote-purpose`).

## Connectivity schemes

`supported-connectivity-schemes-for-activegates` — which topologies are
supported for SaaS and Managed, including chained ActiveGates where one forwards
to another closer to the cluster.

## Configuration

`ingest-from/dynatrace-activegate/configuration/`:

| Page | Topic |
|---|---|
| `configure-activegate` | the main configuration file and module enablement |
| `configure-an-environment-activegate-for-multi-environment-support` | one ActiveGate, several environments |
| `configure-custom-ssl-certificate-on-activegate` | replacing the certificate |
| `configure-trusted-root-certificates-on-activegate` | trusting an internal CA |
| `how-to-configure-ciphers-on-activegate` | cipher suites |
| `set-up-proxy-authentication-for-activegate` | outbound proxy with auth |
| `set-up-reverse-proxy-for-activegate`, `set-up-reverse-proxy-for-oneagent` | fronting with a reverse proxy |
| `where-can-i-find-activegate-files` | file locations |

## The `agctl` CLI

`agctl-command-line-interface` — the command-line surface for configuring and
inspecting an ActiveGate without editing files by hand.

## Security

- `activegate-security` — hardening.
- `activegate-fips-compliance` — FIPS mode.
- Custom SSL certificates, trusted roots and cipher configuration are in the
  configuration pages above.

**The legacy "Update now" action and the `forceUpdate` API flag reach EoL on
Jan 1, 2027**, replaced by Fleet Management auto-update. See
`classic-vs-latest.md`.

## Diagnostics and self-monitoring

- `activegate-diagnostics` — troubleshooting.
- `activegate-sfm-metrics` — self-monitoring metrics, the way to alert on an
  ActiveGate before OneAgents start buffering.
- Health and alerts: `ingest-from/fleet-management/activegate-health-overview`.

## Placement guidance

- **One local egress point** is the usual reason to deploy at all: OneAgents
  talk to the ActiveGate, the ActiveGate talks outbound.
- **Sealed networks** reach Dynatrace only through an ActiveGate.
- **Ingest endpoints terminate here.** OTLP, the metric API, log ingest and RUM
  beacons all land on an ActiveGate with the right module, so ingest volume
  drives sizing as much as OneAgent count does.
- **Cloud monitoring is polling.** AWS, Azure, Kubernetes and VMware monitoring
  run *on* the ActiveGate against provider APIs — that workload is independent
  of how many OneAgents route through it.
- **Group ActiveGates for failover** rather than relying on a single instance.
- **Network zones** (`manage/network-zones`) decide which OneAgent talks to
  which ActiveGate. Set the zone at install with `--set-network-zone` — see
  `oneagent.md`.
