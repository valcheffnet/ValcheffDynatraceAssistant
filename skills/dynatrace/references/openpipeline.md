# OpenPipeline — ingest, routing, processing, storage assignment

Everything entering Grail passes through OpenPipeline. It decides where a record
lands, what it looks like when it gets there, which security context it carries,
and which cost center it is charged to. A bucket definition without routing is an
empty shell.

Corpus: `platform/openpipeline` (52 files).

## Contents

- The data flow
- Configuration scopes
- Ingest sources
- Routing: dynamic and static
- Pipelines, stages, processors
- The processing stage
- DQL inside OpenPipeline
- Pipeline groups
- Access control
- Limits
- Migrating from the classic pipeline
- Design guidance

## The data flow

```
INGEST SOURCES  →  ROUTING  →  PIPELINE                                                   →  GRAIL
OneAgent           Dynamic     Processing → Metric extraction → Data extraction →            System notifications
Extensions         Static      Permissions → Storage                                         Problems, Workflows
API                                                                                          Smartscape
```

Data extraction can **re-ingest** a new record as a different data type into
another pipeline — a log line becoming a business event, for instance. That
re-ingestion loop happens outside OpenPipeline and re-enters at the ingest stage,
so the second pass is charged and processed like any other ingest.

## Configuration scopes

A scope is the data type a pipeline configuration applies to:

Business events · Events (generic) · Events — Davis events · Events — Davis
problems · Events — SDLC events · Logs · Metrics · Security events (new) · Spans
· User events · User sessions

Two are only partially supported: **System events** and **Smartscape events
(topology)**.

## Ingest sources

| | Built-in | Ready-made | Custom |
|---|---|---|---|
| Owner | OpenPipeline | Extension | user or user group |
| Permissions | `settings:read` | `settings:read` | `settings:read`, `settings:write` |
| Access | view-only for all | view-only for all | owner-based access control |
| Scopes | all | Events, Logs, Metrics | Events, excluding Davis problems and Davis events |
| Routing | dynamic | dynamic, static | dynamic, static |
| Pre-processing | not configurable | not configurable | configurable |

Only custom ingest sources allow pre-processing, and only they are
owner-controlled. The endpoint reference is
`platform/openpipeline/reference/api-ingestion-reference`.

## Routing: dynamic and static

- **Dynamic routing** evaluates a DQL matcher per record and picks the pipeline.
- **Static routing** binds an ingest source to one pipeline outright, with no
  matcher evaluated.

Static is available only for ready-made and custom sources. Built-in sources are
always dynamic.

## Pipelines, stages, processors

A pipeline is an ordered sequence of **stages**; each stage holds a fixed set of
permitted **processors**.

```
Processing → Metric extraction → Data extraction → Permissions → Storage
```

The full ordered list, with how many processors actually fire:

| Stage | Purpose | Executed |
|---|---|---|
| Processing | parse into fields, transform schema, filter records | all matches |
| Metric extraction | counter, histogram, value metrics from matching records | all matches |
| Smartscape Node Extraction | extract Smartscape nodes | all matches |
| Smartscape Edge Extraction | extract Smartscape edges | all matches |
| Metric extraction (sampling aware) | sampling-aware counter and histogram | all matches |
| Data extraction | extract a record and re-ingest it as another data type (business event, SDLC event) | all matches |
| Davis | extract and re-ingest as a Davis event | all matches |
| Cost allocation | assign cost center usage to matching records | |
| Product allocation | assign product or application usage | |
| Permissions | `Set dt.security_context` | **first match only** |
| Storage | `Bucket assignment` or `No storage assignment` | **first match only** |

**Permissions and Storage stop at the first match. Every other stage runs all
matches.** A record with two matching bucket-assignment processors goes to
whichever is evaluated first, silently — order is the whole answer, not a
tie-break.

A processor has two halves: a **matcher**, which is a DQL query narrowing the
records it applies to, and a **processing definition** saying what to do with
them.

Extracted metrics go to Grail only — except in the security events (new) and
span scopes.

## The processing stage

Seven processors:

| Processor | What it does |
|---|---|
| **DQL** | runs a restricted subset of DQL, formatting results into string, number, bool, duration, timestamp and arrays of those |
| **Add fields** | adds fields with static or templated values |
| **GeoIP lookup** *(Early Access)* | resolves an IP to geolocation fields |
| **Remove fields** | drops fields |
| **Rename fields** | renames fields |
| **Drop record** | discards the record entirely |
| **Technology bundle Logs** | applies a technology-specific bundle |

**Drop record is where ingest cost is actually saved.** Filtering at query time
costs Query; dropping at ingest removes the record from Ingest & Process and
Retain as well.

GeoIP lookup is Early Access — request access through
`whats-new/preview-releases#geoip-lookup-processor`.

## DQL inside OpenPipeline

The DQL processor accepts a **strict subset**. Anything not on this list is not
available at ingest time:

| Category | Commands |
|---|---|
| Extraction and parsing | `jsonExtract`, `parse` |
| Selection and modification | `fields`, `fieldsAdd`, `fieldsKeep`, `fieldsRemove`, `fieldsRename` |
| Structuring | `fieldsFlatten` |

No `filter`, no `summarize`, no `join`, no `lookup`. Filtering is what the
processor's own matcher does; aggregation belongs to the metric extraction
stage. Reference: `platform/openpipeline/reference/dql/openpipeline-dql-commands`
and `dql-matcher-in-openpipeline`.

`parse` here uses DPL, same as in queries — see `dpl-patterns.md`. A pattern
that has stabilised in a query is a candidate to move here, where it runs once
per record instead of once per query.

## Pipeline groups

Pipeline groups compose a **base pipeline** with **member pipelines** across
**pipeline slots**, giving central teams a way to impose configuration that a
team-owned pipeline cannot skip.

Two mechanisms:

- **Mandate** — the base pipeline's processing is applied regardless of what the
  member pipeline does.
- **Restrict** — the member pipeline is limited in what it may configure.

Limits: 10 pipeline slots, 1000 member pipelines, 100 processors in a base
pipeline. Detail: `platform/openpipeline/concepts/pipeline-groups`.

## Access control

Two separate things that are easy to conflate:

- **Permissions** are environment-level and granted by an administrator against
  the settings schema: `settings:objects:read`, `settings:objects:write`,
  `settings:objects:admin`.
- **Owner-based access control** is per settings object and granted by its
  owner: view or edit.

**Neither works alone.** An accessor with edit access but no `write` permission
cannot edit; a user with `write` permission but no access to the object cannot
either. A settings object is reachable by its owner with sufficient permissions,
by an accessor with matching access and permissions, or by an administrator.

```sql
-- an administrator granting the permission half
ALLOW settings:objects:read, settings:objects:write
  WHERE settings:schemaId = "builtin:openpipeline.events.ingest-sources";

-- read across every pipeline
ALLOW settings:objects:read
  WHERE settings:schemaGroup IN ("group:openpipeline.all.pipelines");
```

The owner still has to share view or edit access on the specific object.

## Limits

`platform/openpipeline/reference/limits`.

| Item | Limit |
|---|---|
| Pipelines | 100 |
| Pipeline groups | 100 |
| Total pipeline object size | 70 MB |
| Routes | 3 000 |
| Total routing object size | 10 MB |
| Ingest sources | 100 |
| Total ingest source object size | 30 MB |
| Processors per pipeline | 1 000 |
| Processors in a base pipeline | 100 |
| Pipeline slots | 10 |
| Member pipelines | 1 000 |

Primary Grail tag rules: 20 rules, 10 source fields per rule, rule name 256
chars, matching condition 4 096 chars, source field expression 256 chars.

**Backdating limits** — records older than this are rejected:

| Data | Earliest accepted timestamp |
|---|---|
| Logs, Events, Business events, System events | ingest time minus **24 hours** |
| Metrics, extracted metrics, Davis events, Security events | ingest time minus **1 hour** |

That one-hour window is the usual cause of a metric backfill silently going
nowhere.

## Migrating from the classic pipeline

`platform/openpipeline/migration-classic-pipeline` and
`platform/openpipeline/migration-settings`. The classic log processing pipeline
maps onto processing-stage processors; classic settings map onto pipeline
configuration.

## Design guidance

- **Route so the default buckets stay empty.** Anything arriving in
  `default_logs` then means routing is wrong or something new appeared — a
  useful signal rather than a dumping ground. See
  `grail-and-data-organization.md`.
- **Set `dt.security_context` in the Permissions stage** for anything without a
  dedicated permission field. It is the only permission field valid on every
  table, and setting it at ingest is what makes record-level IAM possible later.
  See `semantic-fields.md` and `iam-grail-permissions.md`.
- **Cost allocation is a pipeline stage, not an afterthought.** Cost center and
  product assignment happen here, per matching record.
- **Order matters most in Permissions and Storage**, because only the first
  match applies.
- **Move a stable `parse` from query time to ingest time.** Query-time parsing
  is charged on every execution.
