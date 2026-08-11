# ValcheffDynatraceAssistant

Two Claude Code skills for working with Dynatrace: a distilled reference layer,
and the tooling to build your own local copy of the documentation it routes to.

**Not affiliated with, endorsed by, or produced by Dynatrace LLC.** "Dynatrace"
is used here only to name the product these skills are about.

---

## What this is, and what it deliberately is not

**It is** ~39 000 words of distilled reference across 30 files, 85 recorded
places where the official documentation is wrong or contradicts itself, a map of
1 015 UI navigation routes split by platform generation, and a driver that
builds and verifies a documentation corpus.

**It is not a copy of the Dynatrace documentation.** No corpus is included and
none ever will be. The skills expect you to build your own local copy from the
public site, for your own reference, using the driver here. That is a few
minutes of your bandwidth and stays on your disk.

The value is the judgement layer, not the text. Anyone can fetch the docs; the
work was in measuring where they lie.

## What you get

### `skills/dynatrace`

A reference layer that answers from files rather than recollection.

- 30 references covering DQL and DPL, Grail, OpenPipeline, IAM, OneAgent and
  ActiveGate, ingest paths, dashboards, workflows, SLOs, AppSec, licensing, the
  API surface, config as code, and AppEngine app development.
- **`references/gotchas.md`** — 85 numbered entries, each a measured case where
  the documentation does not work as printed. This is the part that does not
  exist anywhere else.
- **`references/ui-map.md`** — how to answer "where is this menu" without
  guessing, keyed by destination and split Classic against latest, because a
  migrated tenant runs both and a path for the wrong one is worse than none.
- `evals/` — three rounds of evaluation with the questions, the expected
  answers, and the results, including the rounds that measured nothing.

### `skills/run-dynatrace-docs`

The driver that builds and checks the corpus.

| subcommand | does |
|---|---|
| `check` | what changed upstream, by `lastmod` |
| `devcheck` | the same for a sitemap without dates, by content hash |
| `verify` | integrity: links, sentinels, encoding |
| `anchors` | do `page.md#anchor` links land on anything |
| `images` | have any images changed |
| `indexes` | rebuild the derived indexes |
| `stats` | per-section counts |

## Requirements

- Claude Code
- Python 3.13 — **not 3.14**: `magika` caps below it and pip silently installs
  an ancient MarkItDown that looks fine and converts nothing
- MarkItDown 0.1.7 with `[all]` extras, in a virtualenv
- The conversion tooling (`url2md.py` and friends), which lives outside this
  repository

## Install

```bash
git clone https://github.com/valcheffnet/ValcheffDynatraceAssistant.git
cd ValcheffDynatraceAssistant
python setup.py
```

`setup.py` asks where your corpus, tooling and Claude home live, substitutes the
`{{PLACEHOLDER}}` tokens, and copies the skills into `~/.claude/skills/`.
Nothing is written outside those paths.

Then build a corpus of your own:

```bash
python <your-md-workflow>/url2md.py https://docs.dynatrace.com/sitemap.xml --sitemap --mirror --strip-prefix docs --frontmatter --docsite --link-prefix=/docs --link-origin https://docs.dynatrace.com -o <your-corpus-dir>
```

Expect roughly 4 400 pages. Re-run `driver.py check` afterwards; it should
report nothing changed.

## On the corpus, plainly

Building a local copy of a vendor's public documentation for your own reference
is ordinary. Redistributing it is not, and this repository does not.

If you build a corpus with these tools, it is yours to read, grep and search.
Do not republish it. Every converted page keeps its `source_url` in frontmatter
so the origin is never in doubt.

The short quotations inside `references/` are attributed to the page they came
from and are there as evidence for a specific claim — usually that the
documentation says something contradictory. They remain the property of their
author.

## Status and limits

Built and measured against docs.dynatrace.com and developer.dynatrace.com during
August 2026.

- **The gotchas decay.** Each says which page and which date it was measured
  against. When Dynatrace fixes something, the entry becomes wrong. Check the
  date before quoting one.
- **The UI map is documented routes, not the interface.** It proves the paths it
  contains; it never proves a menu has no other children.
- **`run-dynatrace-docs` may move.** A general-purpose successor that handles
  any documentation site is in progress. If that lands, this driver stays as the
  Dynatrace-specific wrapper and the generic work moves out.

## Licence

MIT for the skills, references and tooling in this repository. Quoted passages
belong to their original authors. See `LICENSE`.
