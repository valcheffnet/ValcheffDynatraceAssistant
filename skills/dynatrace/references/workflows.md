# Workflows and AutomationEngine

The Workflows app is the frontend for AutomationEngine. It replaces classic
problem notifications and alerting profiles, and it is where anything
event-driven now lives.

Corpus: `analyze-explore-automate/workflows` (94 files).

## Contents

- Vocabulary
- Triggers
- Actions
- Expressions and Jinja
- Permissions — two layers, both required
- Ownership and execution access
- EdgeConnect
- Scheduling
- What replaced what
- Limits

## Vocabulary

| Term | Meaning |
|---|---|
| **Workflow** | the whole automation: a trigger plus tasks |
| **Simple workflow** | a reduced form for straightforward cases |
| **Task** | one step in a workflow |
| **Action** | what a task does — the action type it runs |
| **Execution** | one run of a workflow |
| **Trigger** | what starts it |

Past and ongoing executions are listed in the app; `workflows/running` covers
execution behaviour.

## Triggers

`workflows/trigger`:

| Trigger | Page |
|---|---|
| **Event trigger** | `trigger/event-trigger` — DQL-matched events |
| **Problem trigger** | `trigger/event-trigger#problem-trigger`, with **trigger delay** and **re-trigger on field changes** |
| **Davis event trigger** | `trigger/event-trigger#davis-event-trigger` |
| **Schedule** | `trigger/schedules` |
| **On demand** | manual |

Triggers can be enabled and disabled without deleting the workflow.

**Trigger delay** and **re-trigger on field changes** are the two settings that
decide whether a flapping problem produces one execution or fifty.

## Actions

`workflows/default-workflow-actions`:

| Action | Use |
|---|---|
| **DQL query** | run a query and pass the result on |
| **HTTP request** | call an external system |
| **Run JavaScript** | arbitrary logic in the AppEngine runtime |
| **Run workflow** | call another workflow |
| **Approval request** | pause for a human decision |

Plus connectors for external systems, which is how Slack, Teams, PagerDuty,
ServiceNow, Jira and email notifications are done now.

## Expressions and Jinja

`workflows/reference` documents the expression functions available inside a
workflow:

`calendars()` · `connection()` · `environment()` · `event()` · `execution()` ·
`executions()` · `input()` · `now()` · `timedelta()` · `result()` ·
`scheduling_rules()`

`result()` is how one task reads another's output; `event()` reads the
triggering event; `execution()` and `executions()` reach execution metadata.

Templating is **Jinja**. Variable chips in the UI use underscores, not dots —
`event_name`, not `event.name`. See `gotchas.md`.

## Permissions — two layers, both required

This is the commonest workflow failure and it produces a plain `403 Forbidden`
at task execution rather than at save time.

1. **Account-level permissions** — general AppEngine permissions plus
   AutomationEngine-specific ones, granted in Account Management by an account
   admin.
2. **AutomationEngine authorization settings** — in the Workflows app under
   *Settings > Authorization settings*, enabling the **Primary permissions** and
   **Secondary permissions** the workflow's tasks need.

Having the account permission without enabling it in authorization settings
fails. So does the reverse. `workflows/security` documents the recommended split
between a **Workflows user** and a **Workflows administrator**.

## Ownership and execution access

Every workflow has an **owner**. Execution access follows ownership, with an
administrator able to reach all of them, and the **workflow actor** being the
identity a workflow runs as. A workflow that works for its author and fails for
a colleague is an actor or ownership question, not a logic one.

## EdgeConnect

Secure connectivity from a workflow to on-premise systems, so an HTTP request
action can reach something that is not on the public internet.

## Scheduling

`workflows/schedule` and `trigger/schedules`. `calendars()` and
`scheduling_rules()` exist so schedules can respect business calendars rather
than raw cron.

## What replaced what

| Classic | Latest |
|---|---|
| Problem notifications | per-user email notifications in the **Problems** app |
| Alerting profiles | DQL filtering in the workflow trigger |
| Hardcoded integrations (Ansible, Jira, OpsGenie, PagerDuty, ServiceNow, Slack, Trello, VictorOps, xMatters) | **Workflows connectors** |

The classic model was global to the environment, so no user could set up their
own notification without admin rights. That is the problem Workflows and
per-user notifications solve. See `classic-vs-latest.md`.

## Limits

**The query timeout for workflows is 5 minutes**, the same as Dashboards and
Notebooks — a DQL query action has to return inside it. See
`grail-and-data-organization.md`.

Quickstart: `workflows/quickstart`. Building: `workflows/build`. Managing:
`workflows/manage-workflows`. Use cases: `workflows/use-cases`.
