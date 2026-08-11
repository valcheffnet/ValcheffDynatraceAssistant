# DQL — Dynatrace Query Language

DQL is the **only** query language for Grail. Read-only, pipeline-based. It
replaces the classic-era USQL, metric selectors and log search syntax.

## Contents

- Syntax
- Commands (full list by category)
- Data sources / tables
- `fetch` parameters (cost and performance control)
- Operators
- Data types
- Best practices — cost and performance
- Reaching into nested structures
- Functions by category
- Example queries
- DQL against other languages
- Learn DQL app

Sources:
`/docs/platform/grail/dynatrace-query-language/{dql-guide,dql-reference,commands,functions,operators,data-types,dql-best-practices,dql-comparison}`
(harvested 2026-07-30; the pages carry `Updated on` dates between Oct 2025 and
Jul 2026).

## Syntax

```
command parameter,.. [, optionalparameter],... | command …
```

- Every command returns tabular output: **records** (rows) and **fields**
  (columns).
- Commands chain with `|`. **Order matters**, for the result and for cost and
  performance alike.
- Mandatory parameters are positional; **optional parameters must be named**
  (`from:`, `by:`, `interval:`).
- Group related parameters with `{}`:
  `summarize {min(value), max(value)}, by:{field1, field2}`.
  Careful: DQL operators **cannot** be used on grouped parameters.
- A sub-query is an execution block in square brackets: `[fetch logs]`.
- Assign a column name with `=`: `summarize event_count = count()`.
- Comment: `//`.

### Field naming rules

- Any Unicode character is allowed in a field name.
- A name containing anything outside `a-zA-Z0-9_.` **requires backticks**:
  `` `my host*` ``.
- A name **starting** with anything outside `a-zA-Z_` requires backticks.
- `\` is the escape character; backticks and backslashes inside a name are
  escaped.
- Valid: `dt.entity.host`, `location_US_EAST_1`, `` `my host*` ``,
  `` `LOCAL_MACHINE\\Software` ``.

### Reserved keywords — do not use as field names

`true`, `false`, `null`, `mod`, `and`, `or`, `xor`, `not`

Where such a dimension does exist, it is reachable only through backticks. The
difference is real and silent:

```dql
| fields x = true      // boolean constant, always true
| fields x = `true`    // custom dimension named "true"
| sort not desc        // sorts by the boolean value of dimension `desc`
| sort `not` desc      // sorts descending by a field named "not"
```

## Commands (full list by category)

### Data source
| Command | What it does |
|---|---|
| `fetch` | Loads data from the named resource (table) |
| `data` | Generates sample data at runtime — for tests and demos |
| `describe` | Shows the on-read schema extraction definition for a data object |
| `fieldsSnapshot` | Snapshots the fields in the records of a data object |
| `load` | Loads data from a resource; used for lookup data |

### Metrics
| Command | What it does |
|---|---|
| `timeseries` | Load, filter and aggregate metrics into timeseries output (**this is the command for metrics, not `fetch`**) |
| `metrics` | Retrieves metric series |

### Filter and search
| Command | What it does |
|---|---|
| `filter` | Keeps only records matching the condition |
| `filterOut` | Removes records matching the condition |
| `search` | Finds records by a search condition (free-text style) |
| `dedup` | Removes duplicates |

### Select and modify
`fields` (keeps only the named ones), `fieldsAdd` (evaluates an expression and
adds or replaces a field), `fieldsKeep`, `fieldsRemove`, `fieldsRename`

### Extraction and parsing
`parse` — parses a field against a **DPL pattern** and puts the result into one
or more fields.

### Ordering
`sort` (ascending by default; `desc` reverses), `limit`

### Structuring
`expand` (array → separate records), `fieldsFlatten` (flattens a nested record)

### Aggregation
| Command | What it does |
|---|---|
| `summarize` | Groups by values and aggregates — the core of DQL |
| `makeTimeseries` | Builds a timeseries from raw records in the stream (for charting) |
| `fieldsSummary` | Calculates the cardinality of the values of the named fields |

### Correlation and join
| Command | What it does |
|---|---|
| `join` | Joins the source with a sub-query on a join condition |
| `joinNested` | Adds sub-query results as an array of nested records |
| `lookup` | Adds fields from a sub-query by finding a match (enrichment) |
| `append` | Appends records from a sub-query to the list |

### Smartscape (topology)
| Command | What it does |
|---|---|
| `smartscapeNodes` | Loads Smartscape nodes by type pattern (`*` = all types) |
| `smartscapeEdges` | Loads Smartscape edges by edge type pattern |
| `traverse` | Walks from source to target nodes in a given direction along `edgeTypes` |

## Data sources / tables

The main ones: `logs`, `events`, `bizevents`, `spans`, `metrics`,
`dt.entity.<type>` (monitored entities).

A table groups records by type — `fetch logs` returns records from **every**
bucket the caller can access. Narrow to specific buckets with the `bucket:`
parameter.

Querying entities → see `/docs/platform/grail/querying-monitored-entities`.

## `fetch` parameters (cost and performance control)

```dql
fetch logs,
      from:now() - 24h, to:now() - 2h,       // relative timeframe
      bucket:{"default_logs", "logs_365_*"}, // restrict to buckets (wildcards OK)
      samplingRatio:100,                     // 1 | 10 | 100 | 1000 | 10000
      scanLimitGBytes:100                    // stops processing after N GB
```

- **Timeframe:** `from:`/`to:` with `now() - 2h` (or the short `from:-10m`), or
  absolute `timeframe:"2021-10-20T00:00:00Z/2021-10-28T12:00:00Z"`. When
  unspecified the UI timeframe selector applies; the default is **2 hours**.
- **`samplingRatio:N`** — Grail samples the data **on write** and `fetch` picks
  those partitions. Returns roughly `1/N` of the raw records. Only 1, 10, 100,
  1000 and 10000 are valid. Compensate in the arithmetic:
  `| fieldsAdd c = c*100`.
- **Time alignment operator `@`:** `from:-1d@d` means one day ago, aligned to
  the start of that day.

## Operators

| Category | Operators |
|---|---|
| Arithmetic | `+` `-` `*` `/` `%` |
| Comparison | `<` `<=` `>` `>=` |
| Equality | `==` `!=` |
| Logical | `not` `and` `or` `xor` |
| Subquery | `in` |
| Time alignment | `@` |
| Search | `~` |

**Precedence, strongest to weakest:** `-` (unary) → `*` `/` `%` → `@` → `+` `-`
→ `~` → `==` `!=` `>` `>=` `<` `<=` → `in` → `not` → `and` → `xor` → `or`

`~` is the search operator (partial or pattern match), `==` is exact. The cost
section explains why the choice matters.

## Data types

Strongly typed — functions and operators accept only declared types. The type is
set during parsing or through casting functions.

| Type | Notes |
|---|---|
| `boolean` | `true`/`TRUE`/`false`/`FALSE`. `toBoolean("true")` → true; `toBoolean(0)` → false, any other number → true |
| `long` | Signed, -2^63 … 2^63-1; decimal or hex (`0x0` … `0xFFFFFFFFFFFFFFFF`) |
| `double` | 64-bit IEEE 754; `2.34` or scientific `2.4e2` |
| `timestamp` | A point in time with **nanosecond** precision |
| `timeframe` | Start and end timestamps; reached with `tf[start]`, `tf[end]` |
| `duration` | Amount plus time unit |

**Time literals:** `ns` `ms` `s` `m` `h` `d` `w` `M` (months) `q` (quarters) `y`

> Gotcha: `d` inside **calculations** is treated as a **calendar day**;
> everywhere else it is exactly 24h.

To see nanoseconds in the result, switch the Notebooks visualisation to **raw**.

## Best practices — cost and performance

DQL is **billed per GiB scanned**. What follows is money, not style.

### Recommended command order

1. **Cut the records first** — `filter` / `search`.
2. **Cut the fields early** — `fields`, `fieldsKeep`, `fieldsRemove`.
3. **Process** — `fieldsAdd`, `parse`, `append`.
4. **Aggregate last** — `summarize`, `makeTimeseries`.

Put `sort` **at the end**, not straight after `fetch`; sorting early destroys
performance:

```dql
// BAD
fetch logs | sort timestamp desc | filter content ~ "error"
// GOOD
fetch logs | filter content ~ "error" | sort timestamp desc
```

Do not put `limit` **before** an aggregation — the aggregates come out wrong,
unless that is precisely the intent.

### Filter rules

- **Filter on the field itself, not on a transformation of it:**
  - Bad: `| filter matchesValue(lower(k8s.namespace.name), "astro*")`
  - Good: `| filter k8s.namespace.name ~ "astro*"`
- **`==`/`!=` when the value is known; `~` when it is partial or unknown.**
- **Prefer inclusive filters; avoid negation** (`not … ~ "astro*"`).
- **Do not use `join`/`lookup` to filter** — filter on enriched fields instead.
- For text search, match against words or phrases:
  `| filter content ~ "refused"`.

### Blueprint query

```dql
fetch logs, bucket:{"astroshop_log_*"}, from:-1d@d, samplingRatio:10
| filter loglevel == "ERROR" and k8s.namespace.name ~ "astroshop"
| filter content ~ "error"
| summarize c = count(), by:pod.name
| sort c desc
| limit 5
```

### Datawarping

Grail retrieves only the records matching the query's filters, cutting scanned
bytes. That is why an early `filter` reduces the bill directly, not just the
wall-clock time.


## Reaching into nested structures

A parsed JSON payload is a `record`, not a string. Once `parse content, "JSON:j"`
has run, `j` holds a nested record and **a second `parse` over one of its members
fails** — `parse` takes a string. This is the single most common wrong turn on
nested log payloads.

Four ways in, roughly in order of how often they are the right one:

**1. Bracket path — the default.** Index the record directly. Works for nested
records and for array elements.

```
| fieldsAdd msg = j[error][message],
            status = j[error][status],
            owner = j[error][details][0][owner]
```

**2. `fieldsFlatten` with `depth:`.** `fieldsFlatten j` lifts only the first
level. Nested members below that stay packed unless you say how deep to go
(`platform/grail/dynatrace-query-language/commands/structuring-commands.md`,
"Extract fields with multiple levels of nesting"):

```
| fieldsFlatten j, depth: 2
```

Column names come out dotted — `j.a`, `j.c.d`. Add `prefix:"flat."` to control
the namespace, or `fields: { a, b }` to lift only named members. Note in the
documented example that where a member is a scalar at one depth and a record at
another, the flattened columns differ per row.

**3. `jsonPath()` — one value out of a raw JSON string, no `parse` needed**
(`platform/grail/dynatrace-query-language/functions/string-functions.md`,
line 479):

```
jsonPath(expression, jsonPath [, seek])
```

```
| fieldsAdd city = jsonPath(content, "$.address.city"),
            first = jsonPath(content, "$.children[0]"),
            zip = jsonPath(content, "$['address']['zip']")
```

Returns `long`, `double`, `boolean`, `string`, `array` or `record`. The optional
`seek` (default `false`) makes it search for the first valid JSON object inside
the expression — that is what handles a log line with a text prefix before the
JSON, which otherwise needs `LD JSON:j` in a `parse`.

**4. `expand`** — only for turning an array into one record per element, when you
actually want row multiplication. It is not an accessor. On a large stream
`expand` before a filter is a cost trap; see "Best practices" above.

**Choosing.** One or two values out of a raw string → `jsonPath`, no parse step.
Several values from an already-parsed record → bracket paths. Whole subtree as
columns → `fieldsFlatten` with an explicit `depth:`. Array to rows → `expand`.

**Watch the name collisions.** Flattening or aliasing a member called `status`,
`content`, `timestamp` or `host` onto a `fetch logs` stream shadows a built-in
field. Alias deliberately rather than letting a payload key win.

## Functions by category

Full name list; per-function detail →
`/docs/platform/grail/dynatrace-query-language/functions/<category>`.

**Aggregation** (24): `avg`, `collectArray`, `collectDistinct`, `correlation`, `count`, `countDistinct`, `countDistinctApprox`, `countDistinctExact`, `countIf`, `max`, `median`, `min`, `percentile`, `percentiles`, `percentileFromSamples`, `percentRank`, `stddev`, `sum`, `takeAny`, `takeFirst`, `takeLast`, `takeMax`, `takeMin`, `variance`

**String** (31): `concat`, `contains`, `decodeUrl`, `encodeUrl`, `endsWith`, `escape`, `getCharacter`, `indexOf`, `jsonField`, `jsonPath`, `lastIndexOf`, `levenshteinDistance`, `like`, `lower`, `matchesPattern`, `matchesPhrase`, `matchesValue`, `parse`, `parseAll`, `punctuation`, `replacePattern`, `replaceString`, `splitByPattern`, `splitString`, `startsWith`, `stringLength`, `substring`, `trim`, `unescape`, `unescapeHtml`, `upper`

**Conversion and casting** (39): `asArray`, `asBinary`, `asBoolean`, `asDouble`, `asDuration`, `asIp`, `asLong`, `asNumber`, `asRecord`, `asString`, `asTimeframe`, `asTimestamp`, `asUid`, `decode`, `encode`, `getHighBits`, `getLowBits`, `hexStringToNumber`, `isUid128`, `isUid64`, `isUuid`, `numberToHexString`, `toArray`, `toBoolean`, `toDouble`, `toDuration`, `toIp`, `toLong`, `toString`, `toTimeframe`, `toTimestamp`, `toUid`, `type`, `uid128`, `uid64`, `uuid`, `smartscapeId`, `asSmartscapeId`, `toSmartscapeId`

**Time** (22): `duration`, `formatTimestamp`, `getDayOfMonth`, `getDayOfWeek`, `getDayOfYear`, `getEnd`, `getHour`, `getMinute`, `getMonth`, `getStart`, `getSecond`, `getYear`, `getWeekOfYear`, `now`, `timeframe`, `timestamp`, `timestampFromUnixMillis`, `timestampFromUnixNanos`, `timestampFromUnixSeconds`, `unixMillisFromTimestamp`, `unixNanosFromTimestamp`, `unixSecondsFromTimestamp`

**Array** (28): `array`, `arrayAvg`, `arrayConcat`, `arrayCumulativeSum`, `arrayDelta`, `arrayDiff`, `arrayDistinct`, `arrayElement`, `arrayFirst`, `arrayFlatten`, `arrayIndexOf`, `arrayLast`, `arrayLastIndexOf`, `arrayMax`, `arrayMedian`, `arrayMin`, `arrayMovingAvg`, `arrayMovingMax`, `arrayMovingMin`, `arrayMovingSum`, `arrayPercentile`, `arrayRemoveNulls`, `arrayReverse`, `arraySize`, `arraySlice`, `arraySort`, `arraySum`, `arraytoString`

**Mathematical** (30): `abs`, `acos`, `asin`, `atan`, `atan2`, `bin`, `ceil`, `cos`, `cosh`, `cbrt`, `degreeToRadian`, `e`, `exp`, `floor`, `hypotenuse`, `log`, `log1p`, `log10`, `pi`, `power`, `radianToDegree`, `random`, `range`, `round`, `signum`, `sin`, `sinh`, `sqrt`, `tan`, `tanh`

**Conditional** (2): `coalesce`, `if`
**Boolean** (4): `isFalseOrNull`, `isNotNull`, `isNull`, `isTrueOrNull`
**Network** (10): `ip`, `ipIn`, `ipIsLinkLocal`, `ipIsLoopback`, `ipIsPrivate`, `ipIsPublic`, `ipMask`, `isIp`, `isIpV4`, `isIpV6`
**Hash** (7): `hashCrc32`, `hashMd5`, `hashSha1`, `hashSha256`, `hashSha512`, `hashXxHash32`, `hashXxHash64`
**Bitwise** (7): `bitwiseAnd`, `bitwiseCountOnes`, `bitwiseNot`, `bitwiseShiftLeft`, `bitwiseShiftRight`, `bitwiseOr`, `bitwiseXor`
**Join** (3): `lookup`, `getNodeName`, `getNodeField`
**Vector distance** (4): `vectorL1Distance`, `vectorL2Distance`, `vectorCosineDistance`, `vectorInnerProductDistance`
**General** (6): `classicEntitySelector`, `entityAttr`, `entityName`, `exists`, `in`, `record`

> `classicEntitySelector` bridges to the classic entity-selector syntax — useful
> when migrating from the classic API or dashboards.

## Example queries

**Errors by service and host:**
```dql
fetch logs, from:now() - 24h
| filter loglevel == "ERROR" and not endsWith(log.source, "audit.log")
| summarize errors = count(), by:{dt.entity.service, host.name}
| sort errors desc
| limit 20
```

**Chartable timeseries from logs:**
```dql
fetch logs
| filter loglevel == "SEVERE" or loglevel == "ERROR"
| makeTimeseries count = count(), by:loglevel, interval:5m
```

**Parse plus multi-aggregation (success and failure per IP):**
```dql
fetch logs, from:now()-10m
| filter endsWith(log.source, "pgi.log")
| parse content, "LD IPADDR:ip ':' LONG:payload SPACE LD 'HTTP_STATUS' SPACE INT:http_status LD (EOL|EOS)"
| summarize total_payload = sum(payload),
            failedRequests = countIf(http_status >= 400),
            successfulRequests = countIf(http_status < 400),
            by:{ip, host.name}
| fieldsAdd total_payload_MB = total_payload/1000000
| fields ip, host.name, failedRequests, successfulRequests, total_payload_MB
| sort failedRequests desc
```

**Bizevents filtered to business hours:**
```dql
fetch bizevents
| filter event.type == "booking.process.started"
| fieldsAdd hour = formatTimestamp(timestamp, format:"hh"),
            day_of_week = formatTimestamp(timestamp, format:"EE")
| filterOut (day_of_week == "Sat" or day_of_week == "Sun")
            or (toLong(hour) <= 08 or toLong(hour) >= 17)
| summarize numStarts = count(), by:{product}
```

**Spans with sampling:**
```dql
fetch spans, samplingRatio:100
| summarize c = count(), by:{span.kind, code.namespace, code.function}
| fieldsAdd c = c*100
```

## DQL against other languages

The docs compare DQL with **SQL**, **Splunk SPL** and **KQL** — see
`/docs/platform/grail/dynatrace-query-language/dql-comparison`. Operations
covered: loading, filtering, field selection, calculations and sorting,
grouping and dedup, aggregation.

A rough mental map for someone arriving from Splunk:

| SPL | DQL |
|---|---|
| `index=x sourcetype=y` | `fetch logs, bucket:{"x"}` plus `filter` |
| `search` / `where` | `filter` (`search` exists, but is free-text style) |
| `\| stats count() by f` | `\| summarize count(), by:{f}` |
| `\| timechart span=5m count` | `\| makeTimeseries count(), interval:5m` |
| `\| table a,b` | `\| fields a, b` |
| `\| eval x=...` | `\| fieldsAdd x = ...` |
| `\| rex` | `\| parse` (DPL pattern, not regex) |
| `\| dedup f` | `\| dedup f` |
| `\| lookup` | `\| lookup` / `join` |
| `\| head 5` | `\| limit 5` |
| `earliest=-24h` | `from:-24h` |

> An important difference: `parse` uses **DPL** (Dynatrace Pattern Language),
> not regex. DPL has named matchers by type (`IPADDR:ip`, `LONG:payload`,
> `INT:http_status`, `LD` = "lazy data"). See
> `/docs/platform/grail/dynatrace-pattern-language`.

## Learn DQL app

Interactive tutorials, available to SaaS customers and registered Dynatrace
Community members, plus a 15-day trial. See the Dynatrace Hub.
