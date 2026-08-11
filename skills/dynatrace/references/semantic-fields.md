# Semantic Dictionary — exact field, entity and relationship names

The single most common way a Dynatrace answer goes wrong is a field name that
does not exist. Grail is schema-on-read, so a wrong name does not error — the
query returns nothing, or a column of nulls, and looks like a data problem.
**Never write a field name from memory. Confirm it here or in the corpus first.**

The authority is `{{DOCS_CORPUS}}/semantic-dictionary` — 274 files,
2.44M words, 92 354 table rows, no images. This file carries the shape of that
reference plus the names worth knowing by heart; everything else is one grep
away.

## Contents

- How to find a field name
- Reading a Semantic Dictionary row
- Base fields present everywhere
- Field namespaces (the `##` sections of `fields.md`)
- Fields that carry permissions
- Primary Grail tags
- Per-table field sets
- Entities: `dt.entity.*`
- Entity relationships
- Naming conventions and traps

## How to find a field name

Three greps, in order of narrowness:

```bash
# 1. does this exact name exist at all, and in which domain?
grep -rn '`k8s.namespace.name`' {{DOCS_CORPUS}}/semantic-dictionary --include=*.md

# 2. what fields exist in a namespace?
grep -n '^| `span\.' {{DOCS_CORPUS}}/semantic-dictionary/fields.md

# 3. what does one entity type carry?
grep -A3 '^fetch dt.entity.host$' {{DOCS_CORPUS}}/semantic-dictionary/model/dt-entities.md
```

`fields.md` is the **global** reference: fields with a defined meaning that
appear across monitoring types. `model/*.md` is **per data domain**, and each
domain page opens with a runnable `fetch` query for that data.

| Domain | File |
|---|---|
| Logs and audit logs | `model/log.md` |
| Spans and traces | `model/trace.md` (18 060 words) |
| Davis events, problems, comments | `model/davis.md` |
| Business events, billing, carbon | `model/business-analytics.md` |
| Entities, all types and relationships | `model/dt-entities.md` (52 752 words) |
| System, audit and billing events | `model/dt-system-events.md` (31 408 words) |
| RUM user sessions and events | `model/rum/user-sessions.md`, `model/rum/user-events.md` |
| Security: vulnerability, threat, compliance, detection | `model/security-events/*.md` |
| Smartscape nodes by provider | `model/smartscape/{core,aws,azure,gcp,k8s,db,...}.md` |
| Synthetic | `model/synthetic.md` |
| SDLC / pipeline events | `model/sdlc-events.md` |
| Maintenance windows | `model/maintenance-windows.md` |

## Reading a Semantic Dictionary row

Every table row is `Attribute | Type | Description | Examples`, and the
Description column packs three things together with no separator:

```
| `log.source` | string | stableDisplay name: `Log source`Human-readable attribute
that identifies a log stream.Tags: `permission` | `/var/log/messages` |
```

- **Stability marker**, glued to the front of the description: `stable`,
  `experimental`, `deprecated`, sometimes prefixed `resource`. An
  `experimental` field can be renamed without a deprecation cycle — say so when
  quoting one.
- **Display name** — what the UI shows. The UI label and the DQL field name are
  different strings; a user quoting "Log source" means `log.source`.
- **Tags** — `permission` marks a field usable in an IAM `WHERE` clause;
  `entity-id` marks an entity identifier.

## Base fields present everywhere

| Field | Type | Note |
|---|---|---|
| `timestamp` | timestamp | UNIX epoch **nanoseconds**. When the event originated, not when it was ingested — unless nothing better was available |
| `timeframe` | record[] | the timeframe a timeseries record represents |
| `start_time` / `end_time` | timestamp | data point bounds, nanoseconds |
| `duration` | duration | `end_time - start_time`, nanoseconds |
| `interval` | string | the bucket size of timeseries measurements, e.g. `1 min` |
| `content` | string | the unstructured, human-readable body of a record |
| `event.type`, `event.kind`, `event.provider` | string | classification, on every event-shaped table |

## Field namespaces

`fields.md` groups global fields into ~130 namespaces. The ones that come up
most:

`aws.*`, `azure.*`, `gcp.*`, `cloud.*`, `k8s.*`, `host.*`, `process.*`,
`container.*`, `db.*`, `http.*`, `url.*`, `network.*`, `span.*`, `trace.*`,
`exception.*`, `error.*`, `code.*`, `service.*`, `endpoint.*`, `event.*`,
`log.*`, `metric.*`, `user.*`, `device.*`, `browser.*`, `frontend.*`,
`geolocation.*`, `telemetry.*`, `dt.*`, `primary_tags.*`, `threat.*`,
`vulnerability.*`, `feature_flag.*`, `gen_ai.*`, `faas.*`, `messaging.*`,
`rpc.*`, `tls.*`, `vcs.*`.

Technology-specific namespaces also exist for Apache, Cassandra, ColdFusion,
Elasticsearch, GlassFish, Go, Hybris, IBM, IIS, Java, JBoss, JDBC, Journald,
Kafka, Node, OpenSearch, OpenStack, PHP, PostgreSQL, RabbitMQ, Redis, Servlet,
SNMP, Software AG, Spring, TIBCO, VMware, WebLogic, WebSphere, Winlog, z/OS.
When a user names a technology, its fields are probably already defined — grep
before inventing.

The full namespace list:

```bash
grep -o '^## .*' {{DOCS_CORPUS}}/semantic-dictionary/fields.md
```

## Fields that carry permissions

Exactly fourteen fields are tagged `permission`, and they are the only ones
usable in an IAM record-level `WHERE` clause:

```
aws.account.id        azure.resource.group   azure.subscription   dt.host_group.id
dt.security_context   event.kind             event.provider       event.type
frontend.name         gcp.project.id         host.name            k8s.cluster.name
k8s.namespace.name    log.source
```

`metric.key` is additionally usable, on the `metrics` table only. The
authoritative table of which field works on which table is in
`iam-grail-permissions.md` — this list is the Semantic Dictionary's own view of
the same set, and the two agree.

**`dt.security_context` is the universal escape hatch.** It is the one
permission field valid on every table, and the only one that works for
`entities`. Anything without a dedicated permission field gets isolated by
setting `dt.security_context` at the source or in OpenPipeline.

Regenerate the list:

```bash
grep -rhoP '^\| `[a-z0-9_.]+`(?=.*Tags: `permission`)' \
  {{DOCS_CORPUS}}/semantic-dictionary/model | tr -d '|` ' | sort -u
```

## Primary Grail tags

`primary_tags.__key__` — a small set of customer-selected tags (Kubernetes
labels, AWS/Azure tags, organisational attributes) that Dynatrace attaches to
**all raw telemetry at ingest**. The `__key__` placeholder is replaced by the
tag name, so a tag called `ownership` becomes the field
`primary_tags.ownership`.

Single-value tags hold a string; multi-value tags hold a string array — which
means an IAM `WHERE` on a primary tag needs `MATCH`, not `=`, or it silently
returns false.

Marked `resource experimental`. Configuration lives at `manage/tags/primary-tags`.

## Per-table field sets

### `logs`

`timestamp`, `content`, `loglevel` (`ERROR`, `INFO`, `TRACE`, …), `status`
(only `INFO` or `NONE`, derived from loglevel), `log.source`,
`log.record.uid`, `event.type` = `LOG`.

Audit logs are logs with `audit.*` populated:

```dql
fetch logs | filter isNotNull(audit.action)
```

`audit.action`, `audit.identity`, `audit.result`, `audit.status`, `audit.time`,
`authentication.is_multifactor`.

### `spans`

`span.id`, `span.parent_id`, `span.alternate_parent_id`, `span.name`,
`span.kind`, `span.status_code`, `span.status_message`, `span.events`,
`span.links`, `span.is_exit_by_exception`, `span.exit_by_exception_id`,
`span.is_subroutine`, `span.timing.cpu`, `span.timing.cpu_self`.

`span.kind` values: `server`, `client`, `producer`, `consumer`, `internal`
(the default), `link` (a Dynatrace link node).

IDs are hex-encoded when displayed: `span.id` is 8 bytes, trace IDs 16.

### `events` and `bizevents`

Classified by `event.kind`, `event.type`, `event.provider`. Davis-generated
events, problems and problem comments are described in `model/davis.md`;
business, billing, carbon and price-list events in
`model/business-analytics.md`.

### `metrics`

Queried with `timeseries`, never `fetch`. `metric.key` is the identifier and
the only metrics-specific permission field.

### `user.sessions` / `user.events`

The RUM tables, replacing USQL. `frontend.name` is their permission field.

## Entities: `dt.entity.*`

**111 entity types.** Each is its own table:

```dql
fetch dt.entity.host
| fieldsAdd entity.name, entity.type, id, tags, managementZones
```

Every entity type carries the same core fields:

| Field | Meaning |
|---|---|
| `id` | the entity ID, tagged `entity-id` |
| `entity.name` | resolved in order from `entity.customized_name`, `entity.conditional_name`, `entity.detected_name` |
| `entity.detected_name` | what Dynatrace or the data source detected |
| `entity.type` | `host`, `service`, … |
| `lifetime` | a timeframe record with `start` and `end` — first and last seen |
| `tags` | string array, manual and auto tags, formatted `[context]key:value` |
| `managementZones` | array — still present on entities, classic concept |

Types that appear constantly: `dt.entity.host`, `dt.entity.service`,
`dt.entity.process_group`, `dt.entity.process_group_instance`,
`dt.entity.application`, `dt.entity.cloud_application` (Kubernetes workload),
`dt.entity.cloud_application_namespace`, `dt.entity.kubernetes_cluster`,
`dt.entity.kubernetes_node`, `dt.entity.kubernetes_service`,
`dt.entity.container_group_instance`, `dt.entity.custom_device`,
`dt.entity.synthetic_test`, `dt.entity.disk`, `dt.entity.os`.

Cloud provider types are numerous and mostly suffixed **(Classic)** in the
docs: `dt.entity.ec2_instance`, `dt.entity.aws_lambda_function`,
`dt.entity.elastic_load_balancer`, `dt.entity.s3bucket`,
`dt.entity.dynamo_db_table`, `dt.entity.relational_database_service`,
`dt.entity.azure_vm`, `dt.entity.azure_sql_database`,
`dt.entity.azure_web_app`, `dt.entity.azure_function_app`,
`dt.entity.google_compute_engine`, and about eighty more.

Full list with every field per type:

```bash
grep -o '^fetch dt\.entity\.[a-z_0-9]*' \
  {{DOCS_CORPUS}}/semantic-dictionary/model/dt-entities.md | sort -u
```

> Provider-specific entity fields are frequently marked `deprecated` even while
> the entity type itself is current — on `dt.entity.ec2_instance`, `arn`,
> `awsInstanceId`, `awsInstanceType`, `awsSecurityGroup` and `awsVpcName` all
> are. Check the marker before recommending one in a dashboard that has to keep
> working.

## Entity relationships

Relationships are **record fields** on the entity, not joins. Each has an
opposite direction:

| Field | Opposite |
|---|---|
| `belongs_to` | `contains` |
| `calls` | `called_by` |
| `runs` | `runs_on` |
| `hosts` | `hosted_by` |
| `accessible_by` | `can_access` |
| `balanced_by` | `balances` |
| `instance_of` | `instantiates` |
| `child_of` | `parent_of` |
| `cluster_of` | `clustered_by` |
| `monitored_by` | `monitors` |
| `indirectly_sends_to` | `indirectly_receives_from` |

**The classic API used different names.** Environment API v2 relationship names
map to the DQL record names through the table in
`model/dt-entities.md#relationship-mapping-table` — `isAccessibleBy` becomes
`accessible_by`/`can_access`, `hostsComputeNode` becomes `hosts`/`hosted_by`,
`isChildOf` becomes `child_of`/`parent_of`. Anyone porting a classic entity
selector will be holding the old names.

For topology traversal across entities, use the Smartscape commands
(`smartscapeNodes`, `smartscapeEdges`, `traverse`) rather than chasing
relationship fields by hand — see `dql.md`.

## Naming conventions and traps

- **Dots are namespaces, not paths.** `k8s.namespace.name` is one field name,
  not a nested lookup.
- **Underscores appear inside a segment, never between namespaces.**
  `dt.host_group.id`, `span.status_code`, `entity.detected_name`.
- **Entity table names use underscores; field names use dots.**
  `fetch dt.entity.process_group_instance` versus `dt.entity.service`. Both are
  written with dots as the table name — but the type portion is
  `process_group_instance`, not `process.group.instance`.
- **The UI label is not the field name.** "Log source" → `log.source`, "Span
  kind" → `span.kind`. Every row carries its Display name; when a user quotes a
  label, translate before writing DQL.
- **Field names are case-sensitive in DQL.** Eight documented business-analytics
  examples get their own case wrong — see `gotchas.md`.
- **A name containing anything outside `a-zA-Z0-9_.` needs backticks**, as does
  a name starting with anything outside `a-zA-Z_`. `primary_tags.*` keys taken
  from cloud tags routinely need them.
- **`experimental` means it can move.** Roughly a third of the dictionary is
  marked experimental or deprecated rather than stable. Quote the marker
  whenever the answer will be embedded in a dashboard, alert or IaC file.
