# Application Security, threat observability and investigations

Four distinct products under `secure/`, often confused with each other:
**Runtime Vulnerability Analytics** finds vulnerable code, **Application
Protection** blocks attacks, **Security Posture Management** checks
configuration against standards, and **threat observability** ingests security
events from elsewhere.

Corpus: `secure` (113 files).

## Contents

- The four surfaces
- Monitoring mode coverage — what you get for what you pay
- Runtime Vulnerability Analytics
- Application Protection
- Security Posture Management
- Threat observability
- Investigations
- The security.events table
- XSPM

## The four surfaces

| Surface | Path | Question it answers |
|---|---|---|
| **Runtime Vulnerability Analytics** | `secure/application-security/vulnerability-analytics` | which running code is vulnerable |
| **Application Protection** | `secure/application-security/application-protection` | which attacks are being blocked |
| **Security Posture Management** | `secure/application-security/spm` | does the configuration meet a standard |
| **Threat observability** | `secure/threat-observability` | what do security events from all sources say |

## Monitoring mode coverage — what you get for what you pay

`secure/application-security` documents coverage per OneAgent monitoring mode,
and this is the first thing to check when a capability "does not appear":

- **Full-Stack Monitoring** — the full capability set, because code-level
  instrumentation is what finds code-level vulnerabilities.
- **Infrastructure Monitoring** — a reduced set. No code-level instrumentation
  means no code-level vulnerability detection.
- **Discovery mode** — inventory only.

The mode is set at OneAgent install with `--set-monitoring-mode` and changeable
afterwards through the CLI. See `oneagent.md`.

## Runtime Vulnerability Analytics

`vulnerability-analytics`:

| Page | Topic |
|---|---|
| `application-security-overview` | the surface itself |
| `third-party-vulnerabilities` | vulnerable libraries in running processes |
| `code-level-vulnerabilities` | vulnerabilities in your own code |
| `app-sec-metrics` | the metrics AppSec produces |
| `security-notifications-rva` | notifications |

RVA reports **open vulnerabilities, muted and non-muted** — the muted ones still
exist and still appear through the API and MCP. A count that disagrees with the
UI is usually a muting filter.

## Application Protection

`application-protection/application-protection-rules` — the rules that decide
what gets blocked rather than merely reported. Attack detection runs in the
instrumented process, so it inherits the monitoring-mode constraint above.

## Security Posture Management

`application-security/spm/compliance-standards` — checking configuration against
compliance standards. Findings come from a **scan run**, so "the finding is
stale" is a question about when SPM last ran, not about the check.

## Threat observability

`secure/threat-observability` (35 files): `concepts`, `dql-examples`,
`security-events-ingest`. This is where security events from outside Dynatrace
arrive and become queryable alongside everything else.

`dql-examples` is worth reading before writing a security query by hand.

## Investigations

`secure/investigations` (12 files) — the case-management surface:

`concepts`, `execute-queries`, `query-tree`, `extract-fields`, `filter-logs`,
`define-timeframes`, `enhance-results`, `manage-evidence`, `manage-templates`,
`case-sharing`, `collaborate-with-apps`,
`accelerate-root-cause-analysis`.

The **query tree** is the distinguishing feature: an investigation keeps the
branching set of queries that led to a conclusion, with evidence attached, so
the reasoning survives the incident.

## The `security.events` table

Queried with `fetch security.events`; permission `storage:security.events:read`
plus a bucket permission.

Four sub-models in the Semantic Dictionary, at
`semantic-dictionary/model/security-events/`:

- `vulnerability.md`
- `threat.md`
- `compliance.md`
- `detection.md`

Grep those for exact field names before writing a security DQL query — see
`semantic-fields.md`.

Security events are a separate OpenPipeline configuration scope
(**Security events (new)**), with their own backdating window of **ingest time
minus 1 hour**, same as metrics rather than the 24 hours logs get. See
`openpipeline.md`.

MCP exposes four security tools — Security Posture Agent, Runtime Vulnerability
Agent, Security Event Details Agent, Security Summary Agent — all requiring
`storage:security.events:read`. See `mcp-and-ai-integration.md`.

## XSPM

`secure/xspm` (5 files) — extended security posture management. Also
`secure/threats-and-exploits` (4) and `secure/use-cases` (20), which is the
largest sub-section and worth grepping for a scenario before designing one from
scratch.

Licensing: `license/capabilities/application-security`.
