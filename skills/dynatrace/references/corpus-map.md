# The Dynatrace documentation — the local corpus and the live site

`{{DOCS_CORPUS}}` holds the whole of `docs.dynatrace.com` converted to Markdown:
**4 403 pages, 7.83M words**, snapshot **2026-08-05**, in sync with the live sitemap on that
date. Every page carries YAML frontmatter with its `source_url`, `generation` and `lastmod`,
and every image on every page has been either transcribed into the text or explicitly marked
as decoration.

This is the depth layer. Use it when `references/` does not answer the question. The same
section names apply to the live site, so the maps below serve both grepping the corpus and
building a `dtfetch.sh` path.

## Contents

- Search order
- How to grep the corpus
- Sections
- Second level, by section
- Where things actually live
- Classic vs latest inside the corpus
- Image content is text
- Known-bad pages
- The second corpus: developer.dynatrace.com
- Still live-only: community.dynatrace.com
- Reaching the live site
- How stale is any given page
- Freshness
- Other reports in `_reports/`

## Search order

1. **`references/`** — the distilled answer. Start here.
2. **`references/gotchas.md`** — grep any identifier the user quoted, *before* answering.
   The documentation is wrong in ~200 known places.
3. **This corpus** — grep it. Offline, complete, and it contains the image content.
4. **Live docs** — `scripts/dtfetch.sh <path>` only when the corpus misses the topic
   entirely or the page is newer than the snapshot. Say so when you fall back.

Do not fall back to the live site for something the corpus already has. The corpus is
cleaner (chrome stripped, links resolved) and richer (image content as text) than the page.

## How to grep the corpus

```bash
# an identifier — field name, metric key, permission, endpoint
grep -rn "dt.host.cpu.usage" {{DOCS_CORPUS}} --include=*.md

# narrow to a section first when the term is common
grep -rn "bucket" {{DOCS_CORPUS}}/platform/grail --include=*.md

# find the page for a concept, then read it whole
grep -rl "OpenPipeline" {{DOCS_CORPUS}}/platform --include=*.md

# what a screenshot showed — transcriptions live in stage4 blocks
grep -rn "stage4:start" {{DOCS_CORPUS}}/observe/... --include=*.md

# the URL a local file came from
head -8 {{DOCS_CORPUS}}/platform/grail/dynatrace-query-language.md
```

Links between pages are rewritten to relative `.md` paths, so a link in one file opens the
real neighbouring file. All 30 568 internal links resolve. Cross-page `#anchors` resolve
through `<a id="...">` markers carried over from the site — 17 643 of them. Do not treat
those lines as noise.

## Sections

| Section | Files | Words | Transcribed images | What is in it |
|---|---:|---:|---:|---|
| `dynatrace-api` | 1 148 | 964 162 | 13 | REST reference — the largest section by files, almost no images |
| `ingest-from` | 917 | 1 397 361 | 667 | every ingest path: AWS, Azure, GCP, K8s, OTel, OneAgent, extensions |
| `observe` | 804 | 1 328 690 | 1 063 | RUM, synthetic, infrastructure, applications, business, AI, data |
| `analyze-explore-automate` | 370 | 591 727 | 273 | Logs, dashboards, notebooks, workflows, metrics, alerting |
| `semantic-dictionary` | 274 | 2 442 268 | 0 | **field and entity-type reference — 92 354 table rows, zero images** |
| `whats-new` | 189 | 211 049 | 9 | release notes per component; where deprecations are announced |
| `manage` | 155 | 164 058 | 134 | IAM, data privacy, account management, network zones, segments, tags |
| `platform` | 136 | 196 121 | 55 | Grail, OpenPipeline, AppEngine, AutomationEngine |
| `secure` | 113 | 191 405 | 302 | Application Security, threat observability, XSPM, investigations |
| `deliver` | 97 | 106 610 | 66 | SLOs, Site Reliability Guardian, configuration-as-code, ownership |
| `dynatrace-intelligence` | 71 | 100 918 | 86 | Davis, predictive and generative AI |
| `license` | 67 | 73 256 | 47 | DPS capabilities and rates, classic licensing |
| `discover-dynatrace` | 29 | 35 680 | 18 | getting started, platform overview |
| `manage-your-costs` | 17 | 22 599 | 12 | cost view / allocate / control / predict |
| (section landing pages) | 15 | 6 082 | 2 | one per section, at the corpus root |
| `_external` | 1 | 2 114 | 3 | one captured product-blog article |

## Second level, by section

File counts are the corpus as it stands. Directories ending `-classic` are legacy; see
`classic-vs-latest.md`.

**`dynatrace-api/`** — `environment-api` (774), `configuration-api` (278),
`account-management-api` (86), `basics` (6)

**`ingest-from/`** — `amazon-web-services` (179), `microsoft-azure-services` (159),
`setup-on-k8s` (110), `extensions` (93), `dynatrace-oneagent` (92), `opentelemetry` (71),
`google-cloud-platform` (69), `dynatrace-activegate` (39), `technology-support` (37),
`extend-dynatrace` (35), `setup-on-container-platforms` (15), `fleet-management` (2)

**`observe/`** — `digital-experience` (365), `infrastructure-observability` (281),
`application-observability` (92), `business-observability` (37),
`dynatrace-for-ai-observability` (19), `data-observability` (4)

**`analyze-explore-automate/`** — `workflows` (94), `logs` (93),
`dashboards-and-notebooks` (46), `log-monitoring` (43), `dashboards-classic` (26),
`notifications-and-alerting` (16), `metrics` (15), `smartscape` (12),
`alerting-and-notifications` (7), `explorer` (3), `metrics-classic` (3)

**`whats-new/`** — `dynatrace-api` (45), `saas` (44), `dynatrace-operator` (24),
`activegate` (22), `oneagent` (21), `oneagent-mobile` (10), `edgeconnect` (7),
`technology` (2), `documentation` (1), `zremote` (1)

**`manage/`** — `identity-access-management` (56), `data-privacy-and-security` (25),
`account-management` (18), `network-zones` (15), `segments` (11), `tags-and-metadata` (8),
`tags` (6), `upgrade-guide-landing-page` (3), `settings` (1)

**`platform/`** — `grail` (73), `openpipeline` (52), `oneagent` (4), `upgrade` (1)

**`secure/`** — `threat-observability` (35), `application-security` (22), `use-cases` (20),
`investigations` (12), `vulnerabilities` (7), `xspm` (5), `threats-and-exploits` (4)

**`deliver/`** — `configuration-as-code` (39), `ownership` (10),
`site-reliability-guardian` (10), `pipeline-observability-sdlc-events` (7),
`service-level-objectives` (7), `service-level-objectives-classic` (5),
`release-monitoring` (3), `release-monitoring-classic` (3)

**`semantic-dictionary/`** — `model` (254), `changelog` (9), `tags` (6)

**`dynatrace-intelligence/`** — `anomaly-detection` (20), `root-cause-analysis` (12),
`use-cases` (12), `agentic-and-generative-ai` (11), `reference` (6), `problems-app` (4)

**`license/`** — `capabilities` (47), `classic-licensing` (11), `dps-for-hybrid` (1)

**`discover-dynatrace/`** — `get-started` (25)

**`manage-your-costs/`** — `view` (4), `control` (3), `predict` (3), `allocate` (2)

## Where things actually live

The top-level names are not obvious. This is the mapping that matters:

| Looking for | Go to |
|---|---|
| DQL syntax, commands, functions | `platform/grail/dynatrace-query-language` |
| DPL patterns and matchers | `platform/grail/dynatrace-pattern-language` |
| Buckets, tables, views, retention | `platform/grail` |
| OpenPipeline | `platform/openpipeline` |
| **Exact field and entity-type names** | `semantic-dictionary/model` |
| Metric keys and selectors | `analyze-explore-automate/metrics` |
| Logs app | `analyze-explore-automate/logs` |
| Log Monitoring Classic | `analyze-explore-automate/log-monitoring` |
| Dashboards and Notebooks | `analyze-explore-automate/dashboards-and-notebooks` |
| Dashboards Classic | `analyze-explore-automate/dashboards-classic` |
| Workflows / AutomationEngine | `analyze-explore-automate/workflows` |
| Alerting, notifications | `analyze-explore-automate/notifications-and-alerting` |
| Segments (replaces management zones) | `manage/segments` |
| Tags, auto-tagging rules | `manage/tags-and-metadata`, `manage/tags` |
| IAM, ABAC policies, groups, OAuth | `manage/identity-access-management` |
| Network zones | `manage/network-zones` |
| OneAgent deployment | `ingest-from/dynatrace-oneagent` |
| Kubernetes | `ingest-from/setup-on-k8s` |
| OpenTelemetry | `ingest-from/opentelemetry` |
| Extensions | `ingest-from/extensions` |
| AWS / Azure / GCP | `ingest-from/amazon-web-services`, `microsoft-azure-services`, `google-cloud-platform` |
| RUM, session replay, synthetic | `observe/digital-experience` |
| Hosts, processes, K8s monitoring | `observe/infrastructure-observability` |
| Services, traces, profiling | `observe/application-observability` |
| Business events | `observe/business-observability` |
| SLOs, Site Reliability Guardian | `deliver/service-level-objectives`, `deliver/site-reliability-guardian` |
| Monaco, Terraform | `deliver/configuration-as-code` |
| Application Security | `secure/application-security`, `secure/threat-observability` |
| Environment API v1/v2 | `dynatrace-api/environment-api` |
| Settings schemas (`builtin:*`) | `dynatrace-api/environment-api/settings` (466 files) |
| Classic configuration API | `dynatrace-api/configuration-api` |
| Account-level API | `dynatrace-api/account-management-api` |
| DPS rates and capabilities | `license/capabilities` |

## Classic vs latest inside the corpus

Two signals, and neither is complete on its own:

- **Path suffix** — a directory ending `-classic` is legacy: `dashboards-classic`,
  `log-monitoring` (vs `logs`), `rum-classic`, `services-classic`,
  `service-level-objectives-classic`, `metrics-classic`, `synthetic-monitoring` (vs `synthetic`).
- **Frontmatter `generation:`** — `latest` or `classic`, parsed from the page's own first
  bullet. Reliable where present.
  In the **developer** corpus this field means something slightly
  different: it is declared for the whole site rather than read off each page,
  because that site emits no markers. See "The second corpus" below.

`dynatrace-api` is the exception: **1 045 of its 1 148 files carry no generation marker at
all**, because the API reference is not labelled that way. There, infer from the path —
`configuration-api` is Classic configuration, `environment-api/v2` is the newer surface,
`account-management-api` is account-level. Do not tell a user an endpoint is "latest"
because the frontmatter says nothing.

See `classic-vs-latest.md` for the concept mapping.

## Image content is text

2 750 transcription blocks in 949 files of the docs corpus, plus 101 more in 31
files of the developer corpus (see "The second corpus" below). A block sits immediately after the image it
describes, fenced by sentinels:

```
<!-- stage4:start https://dt-cdn.net/images/... -->
(tables of every visible field and value, code fences, ASCII + mermaid for diagrams)
<!-- stage4:end -->
```

This is where a lot of otherwise-unrecorded content lives: complete placeholder lists,
enumerated dropdown options, IAM policy text drawn in figures, endpoint paths that appear
only in diagrams, preset-dashboard tile inventories. If prose says "select one of the
available options" and does not list them, grep the stage4 blocks on that page.

An image with nothing extractable carries a one-line marker instead:

```
<!-- stage4:skip <url> — 24x24 decorative step marker -->
```

`whats-new` is handled differently by design: its images are release-note screenshots whose
value is the pointer, so they carry a labelled skip rather than a transcription.

## Known-bad pages

Before quoting any query, path, code snippet or control name from this corpus, grep
`references/gotchas.md`. Roughly 200 pages contain something that does not work as printed —
and the corpus faithfully reproduces the error, because it is a faithful copy.

## The second corpus: developer.dynatrace.com

`docs.dynatrace.com` is not all of Dynatrace's documentation. App development
lives on a separate domain, and 204 of its pages are mirrored locally:

```
{{DEV_CORPUS}}        205 pages, 1.97M words, harvested 2026-08-06
```

| Subtree | Pages | What it answers |
|---|---:|---|
| `develop/sdks` | 60 | `@dynatrace-sdk/*` package reference, per-version |
| `develop/guides` | 59 | data access, workflows, navigation and intents, security |
| `develop/platform-services` | 20 | platform API URL structure, versioning, per-service reference |
| `develop/reference` | 13 | app manifest, `app.config`, function and runtime limits |
| `develop/extensions` | 12 | Extensions VS Code tooling |
| `develop/test-and-troubleshoot` | 11 | debugging apps, monitoring your own app |
| `quickstart` | 14 | App Toolkit, first app, tutorial chain |
| `release-notes` | 9 | App Toolkit and design system changelogs |
| `plan` | 4 | AppEngine, AppShell, tech radar |

**This is where app function limits live** — memory, payload caps, timeouts,
concurrency — and no amount of grepping the main corpus will produce them.
Search it the same way:

```bash
grep -rn "256 M" {{DEV_CORPUS}} --include=*.md
grep -rl "app function" {{DEV_CORPUS}}/develop --include=*.md
```

**Not harvested: `design/`, 364 pages.** The Strato design system — components,
data visualizations, tokens, icons. It answers "how do I style this React
component", a different job from the rest of this skill. Same command with a
different `--filter` if it is ever wanted.

**Image content is text here too.** Stage 4 ran on 2026-08-06: **101
transcription blocks and 6 recorded skips across 31 files**, every image
adjudicated. Same sentinel format as the docs corpus, so the same grep works:

```bash
grep -rn "stage4:start" {{DEV_CORPUS}} --include=*.md
```

It is worth grepping. Several of those blocks are the only record of something:
15 keyboard shortcuts from one modal, the full dashboard tile-type list with
shortcuts, the six VS Code extension commands, and context menus the prose
describes only as "select any of the available options".

`{{DEV_CORPUS}}/_assets/` holds 13 images that the site inlined as
base64 and the converter had to decode to files. Pages reference them by relative
path. They are part of the corpus, not scratch.

**Three things about this corpus that differ from the main one.**

*`generation` is declared, not measured.* Every page carries
`generation: "latest"`, set by `--generation latest` at conversion time because
the site emits no `Latest Dynatrace` / `Dynatrace Classic` bullets. The claim is
true — AppEngine exists only on the new platform — but it is a domain-level fact,
where the same field in the docs corpus is read off each page.

*17 pages are Classic bridges.* `develop/sdks/client-classic-environment-v1`,
`client-classic-environment-v2` and `platform-services/services/classic-environment-service`
document calling the **Classic** Environment API **from** a latest-platform app.
The page is latest; its subject is Classic. `generation` cannot express that, so
grep the names when a question is about reaching Classic APIs from an app.

*No `lastmod`.* The sitemap carries none, so `--skip-unchanged` does not work
here and there is no per-page age to check, so date-based drift detection
does not apply to this corpus. Staleness has to be judged by re-fetching, not by
reading the frontmatter.

**Units disagree across the two domains.** developer.dynatrace.com says app
functions get 256 **MB**; `license/capabilities/appengine-functions.md` in the
docs corpus says 256 **MiB**.

## Still live-only: community.dynatrace.com

Forum threads with accepted answers, and product ideas. Not mirrored, and the
weakest of the three sources — read `gotchas.md` DT78 and DT80 before
attributing anything found there to Dynatrace. Returns HTTP 403 intermittently
to non-browser clients; retry with a browser User-Agent and backoff.

**Say where each citation came from** — docs corpus, developer corpus, live
page, or forum thread. They carry different weight, and blending them is how a
forum opinion ends up quoted as documented fact.

## Reaching the live site

Base URL for every path above: `https://docs.dynatrace.com/docs/<path>`. Pages are
server-rendered, so plain text comes out without a browser:

```bash
scripts/dtfetch.sh platform/grail/dynatrace-query-language/functions
# → scripts/cache/platform__grail__dynatrace-query-language__functions.txt
```

The live sitemap, if the section counts above need rebuilding:

```bash
curl -sS https://docs.dynatrace.com/docs/sitemap.xml \
  | grep -o '<loc>[^<]*' | sed 's|<loc>https://docs.dynatrace.com/docs/||'
```

Note the top-level `https://docs.dynatrace.com/sitemap.xml` is a `<sitemapindex>` with two
children; `/docs/sitemap.xml` is the one holding the page list.

## How stale is any given page

Every page carries `lastmod`, and the distribution across sections is uneven
enough to be a working rule. Measured over the whole corpus on 2026-08-05:

| Section | Files | Median age | Untouched 2+ years |
|---|---:|---:|---:|
| `dynatrace-api` | 1 148 | **3.4 years** | **73%** |
| `ingest-from` | 917 | 2.5 years | 54% |
| `manage` | 155 | 1.0 year | 39% |
| `discover-dynatrace` | 29 | 0.9 years | 38% |
| `deliver` | 97 | 0.8 years | 28% |
| `analyze-explore-automate` | 370 | 0.7 years | 27% |
| `platform` | 136 | 0.7 years | 32% |
| `license` | 67 | 0.6 years | 15% |
| `observe` | 804 | 0.6 years | 30% |
| `dynatrace-intelligence` | 71 | 0.4 years | 14% |
| `secure` | 113 | 0.4 years | 8% |
| `manage-your-costs` | 17 | 0.2 years | 6% |
| **`semantic-dictionary`** | 274 | **0.1 years** | **0%** |

Corpus-wide: median age 1 year, **42% of pages untouched for 2 or more years**.

**The rule this produces.** Most documented contradictions are not two valid
views, and they are usually not a Classic-against-latest split either. They are
one maintained page disagreeing with one abandoned page.

- **The Semantic Dictionary is generated and republished every release** — 0%
  stale, median age six weeks. When the dictionary and a prose page disagree
  about a field name, type or deprecation, **the dictionary wins**.
- **`dynatrace-api` is the opposite extreme**: the largest section and the least
  maintained, most of it apparently generated once from a specification and left
  alone. Two thirds of it predates Grail.
- **Check `lastmod` before quoting prose**, especially anything under
  `dynatrace-api` or `ingest-from`. A 2020 page describing an entity type says
  nothing about whether that type still exists.

Two failure modes do *not* fit the pattern, so do not over-apply it:

- **Same-cycle desync.** `advanced-tracing-analytics` (2026-07-14) uses
  `request.is_root_span`; `semantic-dictionary/model/trace` deprecated it on
  2026-07-16. Two days apart — the dictionary simply moves first.
- **A current page that missed a change.** `platform/openpipeline/reference/api-ingestion-reference`
  (2026-06-29) still omits the JSON Lines mime types announced in sprint 318
  (2026-02-05). Recent `lastmod` is not proof of completeness.

Regenerate the table:

```bash
grep -rh "^lastmod:" {{DOCS_CORPUS}} --include=*.md | sort | uniq -c
```

## Freshness

Snapshot 2026-08-05, in sync with the live sitemap on that date (0 new, 0 changed,
0 removed). Upstream changes ~400–500 pages a month. The corpus is its own state file: each
page carries `source_url` and `lastmod`, so changed, new and removed pages are all derivable
from a fresh sitemap. The procedure your corpus was built with should be
recorded alongside it; this skill reads a corpus but does not build one.

If a question turns on behaviour that changed recently, check `lastmod` on the page being
quoted, and fall back to `dtfetch.sh` when it looks stale.

## Other reports in `_reports/`

| File | What it is |
|---|---|
| `discrepancies-*.md` (6) | the raw findings behind `gotchas.md`, per section |
| `IMAGES.md` | every image reference grouped by article, with MD5 and Stage 4 state |
| `image-index.tsv` | the machine-readable twin, for change detection |
| `UPDATE-PLAN.md` | how to refresh the corpus and what breaks |
| `RESUME.md` | build history and current state |
