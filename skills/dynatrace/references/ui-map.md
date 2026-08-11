# UI map — navigation paths, split by generation

**Never state a menu path from memory.** Menus are the highest-variance thing in
Dynatrace: they move between versions, the docs often still describe the Classic
route, and a wrong path reads exactly like a right one. A plausible-sounding
`Settings > X > Y` costs the reader a search and costs you trust, and nothing in
the answer reveals which it was.

The data is extracted from both corpora, so a path question is a **lookup, not a
recall**. A lookup can also return nothing, and "the corpus has no path for this"
is a legitimate answer — see "When the map is silent".

## Contents

- Where the data lives
- The shape is a graph
- Three reasons one destination has several paths
- How to query
- Confidence tiers
- The two UIs at the top level
- When the map is silent

## Where the data lives

```
{{DOCS_CORPUS}}/_reports/ui-map.tsv
```

1 015 rows, 815 distinct destinations, drawn from 2 329 path occurrences across
both corpora, including 74 read out of transcribed screenshots. Columns:

`generation` · `confidence` · `destination` · `path` · `depth` ·
`attested_by` (how many pages) · `newest_lastmod` · `from_screenshot` ·
`example_source`

Grep it. Never read it whole.

## The shape is a graph

One destination is reachable by several routes, and one parent leads to many
destinations. **114 destinations have more than one route.** Answering with the
first hit and stopping is how you give someone a route that exists but is not
the one their screen offers.

Always look at *all* rows for a destination before answering.

## Three reasons one destination has several paths

This is the distinction that makes the map useful, and it cannot be read off the
path alone — it comes from `newest_lastmod`.

**1. A genuine alternative.** Both routes work today, from different entry
points. `OneAgent features` sits under `Settings > Collect and capture > General
monitoring settings` (2026-08-03) and also under `Settings > Preferences`
(2026-08-04). Two current dates, two real doors. Give both.

**2. The menu moved.** Same destination, different parent, and the dates are
years apart. `Log ingest rules`:

| path | newest source |
|---|---|
| `Settings > Collect and capture > Log monitoring > Log ingest rules` | 2026-03-20 |
| `Settings > Log Monitoring > Log ingest rules` | 2022-01-10 |

The second is not an alternative route, it is history. `AWS` is the starker
case: `Settings > Anomaly detection > Infrastructure > AWS` (2018-12-28) against
`Settings > Collect and capture > Cloud and virtualization > AWS` (2026-07-10).
Quoting the old one is a wrong answer that looks sourced.

**Rule: sort a destination's routes by `newest_lastmod` descending. Treat
anything more than about two years behind the freshest as historical unless a
recent page also attests it.**

**3. Casing drift only.** `Collect and capture` against `Collect and Capture`
are the same menu written two ways, usually an old page against a new one. Do
not present them as two options; take the newer spelling.

## How to query

```bash
# every route to a destination, newest first
grep -P "\tLog ingest rules\t" {{DOCS_CORPUS}}/_reports/ui-map.tsv | sort -t$'\t' -k7 -r

# what lives under a menu (prefix query)
grep -P "\tSettings > Collect and capture" {{DOCS_CORPUS}}/_reports/ui-map.tsv

# only the latest platform, only trustworthy rows
grep -P "^latest\thigh\t" {{DOCS_CORPUS}}/_reports/ui-map.tsv | grep -i "openpipeline"
```

Then cite the `example_source` page, and say which generation and how old the
path is. A path without those two facts is not much better than a guess.

## Confidence tiers

Extraction is heuristic — the doc-site writes menu paths as runs of bold text,
and so does ordinary emphasis. Rows are labelled rather than dropped, because a
silently discarded path cannot be argued with later.

| tier | meaning | rows |
|---|---|---:|
| `high` | preceded by "go to"/"open"/"navigate to" **and** starting at a known entry point | 552 |
| `medium` | one of those two signals | 274 |
| `low` | neither — a bold run that may be a form field or a fragment | 189 |

Answer from `high`. Use `medium` with the caveat. Treat `low` as a hint about
where to look in the corpus, not as an answer.

## The two UIs at the top level

Second level under **Settings**, by how many mapped paths pass through it. This
is the fastest way to tell which generation a question is about.

| latest | classic |
|---|---|
| Collect and capture | Web and mobile monitoring |
| Process and contextualize | Log Monitoring |
| Analyze and alert | Processes and containers |
| Server-side service monitoring | Anomaly detection |
| Anomaly detection | Monitoring |
| Preferences | Server-side service monitoring |
| Cloud and virtualization | Cloud and virtualization |
| Environment segmentation | Ownership |
| Storage management | Business Observability |

**Collect and capture** and **Process and contextualize** are the giveaway for
latest; they do not exist in Classic. **Web and mobile monitoring** and the
`-Classic` suffixed apps (`Settings Classic`, `Synthetic Classic`) are the
giveaway for the other direction.

Entry points outside Settings, on latest: `Identity & access management`,
`Connections`, `Extensions`, `Deployment Status`, `Account Management`,
`Subscription`, plus per-app menus (`Notebooks`, `Dashboards`, `Manage`).

**On a migrated tenant both trees exist at once.** The user's work tenant carries
its Classic layer alongside the new apps, so "which one" is a real question, not
a formality. When the question does not settle it, ask rather than assume — see
`classic-vs-latest.md`.

## When the map is silent

A miss is information. Say plainly that the corpus has no path for that
destination, then do one of:

- widen the query — the destination may be recorded under a slightly different
  label;
- grep the corpus prose directly, since a path described in a sentence rather
  than in bold will not have been extracted;
- **ask for a screenshot.** The corpus is a snapshot of the documentation, not
  of the user's tenant, and no index can know what their build shows today.

What must not happen is filling the gap with a fluent guess. The existing prose
warning against exactly that did not prevent it, which is why this file exists:
the fix is a lookup with a possible null, not a firmer instruction.
