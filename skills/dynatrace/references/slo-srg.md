# SLOs and Site Reliability Guardian

Two things that sound similar and answer different questions. An **SLO** tracks
whether a service is meeting its target over time. A **Site Reliability
Guardian** decides whether a specific change is safe to release.

Corpus: `deliver/service-level-objectives` (7 files, latest),
`service-level-objectives-classic` (5), `deliver/site-reliability-guardian`
(10).

## Contents

- SLOs
- The `sli` field
- SLO templates and examples
- SLO tiles on dashboards
- Permissions
- Site Reliability Guardian
- SRG objectives
- Variables, segments and execution context
- Triggering an SRG
- Configuration as code
- Classic

## SLOs

`deliver/service-level-objectives`. Two routes: **from a template**, or a
**custom SLO** driven by DQL.

## The `sli` field

A custom SLO is a DQL query that produces a field named exactly **`sli`**,
returning an **array of `double`** values. The array shape is what makes the
visualisation, trend and error budget consistent — a scalar will not do.

```dql
| fieldsAdd sli = (((total[] - failures[]) / total[]) * 100)
```

The `[]` suffix is array access on the timeseries arrays, which is why both
`total` and `failures` have to be arrays too. For event- or log-based data, use
`makeTimeseries` to produce those arrays before computing the ratio.

The docs' worked example queries the Smartscape 2.0 entity
`dt.smartscape.service` and filters for the `sli` field.

**The commonest mistake is naming the field something else.** `sli` is not a
convention, it is the contract; anything else produces an SLO that saves and
never shows a value.

## SLO templates and examples

`service-level-objective-templates`, `service-level-objective-examples`. Start
from a template unless the SLI is genuinely custom — the templates encode the
array shape correctly.

## SLO tiles on dashboards

Three separate pages, because the tile has three lifecycles:
`service-level-objective-tile-add-to-dashboard`,
`service-level-objective-tile-edit-in-dashboard`,
`service-level-objective-tile-view`.

## Permissions

`service-level-objective-permissions` for SLOs,
`site-reliability-guardian/role-permissions` for SRG. Both sit on top of the
Grail table permissions the underlying query needs — an SLO over logs still
requires `storage:logs:read` and a bucket permission for whoever views it.

## Site Reliability Guardian

`deliver/site-reliability-guardian`. SRG replaces classic **quality gates** and
Cloud Automation. It evaluates a set of objectives against a timeframe and
returns a verdict, which is what a pipeline gates on.

`create-srg`, `duplicate-srg`, `guardian-list`.

## SRG objectives

Each objective is a DQL query with a threshold. The reference carries worked
examples that are worth copying rather than reinventing:

- **Error log entries** — counting errors in a window
- **Request success rate, log based**
- **Request failure rate, log based**

`site-reliability-guardian/reference` holds these plus the objective syntax.

## Variables, segments and execution context

- **Variables** — parameterise a guardian so one definition serves several
  services or environments. Set at trigger time.
- **Segments** — scope the evaluation to a slice of data. Remember segments do
  not restrict access, only context; see `segments-tags.md`.
- **Execution context** (`execution-context`) — what the guardian knows about
  the run that triggered it.

Event structure: `site-reliability-guardian/event-structure` — the shape of the
event a guardian emits, which is what a workflow reacts to.

## Triggering an SRG

`trigger-srg`. The usual path is a **Workflows** action from a pipeline event,
so the release pipeline calls Dynatrace rather than Dynatrace polling the
pipeline. See `workflows.md` and
`deliver/pipeline-observability-sdlc-events`.

`validation-insight-link` connects the guardian result back to the change being
validated.

## Configuration as code

`site-reliability-guardian/config-as-code-srg` — guardians defined in Monaco.
This is the form that belongs in a repository next to the pipeline it gates.
See `config-as-code.md`.

## Classic

`deliver/service-level-objectives-classic` (5 files). Classic SLOs use
functional metrics, which behave differently under the metric-event
transformation to the Anomaly Detection app — the docs call SLO metric events a
separate case with a guide still to come. See `classic-vs-latest.md` and
`davis-problems.md`.
