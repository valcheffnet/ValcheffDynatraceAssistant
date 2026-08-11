# The Dynatrace API — which one, which token, which scope

`dynatrace-api` is the largest section of the corpus by file count (1 148) and
the one with the least labelling: **1 045 of those files carry no generation
marker at all**. Classic against latest has to be inferred from the path.

## Contents

- The four API surfaces
- Token format and prefixes
- Token scopes
- Platform tokens and OAuth clients
- Settings schemas
- Rate limits and payload limits
- Deprecation guides
- Working out which API a question is about

## The four API surfaces

| Surface | Path | Files | What it is |
|---|---|---:|---|
| **Environment API** | `dynatrace-api/environment-api` | 774 | the main surface, v1 and v2 |
| **Configuration API** | `dynatrace-api/configuration-api` | 278 | **Classic** configuration |
| **Account Management API** | `dynatrace-api/account-management-api` | 86 | account-level: users, groups, policies, subscriptions |
| **Basics** | `dynatrace-api/basics` | 6 | auth, tokens, response codes, limits |

Plus the **Platform APIs**, which are the newer app-oriented surfaces
(OpenPipeline, documents, storage, fieldsets) documented alongside the features
that use them rather than in this section.

**Inferring generation from the path**: `configuration-api` is Classic
configuration; `environment-api/v2` is the newer surface; `environment-api/v1`
is older and much of it has a v2 replacement; `account-management-api` is
account-level and orthogonal to both. Do not tell a user an endpoint is "latest"
because the frontmatter says nothing — it says nothing for almost the whole
section.

Environment API v2 sub-areas include `entity-v2`, `events-v2`, `metrics-v2`,
`settings`, `activegates`, `audit-logs`, `credential-vault`, `custom-tags`,
`deployment`, `anonymization`, `application-security`, `business-analytics-v2`,
`cluster-information`.

## Token format and prefixes

A token has three dot-separated components:

```
dt0s01.ST2EY72KQINMH574WMNVI7YN.G3DFPBEJYMODIDAEX454M7YWBUVEFOWKPRVMWFASS64NFH52PX6BNDVFFM572RZM
prefix  public portion (24 chars)   secret portion (64 chars)
```

- **Token identifier** = prefix + public portion. Safe to display and to log —
  this is what belongs in a ticket.
- **Secret portion** — treat as a password. Never displayed, never stored in
  plain text.

| Prefix | Type |
|---|---|
| `dt0s01` | API token |
| `dt0s02` | OAuth2 client created through Account Management, for Dynatrace Apps and the Account Management API |
| `dt0s03` | OAuth2 client for internal and external services and integrations |
| `dt0s04` | chat and identity linking |
| `dt0s06` | OAuth2 refresh token — rotates every 5 to 15 minutes |

The prefix tells you what kind of credential you are looking at without needing
the rest, which is the fastest way to diagnose "this token does not work here".

## Token scopes

`basics/dynatrace-api-authentication` groups them by surface: **OpenPipeline**,
**API v2**, **API v1**, **PaaS**, and other. The ones that recur:

| Scope | Used for |
|---|---|
| `metrics.ingest` | metric ingest |
| `logs.ingest` | log ingest |
| `openTelemetryTrace.ingest` | OTLP traces |
| `openpipeline:logs:ingest`, `:metrics:ingest`, `:traces:ingest` | the OpenPipeline ingest surface |
| `settings.read`, `settings.write` | settings objects |
| `entities.read` | entity queries |
| `activeGateTokenManagement.create` | ActiveGate lifecycle |
| `InstallerDownload` (PaaS) | OneAgent and ActiveGate installers |
| `DataExport` (v1) | problem, event, metric and topology feeds |

The Grail `storage:*:read` permissions are **not** token scopes — they are IAM
policy permissions. A token with every API scope still reads nothing from Grail
without them. See `iam-grail-permissions.md`.

## Platform tokens and OAuth clients

Newer surfaces use **platform tokens** and OAuth clients rather than classic API
tokens. With an OAuth client, effective rights are the **intersection** of the
client's rights and those of the user who created it — so a client created by a
restricted user is restricted regardless of its own scopes.

The Kubernetes operator is the clearest worked example of the split between an
operator token and a data-ingest token; see `ingest-k8s.md`.

## Settings schemas

`dynatrace-api/environment-api/settings` — **466 files**, one per `builtin:*`
schema. This is where a configuration question that starts "which setting
controls…" usually ends.

Grep by schema id:

```bash
grep -rln "builtin:openpipeline" {{DOCS_CORPUS}}/dynatrace-api/environment-api/settings
```

Settings objects are also the unit that owner-based access control applies to —
see `openpipeline.md`.

## Rate limits and payload limits

`basics/access-limit` covers the **payload limit** and **request throttling**.
Response codes: `basics/dynatrace-api-response-codes`. Preview and Early Access
endpoints are flagged in `basics/preview-early-access`.

Log ingest has its own limits — 10 MB request, 50 000 records, 10 MB per log
body. See `logs.md`.

## Deprecation guides

`dynatrace-api/basics/deprecation-migration-guides`, including
`timeseries-to-metrics` (Timeseries API v1 → Metrics API v2 → DQL). Announcements
land in `whats-new/dynatrace-api` (45 pages) and
`whats-new/dynatrace-api/deprecated-apis`.

## Working out which API a question is about

1. **Is it about the account or the environment?** Users, groups, policies and
   subscriptions are Account Management; everything else is environment.
2. **Is it configuration or data?** Classic configuration lives in
   `configuration-api`; data lives in `environment-api`.
3. **Is there a v2?** If a v1 endpoint is named, check for a v2 replacement
   before answering, because the v1 one may be deprecated.
4. **Is it actually Grail?** Anything reading telemetry now goes through DQL,
   not a REST endpoint. `fetch` beats `/metrics/query`.
