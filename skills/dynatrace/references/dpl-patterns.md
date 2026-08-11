# DPL — Dynatrace Pattern Language

DPL is what `parse` speaks. It is **not regex**: it is a left-to-right sequence
of typed matchers, each optionally exporting a named field. Anyone arriving from
Splunk `rex`, Grok or plain regex will reach for the wrong syntax first.

Two places use it:

- **`parse` in DQL** — extract fields from a record at query time
  (`platform/grail/dynatrace-query-language/commands/extraction-and-parsing-commands#parse`)
- **Log processing rules** — reshape data at ingest
  (`analyze-explore-automate/logs/lma-log-processing`)

**DPL Architect** gives instant feedback on match coverage against sample data,
and ships preset patterns for common technologies:
`platform/grail/dynatrace-pattern-language/dpl-architect`.

## Contents

- Pattern structure
- Matching versus parsing
- Matcher expression syntax
- The matcher catalogue
- Groupings
- Modifiers: quantifier, optional, lookaround, configuration
- Worked example
- Common mistakes

## Pattern structure

A pattern is read left to right. Whitespace, line breaks and comments between
matchers are ignored, so the same pattern can be a one-liner or documented:

```
INT ' ' IPADDR:ip EOL
```

```
/* an integer and an IP address separated by a single space, per line */
INT       //an integer
' '       //followed by a single space
IPADDR:ip //followed by an IPv4 or IPv6 address, extracted as field `ip`
EOL       //line terminated with a line feed
```

Comments are `//` to end of line and `/* … */`.

## Matching versus parsing

**Every matcher in the pattern must match. Only the ones with an export name
extract anything.** Separators, brackets and end-of-line markers earn their
place by making the pattern line up; they do not need to produce fields.

A matcher extracts when it is followed by `:name`. That name becomes the field
available to the query.

## Matcher expression syntax

Elements come in this exact order. Putting the optional marker after the export
name is a syntax error, not a silent no-op:

```
[lookaround] MATCHER_EXPR ['(' configuration ')'] [quantifier] [optional] [':' export_name]
```

## The matcher catalogue

Full table: `platform/grail/dynatrace-pattern-language/log-processing-grammar`.

### Lines and strings

| Matcher | Matches |
|---|---|
| `LDATA`, `LD` | any line data up to the next non-optional matcher, within one line |
| `DATA` | the same, but multiline |
| `EOL`, `LF` | line feed |
| `EOLWIN`, `WINEOL` | line feed plus carriage return |
| `CR` | a single carriage return |
| `STRING` | single- or double-quoted string, or a character group (excluding the first 32 ASCII symbols) |
| `SQS` / `DQS` | single- / double-quoted string |
| `CSVSQS` / `CSVDQS` | the same with CSV escaping |
| `UPPER`, `LOWER`, `ALPHA` | `A-Z`, `a-z`, `a-zA-Z` |
| `DIGIT`, `XDIGIT`, `ALNUM` | digits, hex digits, alphanumerics |
| `PUNCT`, `BLANK`, `SPACE`, `NSPACE` | punctuation, space+tab, whitespace, non-whitespace |
| `GRAPH`, `PRINT`, `WORD`, `ASCII`, `CNTRL` | visible, printable, words, ASCII, control characters |

### Numeric

`INT` (`INTEGER`), `LONG`, `HEXINT`, `HEXLONG`, `FLOAT`, `DOUBLE`, `CFLOAT`,
`CDOUBLE` (the `C` variants use a comma as the decimal separator),
`BOOLEAN` (`BOOL`, case-insensitive `true`/`false`).

### Time and date

| Matcher | Format |
|---|---|
| `TIME`, `TIMESTAMP` | configurable — needs a format definition |
| `JSONTIMESTAMP` | `yyyy-MM-ddTHH:mm:ss.SSSZ` |
| `ISO8601` | `yyyy-MM-ddTHH:mm:ssZ` |
| `HTTPDATE` | `dd/MMM/yyyy:HH:mm:ss Z` |

### Network and identifiers

`IPADDR` (v4 or v6), `IPV4` (`IPV4ADDR`), `IPV6` (`IPV6ADDR`), `CREDITCARD`
(validates, so it is the safe way to find card numbers for masking),
`SMARTSCAPEID`.

### Structured data

| Matcher | Purpose |
|---|---|
| `JSON`, `JSON_OBJECT{ jsonFields … }` | JSON object |
| `JSON_ARRAY`, `JSON_ARRAY{jsonValueType}` | JSON array |
| `JSON_VALUE`, `JSON_VALUE{jsonValueType}` | a single JSON value |
| `KVP{patternExprs}` | key-value pairs |
| `ARRAY{patternExprs}` | repeated elements |
| `STRUCTURE{patternExprs}` | captures parsed data as a composite type |
| `ENUM{ string=integer, … }` | maps strings to numeric values |

There is also a dedicated XML page:
`platform/grail/dynatrace-pattern-language/dpl-xml`.

## Groupings

| Syntax | What it is |
|---|---|
| `(patternExpr, …)` | **sequence group** — an ordered run of matchers |
| `(patternExpr \| …)` | **alternatives group** — pick whichever matches |
| `ARRAY{…}` | repeated data elements |
| `STRUCTURE{…}` | composite output type |
| `ENUM{…}` | string-to-number mapping |

A sequence group can carry a field separator in its configuration, which is
usually cleaner than repeating a literal:

```
( HTTPDATE:datetime UPPER:severity ALNUM?:user INT:response )(fs=',') EOL;
```

Character groups are regex-compatible and written in brackets: `[a-zA-Z0-9]`.
Patterns can also reference other named patterns as macros, for building
modular grammars — see `log-processing-macros`.

## Modifiers

### Quantifier

| Quantifier | Repetitions |
|---|---|
| `{min,max}` | between min and max |
| `{min,}` | min to **4096** |
| `{,max}` | 0 to max |
| `{val}` | exactly val |
| `*` | 0 to 4096, same as `{0,}` |
| `+` | 1 to 4096, same as `{1,}` |

4096 is a hard ceiling, not shorthand for unbounded.

```
[a-zA-Z0-9]+:username
```

A character group without a quantifier matches **one character**. Forgetting the
`+` is the most common way a character-group pattern silently truncates.

### Optional modifier

A `?` after the quantifier and before the export name lets the engine emit NULL
and carry on when the element is absent:

```
ALNUM?:user
```

Two different absences exist, and the distinction matters:

```
14/Mar/2016:23:37:06 +0200,INFO,mary01,200   ← everything present
14/Mar/2016:23:37:07 +0200,INFO,,200         ← value missing, separator present
14/Mar/2016:23:37:13 +0200,INFO,500          ← value and separator both missing
```

The optional modifier handles both, but only if it is on the matcher whose value
can vanish. A pattern built against line 1 alone will fail on lines 2 and 3.

### Lookaround

`<<` look behind, `>>` look ahead, `!<<` negative look behind, `!>>` negative
look ahead. Used for conditional branching — deciding what to match next based
on surrounding content without consuming it.

### Configuration

Parentheses after the matcher configure its behaviour; a timestamp needs its
expected format, a sequence group can take `fs=` for a field separator. See
`log-processing-modifiers`.

## Worked example

Pattern against an Apache-style access line — 11 matchers, 4 of which extract:

```
IPV4:ipAddress LD HTTPDATE:time ']' " LD:method SPACE LD '"' INT:responseCode LD EOL
```

Input:

```
117.169.75.66 -[ 14/Mar/2022:23:34:25 +0200 ] " GET //db/scripts/setup.php HTTP/1.1" 404 474"-" "-" \n
```

| Matcher | Matches | Extracts |
|---|---|---|
| `IPV4:ipAddress` | `117.169.75.66` | ✓ |
| `LD` | `-[` | |
| `HTTPDATE:time` | `14/Mar/2022:23:34:25 +0200` | ✓ |
| `']' "` | `] "` — a literal expression | |
| `LD:method` | `GET` | ✓ |
| `SPACE` | one space | |
| `LD` | `//db/scripts/setup.php HTTP/1.1` | |
| `'"'` | `"` | |
| `INT:responseCode` | `404` | ✓ |
| `LD` | `474"-" "-"` | |
| `EOL` | `\n` | |

Result fields: `ipAddress`, `time`, `method`, `responseCode`.

In DQL:

```dql
fetch logs, from:now()-10m
| filter endsWith(log.source, "pgi.log")
| parse content, "LD IPADDR:ip ':' LONG:payload SPACE LD 'HTTP_STATUS' SPACE INT:http_status LD (EOL|EOS)"
| summarize failed = countIf(http_status >= 400), by:{ip}
```

## Common mistakes

- **Writing regex.** `\d+`, `(?<name>…)` and `.*` are not DPL. The equivalents
  are `INT`, `:name` and `LD`.
- **Using `LD` where the line has none left.** `LD` stops at the next
  non-optional matcher *within the line*; for content spanning lines use `DATA`.
- **Character group without a quantifier** — matches exactly one character.
- **Modifier order.** `[lookaround] MATCHER (config) quantifier ? :name`. Any
  other order is a syntax error.
- **Assuming an unmatched pattern produces NULLs.** If any non-optional matcher
  fails, the whole `parse` produces nothing for that record — the record stays,
  the new fields are absent. Test coverage in DPL Architect rather than
  inferring from a query returning fewer rows than expected.
- **Parsing at query time what should be parsed at ingest.** `parse` in DQL runs
  on every execution and costs scanned bytes each time; an OpenPipeline
  processor runs once. Reach for query-time parsing while exploring, then move
  the stable pattern into ingest.
