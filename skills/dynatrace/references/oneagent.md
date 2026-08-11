# OneAgent — deployment, configuration, updates

OneAgent is the auto-discovery and instrumentation agent. One binary per host;
what it does is decided by monitoring mode, installer parameters and
process-group settings, not by which package was downloaded.

Corpus: `ingest-from/dynatrace-oneagent` (92 files).

## Contents

- Monitoring modes
- Host requirements
- Installation
- Installer parameters
- Changing configuration after install
- Host identity, groups and tags
- Security context at the agent
- Updates and update windows
- Adaptive Traffic Management
- Aging mechanism
- Cost allocation
- Where to look for the rest

## Monitoring modes

| Mode | What it does |
|---|---|
| `fullstack` | Full-Stack Monitoring — deep code-level instrumentation, traces, all telemetry |
| `infra-only` | Infrastructure Monitoring — hosts, processes, logs, network; **no code-level instrumentation and no traces** |
| `discovery` | Discovery mode — inventory without monitoring |

Set at install with `--set-monitoring-mode`, changed afterwards with the same
flag through the OneAgent CLI. The mode drives licence consumption, so "why is
this host not producing traces" is usually a mode question rather than an
instrumentation one.

## Host requirements

- **CPU:** x86-64-v2 microarchitecture is the **minimum baseline** — SSE3,
  SSSE3, SSE4.1, SSE4.2, POPCNT, CMPXCHG16B. Intel from Nehalem, AMD from
  Bulldozer. Systems below that baseline **cannot run OneAgent at all**. In
  virtualised environments CPU feature passthrough has to be enabled or the
  guest will not meet it.
- **Memory:** at least 256 MB free to run the installation or an update, and
  256 MB of virtual memory during installation. Deep monitoring adds per-process
  RSS on top of the application's own demand, and the increase is **not** a
  constant or a fixed proportion — it varies by technology and configuration.
- **Kubernetes and other platforms with memory limits:** the limit applies to
  RSS, and OneAgent code modules raise RSS. **Raise workload memory limits when
  enabling deep monitoring**, or workloads get OOM-killed after instrumentation
  with no obvious cause.
- **Permissions:** the *Download/install OneAgent* environment permission,
  elevated privileges to start the installation (there is a non-privileged
  installation path with its own requirements), and the ability to restart the
  application services.
- **Network:** outbound connectivity to the Dynatrace cluster or an ActiveGate.
  Firewall policies usually need the Dynatrace addresses allow-listed
  explicitly.

Architecture and OS coverage: `ingest-from/technology-support`.

## Installation

The UI path is **Discovery & Coverage → Install → Install OneAgent**, which
generates the command with the tenant and token filled in.

Per-OS installation and operation pages exist for **Linux, Windows, AIX, Solaris
and z/OS**, each split into `installation/` and `operation/`. Linux also carries
pages for non-privileged installation, Flatcar OS, AppArmor-confined
applications, PowerPC big-endian, and proxy configuration during installation.

## Installer parameters

These are the `--set-*` flags accepted by the installer and, for most of them, by
the CLI afterwards:

| Parameter | Purpose |
|---|---|
| `--set-server` | the endpoint OneAgent reports to (cluster or ActiveGate) |
| `--set-tenant`, `--set-tenant-token` | environment identity and token |
| `--set-proxy` | proxy address |
| `--set-monitoring-mode` | `fullstack`, `infra-only`, `discovery` |
| `--set-host-group` | host group assignment — see below |
| `--set-host-name` | override the detected host name |
| `--set-host-id-source` | how host identity is derived |
| `--set-host-tag` | tag applied to the host |
| `--set-host-property` | arbitrary host property |
| `--set-network-zone` | network zone membership |
| `--set-auto-update-enabled` | agent auto-update on or off |
| `--set-auto-injection-enabled` | deep-monitoring injection on or off |
| `--set-app-log-content-access` | allow access to application log content |
| `--set-system-logs-access-enabled` | allow access to system logs |
| `--set-extensions-ingest-port`, `--set-extensions-statsd-port` | local ingest ports for Extensions and StatsD |
| `--set-watchdog-portrange` | watchdog port range |
| `--set-param` | generic parameter passthrough |
| `--restart-service` | restart services after install |

## Changing configuration after install

`ingest-from/dynatrace-oneagent/oneagent-configuration-via-command-line-interface`
— the CLI takes the same `--set-*` flags, so host group, monitoring mode,
network zone and update behaviour are all changeable without reinstalling.

Feature-level configuration (which technologies are deeply monitored, what is
captured) is done in the web UI or the API, at two levels: **global** and **per
process group**. Process-group settings override global.
`ingest-from/dynatrace-oneagent/oneagent-features`.

## Host identity, groups and tags

- **Host group** (`--set-host-group`) is structural: it scopes configuration,
  drives naming, and is a permission field (`dt.host_group.id` — one of the
  fourteen fields usable in IAM record-level rules, see `semantic-fields.md`).
- **Host tags** (`--set-host-tag`) and **host properties**
  (`--set-host-property`) are metadata for filtering and auto-tagging rules.
- **`--set-host-id-source`** determines how the host is identified across
  reboots and re-imaging. Changing it creates a new host entity, which looks
  like host churn in licensing.

## Security context at the agent

`ingest-from/dynatrace-oneagent/oneagent-security-context` — OneAgent can set
`dt.security_context` on the data it sends, so record-level IAM works without an
OpenPipeline rule. This is the earliest point at which the context can be
attached, and the most reliable, because it does not depend on a pipeline
matcher.

Agent hardening: `oneagent-security`, plus per-OS security pages.

## Updates and update windows

`ingest-from/dynatrace-oneagent/oneagent-update` covers four things: monitoring
which agents updated, configuring the update policy, defining **update windows**,
and disabling automatic updates.

Version support is not open-ended — OneAgent 1.299 and older reach EoL on
**Sep 1, 2026**. The full EoS/EoL table is in `classic-vs-latest.md`.

The legacy ActiveGate "Update now" action and the `forceUpdate` API flag reach
EoL on **Jan 1, 2027**, replaced by Fleet Management auto-update.

## Adaptive Traffic Management

`ingest-from/dynatrace-oneagent/adaptive-traffic-management` — when trace volume
exceeds the environment's capacity, Dynatrace reduces the captured share rather
than dropping data unpredictably. Relevant when someone asks why span counts do
not match request counts: the answer may be sampling, not lost data. Compensate
in DQL with `samplingRatio` arithmetic — see `dql.md`.

## Aging mechanism

`ingest-from/dynatrace-oneagent/oneagent-aging-mechanism` — how OneAgent handles
hosts that stop reporting, and when their entities age out.

## Cost allocation

`ingest-from/dynatrace-oneagent/oneagent-cost-allocation` — attributing host and
ingest consumption to cost centers from the agent side. The pipeline side of the
same question is the Cost allocation stage in `openpipeline.md`.

## Where to look for the rest

| Topic | Path |
|---|---|
| Requirements per OS and technology | `ingest-from/technology-support` |
| Attribute enrichment | `dynatrace-oneagent/oneagent-attribute-enrichment` |
| Agent health | `dynatrace-oneagent/oneagent-health` |
| Troubleshooting | `dynatrace-oneagent/oneagent-troubleshooting` |
| Ansible deployment | `dynatrace-oneagent/deployment-orchestration/ansible` |
| OneAgent with OpenTelemetry | `dynatrace-oneagent/oneagent-and-opentelemetry` |
| Kubernetes deployment | `ingest-from/setup-on-k8s` — the operator, not the host installer |
