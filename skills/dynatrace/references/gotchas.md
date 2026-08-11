# Dynatrace doc gotchas — where the documentation disagrees with the product

Roughly 200 verified cases in which `docs.dynatrace.com` contradicts the product it
documents. Every one was found by reading the page's own screenshots against its own
prose during a full vision pass over 2 259 unique images, so each entry names both
sides: what the documentation says, and what the product actually shows.

**This file exists to be grepped before answering, not read end to end.**

```bash
grep -n "grant_type" references/gotchas.md          # the identifier the user quoted
grep -nE "^## DT[0-9]+\." references/gotchas.md     # list every entry
grep -n "^### Class A" references/gotchas.md        # the ones that break execution
```

Every entry carries the literal string from **both** sides, so a grep finds it whether
the user quotes the docs or the UI.

## Contents

85 numbered entries. Grep the identifier the user quoted (`grep -n "calc:service" gotchas.md`); every entry carries the literal string from both the docs and the product, so a hit lands whichever form was typed.

- **Class A — the documented thing does not work** (DT1-DT24, 24 entries)
- **Class B — the control is not called what the docs call it** (DT25-DT44, 20 entries)
- **Class C — the figure teaches something the prose does not** (DT45-DT57, 13 entries)
- **Class D — renames that reached only one side** (DT58-DT66, 9 entries)
- **Class E — product typos, reproduce verbatim** (DT67-DT70, 4 entries)
- **Class F — caveats about the documentation itself** (DT71-DT85, 15 entries)

## How to use a hit

If a grep hits, say so plainly and give the working form. Do not silently "correct" the
user — they are usually quoting the official page, and telling them *why* it fails is the
answer. If a grep misses, the corpus at `{{DOCS_CORPUS}}` is the next stop
(see `corpus-map.md`); a miss is not evidence the page is correct.

## Severity classes

| Class | Meaning | Entries |
|---|---|---|
| **A** | Copy-paste fails: the documented query, path, code or identifier does not work | DT1–DT24 |
| **B** | Navigation fails: the control or page has a different name than documented | DT25–DT44 |
| **C** | The figure teaches something the prose does not say, or says the opposite | DT45–DT57 |
| **D** | A rename reached only one side; search by both names | DT58–DT66 |
| **E** | Product-UI typos — reproduce verbatim, never "fix" | DT67–DT70 |
| **F** | Caveats about the docs themselves, not about the product | DT71–DT76 |

---

# Class A — the documented thing does not work

## DT1. `security.events` is drawn as `vents.security` in the Amazon ECR figure

- **Page:** `secure/threat-observability` — Amazon ECR ingest diagram
- **Figure shows:** `/platform/ingest/v1/vents.security`
- **Correct:** `/platform/ingest/v1/security.events` — as drawn in the sibling GuardDuty and Security Hub figures
- Missing `e`, and the two words transposed. Copying the path from the picture gives a 404.
  The most directly harmful defect found anywhere in the corpus.

## DT2. `query_name` is published as `uery_name`

- **Page:** `secure/…/operationalize-query-results`
- **Documented query:** `| fields srcaddr, uery_name, answer=answers[Rdata]`
- **Correct:** `query_name`
- The page's own screenshot proves the consequence — the result column header reads
  `uery_name (undefined)` and every value is `null`. The error is in the prose *and* the
  image, so it shipped broken.

## DT3. DQL field names are case-sensitive; eight business-analytics examples get the case wrong

- **Page:** `observe/business-observability/bo-analysis` and siblings
- **Prose uses:** `amount`, `price`, `accountId`
- **Screens use:** `Amount`, `Price`, `` `Account ID` ``
- Affects at least eight worked examples: `avg(Price)`, `sum(Amount)`, `bin(Amount, 2000)`,
  `` `Card Type` ``, `isNotNull(Price)`. One of the two forms returns nothing; the screens are
  the working side.

## DT4. The "dollar volume" example filters sells, not buys

- **Page:** `observe/business-observability/bo-analysis`
- **Prose:** filters `com.easytrade.quick-buy` / `com.easytrade.long-buy`, `avg(amount*price)`
- **Screen:** filters `com.easytrade.nginx.long-sell` / `.quick-sell`, `avg(Amount*Price)`
- Same heading, different metric. The largest single divergence in that section.

## DT5. `calc:service:` should be `calc:service.`

- **Page:** `deliver/service-level-objectives-classic/slo-definition-configuration-examples.md` step 3
- **Prose:** metric ID `calc:service:fastcreditcardrequests` (colon)
- **UI field "Metric key for API usage":** `calc:service.fastcreditcardrequests` (dot)

## DT6. Multi-value `in()` needs braces

- **Page:** `deliver/service-level-objective-upgrade-classic.md`
- **Prose:** omits the braces
- **Screen:** `| filter in(name, {"astroshop-checkoutservice", …})`
- The braced array form is the valid one.

## DT7. Three workflow tasks are documented without the execution ID

- **Page:** `deliver/self-service-kubernetes-use-case.md` — `parse_predictions`, `find_manifest`,
  `create_suggestion_applied_event`
- **Prose:** `export default async function () {` … `await execution();`
- **Screens:** `export default async function ({execution_id})` … `await execution(execution_id)`
- The documented form never receives the ID. Same divergence appears in
  `analyze-explore-automate` workflow pages (`count-fields-workflow-step`,
  `check-and-alert-step`).

## DT8. Steps 7 and 8 of the Kubernetes self-service tutorial have their field lists swapped

- **Page:** `deliver/self-service-kubernetes-use-case.md`
- `update_manifest` (GitHub *Create or replace file*) actually takes
  Source branch = `find_manifest.defaultBranch`,
  Branch = `apply-davis-predictions-{{apply_suggestions.time}}`, plus File path / content /
  commit message.
- `create_pull_request` actually takes Source branch = `apply-davis-predictions-…`,
  Target branch = `find_manifest.defaultBranch`, plus PR title / description.
- The prose assigns each set to the other task. Following it configures both wrongly.

## DT9. Workflow variable chips use `_`, not `.`

- **Page:** same
- **Prose:** `find.manifest.owner`, `.repository`, `.filePath`, `.defaultBranch`
- **UI:** `find_manifest.…` — underscore, matching the task name

## DT10. OAuth POST parameter is `grant_type`, not `grant_Type`

- **Page:** `observe/digital-experience/rum-classic` HTTP-monitor OAuth setup
- **Prose:** `grant_Type`
- **UI / OAuth 2.0 spec:** `grant_type`

## DT11. The generated OAuth object is `bearerToken-2`, not `bearToken-2`

- **Page:** same
- **Prose:** `bearToken-2`
- **Generated script:** `bearerToken-2`

## DT12. NAM figures use deprecated dimension names throughout

- **Pages:** `observe/…/networks/nam-monitor-metrics.md` and `nam-monitor-metrics-latest.md`
- **Figures use:** `multi_protocol.request.target_address`,
  `multi_protocol.request.tcp_port_number`, `multi_protocol.result.status`
- **Current:** `request.target_address`, `result.status.message`
- Here the *images* are stale and the prose is right — the reverse of the usual direction.
  Affects every NAM figure in the section.

## DT13. `timeseries count(metric.key, scalar: true)` is a placeholder, not a query

- **Page:** `observe/infrastructure-observability/…notebooks`
- **Prose:** the literal token `metric.key`
- **Screen:** a real key, e.g.
  `timeseries count(com.dynatrace.extension.network_device.if.status, scalar: true)`
- The prose form does not execute.

## DT14. The action-naming regex is published without its leading `.*` and with `category` truncated

- **Page:** `observe/digital-experience/rum-classic` — `action-naming-examples-3`
- **Prose:** `.*/api/request/.*/contact?category=UFO`
- **Screen:** `/api/request/.*/contact?categor=UFO`
- Also: naming pattern is `Customer contact request for UFOs` in the image vs
  `Customer Contact Request for UFO` in the prose, and the input is `pageUrlPath`.

## DT15. The request-attribute example needs `Journey:` with no space

- **Page:** `observe/application-observability/…request attributes`
- **Prose:** values beginning `Journey :` (space before colon)
- **Screen + its own regex:** `Journey:` — `(?>Journey:)`
- The space breaks the match.

## DT16. `fieldsRemove` field names are quoted in the working form

- **Page:** `analyze-explore-automate/metrics/best-practices-metrics.md`
- **Prose:** `fieldsRemove user.id, request.id`
- **Screen:** `fieldsRemove "user.id", "request.id"`

## DT17. The metric-selector conversion example omits `interval` and reorders the pipe

- **Page:** `analyze-explore-automate/metrics/metric-selector-conversion.md`
- **Prose:** `timeseries usage = avg(dt.host.cpu.usage), by:{ dt.entity.host } | sort … | fieldsAdd … | limit 20`
- **Screen:** adds `interval: 10m`, and `fieldsAdd` comes **before** `sort`

## DT18. The 5xx migration example applies no filter at all

- **Page:** `analyze-explore-automate/metrics/runtime-metric-migration.md`
- **Prose:** `sum(...)` filtered `500 <= status and status <= 599`
- **Screen:** no filter, aggregation `avg`, split **by** `status` — all four series
  (200 / 302 / 404 / 500) rendered

## DT19. The syslog matcher has a second clause the prose omits

- **Page:** `analyze-explore-automate/logs/lma-log-ingestion-syslog.md`
- **Prose quotes:** `matchesValue(dt.openpipeline.source, "extension:syslog")`
- **Dialog shows:** that **or** `matchesValue(log.source, "/var/log/syslog")`

## DT20. Compliance use-case field names do not exist as written

- **Page:** `analyze-explore-automate/…compliance-use-case-2-scenario-2`
- **Prose:** `Affected.patient patient_id`, `actor.id`, `affected_case`
- **Record:** `affected.patient`, `actor`, `affected.case` — no `patient_id`, no `affected_case`
- `compliance-use-case-3-scenario-2-1`: prose `Acquirer MerchantReferenceNo` /
  `AcquireMerchantID` vs record `acquirerMerchantReferenceNo` / `acquirerMerchantId`.
  That record also renders its `url` as `http=//api-gateway.svc=8080/trprc/2.0/sale`
  (equals signs where colons belong).

## DT21. The synthetic availability query is documented with extra `by:` dimensions

- **Page:** `observe/digital-experience/synthetic` — included-maintenance example
- **Prose:** `by:{dt.entity.http_check, dt.maintenance_window_ids, interpolated}`
- **Screen:** `by:{dt.entity.http_check}` only, with `av =` and
  `| fields avgAV=arrayAvg(av)`

## DT22. `fetch events` in the data-volume example needs an explicit window

- **Page:** `observe/data-observability/…detect-data-volume-drops`
- **Prose:** `fetch events`
- **Screen:** `fetch events, from:now()-1h, to:now()`

## DT23. Cordova install command names the old package

- **Page:** `observe/digital-experience/…apache-cordova.md`
- **Screen:** `cordova plugin add dynatrace-cordova-plugin --save`
- **Current:** `@dynatrace/cordova-plugin`
- The same figure calls the button "Download dynatrace.config" where the prose says
  "Download dynatrace.config.js".

## DT24. The logcat filter in the image carries an extra term and an unmatched quote

- **Page:** `observe/digital-experience/…mobile`
- **Prose:** `tag~:^dtx|^caa`
- **Screen:** `package:mine tag~:^dtx|^caa"`

---

# Class B — the control is not called what the docs call it

## DT25. "Metric events" is now "Custom events for alerting"

- **Pages:** `ingest-from/amazon-web-services/aws-set-up-metric-events-for-alerting.md`,
  the Azure equivalent, and `analyze-explore-automate` alerting pages
- **Prose:** Settings > Anomaly detection > **Metric events**
- **UI:** **Custom events for alerting** (breadcrumb and page title)

## DT26. "Manage services" / "Services" is "Manage supporting services"

- **Pages:** AWS and Azure metric-event setup
- **Prose:** "Select **Manage services**" / "Go to **Services** → **Add service**"
- **UI:** breadcrumb reads **Manage supporting services**; no "Services" tab exists

## DT27. Cloud metric-event step numbering does not match the UI

- **Page:** `aws-set-up-metric-events-for-alerting.md`
- **Prose steps:** 1 create / 2 configure / 3 disable
- **UI steps:** 1 Create recommended / 2 Enable recommended / 3 Adjust recommended
- The image attached to prose step 2 shows UI step 3.

## DT28. Tag-rule save button is "Create rule"

- **Page:** `tags-and-management-zones-aws.md` step 6
- **Prose:** "Select **Save changes**"
- **UI:** **Create rule**

## DT29. Browser-monitor wizard button is "Select frequency and locations"

- **Pages:** `create-a-single-url-browser-monitor.md` step 6,
  `record-a-browser-clickpath.md` step 7
- **Prose:** **Next**
- **UI:** **Select frequency and locations** (affects three captures)

## DT30. Segment button is singular

- **Page:** `secure/vulnerabilities/manage-results`
- **Prose:** "select **Segments**"
- **UI:** **+ Segment**

## DT31. Evidence presets are named with the `IPs` suffix

- **Pages:** `secure/…/manage-evidence`, `threat-hunting` step 7
- **Prose:** presets **Safe** / **Suspicious**
- **Menu:** **Safe IPs** / **Suspicious IPs** (and the panel itself reverses this — see DT73)

## DT32. Pipeline is called "Custom vulnerability findings" in the dialog

- **Page:** `secure/…/ingest-and-process`
- **Prose:** pipeline **Custom security findings**
- **Dialog:** **Custom vulnerability findings**
- The same screenshot titles it `Custom security findings` while its ID is
  `pipeline_Custom_vulnerability_findings_9495` — the rename reached the label, not the identifier.

## DT33. Maintenance windows: "Add", not "Create"

- **Page:** `analyze-explore-automate/…maintenance windows`
- **Prose:** `Settings > Maintenance windows > Monitoring, alerting, and availability`, then
  "**Create** maintenance window"
- **UI:** plain Maintenance windows page with an **Add maintenance window** button

## DT34. Notification-integration field names

| Page | Prose | UI |
|---|---|---|
| `notifications/…/servicenow` | "Problem to Incident **Transform** Map" | "Problem to Incident **Transformation** Map" |
| `notifications/…/jira` | "Jira endpoint **URI**" | "Jira endpoint **URL**" |
| `upgrade-guide-alert-notification.md` step 3 | `ProblemDetailsJSON` | `{ProblemDetailsJSONv2}` |

## DT35. Workflow notifications are toggled by the bell icon

- **Page:** `analyze-explore-automate/workflows/workflows-notifications.md`
- **Prose:** "Select ⋮ > **Turn on notifications**"
- **UI:** the highlighted control is the bell icon; no overflow menu is open

## DT36. Log-pattern feedback buttons

- **Page:** `analyze-explore-automate/logs/patterns-preview`
- **Prose:** "I'm satisfied" / "I'm not satisfied"
- **UI:** `Helpful` / `Not helpful`

## DT37. Table-visualization option is singular

- **Page:** `analyze-explore-automate/…visualization-table.md`
- **Prose:** "We selected **Values**"
- **UI:** the option is `Value`; `Row values` is a separate option
- Same page: the prose says a yellow row marker at or above 15; the swatch is orange.

## DT38. "Top database statements" control is "View database statements"

- **Page:** `observe/application-observability/…top-database-statements`
- **Prose:** select **Top database statements**
- **UI:** control reads `View database statements`; node tooltip reads `Statements`.
  The string "Top database statements" does not appear.

## DT39. HTTP-monitor execution link

- **Page:** `observe/…/synthetic-details-for-http-monitors-classic.md`
- **Prose:** **Analyze execution details**
- **UI (three captures):** **Analyze last execution**

## DT40. Capture-properties navigation path is obsolete

- **Page:** `observe/digital-experience/rum` — properties capture
- **Prose:** `Experience Vitals > Overview > Web > frontend > Settings tab > Capture properties`
- **UI:** Settings app — `Collect and capture > Data scope and enrichment > Capture properties`,
  with a `Web frontend` scope selector. The dialog is titled **Create event property**, not
  "New property".

## DT41. Account Management label drift

| Page | Prose | UI |
|---|---|---|
| credential vault | "Turn on local playback…" | "Enable local playback of Synthetic browser monitors without entering credentials" |
| DPS cost summary | "Cost and usage" | "Cost and usage details" |
| DPS environment analysis | "Environment cost and usage analysis" | "Capability cost and usage analysis" |
| notification center | filter "Capability" | "Capabilities" |
| classic license usage | bar colours Blue / Brown / Red | legend: "Consuming / Consuming overages / Overage amount exceeded" |
| cost management | three tabs (Cost Allocation, Budget alerts, Cost monitors) | only **Cost allocation** visible |
| cost management | allowlists for `dt.cost.costcenter` **and** `dt.cost.product` | only the Cost center allow list |

The notification-center capture shows **Entitlements** in the top nav where the sibling
audit-log capture shows **Contracts**. The text does not say which is current.

## DT42. Legacy SAML group field

- **Page:** `manage/identity-access-management` (legacy group management)
- **Prose:** "SAML Group Attribute Value"
- **UI:** **Security group claim name** (value `DynatraceAccountAdmin` matches)

## DT43. Case-sensitive filter values in the UI

- `secure/…/monitor-sign-in-activity` — prose filters Product for `Azure`; the dropdown value
  is lowercase `azure`.
- `secure/…/monitor-sign-in-activity` — prose "Top 10 addresses by failed sign-in attempts";
  tile reads "Top 10 **IP** addresses…".
- `observe/…/user-sessions` — prose filters `User tag: Zara`; the page shows lowercase `zara`
  and the only chip present is `Application type: Mobile`.
- `dynatrace-api` / `containerized-locations.md` — API Explorer shows `{locationId}`; the prose
  writes `{LocationId}`.

## DT44. Azure log-forwarder blade is one portal generation behind

- **Page:** `ingest-from/microsoft-azure-services/set-up-log-forwarder-azure.md`
- **Prose:** "go to **Environment variables**"
- **Screen:** the older **Settings > Configuration** blade with the "Add/Edit application
  setting" panel

---

# Class C — the figure teaches something the prose does not

## DT45. The ABAC diagram has its column headers swapped

- **Page:** `manage/identity-access-management/access-concepts.md`
- In the **Resources** panel, the column headed *Attributes* lists
  `read` / `write` / `admin` / `action A` / `action B`, and the column headed *Actions* lists
  `extension-name` / `host` / `host-group` / `schema-id` / `schema-group` / `project` /
  `stage` / `service` / `attrib A` / `attrib B`.
- The prose describes the correct arrangement. The defect is in the figure — the one people
  open to learn the permission model.

## DT46. Federation Discovery: the diagram documents a resolution step the prose omits

- **Pages:** `manage/…/access-saml/federation-concepts.md`, `identity-concepts.md`
- **Diagram chain:** environment federated domain → **account federated domain** →
  account default federation → global / credentials
- **Prose list:** omits the account-federated-domain step and orders the rest differently
- This is the order in which a login resolves to an identity provider, so the missing step is
  behavioural, not cosmetic.

## DT47. The rule-scope hierarchy has four levels, not three — confirmed twice independently

- **Pages:** `analyze-explore-automate/log-monitoring/…timestamp-configuration.md`,
  `logs/…lma-timestamp-configuration.md`, `logs/…log-storage`
- **Prose:** "Three hierarchy scopes are supported: host, host group, and environment"
- **Figures:** four, with **Kubernetes cluster** inserted second — Host (1) → Kubernetes
  cluster (2) → Host group (3) → Environment (4)
- Priority order decides which rule wins.

## DT48. Session-replay masking is documented backwards

- **Pages:** `observe/digital-experience/…url-exclusion-and-masking.md`,
  `configure-session-replay-web.md`
- **Prose:** numeric input masked as zeros (`0000`), non-numeric as asterisks
- **Screen:** the digits `123` are masked as `***`

## DT49. Three wrong illustrations, entire

- `analyze-explore-automate/logs/lma-send-syslogs-via-fluentd.md` — the figure named
  `Stream_syslog_to_Dynatrace_with_Fluentd` is **the NetFlow diagram** (Cisco device, Juniper
  device, NetFlow record source, NetFlow Input plugin). No syslog wording anywhere.
- `logs/…/log-storage` — every box is labelled "timestamp rule", but the page documents log
  **ingest** rules (`builtin:logmonitoring.log-storage-settings`).
- `observe/…/source-map-support-for-javascript-error-analysis.md` — "the following image
  depicts a minified JavaScript file"; the image contains no source at all.

## DT50. Wrong illustration for the caption — the rest

| Page | Caption promises | Image shows |
|---|---|---|
| `observe/…/service-flow-metrics.md` | `easyTravel-Business`, "8,490 of 127,000" calls | `JourneyService`, **28.2k of 455k** |
| `observe/…/user-properties` (4 images) | "our easyTravel sample **web** application" | **Mobile app settings** for `easyTravel Mobile` |
| `observe/…/mobile exclusion rules` | a rule ignoring `401 Unauthorized` | `429, 505-507`, for a different app |
| `observe/…/kubernetes-app.md` | "1 node out of 5 is unhealthy" | `Nodes ● 2`, no unhealthy count |
| `secure/investigations.md` | selecting an IP range and building a DQL filter | one IP added to an evidence list; the DQL behaviour is on the *previous* image |
| `secure/…/automated-threat-alert-triaging` | "Customize the DQL query action" | a canvas with no DQL-query action; the DQL belongs to the event trigger's filter |
| `secure/…/ingest-microsoft-entra-id.md` | two ingest options documented | only Option 2 (Azure Native Dynatrace Service) drawn |
| `deliver/release-validation-automated.md` | "a workflow for an SRG" | the **All guardians** overview page |
| `analyze-explore-automate/dashboards-new.md` | CPU-per-host chart with a red threshold bar | single series `avg(dt.host.disk.write_time)`, green band |
| `analyze-explore-automate/compliance-use-case-2-scenario-1` | "Log example from online patient portal" | the e-commerce demo (`cartservice`, `checkoutservice`, …) |

## DT51. The data-volume-drop tutorial pictures a different analyzer and a different trigger

- **Page:** `observe/data-observability/…detect-data-volume-drops.md`
- The panel is an **anomaly-detection** analyzer (Detection quantile, Threshold 20); the steps
  describe **Generic Forecast Analysis** (Coverage probability, Data points to predict).
- The trigger shown is a **Time interval** ("Run every 60 mins"); the steps instruct a
  **Cron schedule** `0 * * * *`.
- Start/end read `-72h` / `-1h` against the prose's `now-72h` / `now-1h`.
- Same page: prose claims "three distinct values for `dt.entity.host`" where the image shows
  `1 record`; and "75 % of records from a single host" where the top bucket is `null` at 71 %
  and the largest real host is 22 %.

## DT52. Fields and controls that do not exist as described

- `observe/…/synthetic-details-for-http-monitors-classic.md` — the Properties card is
  documented as showing DEM-unit consumption; it has
  `Number of HTTP requests in timeframe: 288` and no DEM row.
- `observe/…/configure-browser-monitors.md` — says nine Advanced setup controls appear as
  "Additional options" at creation; the form shows six (client certificates, ignore status
  codes and deprecated JS frameworks are absent).
- `observe/…/user-action-naming` — the UI has a third tab, **Naming rules for custom actions**,
  the prose never mentions.
- `observe/…/global-event-capture` — the panel offers a `Blur` wrapper missing from the page's
  list of interaction types, and splits types unevenly between the two capture groups (only
  `MouseUp` and `Click` appear in both).
- `observe/…/session-details` — prose lists chips "action type, Apdex rating, error type,
  conversion goal"; the image has **Rage click: Yes** and neither error type nor conversion goal.
- `observe/…/dashboards` — prose "two of the three web vitals, FID and LCP"; the Web vitals
  section holds three tiles: FID, **FCP**, LCP.
- `xspm/review-findings` — the step describes an expanded System filter listing SPM-enabled
  systems; the selector is collapsed at `All systems (4)`.

## DT53. Stale counts

- `analyze-explore-automate/logs/lma-openpipeline.md` — the figure
  `Routing_the_logs_through_OpenPipeline` shows **5** stages (Processing → Metric extraction →
  Data extraction → Permissions → Storage); the table beneath it documents **11**, adding
  Smartscape Node/Edge Extraction, Davis, Cost allocation and Product allocation.
- `logs/…/log-errors-pipeline-example` — Event properties table lists 6; the screenshot shows
  8, adding `event.name` and `event.description`.
- `workflows/…/running.md` — prose lists five title-section controls including "rerun the last
  execution" and "open the execution history"; only **Edit workflow**, `Cancel`, `Refresh`
  and `⋮` are visible.
- `monitor-azure-hdinsight.md` — prose lists 3 service-technology rules; the screenshot shows
  4, adding `Apache Hadoop YARN`.

## DT54. `dql-examples.md` screenshots predate their own queries

- **Page:** `secure/threat-observability/dql-examples.md` — systematically stale
- two grids expose `vulnerability.parent.resolution.status` and
  `vulnerability.parent.mute.status`, which the documented `summarize` never emits
- one shows `affected_entity.vulnerable_functions` / `# Function usages` where the query
  projects `vulnerable_function` / `Usages`
- one shows `dt.entity.host` / `Name` / `Owner team` where the query projects
  `entity_id` / `Host` / `Team`
- one carries an extra **Owner team** column
- "Top 10 process groups" runs `| limit 10` but the capture shows `5 records`
- elsewhere a table is not sorted descending (174 / 156 / 132 / 159) although its query ends
  ``| sort `count()` desc``

## DT55. A tutorial that sends you after the wrong pod

- **Page:** `secure/…/threat-hunting.md`
- One capture holds `172.31.3.52` as the **Suspicious pod**; the prose and three sibling
  captures give `172.31.29.138`. `172.31.3.52` appears elsewhere only as a *destination*.
- Same page: a query declares `timeframe: "05:00:00Z/06:00:00Z"` while the result bar renders
  `07:00:00 – 08:00:00` — same instant, UTC vs local, but it reads as a different result.

## DT56. Metric-level contradictions in the AWS presets

- **Amazon Lex** — dashboard legend reads `RuntimeSucessfulReq…` (one `c`); the metric table
  has `RuntimeSuccessfulRequestLatency`. A name copied from the dashboard will not resolve.
- **Amazon DocumentDB** — the *Available metrics* table gives `VolumeReadIOPs` /
  `VolumeWriteIOPs` with Statistics `Average`; the preset dashboard charts them as `Sum`.
- **Amazon EC2 API** — the tile **Client errors by region** is bound to
  `ServerErrors Sum (by Region)`, the same series as the Server errors section.
- **Elastic Transcoder** — the *Available metrics* table's description column is offset by one
  row against its metric names, leaving `BilledHDOutput` / `BilledSDOutput` Sum rows blank.

## DT57. Thresholds and units that do not line up

- private synthetic locations: legend says green is "not greater than 80 %", the prose table
  says "below 80 %" — they differ at exactly 80 %.
- `Duration p95` `5.82 s` is quoted in the prose as "the slow response time"; **Avg duration**
  is `5.16 s`.
- a freshness column renders `4 ns` / `3 ns` where the prose speaks of minutes.
- `analyze-explore-automate/…visualization-chart-area.md` — prose "Green from 0 % to 75 %";
  the screen reads `Good: 9 – 75%`.
- `license/capabilities/app-infra-observability/full-stack-monitoring.md` — prose "1.58 TiB
  over the past 30 days"; the screenshot is a six-hour window showing `10.7 GiB`.
- `license/classic-licensing/davis-data-units/metric-cost-calculation.md` — prose describes a
  three-series intraday chart with the limit exceeded 09:30–10:45; the image is a month view
  with two series and no exceedance. The file is named `ddus-replacement3`.
- `manage-your-costs` (Traces – Retain) — the Y axis reads `GiB scanned`, the unit for Traces
  **Query**; the page states Retain is measured in **GiB-day**.

---

# Class D — renames that reached only one side

Search by **both** names; the corpus contains pages using each.

## DT58. Davis AI → Dynatrace Intelligence

`deliver/self-service-kubernetes-use-case.md` was rebranded; its screenshots were not. Six
strings differ, several of which the reader types verbatim:

| What | Prose | Screenshot |
|---|---|---|
| PR title | `Apply suggestions predicted by Dynatrace Intelligence` | `…by Dynatrace Davis AI` |
| `create_scaling_events` title | `Suggesting to Scale Because of Dynatrace Intelligence Predictions` | `…Because of Davis AI Predictions` |
| `create_suggestion_applied_event` title | `Applied Scaling Suggestion Because of Dynatrace Intelligence Prediction` | `…Because of Davis AI Prediction` |
| `add_vertical_scaling_suggestions` | `Dynatrace Intelligence has detected that the ${workload.kind}…` | `Davis AI has detected…` |
| Workflow names | **Predict Resource Usage**, **Commit Dynatrace Intelligence Prediction** | **Predict Kubernetes Resource Usage [Predictive Kubernetes Scaling]**, **Commit Davis Prediction […]** |
| Annotation prefix | `predictive-kubernetes-scaling.observability-labs.dynatrace.com/…` | `predictive-labs.dynatrace.com/…` |

Also: `dashboards-new.md` prose says "Davis AI analysis" / "Davis AI analysis chart"; the UI
reads `AI analysis` / `AI analysis chart`. A `secure` figure labels a node "Dynatrace CoPilot"
where the prose says "the Dynatrace Intelligence generative AI workflow action".

## DT59. PurePath → Trace

- Image: `52 PurePaths`, button `View PurePath`
- Prose: **Traces**, **View trace**

## DT60. Security Investigator → Investigations

Every Investigations screenshot across `secure/use-cases`, `secure/investigations` and
`threat-hunting` still shows the app titled **Security Investigator**; the prose calls it
**Investigations**. Systematic, not per-page.

## DT61. Basic authentication → HTTP authentication

- Screenshot section: **Basic authentication** / **Enable basic authentication**
- Prose (`browser-clickpath-events.md`, `configure-browser-monitors.md`): **Enable HTTP
  authentication**, with basic listed as one of four methods (basic, digest, NTLM, Negotiate)

## DT62. Message processing → Messaging, Outbound requests → Outbound calls

Older service-detail captures use the first pair; newer ones use the second. Searching by one
name will not find pages using the other.

## DT63. Azure Spring Cloud → Azure Spring Apps

The dashboard title is `Azure Spring Cloud`; the page is *Monitor Azure Spring Apps*.

## DT64. AWS ↔ Amazon prefix swap in the shipped preset dashboards

One upstream defect class, not fifteen typos. The direction is inconsistent:

| Service | Dashboard says | Docs say |
|---|---|---|
| AppStream | `AWS AppStream 2.0` | Amazon AppStream 2.0 |
| Route 53 Resolver | `AWS Route53Resolver` | Amazon Route 53 Resolver |
| Transit Gateway | `Amazon Transit Gateway` | AWS Transit Gateway |
| ECS Container Insights | `AWS ECS ContainerInsights` | Amazon ECS Container Insights |
| MediaPackage | `Amazon MediaPackage Live` | AWS Elemental MediaPackage |
| MediaPackage VOD | `Amazon MediaPackage Video on Demand` | AWS Elemental MediaPackage Video on Demand |
| MediaConvert | `AWS MediaConvert` | AWS Elemental MediaConvert |
| MediaTailor | `AWS Media Tailor` | AWS Elemental MediaTailor |
| WorkSpaces | `AWS Workspaces` | Amazon WorkSpaces |
| CloudSearch | `AWS CloudSearch` | Amazon CloudSearch |
| Elastic Inference | `AWS Elastic Inference` | Amazon Elastic Inference |
| WAF | `Amazon WAFV2` | AWS WAF (WAFv2 is the API version, not the product) |
| GameLift | `Amazon Gamelift` | Amazon GameLift |
| App Service Environment | `Azure App Service Environment` | App Service Environment V2 |

## DT65. Names that differ by one character in worked examples

`easyTravel-Business` vs `easyTravelBusiness` · `Custom Frontend` vs `CustomerFrontend`
(the UI has `eT-demo-1-CustomerFrontend`) · `doaks-prod1-eastus-cassandra` vs
`'doaks-prod1-eastus cassandra'` · `cluster_prod-us-east-1-virginia` vs `-8-virginia`
(same worked example, four figures) · `Easytravel` vs `easyTravel` ·
`easytravel-dynatrace-dev` vs `easytravel dynatrace-dev` ·
`bizevents.easyTrade.*` vs `bizevents.EasyTrade.*` ·
`webshop.checkout_statistics` vs `easytravel.checkout_statistics` (same page, prose
contradicts itself) · `characteristics.has_w3c_navigation_timings` vs
`has_w3c_navigation_timing` (singular, in the diagram) ·
`entity_tags` vs `entity.tags` (Examples 3/7 vs Example 6 on one page).

## DT66. Two W3C timing names, one of which is not W3C

- One Dynatrace figure labels the TLS mark `secureConnectStart`.
- The sibling figure and the "Load action timings" table use `secureConnectionStart`, which is
  the W3C name. `secureConnectStart` does not exist in the specification.

Related: `error-analysis` prose classifies web-app errors as **Request** / Custom /
JavaScript; the UI dimension is **HTTP** / JavaScript / Custom — the value `Request` does not
exist. Affects four images.

And: a synthetic legend labels successful requests `SUCCESS` where the prose says `HEALTHY`.

---

# Class E — product typos, reproduce verbatim

These are in the product UI, confirmed by crop and upscale of the original assets. If a user
quotes one, it is not their mistake — and "fixing" it in a query or a search will fail.

## DT67. Typos in shipped dashboards and panels

`Performace` (Chatbot section header) · `Succesfull workflows` (SWF) · `Incomming Bytes`
(Transit Gateway) · `successfull pull count` (Container Registries — the push tile spells it
correctly) · `Recieved shares` (Data Share, contradicting its own subtitle) ·
`Successfull jobs count` (Data Lake Analytics) · `Starting node nount` and `Unvailable nodes`
(Azure Batch) · `ouput` (Media Services) · `Availibility` (Storage Sync) · `ARP` vs `Arp`
(ExpressRoute) · `Occurences` · `exerience` · `Journey pirce` · `Custommer Connect` ·
`Ingest & Proccess` (Usage-Traces donut legend, correct in the adjacent trend legend).

## DT68. Typos in the Dynatrace UI chrome

`View serivce flow` (five separate captures) · `Placholder(s)` (request-naming rule editor
section header) · `People in your environmetn with the link` (Share dialog) · `non-critcal`
(issue-label hint) · `Application Health Status after Succesfull Sync` (ArgoCD dashboard).

## DT69. Typos inside official diagrams

`Final Penetration Tes Report` · `Coden signing certificate` · `3 party library scan` ·
`Request and evalute` · `Intergrate` · `Singed installer/image` · `Idp` (for IdP) ·
`Dynatrace Saas` (elsewhere `Dynatrace SaaS`) · `Automatic failover & data Redundancy` ·
`Your Dynatrace monitoring environemnt` · `Code & Profilling` (OpenTelemetry diagram) ·
`Synk` / `Synk extension` (should be Snyk) · `Functional Apps` (should be Azure Function app) ·
`Azure Entra ID` (should be Microsoft Entra ID) · `Azure Sentinel` (should be Microsoft
Sentinel) · `applicaton` — this last one is in the *prose*, where the image is correct.

## DT70. Rendering bugs, not typos

- A thread-group list renders `87 %` where the bar width and the descending sort order both
  say `0.87 %`.
- A result header reads `Scanned bytes: 1k MB`.
- One vulnerability shows three figures on one screen: `Critical 10.0` in the prioritization
  table, `Critical 9.9` with a "lowered" arrow in the detail badge, and `CVSS Critical 10`.
- A Sentinel panel reads `Events ingested` as **1k** in the KPI tile and **1.3k** in the
  connection row.
- The Syslog technology bundle lists entries 5 and 6 both as "Syslog loglevel processor".
- QuickStart shows one **Slowest endpoint** finding as `30.71 s` in one panel and
  `30,714 ms (30.71 min)` in another — wrong by a factor of 60.

---

# Class F — caveats about the documentation itself

## DT71. Alt text is unreliable in `observe/digital-experience`

Nine files carry transposed, duplicated or plainly wrong alt text — the single most repeated
defect in that section. Examples: an alt naming a rule editor on an image of a result list;
`Waterfall analysis` on a Settings page; `Scatter plot filters` on two images showing
different behaviour; `User actions` on a Contributors-breakdown tile; nine images on one page
sharing `alt="Multi-dimensional analysis"` while three show the application-overview page; on
`waterfall-analysis.md` seven of nine images share one generic alt. One file's URL **slug**
describes a different chart than its (correct) alt.

Alt text is the only description that survives conversion, so these propagate into the corpus.
Do not trust an alt string as evidence of what a figure shows.

## DT72. A tutorial illustrated from two different incidents

`observe/application-observability/…/problems-logs-traces.md` narrates one continuous
investigation using screenshots from **two** problems: `P-2111406` (2021-11-11) for the first
four, `P-2111554` (2021-11-17) for the rest. The same page writes `P-2205042` where the image
shows `P-22052042`.

The synthetic section has the same defect in miniature: two captures presented as the top and
bottom half of one page report different scope (`2 locations`, Portland + Dublin, 11:30–15:15
vs `Locations: 1`, Platform Private location, 09:50–11:15).

## DT73. Two of our own pages name one panel differently

`filter-logs.md` heads the panel **Evidence collection**; `manage-evidence.md` and the newer
captures in the same section head it **Evidence lists**.

## DT74. Undocumented values recovered only from figures

- `ingest-runecast-analyzer.md` never states the OpenPipeline ingest path
  `/platform/ingest/v1/security.events`; it exists only inside the figure.
- The Runecast modal accepts `openpipeline.events_security` **or**
  `openpipeline.events_security.custom` depending on endpoint; the page lists only the first.
  A superset, not an error.
- The AWS auto-tagging placeholder list (~57 entries) and the process-group naming placeholder
  list (16 entries) exist only as screenshots; no page enumerates them.
- The eight deprecated JavaScript frameworks are named in one image only.
- The notification-type list (Ansible / Custom Integration / Email / Jira / OpsGenie /
  PagerDuty / ServiceNow / Slack / Trello) appears only in a dropdown capture, and that
  capture is itself cut off mid-`Trello` with more entries below.

## DT75. Test and demo data left in shipped assets

**AWS Storage Gateway** preset dashboard is titled **"AWS Storage Gateway foo"**.
Event Grid shows `EVENT-SUUBSCRIPTION-TOPIC-COPY` in three tiles and
`EVENT-SUBSCRIPTION-TOPIC-COPY` in a fourth. PostgreSQL dashboards mix `postgressql-test` and
`demo-postgresql-001`. Power BI lists `DataSets` and `Datasets` as separate dimension values.
Azure Container Instances names two different tiles `Memory usage by container group`.

## DT76. Two Brandfolder URLs serve one file

`Runtime_Vulnerability_Analytics_Consumption-Light_Mode` and
`Full-Stack_Monitoring_Consumption-Light_Mode` are byte-identical (same md5, verified with two
separate requests). The RVA page therefore carries the footnote "Minimum billed memory for a
**Full-Stack** host is 4 GiB". The figures match the RVA prose
(1.0 / 6.375 / 0.5 / 0.125 → 8.0 GiB/h), so no calculation is wrong — but the footnote belongs
to a different product.

Unrelated but in the same class: `set-up-log-forwarder-azure.md` lines 170–176 has a mangled
**Self-monitoring metrics** table — names, descriptions and dimensions shifted across columns,
so `all_requests` reads as having dimension `dynatrace_connectivity_failures`. It reads as
authoritative nonsense.

---


## DT77. A contradiction is usually a stale page, not two valid views

**Both sides look authoritative.** The docs carry no visible age, so a 2020 page
and a 2026 page read the same on screen.

Measured over the whole corpus: median page age **1 year**, but **42% of pages
are untouched for 2 or more years**, and the distribution is lopsided —
`semantic-dictionary` 0% stale, `dynatrace-api` **73%** stale with a median age
of **3.4 years**.

Worked examples, all verified:

- DPL export names: the rule *"may contain only lower or uppercase letters and
  numbers"* is on `log-processing-modifiers` (**2022-05-18**); Dynatrace's own
  examples using underscores — `INT:http_status`, `TIMESTAMP:date_time` — are on
  pages from **2026-06-09**.
- `HOST_GROUP` persists as an entity type in `entity-v2/get-all-entity-types`
  (**2020-04-24**) while `semantic-dictionary/fields` (**2026-07-27**) marks
  `dt.entity.host_group` deprecated in favour of `dt.host_group.id`.
- `post-ingest-logs` (**2021-05-05**) says payload types are defined by the
  **Accept** header in its parameter table, while the same page's intro
  correctly says **Content-Type**.
- `get-event-properties` (**2021-10-07**) documents `filterable` in the schema
  table but omits it from the example response.

**What to do:** when two pages disagree, check `lastmod` on both. The
Semantic Dictionary is regenerated every release and wins on field names, types
and deprecation status. See `corpus-map.md` for the full table.

**Do not over-apply.** Two counter-examples: `advanced-tracing-analytics`
(2026-07-14) uses `request.is_root_span` two days before the dictionary
deprecated it, and `openpipeline/reference/api-ingestion-reference` (2026-06-29)
is recent yet still omits the JSON Lines mime types from sprint 318. A fresh
`lastmod` does not prove completeness.

## DT78. A field the docs tell you not to query, that support tells you to query

`characteristics.classifier` on `user.events` is the documented example. The
Semantic Dictionary
(`semantic-dictionary/model/rum/user-events.md`, line 46) describes it as:

> "The main characteristic of the user event determined with the following
> priority in case of overlapping characteristics: `error`, `page_summary`,
> `view_summary`, `navigation`, `app_start`, `visibility_change`,
> `user_interaction`, `request`, `property`, `api`, `invalid`, `sfm`. **Used for
> internal optimization when storing the data and not intended for query
> usage.**"

It is also marked `experimental`.

Meanwhile the practical advice in circulation is to filter on it to reconcile
DQL session counts against USQL, e.g. `| filter characteristics.classifier ==
"navigation"`. **Attribution, because it changes how much weight this carries:**
that advice comes from a Dynatrace Community thread where the accepted answer
was written by the person who asked the question, relaying what their own
support case had told them — not from a Dynatrace employee posting an official
position, and not from any documentation page. The same post concedes "we were
not able to get a definitive answer on this from support."
([thread](https://community.dynatrace.com/t5/Dashboarding/USQL-vs-DQL-different-session-counts-contradictory-docs-on/td-p/301305))

**How to answer.** Lead with the supported route: `fetch user.sessions` counted
with `count()` is the object that corresponds to a USQL session, and `user.events`
is an event stream where not every session id ever becomes a registered session
(`observe/digital-experience/rum/web-frontends/concepts/user-sessions-web.md`,
"Aggregation of user events into sessions"). Mention the classifier filter as a
workaround that is reported to work, label where it came from, and say the field
is flagged experimental and not intended for queries. Do not present it as the
documented answer, and do not silently omit it either — someone reading the same
forum thread will ask why.

**The general shape.** A support case, a forum post and the documentation are
three different authorities with three different lifetimes. When they disagree,
say which one each claim rests on rather than blending them into one voice.

---

## DT79. Settings that exist in the product but nowhere in the documentation

**Settings > Server-side service monitoring > Deep monitoring > "Exclude
specific incoming web request URLs"** is the worked example. Searching the whole
corpus for that string and every plausible variant returns nothing:

- no page describes it;
- `dynatrace-api/environment-api/settings/schemas.md` lists exactly two
  URL-related service schemas, `builtin:url-based-sampling` and
  `builtin:url-path-pattern-matching-rules` — neither is this;
- no Configuration API v1 endpoint covers it.

Yet the Deep monitoring page itself is real and current: other sections of it are
cited in `manage/data-privacy-and-security/data-privacy/personal-data-captured-by-dynatrace.md`
and `observe/infrastructure-observability/database-services-classic/support-for-sql-bind-variables.md`.

**What this means in practice.** A legacy Settings 1.0 control with no schema
cannot be managed through the Settings API, so Monaco and Terraform cannot reach
it. If a question is about automating such a setting, that is the answer — not
"look for the right schema id".

**How to answer.** Say the control exists, say the documentation does not cover
it, and separate what you read in the docs from what you read on the forum.
Do not manufacture a schema id to fill the gap.


## DT80. A community rank is not a staff badge

Dynatrace Community ranks — **Visitor, Observer, Helper, Advisor, Mentor, Guru,
Champion, Leader, Pro** — are earned by forum activity. They say nothing about
employment. "DynaMight" is a recognition programme for community members, also
not staff. Dynatrace employees carry a separate marker, and threads that have one
show it as **Dynatrace Employee** or **Community Team**.

**The failure this causes.** It is tempting to read the word "Dynatrace" in a
rank name as a staff designation and promote a forum reply to an official
position. That inference is wrong, and it converts one person's experience into
apparent vendor confirmation. Observed on a real answer: `imsingh`, rank
*Mentor*, answering
[Clarification on AppFunctions limitation](https://community.dynatrace.com/t5/Developer-Q-A-Forum/Clarification-on-AppFunctions-limitation/td-p/218506)
— cited as staff on the strength of the rank alone; the thread carries no
employee badge at all.

**Related, and just as easy to get wrong:** an *accepted* answer is marked
accepted by whoever asked. Frequently that is the asker answering themselves
after opening a support ticket — see DT78. Accepted means "this resolved it for
me", not "Dynatrace confirms this".

**How to cite a forum answer.** Name the thread, say it is a community answer,
and if the substance came from a support case say that too. Only call someone
Dynatrace staff if the page shows the employee marker. When a forum claim and a
documentation page disagree, the page wins unless the page is visibly stale
(DT77).


## DT81. The DPL export-name rule forbids what Dynatrace's own examples use

`platform/grail/dynatrace-pattern-language/log-processing-modifiers.md`
(**2022-05-18**), line 163, on export names:

> "may contain only lower or uppercase letters and numbers"

Read literally, an underscore is illegal. Dynatrace's own patterns use them
freely:

- `platform/grail/dynatrace-pattern-language/log-processing-lines-strings.md`
  line 93 — `TIMESTAMP:date_time ','`
- `deliver/site-reliability-guardian/reference.md` (**2025-02-06**) lines 110
  and 147 — `INT:http_status`

**What to answer.** Underscores work; the rule statement is stale, not the
examples. Say so rather than propagating a restriction that would make a user
rewrite working patterns. Note the same page also allows `` ` `` -quoted export
names, which is the documented escape hatch for anything unusual.

---

## DT82. `post-ingest-logs` contradicts itself on which header selects the payload type

`dynatrace-api/environment-api/log-monitoring-v2/post-ingest-logs.md`
(**2021-05-05**) says both things on one page:

- line 24: "Be sure to set the correct **Content-Type** header … for example:
  `application/json; charset=utf-8`"
- line 48: "The endpoint accepts one of the following payload types, defined by
  the **Accept** header"

**`Content-Type` is the correct one.** `Accept` declares what the client wants
back, and using it to declare what is being sent is a category error that will
simply not work.

There is a third path the same page documents and that is easy to miss: a
**`content-type` query parameter** (line 44) which "has priority over value
provided in Content-Type header". Useful when a log shipper will not let you set
headers.

---

## DT83. `get-event-properties` has two response samples and only one shows `filterable`

`dynatrace-api/environment-api/events-v2/get-event-properties.md`
(**2021-10-07**) documents `filterable` properly in the schema table (line 73)
and in the **Response body JSON models** template (line 119). But the concrete
**Example > Response body** (line 190 onward) returns three properties —
`dt.event.allow_davis_merge`, `dt.event.baseline.service_method`,
`dt.event.baseline.total_load` — and **none of them carries `filterable`**.

That matters because `filterable` is the field that decides whether a property
can be used in an `eventSelector` at all (see the events selector gate). Someone
who reads only the worked example concludes the field does not exist and never
learns why their selector returns 400.

**What to answer.** Point at the schema table, not the example, and mention that
the example is incomplete so the user does not think their tenant is returning
something different.

---

## DT84. `request.is_root_span` is deprecated in the dictionary and still used in prose

`semantic-dictionary/model/trace.md` and `semantic-dictionary/fields.md`
(**2026-07-16**):

> "**deprecated** Replaced by `transaction.is_root_span` in combination with
> `transaction.is_endpoint_request`."

Still used as current in at least four pages, including
`observe/application-observability/distributed-tracing/advanced-tracing-analytics.md`
(**2026-07-14**, two days before the deprecation) and
`platform/grail/dynatrace-query-language/commands/aggregation-commands.md`
(**2026-03-23**).

**What to answer.** Give the replacement pair, and note that the old field still
works — a deprecation is not a removal, and a user with a working dashboard does
not need to be told it is broken. This is the same-cycle desync case from DT77:
the dictionary moves first, prose catches up later.

---

## DT85. The OpenPipeline ingest reference omits mime types the endpoint accepts

`platform/openpipeline/reference/api-ingestion-reference.md` (**2026-06-29**)
lists the logs payload as `text/plain` and `application/json` only.

Sprint 318 (**2026-02-05**) announced JSON Lines support on the same
`/logs/ingest` endpoint, and `post-ingest-logs.md` lists all five accepted
types: `application/jsonl`, `application/jsonlines`, `application/x-ndjson`,
`application/jsonlines+json`, `application/x-jsonlines`.

**What to answer.** JSONL works. Cite `post-ingest-logs.md` rather than the
OpenPipeline reference for the accepted types.

**The general point.** A recent `lastmod` is not proof of completeness — this
page is four months newer than the feature it fails to mention. When a reference
page and a release note disagree about whether something exists, the release
note announcing an addition wins; nobody announces a feature that did not ship.


## Provenance

Every entry above was produced by comparing a page's screenshots against its own prose during
a Stage 4 vision pass over the whole of `docs.dynatrace.com` (4 390 pages, 2 259 unique
images), 2026-08-05. The per-image detail — the full transcription that produced each finding
— lives in a `stage4` block next to the image in the corpus. To read one:

```bash
grep -rn "stage4:start" {{DOCS_CORPUS}}/<path-to-page>.md
```

Findings were recorded only where the image and the prose disagree on something checkable.
Where a value was clipped, blurred or otherwise unreadable, it was marked as such and never
reconstructed — so an entry above is a real disagreement, not an artefact of transcription.
