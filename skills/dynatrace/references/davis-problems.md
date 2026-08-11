# Davis AI, anomaly detection and problems

Davis is causal, not just statistical: it correlates events across topology
layers to name a root cause, rather than reporting every anomaly separately.
Understanding the **problem lifecycle** is what makes the rest make sense.

Corpus: `dynatrace-intelligence` (71 files).

## Contents

- Events, incidents and problems
- The problem lifecycle
- Root cause analysis
- Duplicate problems and processing state
- Anomaly detection: the detector types
- Sensitivity
- Custom alerts with DQL
- Metric events and the transpiler
- The Problems app
- Frequent issues
- Agentic and generative AI

## Events, incidents and problems

| Term | Meaning |
|---|---|
| **Davis event** | one observation of abnormal behaviour on one entity |
| **Incident** | a degradation affecting an entity |
| **Problem** | the correlated whole, opened on the first indicator and holding the causal chain |

A problem is opened on **the first Davis event** and stays active while any
affected entity remains unhealthy. Problems are stored as events in Grail and
queried with `fetch events`; field detail is in
`semantic-dictionary/model/davis.md` (Davis event reports, Davis events, Davis
problems, Problem Comments).

## The problem lifecycle

The documented five-stage progression, across the Application, Services and
Infrastructure layers:

```
01  Problem #001 appears. Root cause: performance incident at infrastructure level.
02  Service layer becomes affected.
03  More incidents affect the service layer.
04  Application level affected; end users start experiencing errors.
05  Dynatrace correlates the incidents and identifies the root cause.
```

The root cause is identified at the **end**, by correlating back to stage 01 —
not at the moment the first event arrives. That is why a problem's root cause
can change while it is open, and why an early notification may name a symptom.

`root-cause-analysis/concepts` also covers **problem timing** — when a problem
starts and ends relative to the events inside it.

## Root cause analysis

`root-cause-analysis/concepts` sections: root cause analysis, **fault tree
analysis**, **impact analysis**. Event correlation:
`root-cause-analysis/event-analysis-and-correlation`.

Impact analysis is what decides severity: a problem affecting real users ranks
differently from one confined to infrastructure.

## Duplicate problems and processing state

Two sections that answer common confusion:

- **Duplicate problems** — when Dynatrace opens a second problem for what looks
  like the same thing, and why.
- **Problem processing state** — problems have a processing state distinct from
  their open/closed status.

## Anomaly detection: the detector types

`dynatrace-intelligence/anomaly-detection`. The Davis analyzers, also exposed
through MCP:

| Detector | What it does |
|---|---|
| **Static thresholds** | fixed threshold, no learning |
| **Auto-adaptive threshold** | one threshold learned from the data's distribution |
| **Seasonal baseline** | dynamic baseline with daily and weekly seasonality |
| **Automated multidimensional baselining** | baselines across dimensions |
| **Changepoint** | events, outliers, significant trends |
| **Forecast** | predicted future values |

Pages: `static-thresholds`, `auto-adaptive-threshold`,
`automated-multidimensional-baselining`, `anomaly-detection-configuration`.
API setup: `set-up-anomaly-detectors-via-api`.

## Sensitivity

`anomaly-detection/adjust-sensitivity-anomaly-detection`, with separate pages
per domain: applications, services, services-database, infrastructure,
extensions. Sensitivity is per domain, not global — turning it down for services
does nothing to infrastructure alerting.

## Custom alerts with DQL

The **Anomaly Detection app** is the latest surface: real-time analysis of Grail
data through DQL, alerting on **logs, spans and business events** as well as
metrics.

`anomaly-detection/anomaly-detection-app` with `configure-a-simple-ad` and
`configure-an-advanced-ad`. Both require a DPS licence and app permissions,
configured on first run through *Edit > Authorization settings*.

## Metric events and the transpiler

Classic metric events convert to DQL custom alerts through
*Add Custom alert > Improve metric events with DQL > Transform*. The caveats
matter more than the procedure:

- **Only metric selectors are transpiled.** Metric key events are not.
- The original metric event is **auto-disabled** once transformed.
- The post-transform check **does not verify correctness** — it cannot tell
  whether the metric has data or the tags exist. Verify manually via
  *More actions > Open with > View and execute Grail query*.
- Transformed events show State `Disabled`, Migrated `Yes`.
- **SLO metric events are a separate case** with no guide yet.
- Extension-based alerts and AWS/Azure recommended alerting rules follow the
  same path.

Full detail in `classic-vs-latest.md`.

## The Problems app

`dynatrace-intelligence/problems-app`:

- `problem-mode-overview` — the modes and their drill-downs
- `problems-app-custom-problem-field-examples` — adding custom fields
- `resolve-problems-with-troubleshooting-guides` — attaching guides, which is
  what the MCP Troubleshooting Agent searches (it needs **Enable document
  suggestion** in Settings)
- `upgrade-guide-problems` — coming from the classic problem feed

**Per-user email notifications live here**, not in a global configuration. That
is the change from classic alerting profiles: a user can subscribe themselves
without admin rights. See `workflows.md`.

## Frequent issues

`root-cause-analysis/detection-of-frequent-issues` — Dynatrace suppressing
recurring known behaviour so it does not drown real problems.

## Agentic and generative AI

`dynatrace-intelligence/agentic-and-generative-ai` (11 files) — Davis CoPilot
and Dynatrace Assist, plus a dedicated data-privacy page. The MCP surface for
all of this is in `mcp-and-ai-integration.md`.
