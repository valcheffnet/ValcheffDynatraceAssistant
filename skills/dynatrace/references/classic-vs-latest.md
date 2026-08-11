# Dynatrace Classic → latest Dynatrace

## Contents

- Deprecation status — what has actually been announced
- How to tell which is which
- Mapping table
- The central change: management zones → three concepts
- Metric alerting: metric events → Anomaly Detection app
- Alert notifications: problem notifications + alerting profiles → Workflows
- "Restrict to latest apps"
- What does not change
- Default retention at start
- Remaining upgrade guides in the docs

Sources: `/docs/manage/upgrade-guide-landing-page` (plus sub-pages),
`/docs/platform/upgrade`, `/docs/platform/upgrade/metric-alerting`,
`/docs/whats-new/technology/end-of-life-announcements` (harvested 2026-07-30).

## Deprecation status — what has actually been announced

**There is no published EOL date for Dynatrace Classic as a whole.** Verified in
`whats-new/technology/end-of-life-announcements` (Updated Jul 14, 2026), which
announces only these:

| Component | EoS | EoL |
|---|---|---|
| OneAgent 1.141 and older | 2018 | Aug 1, 2025 |
| OneAgent 1.215 and older | Apr 29, 2022 | Oct 1, 2025 |
| OneAgent 1.241 and older | Jun 8, 2023 | Jan 1, 2026 |
| OneAgent 1.299 and older | Sep 30, 2025 | **Sep 1, 2026** |
| Python Extension Framework 1.0 (OneAgent + ActiveGate) | Sep 1, 2024 / Sep 30, 2025 | with OneAgent/AG 1.299 |
| Native mobile apps (iOS/Android) | — | sunset **Jun 30, 2026** |
| Legacy ActiveGate "Update now" action + `forceUpdate` API flag | — | **Jan 1, 2027** (replaced by Fleet Management auto-update) |

**Management zones:** the docs say it outright — *"There is currently no
end-of-life date for management zones."* But using the latest apps, and
ingesting or querying data in Grail, requires adopting the new concepts.

**Dynatrace terminology:**
- **EoS (End of Support)** — the last date with bug fixes and security updates.
  After it the component still runs, but unmaintained, and the customer carries
  the risk.
- **EoL (End of Life)** — Dynatrace disables, removes or blocks the component.
  Support tickets are no longer accepted.

> Practical consequence: plan the migration because new functionality exists
> only there (and because Classic receives no investment), not because a date is
> scheduled. If someone needs a date for a business case, as of Jul 2026 none is
> published for Classic or management zones.

## How to tell which is which

Every doc page carries a tag under the title: **`Latest Dynatrace`** or
**`Dynatrace Classic`**. The same feature often has two separate pages. URLs
ending in `-classic` are legacy.

Classic sections in the docs, with page counts:
`dashboards-classic` (27), `log-monitoring` (44, against `logs` 94 for latest),
`metrics-classic` (4), `smartscape-classic` (1),
`service-level-objectives-classic` (6), `release-monitoring-classic` (4),
`classic-licensing` (12), `explorer` (4 — Data Explorer).

## Mapping table

| Classic | latest Dynatrace | Notes |
|---|---|---|
| **Management zones** | **Buckets** + **IAM policies** + **Segments** (three separate concepts) | See below — the most important change |
| Permissions via management zones | IAM ABAC policies (`ALLOW … WHERE …`) | Evaluated at query time |
| Dashboards Classic | **Dashboards** app | `/docs/analyze-explore-automate/dashboards-and-notebooks` |
| Data Explorer | **Notebooks** + DQL / Dashboards | The `explorer` section is classic |
| USQL (User Session Query Language) | **DQL** (`fetch user.sessions`, `fetch user.events`) | |
| Metric selectors | **DQL** `timeseries` command | `classicEntitySelector()` bridges the entity-selector syntax |
| Timeseries API v1 | Metrics API v2 → DQL | `/docs/dynatrace-api/basics/deprecation-migration-guides/timeseries-to-metrics` |
| Log Monitoring Classic | **Logs** app + **OpenPipeline** | `log-monitoring` (classic) against `logs` (latest) |
| Classic log processing pipeline | OpenPipeline | `/docs/platform/openpipeline/migration-classic-pipeline` |
| Metric events (metric key / metric selector) | **Anomaly Detection** app with DQL custom alerts | There is a transpiler — see below |
| Automated baselining / OOTB detectors | Davis analyzer: static, auto-adaptive thresholds, seasonal baseline | |
| Problem notifications + Alerting profiles | **Workflows** (connectors) + per-user email notifications in the **Problems** app | See below |
| SLOs Classic | **Service-Level Objectives** app | `service-level-objectives-classic` (6) against `service-level-objectives` (8) |
| Release monitoring classic | Release monitoring (latest) | |
| Smartscape Classic | Smartscape on Grail (`smartscapeNodes`/`smartscapeEdges`/`traverse`) | |
| Quality gates / Cloud Automation | **Site Reliability Guardian** | `/docs/deliver/site-reliability-guardian` |
| Native mobile app | Responsive web UI + Workflows notifications (Slack/Teams/PagerDuty/email/ntfy) | Sunset Jun 30, 2026 |
| Python Extensions 1.0 | Extensions 2.0 framework | |
| ActiveGate "Update now" | **Fleet Management** auto-update (target version plus update windows) | EoL Jan 1, 2027 |
| Classic licensing (host units, DDUs …) | **DPS** — Ingest & Process / Retain / Query | `license/classic-licensing` against `license/capabilities` |

## The central change: management zones → three concepts

Classic management zones did **two things at once**: access control *and*
filtering. That was flexible, but it became a bottleneck in large enterprise
environments with a lot of data. Management zones also required the data to be
**tied to a monitored entity**, or they did not work at all.

Latest splits that apart:

| Concept | Mechanism | Answers |
|---|---|---|
| **Data partitioning** | Grail **buckets** | Logical organisation, retention, performance, compliance separation, cost allocation |
| **Data access control** | **IAM policies** (ABAC) | Who may see or do what |
| **Data segmentation** | **Segments** | Runtime multidimensional filtering for context |

**How access control differs in substance:**
- Classic: controls access to monitoring data (traces, metrics) **indirectly,
  through entity IDs**.
- Latest: controls access on **permission-relevant fields** plus the new
  `dt.security_context` field — **with no entity relation needed**.

Every Dynatrace component guarantees that the table-relevant permission fields
are present on each record (event, log, span) or metric, giving one consistent
permission model across the environment.

**Critical to understand:** segments are **not** a security boundary. They
filter only data the user already has IAM access to. A colleague expecting
management-zone-like isolation from a segment is mistaken — isolation comes
from bucket plus IAM policy.

Straight from the docs FAQ: *"Segments themselves don't restrict access; they
filter and contextualize data that users are authorized to see."*

### Recommended migration order

1. **Plan the buckets** — group data by logic and compliance need (region,
   environment, sensitivity) with retention, cost and performance in mind.
2. **Roll out access controls** — who sees what, by role or by attribute.
3. **Build the segments** — business-aligned dynamic views for self-service.

Detail: `grail-and-data-organization.md`, `iam-grail-permissions.md`.

## Metric alerting: metric events → Anomaly Detection app

**Prerequisites:** an active **DPS** licence plus permissions for the Anomaly
Detection app.

Classic had two kinds of metric event:
- **Metric key events** — evaluate a single metric; **static thresholds only**.
- **Metric selector events** — a complex query through a metric selector, able
  to include historical data and arithmetic across several metrics.

Latest: the **Anomaly Detection** app, doing real-time analysis of Grail data
through DQL. It offers more than classic:
- DQL queries, not only metric records
- alerting on **logs, spans and business events**, not only metrics
- advanced queries across more data records

**Transform procedure:**
1. On first run → *Anomaly Detection* > **Edit > Authorization settings** →
   select the required permissions.
2. *Add Custom alert* > **Improve metric events with DQL** → pulls in every
   available metric event.
3. Select and **Transform**.

**Limits and gotchas:**
- **Only metric selectors are transpiled.** Metric key events are not.
- The original metric event is **auto-disabled** and the new configuration
  becomes active.
- The post-transform check **does not guarantee** correctness — it cannot detect
  whether the metric's data actually exists or whether the required tags are
  present. **Verify manually:** *More actions > Open with > View and execute
  Grail query*.
- On the Transformation page, transformed events show State = `Disabled`,
  Migrated = `Yes`.
- **SLO metric events** are a separate case: SLOs use functional metrics, which
  behave differently under transformation. The docs say "We're working on a
  separated guide."
- Extension-based alerts (F5 BIG-IP, for example) also go through the
  transpiler; DQL Alerting templates are expected for more technologies.
- AWS and Azure recommended alerting rules create metric events, so they follow
  the same path.

## Alert notifications: problem notifications + alerting profiles → Workflows

**Requires an active DPS licence.**

**The problem with classic:**
- Configurations were always **global to the environment**, so no user could set
  up their own email notification without admin permissions.
- Integrations were **hardcoded** and inflexible.

Classic out-of-the-box channels: Ansible, Custom Integration (generic HTTP
webhook), Email, Jira, OpsGenie, PagerDuty, ServiceNow, Slack, Trello,
VictorOps, xMatters.

Classic **alerting profiles** filtered on: management zones, problem categories
(Availability, Error, Slowdown, Resource, Custom, Monitoring unavailable),
problem event type plus text filter, and problem duration.

**Latest:**
- **Personal email notifications** through the **Problems** app — per user, no
  admin rights needed.
- **Workflows connectors** for external systems — flexible integration.
- **Jinja template engine** for dynamic workflow configuration.
- **EdgeConnect** for secure connectivity to on-premise systems.
- Filtering happens in **DQL** over Grail.

Concepts needed: Workflows (including Simple workflows), connectors, Jinja,
EdgeConnect, individual problem notifications, DQL filtering.

## "Restrict to latest apps"

There is an option to restrict users to the latest apps, hiding the classic UI →
`/docs/manage/upgrade-guide-landing-page/upgrade-guide-prevent-classic`. Useful
during rollout so people do not learn a UI that is going away.

## What does not change

From the docs, explicitly: *"these adaptations only apply to the usage of new
and improved functionality referred to as 'Latest Dynatrace'. Existing
functionality is not affected."*

Classic functionality keeps working in parallel. The upgrade guide targets
**SaaS admins with environments on AWS or Azure**.

Users can already switch to the new UI, but much of the functionality there is
still derived from existing views that rely on **management zones and classic
permissions**.

## Default retention at start

Logs, events and business events use their own tables with default buckets and
**35 days retention**. Default buckets are prefixed `default_` and **cannot be
modified**.

## Remaining upgrade guides in the docs

`/docs/manage/upgrade-guide-landing-page/`:
- `upgrade-guide-concepts` — the new concepts (60-min read)
- `upgrade-guide-alert-notification` — alert notifications (60-min read)
- `upgrade-guide-prevent-classic` — restricting to the latest apps

`/docs/platform/upgrade/`:
- `metric-alerting`

Plus segments upgrade guidance (management zones → segments with concrete
examples) and dashboards guidance. The docs say the list will grow.

Other specific migration guides:
- `platform/openpipeline/migration-classic-pipeline`, `platform/openpipeline/migration-settings`
- `analyze-explore-automate/metrics/upgrade/{kubernetes,rum,runtime,service}-metric-migration`
- `dynatrace-api/basics/deprecation-migration-guides/timeseries-to-metrics`
- `whats-new/dynatrace-api/deprecated-apis`
- `manage/network-zones/migration/{plan,deploy,analyze,verify}`
- `deliver/configuration-as-code/monaco/guides/{deprecated-migration,migrating-to-v2}`
- `ingest-from/setup-on-k8s/guides/migration/*` (classic→cloud-native, classic→app-monitoring, CSI→ephemeral volumes, DynaKube API versions)
