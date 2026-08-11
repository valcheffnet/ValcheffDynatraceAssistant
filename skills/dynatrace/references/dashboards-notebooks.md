# Dashboards and Notebooks

Both are **documents** in the same document service, both run DQL, and the
difference that decides which to use is where the data lives.

Corpus: `analyze-explore-automate/dashboards-and-notebooks` (46 files), plus
`dashboards-classic` (26).

## Contents

- The distinction that matters
- Visualizations
- Drilldowns and navigation
- Ready-made documents
- The document API
- Versioning
- Remote environment data
- Classic
- Variables
- Cost and the 5-minute ceiling

## The distinction that matters

| | Notebooks | Dashboards |
|---|---|---|
| Verb | something you **read** | something you **view** |
| Data | **stored within the notebook** | **queried when the dashboard is opened** |
| For | ad-hoc analysis, incident investigation, documentation, training, collaboration | continuous real-time monitoring, KPIs, health overview, SLO tracking |

That storage difference drives everything else. A notebook is a captured
analysis whose numbers stay put; a dashboard re-queries on every open, so every
open costs Query. A dashboard left on a wall re-queries continuously.

Notebooks replace the classic **Data Explorer**; Dashboards replace
**Dashboards Classic**. See `classic-vs-latest.md`.

## Visualizations

`edit-visualizations/` carries one page per type: area, band, bar, categorical
bar, donut, line, pie, single value, gauge, heatmap, histogram, honeycomb, and
more. Each documents its own data-shape requirements.

Two shapes of query feed them:
- `timeseries` for metrics
- `makeTimeseries` over `fetch` for records

A visualization that renders empty is usually being fed records where it expects
a timeseries. See `dql.md`.

## Drilldowns and navigation

`drilldowns-and-navigation` — moving from a tile into the underlying data or
another document. This is the page whose anchors are most frequently referenced
from elsewhere in the corpus.

## Ready-made documents

`ready-made-documents` — preset dashboards and notebooks shipped by Dynatrace.
Worth checking before building: the tile inventories of several presets exist in
the corpus only as image transcriptions, so grep the stage4 blocks on those
pages when the prose does not list what a preset contains. See `corpus-map.md`.

## The document API

`document-api` — programmatic access to dashboards and notebooks, with separate
structure references for each:

- `document-api/document-structure-dashboards`
- `document-api/document-structure-notebooks`

Permission: `document:documents:read` (the same scope the MCP Document Agent
uses — see `mcp-and-ai-integration.md`).

The document API is how dashboards get into version control; the alternative is
Monaco, see `config-as-code.md`.

## Versioning

`document-version` — document versions, which is what makes a shared dashboard
safe to edit.

## Remote environment data

`remote-environment-data` — pulling data from another environment into a
document. Relevant for multi-tenant setups where one team needs a view across
environments.

## Classic

`analyze-explore-automate/dashboards-classic` (26 files) and
`analyze-explore-automate/explorer` (Data Explorer, 3 files). Both legacy.
Dashboards Classic still exists and still works; the upgrade guidance is in
`manage/upgrade-guide-landing-page`.

## Variables

Source: `analyze-explore-automate/dashboards-and-notebooks/dashboards-new/components/dashboard-component-variable.md`.

Four types: **DQL** (values come from a query), **List** (a CSV of literal
values), **Code**, **Free Text**. Any of them can have **Multi-select** turned
on, and that choice changes how the tile has to reference it:

```
| filter in(host.name, array($Host))     // multi-select
| filter host.name == $Host              // single value
```

Referenced as `$Name`. Usable in DQL tiles, as values inside code tiles, and as
placeholders in tile titles and Markdown tile text.

### The three limits that produce support questions

**A variable is a string or a number, nothing else.** A case needing another
data type fails the query rather than coercing. `duration` is the one people hit:

```
| summarize count(), by: {loglevel, bin(timestamp, $resolution)}                     // fails
| summarize count(), by: {loglevel, bin(timestamp, duration(toLong($resolution), unit:"m"))}   // works
```

Same shape for comparing a number against a string field — wrap with
`toString($amount)`.

**In a code tile, a variable is reachable only inside the default function.**
Verbatim: *"For security reasons, when using variables in code tiles, you can
only access them within the default function."* This is not a scoping quirk to
work around — it is a deliberate boundary. A helper function defined in the same
tile cannot see `$Var`; pass the value in as an argument from the default
function.

**Variable values live in the dashboard URL, capped at 30 KB.** Past that they
are simply not stored, and the failure is silent in two directions: someone
opening your shared link sees none of your selections, and your own bookmark
loses them after 90 days. A multi-select over a large value list is the usual
way to exceed it.

## Cost and the 5-minute ceiling

- **The query timeout for Dashboards, Notebooks and workflows is 5 minutes.**
  Bucket sizing has to allow a result inside it — see
  `grail-and-data-organization.md`.
- **Every dashboard open costs Query.** A tight timeframe, a `bucket:` filter
  and early `filter` are not stylistic choices on a dashboard that ten people
  keep open.
- Some apps consume no query budget when displaying their initial state; a
  custom dashboard is not one of them.
- A frequently-run span or log query is often cheaper as a **calculated service
  metric** or an OpenPipeline-extracted metric — computed once at ingest rather
  than on every open. See `metrics.md` and `traces-services.md`.
