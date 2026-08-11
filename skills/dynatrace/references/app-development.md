# App development — AppEngine, app functions, the SDK

Everything here comes from the **developer corpus**,
`$DT_DEV` (205 pages, harvested 2026-08-06). None of it is
in the docs corpus, and grepping `$DT_DOCS` harder will not
produce it. Cite the developer corpus explicitly when answering from this file.

## Contents

- App function limits
- What the runtime blocks
- The runtime is Node-shaped but not Node
- Reaching an external host
- `app.config.json`
- Permissions and scopes
- Platform service URLs
- The SDK packages
- App Toolkit (`dt-app`)
- Intents
- Known documentation problems

## App function limits

Verbatim from `develop/reference/javascript-runtime.md`, "Runtime limitations":

- execution times out after **120 seconds**
- functions **can't call functions of other apps**
- functions can't call the **function executor** API
- functions are deployed in an environment with **256 MB of RAM**
- functions **can't send binary responses**
- inputs and outputs can't be larger than **5 MB**, respectively
- there is a **concurrency limit**; exceeding it returns **429 Too Many Requests**
- calls to external hosts must be explicitly allowed
  (`develop/guides/app-functions/allow-outbound-connections.md`)
- the **WebSocket API is unavailable**

**The 256 MB is not an app-wide budget.** The sentence attaches the memory to the
environment a function runs in, and each `.ts` file under `/api` deploys as its
own function with its own endpoint. Adding a sixth function does not shrink the
other five.

**What is genuinely undocumented** is whether *concurrent invocations of the same
function* each get a fresh 256 MB or contend for one. Nothing in either corpus
addresses it. Say so rather than picking a side; the safe design is stateless
functions that stay well under the limit.

**"No binary responses" is not the same as "JSON only".** The runtime calls
`JSON.stringify` on whatever the function returns, so plain strings are fine — a
bare string is valid JSON, and the toolkit's own generated function returns
`'Hello world'`. The real consequence is broader than the format: there is no
control over the response at all. No `Content-Type`, no `Response` object, no
streaming, no `image/png`. Shipping bytes means base64 inside a JSON string,
under the 5 MB output cap.

## What the runtime blocks

Removed with a stated reason, same page:

| Removed | Why |
|---|---|
| `globalThis.window` | was used to wrongly detect a browser context |
| `eval("...")` | remote code execution if the input is untrusted — the docs name dashboard variables sourced from logs as the example |
| `new Function("...")` | identical risk |

`eval` can be re-enabled per app via `app.functionSandbox.unsafe-eval`, and doing
so **requires a `comment` explaining why** — the schema enforces the
justification, not just the flag.

## The runtime is Node-shaped but not Node

`develop/reference/javascript-runtime.md` lists what is available and, more
usefully, what is **stubbed**.

**Stubbed: `process`, `fs`, `fs/promises`.** They import successfully — that is
the point, third-party packages expect them — but *every exposed function throws
when called*. This is the single most common cause of "works on my laptop, fails
in the tenant": a dependency that touches the filesystem passes `npm install`,
passes local `dt-app dev`, and dies on the deployed function.

Available with caveats worth knowing before designing around them:

| Module | Caveat |
|---|---|
| `http`, `https` | client only — **creating a server is not supported** |
| `crypto` | some algorithms, custom certificates and Diffie-Hellman are unsupported |
| `zlib` | no Brotli |
| `string_decoder` | no `ascii`, `utf16le`, `latin1` |
| `perf_hooks` | no `timerify`, `eventLoopUtilization`, `monitorEventLoopDelay` |

Otherwise present: `assert`, `buffer`, `console`, `events`, `path`,
`querystring`, `stream` (+ `/consumers`, `/promises`, `/web`), `timers`, `url`,
`util`.

## Reaching an external host

Two separate walls, and they are enforced in different places. Confusing them
wastes a lot of time.

**From the app UI you cannot.** `develop/guides/security/configure-csp-rules.md`:
*"You can't configure the `connect-src` directive for your app. That means you
can't fetch resources from external domains."* Note which CSP directives
`app.config.json` does expose — `font-src`, `img-src`, `media-src`, `style-src`,
`script-src` — and that `connect-src` is deliberately absent from that list. The
documented answer is to move the call into an app function.

**From an app function you can, once the environment allows the host.** Outbound
requests are blocked by default. The allowlist is **not** part of the manifest:
it lives in **Settings app → General → Environment management → External
requests** (`develop/guides/app-functions/allow-outbound-connections.md`). So it
is an environment-level change, which usually means a different person and a
different change process than shipping the app.

Enforcement can also be switched off wholesale, permitting any host. The page
carries its own warning about that; treat it as a last resort rather than a
setup step.

## `app.config.json`

Source: `quickstart/app-toolkit.md`.

Top level: `environmentUrl` (required) — the environment the project targets.

Under `app`: `id` (required, **≤50 characters, lowercase alphanumeric only**),
`name` (required, ≤40), `version` (required), `description` (required, ≤80),
`icon` (`.svg` recommended, auto-generated if absent), `hidden` (keeps a widget
app out of the App Launcher), `intents`, `pageTokens`, `scopes` (**required**),
`selfMonitoringAgent`, and a `csp` block with `font-src`, `img-src`, `media-src`,
`style-src`, `script-src`.

Under `build`: `mode`, `sourceMaps` (`true` = app code only, `'all'` = including
`node_modules`), `namedChunks` (readable chunk names instead of content hashes —
only with `--optimize`, and the dev server never obfuscates regardless),
`sourceRoot`.

**Build targets are fixed and not configurable**: app UI compiles to `es2022`,
functions to `esnext`.

## Permissions and scopes

Schema (`develop/platform-services/core-concepts/authentication.md`):

```
<Service-Name or Service-Namespace>:<Resource>:<Action>
```

```
app-engine:apps:install        document:documents:delete
\________/ \__/ \_____/        \______/ \_______/ \____/
namespace   res   action       namespace    res    action
```

The namespace and resource match the segments of the platform service URL, so a
permission can be derived from the endpoint being called.

Deploying an app needs `app-engine:apps:install` and `app-engine:apps:run`;
uninstalling needs `app-engine:apps:delete`
(`develop/guides/deploy-your-app.md`).

## Platform service URLs

```
<Root>/platform/<Service-Namespace>/<Service-Name>/<Version>/<Api-Resources>
```

`<Root>` is `<your-environment-id>.apps.dynatrace.com` — note **`.apps.`**, not
the `.live.` host the Classic API uses. `platform` is mandatory. `<Version>` is
`v<Major>` only.

Swagger for every platform service:
`<environment-id>.apps.dynatrace.com/platform/swagger-ui/index.html`.

## The SDK packages

30 packages under `develop/sdks/`, each documented per version. The ones worth
knowing by name:

| Package | For |
|---|---|
| `client-query` | DQL execution |
| `client-document` | dashboards and notebooks as documents |
| `client-automation` | workflows |
| `client-iam` | policies, groups, permissions |
| `client-app-settings`, `client-settings` | app and platform settings |
| `client-bucket-management` | Grail buckets |
| `client-filter-segment-management` | segments |
| `client-service-level-objectives` | SLOs |
| `client-davis-analyzers` | Davis analyzers |
| `client-app-engine-registry`, `client-app-engine-edge-connect` | app registry, EdgeConnect |
| `client-hub` | Hub |
| `client-notification` / `-v2` | notifications |
| `client-synthetic` | synthetic monitors |
| `client-state`, `client-resource-store` | app state and stored resources |
| `navigation`, `react-hooks`, `units`, `app-utils`, `automation-utils`, `app-environment`, `user-preferences` | UI and utility |

**`client-classic-environment-v1` and `client-classic-environment-v2` are
bridges.** They call the **Classic** Environment API from a latest-platform app.
The page is latest, the subject is Classic — worth naming explicitly when someone
asks how to reach a Classic endpoint from an app, since the `generation` field
cannot express that distinction. Same for
`platform-services/services/classic-environment-service`.

## App Toolkit (`dt-app`)

Commands documented in `quickstart/app-toolkit.md`: `create`, `dev`, `build`,
`deploy`, `info`, `update`, `uninstall`, `version`, `function`, `action`,
`analyze`, `migration`, `help`, `commands`.

`dt-app generate function <name>` scaffolds a function plus its test and prints
ready-made `curl` examples for it.

## Intents

Every Dynatrace app runs inside an **iframe hosted by the AppShell**
(`develop/guides/navigation/intents/about-intents.md`). Ordinary links can move
between apps but cannot carry structured context; intents can — entity ids,
timeframes, queries — coordinated by the platform so the target app knows what to
show.

**Explicit** intents name the target app: one click, no dialog. **Implicit** ones
let the platform offer the apps that declared they can handle the payload, which
is what the "Open with…" entry does. An app declares what it handles via
`app.intents` in `app.config.json`, authored with `IntentDeclaration` from
`@dynatrace-sdk/navigation`.

## Known documentation problems

**The two domains disagree on units.** developer.dynatrace.com says app functions
get 256 **MB**; `license/capabilities/appengine-functions.md` in the docs corpus
says 256 **MiB**. The difference is 12 MB of headroom, which matters only at the
margin, but quote whichever domain you are citing rather than harmonising them
silently.

**Community answers on app limits are not vendor statements.** The most-cited
answer on whether the 256 MB is shared comes from a forum reply whose author
carries the rank *Mentor* — a community activity rank, not a staff badge. See
`gotchas.md` DT80 before attributing anything found there to Dynatrace.
