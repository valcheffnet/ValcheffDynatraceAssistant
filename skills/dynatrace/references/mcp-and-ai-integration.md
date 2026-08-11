# Dynatrace MCP and AI integration

`github.com/dynatrace-oss/dynatrace-mcp`, `github.com/Dynatrace/dynatrace-for-ai`.
Harvested 30 July 2026.

## Contents

- Three different things — do not confuse them
- Hosted MCP server
- Operational considerations
- Without a tenant of your own
- Related docs paths

Source: `docs.dynatrace.com/docs/dynatrace-intelligence/dynatrace-mcp`
(Updated Jul 15, 2026).

## Three different things — do not confuse them

| Variant | What it is | Status (Jul 2026) |
|---------|------------|-------------------|
| **Remote / hosted MCP server** (`dynatrace-mcp` through mcp-gateway) | Dynatrace hosts the server; connect by URL with a bearer token. No local installation. | The current recommended path |
| **Local OSS MCP server** (`@dynatrace-oss/dynatrace-mcp-server`, npx, stdio) | Runs locally, offers more write tools (Slack, email, notebooks) | **Deprecated since v2.1.2** → migrate |
| **Dynatrace for AI plus `dtctl`** | Agent Skills packages and a kubectl-style CLI for the platform | The successor to the local server for local development |

The local OSS server was richer — write operations such as `send_slack_message`,
`send_email`, `send_event` and `create_dynatrace_notebook` — but it is
deprecated. The hosted server is currently **read-only in substance**: it
executes DQL and analyses, it does not change configuration.

## Hosted MCP server

### Endpoint

```
https://{environment-name}.apps.dynatrace.com/platform-reserved/mcp-gateway/v0.1/servers/dynatrace-mcp/mcp
```

### Tools (18, from the table in the docs)

**DQL and data**

| Tool | What it does | Permissions |
|------|--------------|-------------|
| Grail Query Agent | Natural language → DQL. Does **not** execute the query. | `davis-copilot:nl2dql:execute` — *Early Access* |
| DQL Explanation Agent | DQL → a natural-language explanation | `davis-copilot:dql2nl:execute` — *Early Access* |
| Data Analysis Agent | Executes any valid DQL, returns the raw result. **Capped at 1000 records.** | `storage:buckets:read` plus per-table (`storage:logs:read` and so on) |
| Help Agent | General questions about the Dynatrace product | `davis-copilot:conversations:execute` — *Early Access* |

**Problems and RCA**

| Tool | What it does | Permissions |
|------|--------------|-------------|
| Root Cause Agent | Lists all problems (active or closed, by choice) | `storage:buckets:read` plus `storage:events:read` |
| Root Cause Details Agent | Detail for one Davis problem | the same |
| Kubernetes Agent | Events for Kubernetes clusters (all, or specific ones) | the same |

**Timeseries analysis (Davis analyzers)** — all require `storage:buckets:read`
plus `davis:analyzers:read` and `davis:analyzers:execute`

| Tool | What it does |
|------|--------------|
| Forecasting Agent | Forecasts future values with a statistical model |
| Changepoint Agent | Finds events, outliers and significant trends |
| Static Threshold Analysis Agent | Anomalies against a fixed threshold |
| Seasonal Baseline Agent | A dynamic baseline with daily and weekly seasonality |
| Auto-adaptive Threshold Analysis Agent | One threshold, learned from the data's distribution |
| Log Pattern Agent | Common patterns in the logs (also needs `storage:logs:read`) |

**Security** — all require `storage:buckets:read` plus
`storage:security.events:read`

| Tool | What it does |
|------|--------------|
| Security Posture Agent | Compliance findings and misconfigurations from the latest SPM run |
| Runtime Vulnerability Agent | All open vulnerabilities (muted and non-muted) from RVA |
| Security Event Details Agent | Detail by finding ID, scan ID or title |
| Security Summary Agent | Overview of security events (external plus Dynatrace detection findings) |

**Navigation and context**

| Tool | What it does | Permissions |
|------|--------------|-------------|
| Document Agent | Finds accessible Dashboards and Notebooks by name | `document:documents:read` |
| Troubleshooting Agent | Globally shared troubleshooting guides matched to a problem description. Requires **Enable document suggestion** in Settings. | `davis-copilot:document-search:execute` — *Preview* |
| Smartscape Agent | Entity name ↔ entity ID | `storage:entities:read` |

### Authentication

A bearer token in the `Authorization` header. Two options:

- **Platform token** — recommended by the docs, because OAuth-generated tokens
  are short-lived.
- **Confidential OAuth client, Authorization Code grant** — the MCP client (VS
  Code, for example) runs the flow itself. **Both client ID and client secret**
  are needed; without the secret there is no auto-refresh and the connection
  drops at expiry.

**Not supported as of Jul 2026:** CIMD, public OAuth clients, dynamic client
registration.

### Permission gotchas

1. On top of the per-tool permissions, **both the user and the token** need
   `mcp-gateway:servers:invoke` and `mcp-gateway:servers:read`.
2. With an OAuth client, the effective rights are the **intersection** of the
   client's rights and those of the user who created it.
3. The token acts only within the user's own permissions, so MCP does not bypass
   IAM/ABAC. The Data Analysis Agent explicitly "respects permission scopes".
4. Full OAuth client scope list for all tools, from the docs:
   `ai:operator:execute`, `mcp-gateway:servers:{invoke,read}`,
   `davis-copilot:{conversations,nl2dql,document-search,dql2nl}:execute`,
   `davis:analyzers:{read,execute}`, `document:documents:read`,
   `storage:{bizevents,buckets,system,spans,entities,user.events,user.sessions,user.replays,smartscape,events,metrics,logs,files,security.events}:read`

### VS Code setup

`.vscode/mcp.json`:

```json
{ "servers": { "dynatrace-mcp": {
  "url": "https://{environment-name}.apps.dynatrace.com/platform-reserved/mcp-gateway/v0.1/servers/dynatrace-mcp/mcp",
  "headers": { "Authorization": "Bearer YOUR_TOKEN" }
}}}
```

For OAuth, supply **only** the `url` with no header — VS Code asks for the
client ID and secret at startup.
Verify: Copilot Chat → `ctrl+#` → Tools → `dynatrace-mcp (All tools)` → "Show me
last 10 logs".

## Operational considerations

- **DQL through MCP is billable on Query (GiB scanned)** like any other DQL. An
  LLM iterating over queries spends real money, so put a narrow timeframe and a
  bucket in the prompt.
- The **1000-record cap** on the Data Analysis Agent means the agent should
  `summarize` rather than dump raw records.
- In a banking context, MCP is not a new attack surface on the data — IAM still
  applies — but it **sends log content to an external LLM**. That is a data
  governance question, not a technical one. The scope is cut with per-tool
  permissions (no `storage:logs:read` means no logs) and with bucket-level IAM
  policies.

## Without a tenant of your own

The MCP server has **no offline or mock mode** — every tool needs an environment
URL and a bearer token, including the Help Agent, which wants
`davis-copilot:conversations:execute`. Without a tenant it does nothing.

Free ways to get a tenant:

| Option | URL | What it gives |
|--------|-----|---------------|
| **Playground** | `https://playground.apps.dynatrace.com` | A pre-configured sandbox with sample data, monitoring Kubernetes applications. No installation. |
| **Free trial** | `dynatrace.com/trial` | 15 days with your own data — requires OneAgent on a host |

`github.com/dynatrace-oss/dt-mcp-playground` — the repo from the DevHUB sessions
at Perform 2026: VS Code plus Copilot Chat (Agent mode) plus `.vscode/mcp.json`
pointing at the Playground, with browser-based auth so no token is created by
hand. It ships ready-made `/` prompts. It uses the **local npx server**, not the
hosted gateway, and explicitly provides **no** mock data — a real Dynatrace
account is needed for Playground access.

Unverified: whether the Playground allows creating Platform tokens or OAuth
clients. The docs do not say, and the repo sidesteps the question with browser
auth.

**Knowledge with no access at all:** `npx skills add dynatrace/dynatrace-for-ai`
— Agent Skills packages with DQL and domain knowledge, plain text, working
without a tenant.

## Related docs paths

- `dynatrace-intelligence/dynatrace-mcp`
- `dynatrace-intelligence/agentic-and-generative-ai` (Davis CoPilot / Dynatrace Assist)
- `dynatrace-intelligence/agentic-and-generative-ai/agentic-and-generative-ai-data-privacy`
