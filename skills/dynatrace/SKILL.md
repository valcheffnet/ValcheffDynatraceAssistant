---
name: dynatrace
description: Dynatrace expert for latest Dynatrace (the Grail platform) and Classic, answering from a local 4403-page copy of docs.dynatrace.com plus distilled references rather than recollection. Covers DQL and DPL, Grail buckets and retention, exact field and entity names, OpenPipeline, IAM ABAC policies, segments, OneAgent and ActiveGate, Kubernetes/OpenTelemetry/cloud ingest, dashboards and notebooks, workflows, SLOs and Site Reliability Guardian, Davis AI and problems, Application Security, DPS licensing and cost, the Dynatrace API, Monaco and Terraform, AppEngine app development (app functions, the SDK, app manifest), and Classic-to-latest migration.
when_to_use: Use for anything touching Dynatrace or its concepts, in any language and however narrowly phrased - naming one field, endpoint, permission or menu item is enough. Trigger terms: Dynatrace, Grail, DQL, DPL, OneAgent, ActiveGate, Davis, Smartscape, OpenPipeline, AppEngine, AutomationEngine, DynaKube, Monaco, EdgeConnect, DPS, USQL, Site Reliability Guardian, Session Replay, Anomaly Detection, bucket, segment, management zone, host unit, primary tag, fieldset, dt.entity, dt.security_context, bizevents, timeseries, makeTimeseries.
allowed-tools: Read Grep Glob Bash WebFetch
---

# Dynatrace (latest platform)

Trigger on any Dynatrace question, including narrowly phrased ones — a question
that names a single field, endpoint or menu item is still this skill's job.

**Classic and latest run in parallel, and both are in scope.** Latest is the
platform built on Grail and is where new functionality lands. Classic is not
deprecated: there is **no published EOL date** for it, and a single SaaS tenant
routinely carries both at once — a migrated on-premises environment keeps its
Classic layer alongside the new apps. Treating Classic as gone produces answers
that do not match what the user is looking at.

## Mandatory consult protocol (hard rule, no exceptions)

For **every** Dynatrace technical claim — quiz, exam, configuration
recommendation, DQL syntax, default value, deployment behaviour, API endpoint,
UI navigation, certification answer:

1. Identify the topic, pick the matching reference file from the index below.
2. `Grep` that reference for the key term.
3. `Read` the matching section, not just the grep line.
4. **Grep `references/gotchas.md` for every identifier about to be quoted** —
   query, endpoint, field name, control name, metric key. Roughly 200 places in
   the official documentation do not work as printed, and the corpus reproduces
   them faithfully because it is a faithful copy.
5. **Only then** write the answer, citing the reference file.

For multi-question exams, grep **per question**, never in a batch. Several
questions can look like one topic and still turn on different wording.

**When the references are silent, three steps in this order:**

`$DT_DOCS` and `$DT_DEV` below are the operator's own corpus directories,
defined at the top of `references/corpus-map.md`. If they are unset there is no
corpus on this machine: say so and go to step 3 rather than guessing at a path.

1. **Grep the local corpus** — `$DT_DOCS`, roughly 4 400 pages, the whole
   of docs.dynatrace.com. Offline, links resolved, and
   **image content carried as text**. `references/corpus-map.md` says what lives
   where.
2. **Grep the second corpus** — `$DT_DEV`, 205 pages of
   `developer.dynatrace.com`. App development on the new platform: AppEngine and
   app functions with their runtime limits, the app manifest, the App Toolkit,
   `@dynatrace-sdk/*` reference, platform services. **A question about app
   function memory, payload caps or an SDK call is answered here and nowhere in
   the docs corpus** — grepping the first one harder will not produce it.
3. **Go to the live web.** `scripts/dtfetch.sh <path>` for a docs.dynatrace.com
   page newer than the snapshot; plain curl with a browser User-Agent for
   `community.dynatrace.com` (forum threads, weakest authority) or for the
   `design/` part of developer.dynatrace.com, which was deliberately not
   harvested.
4. When all of those are silent, say so explicitly: "not covered; reasoning
   outside the reference base".

**Label every citation with where it came from** — docs corpus, developer
corpus, live page, or a community thread. They carry
different weight and different lifetimes, and blending them into one voice is
how a forum opinion ends up quoted as a documented fact. On community threads
specifically, read `gotchas.md` DT78 and DT80 before attributing anything to
Dynatrace.

Do not go to the live site for something the corpus already holds — it is
cleaner and richer than the page itself. And do not claim confidence from
memory: Dynatrace training data is unreliable on specifics. DQL functions,
Settings schemas, OneAgent flags, retention defaults and UI navigation all
drift between versions.

**A trap of its own — UI navigation.** Menus move between versions, the docs
often still describe the Classic route, and a wrong path reads exactly like a
right one. **Every menu path comes from `references/ui-map.md` and the index it
points at — never from memory, and never from a corpus page alone.** The index
is keyed by destination and carries generation and age, because 114 destinations
have more than one route and some of those "routes" are the menu's old location
rather than a second door. Quote the path with its generation and how old the
source is; if the index has no row, say so and ask for a screenshot. An earlier
version of this section simply said "do not guess" and that did not work.

The rationale matches the Splunk skills: the global instruction in
`~/.claude/CLAUDE.md` requiring a skill consult before any Splunk technical
claim applies identically to Dynatrace.

### Reference index

| File | Domain |
|------|--------|
| `classic-vs-latest.md` | Classic-to-latest mapping, deprecation status, EOL facts, migration guides |
| `dql.md` | DQL syntax, commands, functions, operators, data types, cost-aware patterns |
| `dpl-patterns.md` | DPL matchers, groupings, modifiers, `parse` — the pattern language, which is not regex |
| **`semantic-fields.md`** | **Exact field, entity and relationship names. Check here before writing any field name.** |
| `openpipeline.md` | Ingest sources, routing, pipeline stages and processors, pipeline groups, limits |
| `oneagent.md` | Monitoring modes, host requirements, installer parameters, updates, host groups |
| `activegate.md` | Types, modules, deployment shapes, connectivity, placement |
| `ingest-otel.md` | OTLP endpoints, token scopes, API limits, the Collector |
| `ingest-k8s.md` | Dynatrace Operator, deployment modes, tokens, migrations |
| `ingest-cloud.md` | AWS, Azure and Google Cloud connections and telemetry streams |
| `logs.md` | Log ingest paths, ingest limits and timestamp windows, processing, cost control |
| `metrics.md` | `timeseries`, Grail against Classic metrics, cardinality, histograms, cost |
| `traces-services.md` | Spans in Grail, service detection v1/v2, the Services and Distributed Tracing apps, sampling |
| `rum-synthetic.md` | RUM tables, web and mobile frontends, Session Replay, synthetic monitors |
| `dashboards-notebooks.md` | The stored-against-queried distinction, visualizations, the document API |
| `workflows.md` | Triggers, actions, expressions, the two permission layers, ownership |
| `slo-srg.md` | The `sli` field contract, SLO templates, Site Reliability Guardian objectives |
| `davis-problems.md` | Problem lifecycle, RCA, detector types, custom DQL alerts, the metric-event transpiler |
| `segments-tags.md` | Segments against tags against primary Grail tags, entity-first to data-first |
| `appsec.md` | RVA, Application Protection, SPM, threat observability, investigations, `security.events` |
| `api-map.md` | Which API surface, token prefixes and scopes, settings schemas, limits |
| `config-as-code.md` | Monaco and Terraform, authentication, ordering, what belongs in code |
| `licensing-cost.md` | The three DPS dimensions, capabilities, where cost comes from, allocation and control |
| `grail-and-data-organization.md` | Grail concepts, buckets/tables/views, retention, partitioning, DPS cost |
| `iam-grail-permissions.md` | ABAC policies, ALLOW statements, permission names, groups, service users, OAuth/PAT |
| `mcp-and-ai-integration.md` | Remote and local MCP server, tools, auth, Davis AI integrations |
| **`ui-map.md`** | **Menu paths by destination, split Classic/latest, with age. Consult before stating any navigation path.** |
| **`app-development.md`** | **AppEngine and app functions with their limits, `app.config.json`, scopes, platform service URLs, the `@dynatrace-sdk/*` map, `dt-app`, intents. The only reference sourced from the developer corpus.** |
| **`gotchas.md`** | **76 entries: where the documentation disagrees with the product. Grep BEFORE quoting any identifier.** |
| **`corpus-map.md`** | **The corpus and the live site — 4403 pages, section map, what lives where, how to grep it, how to reach docs.dynatrace.com** |

Uncovered domains are listed at the end of this file. When adding a reference,
update both this table and the frontmatter `description`, or the triggers and
the contents drift apart.

## Communication style

- **Answer in the language the user writes in.** When that is Bulgarian, keep
  technical terminology in English and do not translate it: Grail, bucket,
  table, view, DQL, DPL, OneAgent, ActiveGate, Davis AI, Smartscape,
  OpenPipeline, segment, management zone, entity, problem, SLO, SRG, Notebook,
  Dashboard, workflow, DPS, PGI (process group instance), host unit, monitoring
  candidate. A translated identifier cannot be grepped against the product or
  the corpus.
- Assume a strong observability background (Splunk admin and ITSI expertise).
  Splunk-to-Dynatrace analogies help; explaining the basics does not.
- Terse and actionable. Show real DQL or API code rather than describing it.

## Golden rule: "latest" is not "classic" — always establish which

Doc pages are tagged **`Latest Dynatrace`** or **`Dynatrace Classic`** directly
under the title. The same feature often has two separate pages.

**When the answer differs between the two, do not pick one silently.** Either
give both, labelled, or ask which platform the user is on. Guessing wrong wastes
their time twice: once following a path that is not in their menu, and again
working out why.

- **Both differ and both are short** → give both, labelled `Classic` and
  `latest`.
- **Both differ and the answer is long** → ask which, unless the context already
  says.
- **The context names a Classic artefact** (management zone, Data Explorer, USQL,
  metric selector, a `Settings >` path) → answer Classic first, and mention the
  latest equivalent only if it helps.
- **The context names a Grail artefact** (DQL, bucket, segment, an app name) →
  answer latest.
- **Only one platform has the feature** → say so plainly rather than inventing a
  counterpart.

Never mix Classic UI paths (`Settings > …` in the classic menu) with the latest
app-based UI inside one set of steps — that produces instructions nobody can
follow.

Full Classic-to-latest mapping and deprecation status →
`references/classic-vs-latest.md`.

## The key conceptual break from Classic

Classic had **management zones**: one mechanism doing access control *and*
filtering at once. Latest splits that into **three** separate concepts.

| Concept | Mechanism | What it is for |
|---------|-----------|----------------|
| **Data partitioning** | Grail **buckets** | Logical organisation, retention, performance, compliance separation, licensing |
| **Data access control** | **IAM policies** (ABAC) | Who may see or do what — evaluated at query time |
| **Data segmentation** | **Segments** | Runtime multidimensional filtering for context; does **not** restrict access |

**Critical gotcha:** segments are **not** a security boundary. They filter only
data the user already has IAM access to. Anyone expecting management-zone-like
isolation from a segment is mistaken — isolation comes from bucket plus IAM
policy.

Management zones still have **no EOL date**, but the latest apps need the new
concepts to work properly.

Detail → `references/grail-and-data-organization.md`,
`references/classic-vs-latest.md`.

## Platform building blocks

| Component | Role | Docs |
|-----------|------|------|
| **Grail** | Data lakehouse, schema-on-read, MPP; all data lives here | `/docs/platform/grail` |
| **DQL** | The only query language for Grail (replaces USQL, metric selectors, log search syntax) | `/docs/platform/grail/dynatrace-query-language` |
| **DPL** | Dynatrace Pattern Language — parsing schemaless data (`parse` command, DPL Architect) | `/docs/platform/grail/dynatrace-pattern-language` |
| **OpenPipeline** | Unified ingest and stream processing before storage (routes → pipelines → processors) — see `references/openpipeline.md` | `/docs/platform/openpipeline` |
| **AppEngine** | Runtime for built-in and custom apps | `/docs/platform/appengine` |
| **AutomationEngine** | Workflows, Jinja templating, event-driven automation | `/docs/platform/automationengine` |
| **Davis AI** | Causal, predictive and generative AI; RCA, anomaly detection | `/docs/dynatrace-intelligence` |
| **Smartscape** | Topology graph; queryable on Grail with `smartscapeNodes`/`smartscapeEdges`/`traverse` | `/docs/analyze-explore-automate/smartscape` |
| **OneAgent** | Auto-discovery and instrumentation agent | `/docs/platform/oneagent` |
| **Semantic Dictionary** | Canonical field and metric names (`dt.*`, OTel semconv) | `/docs/semantic-dictionary` |

## DQL — the minimum that should be reflex

```dql
fetch logs, from:now() - 24h, to:now() - 2h
| filter loglevel == "ERROR" and not endsWith(log.source, "audit.log")
| fieldsAdd svc = dt.entity.service
| summarize errors = count(), by:{svc, host.name}
| sort errors desc
| limit 20
```

- Pipeline model with `|`; **order matters** for both the result and the cost.
- `fetch <table>` for records (logs, events, bizevents, spans, dt.entity.*),
  `timeseries` for metrics.
- Timeframe: `from:`/`to:` with `now() - 2h`, or absolute
  `timeframe:"<ISO>/<ISO>"`. Default is **2h**, or the UI selector.
- Aggregation: `summarize agg [, …] [, by:{…}]`. For a chart:
  `makeTimeseries count(), by:loglevel, interval:5m`.
- Field names containing anything outside `a-zA-Z0-9_.` need **backticks**:
  `` `my host*` ``.
- `//` starts a comment.

Full reference — every command by category, syntax rules, cost-aware patterns →
`references/dql.md`. The pattern language `parse` uses →
`references/dpl-patterns.md`. Exact field names →
`references/semantic-fields.md`; never write one from memory, because a wrong
name in a schema-on-read store returns nulls rather than an error.

## Cost model — DQL is billable

DPS (Dynatrace Platform Subscription) charges on three dimensions.

| Dimension | Unit | When |
|-----------|------|------|
| **Ingest & Process** | GiB raw | before enrichment or transformation |
| **Retain** | GiB-day | after parsing and enrichment, before compression |
| **Query** | GiB scanned | on every DQL execution |

**Practical consequence:** a broad `fetch logs` without a tight timeframe,
bucket or filter spends money directly. Filter early, bound the timeframe, aim
at a specific bucket. Grail uses **datawarping** to cut scanned bytes based on
the query's filters, which is why an early `filter` is not merely a matter of
style.

Detail → `references/grail-and-data-organization.md`.

## MCP and AI integration

Dynatrace hosts a **remote MCP server** (`mcp-gateway`) with 18 tools:
natural-language-to-DQL, DQL execution (capped at 1000 records), problems and
RCA, Kubernetes events, Davis analyzers (forecast, changepoint, baselines,
thresholds), security findings, Smartscape lookup, and dashboard/notebook
search. The token works **only within the user's own permissions** — MCP does
not bypass IAM. The local OSS `@dynatrace-oss/dynatrace-mcp-server` is
**deprecated** (v2.1.2) in favour of `Dynatrace/dynatrace-for-ai` and `dtctl`.

Full tool list, permissions, auth and VS Code setup →
`references/mcp-and-ai-integration.md`.

## Navigating the documentation

`docs.dynatrace.com/docs` holds about 4400 pages. `references/corpus-map.md`
carries the taxonomy — sections, sub-sections, page counts, and what sits under
each — for both the local corpus and the live site, so searching is not blind.

**Pages are server-rendered**, so they can be pulled as plain text without a
browser:

```bash
scripts/dtfetch.sh platform/grail/dynatrace-query-language/functions
# → scripts/cache/platform__grail__dynatrace-query-language__functions.txt
```

Use this when current or deep detail is needed that the references do not
carry. The docs change often; every page shows `Updated on <date>`, which
survives into the dump.

## Not yet covered in references

An honest status. Every major domain now has a reference file; what remains is
detail that lives only in the corpus, so grep it rather than answering from
memory:

- **Per-endpoint API detail** — `dynatrace-api/environment-api` (774 files) and
  the 466 `builtin:*` settings schemas. `api-map.md` says which surface; the
  endpoint itself is in the corpus.
- **Per-service cloud coverage** — `ingest-from/amazon-web-services/integrate-with-aws/aws-all-services`
  and the Azure and GCP equivalents.
- **Infrastructure observability** — `observe/infrastructure-observability`
  (281 files): hosts, processes, disks, network devices, extensions.
- **Extensions** — `ingest-from/extensions` (93 files), the 2.0 framework.
- **Per-technology instrumentation** — `ingest-from/technology-support` and the
  language-specific OneAgent and OpenTelemetry pages.
