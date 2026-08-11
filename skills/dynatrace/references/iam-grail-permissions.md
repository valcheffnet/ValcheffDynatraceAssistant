# IAM and permissions in Grail (ABAC)

Latest Dynatrace uses **ABAC** (Attribute-Based Access Control). Policies are
evaluated **at query time**, so access is always current and context-dependent.
OIDC, OAuth 2.0, SAML and SCIM are supported (federating users and groups from
an IdP).

**Without permissions a user can query nothing from Grail.**

## Contents

- Where it is configured
- The four permission levels
- Bucket permissions
- Table permissions
- Record-level permissions
- Field-level permissions (fieldsets)
- File permissions (lookup data) — Preview
- DENY — bucket level only
- Policy boundaries
- Predefined global policies
- Best practices
- A practical design order

Sources: `/docs/platform/grail/organize-data/assign-permissions-in-grail`
(Updated Apr 10, 2026), `/docs/manage/identity-access-management`.

## Where it is configured

*Account Management* → (pick the account, if there is more than one) →
**Identity & access management > Policy management** → **Create policy**: Name,
Description, Policy statement.

## The four permission levels

```
bucket  →  table  →  record  →  field
```

**Mandatory rule: both a bucket permission and a table permission are always
required.** Either one alone does nothing.

## Bucket permissions

All of them start with `storage:buckets:read`. `WHERE` narrows the scope.

**Conditions:** `storage:bucket-name`, `storage:table-name`

**Operators:**

| Operator | Meaning |
|---|---|
| `=` | equality |
| `STARTSWITH` | prefix |
| `IN` | equality against any value in a list |
| `MATCH` | pattern matching against a list of patterns — generalises and extends both `STARTSWITH` and `IN` |

```sql
ALLOW storage:buckets:read WHERE storage:bucket-name MATCH ("default_*", "common_logs");
```

### Included queries (logs only)

Applies only when **Log Management & Analytics – Retain with Included Queries**
is on the rate card.

Condition `storage:query-consumption`:
- `ON_DEMAND` — queries may scan all retained data. **The default** when
  unspecified.
- `INCLUDED` — queries scan only included query data, so they **generate no
  additional Query consumption**.

```sql
-- included query data across all buckets
ALLOW storage:buckets:read WHERE storage:query-consumption="INCLUDED";

-- included only in one bucket
ALLOW storage:buckets:read WHERE storage:bucket-name="common_logs" AND storage:query-consumption="INCLUDED";

-- included everywhere, full retained access only in common_logs
ALLOW storage:buckets:read WHERE storage:query-consumption="INCLUDED";
ALLOW storage:buckets:read WHERE storage:bucket-name="common_logs" AND storage:query-consumption="ON_DEMAND";

-- everything retained (these two are equivalent)
ALLOW storage:buckets:read WHERE storage:query-consumption="ON_DEMAND";
ALLOW storage:buckets:read;
```

> This is a direct cost-control mechanism: give `INCLUDED` to the broad user
> base, and `ON_DEMAND` only to those who genuinely need to dig deep.

## Table permissions

| Table | Permission | DQL commands and functions affected |
|---|---|---|
| `logs` | `storage:logs:read` | `fetch` |
| `events` | `storage:events:read` | `fetch` |
| `security.events` | `storage:security.events:read` | `fetch` |
| `metrics` | `storage:metrics:read` | **`timeseries`** |
| `bizevents` | `storage:bizevents:read` | `fetch` |
| `spans` | `storage:spans:read` | `fetch` |
| `entities` | `storage:entities:read` | `fetch`, `classicEntitySelector`, `entityAttr`, `entityName` |
| `smartscape` | `storage:smartscape:read` | `smartscapeNodes`, `smartscapeEdges`, `getNodeName()`, `getNodeField()` |
| `dt.system.events` | `storage:system:read` | `fetch` |
| `user.events` | `storage:user.events:read` | `fetch` |
| `user.sessions` | `storage:user.sessions:read` | `fetch` |

Restricting a table permission to a bucket:
```sql
ALLOW storage:logs:read WHERE storage:bucket-name="default_logs";
```

## Record-level permissions

Fine-grained filtering per record, through a `WHERE` on the table permission.

```sql
ALLOW storage:logs:read WHERE storage:dt.security_context="TeamA";
```

### Supported fields

| Field | IAM condition | Supported tables |
|---|---|---|
| `event.kind` | `storage:event.kind` | events, security.events, bizevents, system |
| `event.type` | `storage:event.type` | events, security.events, bizevents, system |
| `event.provider` | `storage:event.provider` | events, security.events, bizevents, system |
| `k8s.namespace.name` | `storage:k8s.namespace.name` | events, security.events, bizevents, logs, metrics, spans, smartscape |
| `k8s.cluster.name` | `storage:k8s.cluster.name` | same as above |
| `host.name` | `storage:host.name` | same as above |
| `dt.host_group.id` | `storage:dt.host_group.id` | same as above |
| `metric.key` | `storage:metric.key` | metrics |
| `log.source` | `storage:log.source` | logs |
| `dt.security_context` | `storage:dt.security_context` | **all of them**: events, security.events, bizevents, system, logs, metrics, spans, entities, smartscape, user.events, user.sessions |
| `gcp.project.id` | `storage:gcp.project.id` | events, security.events, bizevents, logs, metrics, spans, smartscape |
| `aws.account.id` | `storage:aws.account.id` | same as above |
| `azure.subscription` | `storage:azure.subscription` | same as above |
| `azure.resource.group` | `storage:azure.resource.group` | same as above |
| `frontend.name` | `storage:frontend.name` | user.events, user.sessions, metrics, smartscape |

**`dt.security_context` is the universal escape hatch.** For anything without a
dedicated field, set `dt.security_context` either at the data source or in the
OpenPipeline processing pipeline.

### `MATCH` is mandatory for array values

`=`, `IN` and `STARTSWITH` work only on fields holding a **single string
value**. When the field contains an array those operators **always return
false**, silently.

```sql
-- matches both "crn-70400-alpha" and ["crn-70131", "crn-70400-beta", "crn-70500"]
ALLOW storage:logs:read WHERE storage:dt.security_context MATCH ("crn-70400-*");
```

If the field might ever hold an array, **always use `MATCH`**.

### Combining bucket and record level

```sql
ALLOW storage:logs:read WHERE storage:bucket-name="unrestricted_logs";
ALLOW storage:logs:read WHERE storage:bucket-name="default_logs"
                          AND storage:dt.security_context="TeamA";
```

### Limits

- **100 statements per policy**
- **200 policies per account**

Hence `MATCH` rather than a series of `=`/`IN`/`STARTSWITH`, and combining logs,
events and metrics into one statement wherever possible.

### Entities — `dt.security_context` only

Unlike monitoring data, entity permissions allow filtering **only** on
`dt.security_context`.

## Field-level permissions (fieldsets)

Hides fields holding sensitive data. A field counts as sensitive when it belongs
to a **fieldset**. Without permission for that fieldset the field does not
appear in results and cannot be used for filtering or grouping.

```sql
ALLOW storage:fieldsets:read WHERE storage:fieldset-name="builtin-sensitive-spans"
```

**Predefined fieldsets:**
- `builtin-sensitive-spans` — drops every span field considered sensitive
- `builtin-request-attributes-spans` — drops request attribute data marked
  sensitive
- `builtin-sensitive-user-events-and-sessions` — drops sensitive fields in
  user.events and user.sessions

**Limits:**
- The predefined fieldsets apply **only** to `spans`, `user.events` and
  `user.sessions`. **They do not apply to logs or events.**
- Custom fieldsets can be scoped `BUCKET` or `TABLE`; otherwise they cover all
  buckets and tables.
- They work with `smartscape`, but **not with `entities`**.

### A custom fieldset through the API

*Dynatrace API* → definition **Grail - Fieldsets**. Endpoints:
`GET/POST /fieldsets`, `GET/PUT/DELETE /fieldsets/{fieldsetUid}`.

```
POST https://<env>/platform/storage/fieldsets/v1/fieldsets
{
  "name": "sensitive-fields-retail",
  "description": "Sensitive fields retail",
  "enabled": true,
  "scope": "BUCKET",
  "fields": ["credit_card", "DOB"],
  "buckets": ["logs_retail"]
}
```
Unmasking for the authorised:
```sql
ALLOW storage:fieldsets:read WHERE storage:fieldset-name="sensitive-fields-retail"
```

> Banking use case: put PII and PCI fields (card numbers, IBAN, DOB, names) in a
> custom fieldset per bucket, with unmask permission for a narrow group.
> Careful: **do not include essential fields** such as `timestamp`, `id` or
> `content` in a fieldset.

## File permissions (lookup data) — Preview

- `storage:files:read` — reading lookup data through DQL
- `storage:files:write` — upload through the REST API
- `storage:files:delete` — delete through the REST API

Condition `storage:file-path`, with operators `=`, `IN`, `startsWith`.

```sql
ALLOW storage:files:read   WHERE storage:file-path startsWith "/lookups/";
ALLOW storage:files:write  WHERE storage:file-path startsWith "/lookups/";
ALLOW storage:files:delete WHERE storage:file-path startsWith "/lookups/";
-- narrower
ALLOW storage:files:read WHERE storage:file-path startsWith "/lookups/public/";
ALLOW storage:files:read WHERE storage:file-path startsWith "/lookups/http_status_codes";
```

The folder-like structure is what makes access to subsets manageable.

## DENY — bucket level only

**Key limitation:** a `DENY` statement works on **buckets**, but **not at record
level**. The docs put it precisely: *"Conditional `DENY` statements involving
Grail table permissions are not supported and are executed as unconditional
`DENY`."*

That wording matters. The condition is not ignored with a warning and it does
not fail - the statement still executes, with the `WHERE` clause discarded.

```sql
-- VALID: denies access to logs in logs_delivery
DENY storage:buckets:read WHERE storage:bucket-name="logs_delivery";

-- TRAP: runs as `DENY storage:logs:read`, blocking every log for that user
DENY storage:logs:read WHERE storage:dt.security_context="sensitive";
```

`DENY` always overrules `ALLOW`, and once a `DENY` matches a request every
subsequent `ALLOW` is ignored. Evaluation order is unconditional DENY first,
then conditional DENY.

**The documented advice is to avoid `DENY` altogether**: grant only what is
needed through scoped `ALLOW` statements, or use policy boundaries. An
unconditional `DENY` blocks the whole API surface for that user.

So **strict access isolation requires buckets**, not just record-level
permissions. Excluding at bucket level guarantees the data enters none of that
user's queries, full table scans included.

> Trace gotcha: spans from one trace can sit in different buckets. Without
> permission on every relevant bucket, the user **sees no trace at all**.

## Policy boundaries

A boundary bundles record- and resource-level restrictions so they can be reused
across permission assignments, instead of writing the same `WHERE` clause into
twenty policies. Selecting a boundary alongside a policy **further restricts**
that policy - it can never widen it, and it can narrow it to no access at all.

The documented use case is exactly the one that keeps coming up: restricting the
built-in **Read logs** policy for twenty user groups to one Kubernetes namespace.

1. Create a boundary, say **K8s DEV**, containing:
   ```
   storage:k8s.namespace.name = "DEVELOPMENT";
   ```
2. Select that boundary when assigning the **Read logs** default policy.

Boundaries support every condition available in the IAM reference, which is what
makes them the answer to "how do I scope a default policy without cloning it".

**Limits and traps:**

- **10 restrictions per boundary.** More means more boundaries, assigned
  together.
- **Security policies only** - no role-based support.
- **No `AND` operator.** Every line is a single condition. For logical operators
  with reusable definitions, use policy templating
  (`manage/identity-access-management/.../advanced/iam-policy-templating`).
- **Only conditions matching a service configuration are applied** to that
  service's permissions; global conditions apply everywhere.
- **Repeated condition names multiply the statements** - each repetition
  produces its own statement.
- **More than one boundary is evaluated separately per boundary**, and the docs
  warn this can produce *unintended unconditional access*. A policy like
  `ALLOW storage:logs:read, storage:entities:read;` bound to a boundary that
  only constrains `storage:host.name` leaves the permissions the boundary does
  not name unconstrained.

Full detail:
`manage/identity-access-management/permission-management/manage-user-permissions-policies/iam-policy-boundaries`.

## Predefined global policies

There is one per table (logs, events, bizevents, security events, metrics,
entities, spans) plus three general ones: **Read all data**, **Read default
monitoring data**, and **Read all system data**.

**Access to all logs:**
```sql
ALLOW storage:buckets:read WHERE storage:table-name="logs";
ALLOW storage:logs:read;
```

**Read all data** (only where genuinely justified):
```sql
ALLOW storage:buckets:read;
ALLOW storage:system:read,
      storage:events:read,
      storage:security.events:read,
      storage:logs:read,
      storage:metrics:read,
      storage:entities:read,
      storage:bizevents:read,
      storage:spans:read,
      storage:smartscape:read;
```

**Read all default monitoring data** (grants no access to custom buckets):
```sql
ALLOW storage:buckets:read WHERE storage:bucket-name MATCH ("default_*");
ALLOW storage:events:read, storage:logs:read, storage:metrics:read,
      storage:entities:read, storage:bizevents:read, storage:spans:read,
      storage:smartscape:read;
```

**Read all system data** (audit events, billing events, query execution events —
for system admins):
```sql
ALLOW storage:buckets:read WHERE storage:bucket-name MATCH ("dt_*");
ALLOW storage:system:read;
```

## Best practices

- **Do not forget the bucket permissions** — the most common cause of "I can't
  see any data".
- **The most dangerous trap:** if an **unconditional table permission exists in
  any other policy** that applies to this user, the `WHERE` clauses become
  **irrelevant** and the user sees every record in that table. One broad policy
  kills the whole fine-grained scheme. Audit for unconditional permissions.
- Use `MATCH` instead of combinations of `=`/`IN`/`STARTSWITH` — the
  100-statement limit runs out fast.
- With `MATCH` and a wildcard, place `*` **before or after a word separator**
  (`-`, `_`, `.`, `/`). `MATCH ("db-tech-*")` is more efficient than
  `MATCH ("db-tech*")`, because `matchesValue` in DQL performs better when
  separators are present.
- Combine logs, events and metrics into one statement where applicable.
- In custom fieldsets, do not include essential fields (`timestamp`, `id`,
  `content`).

## A practical design order

1. **Buckets** — plan the partitioning (retention, cost, compliance,
   sensitivity). See `grail-and-data-organization.md`.
2. **Security context at ingest** — set `dt.security_context`, and any dedicated
   fields, at the source or in OpenPipeline, so there is something to filter on
   later.
3. **IAM policies** — bucket, table, record and field, per group.
4. **Segments** — for convenient runtime views. **They are not a security
   boundary.**
