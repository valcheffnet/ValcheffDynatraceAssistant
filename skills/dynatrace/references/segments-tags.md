# Segments, tags and primary Grail tags

Three overlapping mechanisms that classic collapsed into one. Getting them
straight is the difference between a working access model and a leaky one.

Corpus: `manage/segments` (11 files), `manage/tags` (6),
`manage/tags-and-metadata` (8).

## Contents

- The three-way split
- Segments
- Standard tags
- Primary Grail fields
- Primary Grail tags
- Where primary tags come from
- Entity-first against data-first
- Migrating from management zones

## The three-way split

| Concept | Mechanism | What it does |
|---|---|---|
| Data partitioning | Grail **buckets** | retention, cost, performance, compliance separation |
| Data **access control** | **IAM policies** (ABAC) | who may see what, at query time |
| Data **segmentation** | **Segments** | runtime filtering for context |

**Segments are not a security boundary.** From the docs' own FAQ: *"Segments
themselves don't restrict access; they filter and contextualize data that users
are authorized to see."* Anyone expecting management-zone-style isolation from a
segment is mistaken — isolation comes from bucket plus IAM policy. See
`iam-grail-permissions.md`.

## Segments

`manage/segments`: `concepts`, `getting-started`, `reference`, `use-cases`, and
`upgrade-guide-segments` for coming from management zones.

Segments are business-aligned dynamic views for self-service. They are the
**third** step in the recommended migration order, after buckets and access
controls — building segments first produces convenient views over an access
model that does not exist yet.

Segments also scope Site Reliability Guardian evaluations; see `slo-srg.md`.

## Standard tags

Any tags defined for infrastructure or application workloads: cloud tags,
Kubernetes labels and annotations, host- and process-level tags.

**They live only on the respective Smartscape node.** Dynatrace does **not**
enrich raw telemetry with them. That single fact explains most "why can't I
filter my logs by this tag" questions.

`manage/tags/tags-strategy`, `tags-best-practices`, `tags-domain-k8s`,
`tags-domain-oneagent`. Auto-tagging rules and metadata:
`manage/tags-and-metadata` (`basic-concepts`, `setup`, `reference`,
`use-cases`).

## Primary Grail fields

A small set of fields Dynatrace attaches to all raw telemetry — the cloud and
Kubernetes identifiers, host name, host group. Several of them are the
permission-relevant fields listed in `semantic-fields.md`.

`manage/tags/primary-tags` covers availability, enrichment and which of them are
permission-relevant.

## Primary Grail tags

Customer-defined, prefixed `primary_tags.*` — `primary_tags.team`,
`primary_tags.app`, `primary_tags.stage`.

What makes them different from standard tags:

- **Available before data enters the processing pipeline**, so they can drive
  pipeline routing and bucket assignment from the earliest stage.
- **Enriched on every signal** — logs, metrics, spans, events and problems — and
  on each relevant Smartscape node.
- **Derived signals inherit them.** Service metrics, Davis events and Davis
  problems carry the same tags as the logs and spans that triggered them, so
  ownership metadata survives the whole chain.

What that enables: routing data to the right pipeline, processing it in
OpenPipeline, selecting buckets, defining cost allocation, and defining access
control for telemetry.

**Multi-value primary tags are arrays**, so an IAM `WHERE` on one needs `MATCH`,
not `=`. See `iam-grail-permissions.md`.

Limits (from OpenPipeline): 20 rules, 10 source fields per rule, rule name 256
chars, matching condition 4 096 chars, source field expression 256 chars.

## Where primary tags come from

| Source | How |
|---|---|
| OneAgent | at installation, or via `oneagentctl` |
| Kubernetes | namespace or cluster labels and annotations, scoped to the environment or one cluster |
| AWS / Azure / Google Cloud | cloud resource tags and labels, scoped to the environment or one account, subscription or project |
| OpenTelemetry | resource attributes via `OTEL_RESOURCE_ATTRIBUTES` |
| Host or process metadata | properties of hosts and processes — **coming soon** |
| OpenPipeline | derived or transformed from any incoming field at ingest time, through primary Grail tag rules |

The OpenPipeline route is the fallback when the source cannot be changed;
everything else attaches the tag before it reaches Dynatrace.

## Entity-first against data-first

`manage/tags/tags-difference-classic` frames the shift:

| Entity-first (classic) | Data-first (latest) |
|---|---|
| Query an entity by its tag, then fetch its data | Query the data directly by primary fields and tags |
| Route alerts based on tags applied to entities | Route alerts on the primary fields and tags carried by the alert events themselves |
| Encode context in service names so it surfaces in lists | Use primary fields and tags as columns in service lists, apps and dashboards |

Consequences the page draws out: **no propagation rules are needed**, because
enrichment happens at ingest rather than being inherited across the topology;
and **primary Grail fields already cover infrastructure context**, so the
classic habit of building auto-tags to carry cloud and Kubernetes identity is
redundant.

Classic also had management zones based on auto-tags and host group naming
schemes. Both are superseded.

## Migrating from management zones

`manage/segments/upgrade-guide-segments`, plus
`manage/upgrade-guide-landing-page/upgrade-guide-concepts`.

Management zones have **no EOL date**, and they still appear on entities as the
`managementZones` field. But they do not carry into Grail record permissions,
which is why the latest apps need the new concepts. Recommended order: buckets,
then access controls, then segments. See `classic-vs-latest.md`.
