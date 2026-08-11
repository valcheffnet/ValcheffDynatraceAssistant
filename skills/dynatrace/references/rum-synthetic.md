# RUM and Synthetic — digital experience

The largest section of the corpus by page count: `observe/digital-experience`
(365 files). Two halves that share a data model — real user data and simulated
user data — plus Session Replay sitting across both.

## Contents

- Latest against Classic
- RUM data model
- Web frontends
- Mobile frontends
- Session Replay
- Data privacy
- Synthetic monitoring
- Permissions
- Business insights

## Latest against Classic

| | Latest | Classic |
|---|---|---|
| RUM | `observe/digital-experience/rum` | `rum-classic` |
| Session Replay | `session-replay-latest` | `session-replay` |
| Synthetic | `synthetic` | `synthetic-monitoring` |
| Query | DQL over `user.sessions` / `user.events` | USQL |

Transition guide: `rum/transition-from-rum-classic`.

> **Session Replay (latest) left Preview on 2026-08-04.** Twelve pages dropped
> their `Preview` badge in a single update. Anything written before that date
> describing it as Preview is stale.

## RUM data model

Two Grail tables:

| Table | Permission | Contents |
|---|---|---|
| `user.sessions` | `storage:user.sessions:read` | one record per session |
| `user.events` | `storage:user.events:read` | individual user actions and events |

`frontend.name` is the permission field for both, and also for `metrics` and
`smartscape`. Field detail: `semantic-dictionary/model/rum/`. See
`semantic-fields.md`.

Sensitive RUM fields are masked through the predefined fieldset
`builtin-sensitive-user-events-and-sessions` — see `iam-grail-permissions.md`.

Concepts: `rum/concepts`, `rum/users-and-sessions`.

## Web frontends

`rum/web-frontends`. Instrumentation is the JavaScript agent, injected
automatically by OneAgent or added manually; the snippet formats page carries
the variants. **Experience Vitals** (`rum/experience-vitals`) is the current
metric surface. Error analysis: `rum/error-inspector`.

Infrastructure requirements for pass-through:
`rum/infrastructure-pass-through-requirements`. RUM beacons terminate on an
ActiveGate with the **Beacon forwarder** module — see `activegate.md`.

## Mobile frontends

`rum/mobile-frontends`. Native iOS and Android instrumentation.

> The **native Dynatrace mobile apps** (iOS/Android for viewing Dynatrace, not
> for instrumenting yours) sunset **Jun 30, 2026**, replaced by the responsive
> web UI plus Workflows notifications. Do not confuse the two — mobile *RUM* is
> unaffected. See `classic-vs-latest.md`.

## Session Replay

`session-replay-latest`, split into
`configure-session-replay-web` and `configure-session-replay-mobile`.

Web configuration covers enablement and cost control, opt-in mode, resource
capture, URL exclusion, URL exclusion and masking, restrictions, and the
strong-privacy-requirements path. Mobile covers Android and iOS separately,
including a screenshot debugger.

Masking is the part that matters in a regulated environment: the strong privacy
requirements page describes the process for environments where recording is
constrained by policy rather than by preference.

## Data privacy

`rum/data-privacy` and, platform-wide,
`manage/data-privacy-and-security` (25 files). RUM is where personal data
actually enters the platform, so masking decisions belong at instrumentation
time, not at query time — a masked-at-query field was still ingested and
retained.

## Synthetic monitoring

`observe/digital-experience/synthetic` (latest):

| Page | Topic |
|---|---|
| `new-browser-monitoring-experience` | the current browser monitor surface |
| `architecture-communication-latest` | how monitors reach targets and report back |
| `synthetic-access-control` | who can see and edit monitors |
| `primary-grail-tags-synthetic` | primary tags on synthetic data |
| `segments-and-notebooks-metrics-events` | analysing synthetic results |

Classic: `synthetic-monitoring`, which also holds private location setup.

**Private synthetic locations run on a synthetic-enabled ActiveGate**, which is
a distinct capability set with its own hardware requirements — not the same as
adding a module to a routing ActiveGate. See `activegate.md`.

Entity types: `dt.entity.synthetic_test`, `dt.entity.synthetic_test_step`,
`dt.entity.synthetic_location`, `dt.entity.http_check`,
`dt.entity.http_check_step`, `dt.entity.external_synthetic_test`. Field detail:
`semantic-dictionary/model/synthetic.md`.

## Permissions

`rum/permissions` for RUM, `synthetic/synthetic-access-control` for synthetic.
Both sit on top of the Grail table permissions rather than replacing them.

## Business insights

`observe/digital-experience/business-insights` — connecting user behaviour to
business outcomes. Overlaps with `observe/business-observability` and business
events; field detail in `semantic-dictionary/model/business-analytics.md`.

Use cases across the whole section: `observe/digital-experience/dem-use-cases`.
