# ValcheffDynatraceAssistant

A Claude Code skill that answers Dynatrace questions from a distilled reference
layer instead of recollection.

**Not affiliated with, endorsed by, or produced by Dynatrace LLC.** "Dynatrace"
is used here only to name the product this skill is about.

---

## What this is

~39 000 words of distilled reference across 30 files, 85 recorded places where
the official documentation is wrong or contradicts itself, and a map of 1 015 UI
navigation routes split by platform generation.

The value is the judgement layer. Anyone can read the docs; the work was in
measuring where they mislead.

## What you get

- **30 references** covering DQL and DPL, Grail, OpenPipeline, IAM, OneAgent and
  ActiveGate, ingest paths, dashboards, workflows, SLOs, AppSec, licensing, the
  API surface, config as code, and AppEngine app development.
- **`references/gotchas.md`** — 85 numbered entries, each a measured case where
  the documentation does not work as printed: a rule contradicted by the
  vendor's own examples, a field deprecated in one place and current in another,
  a limit stated twice with different numbers. This part does not exist anywhere
  else.
- **`references/ui-map.md`** — how to answer "where is this menu" without
  guessing. Keyed by destination and split Classic against latest, because a
  migrated tenant runs both and a path for the wrong one is worse than none. It
  also separates a genuine second route from a menu that simply moved.
- **`references/corpus-map.md`** — how the documentation is laid out, which
  sections are maintained and which are years stale, and how to search it.
- **`evals/`** — three rounds of evaluation with the questions, the expected
  answers, and the results. Including the first round, which measured nothing
  and says so.

## The corpus

For anything its own references do not cover, the skill greps a local Markdown
copy of `docs.dynatrace.com` and `developer.dynatrace.com`. **That copy is
yours to build** — the repository holds knowledge about the documentation, not
the documentation itself, and nothing here fetches anything.

Any HTML-to-Markdown pipeline will do. What the skill expects:

- a mirrored directory tree matching the site's URL paths
- one `.md` per page, with the source URL in frontmatter

For scale, the corpus this skill was measured against:

| | pages | words |
|---|---:|---:|
| `docs.dynatrace.com` | 4 437 | 7 867 499 |
| `developer.dynatrace.com` | 205 | 1 982 166 |
| **together** | **4 642** | **9 849 665** |

Those figures are from August 2026 and will drift as the sites do. They are
here so you know what to expect: about 70 MB of Markdown on disk.

Two shell variables, `DT_DOCS` and `DT_DEV`, tell the skill where that copy
lives; they are documented at the top of `references/corpus-map.md`. If you have
no corpus yet the skill still loads — it just tells you when an answer would
need one, instead of inventing it.

## Install

```bash
git clone https://github.com/valcheffnet/ValcheffDynatraceAssistant.git
cp -r ValcheffDynatraceAssistant/skills/dynatrace ~/.claude/skills/
```

That is all of it — the skill is Markdown, read in place.

**It works with GitHub Copilot too.** Agent Skills is an open standard, and
`~/.claude/skills/` is one of the directories Copilot reads, so a single copy
serves both. See [INSTALL.md](INSTALL.md) for Copilot's own paths, the Windows
form, how to point the skill at a corpus, and how to check it loaded.

## Status and limits

Built and measured against docs.dynatrace.com and developer.dynatrace.com during
August 2026.

- **The gotchas decay.** Each records the page and the date it was measured
  against. When Dynatrace fixes something, the entry becomes wrong. Check the
  date before quoting one.
- **The UI map is documented routes, not the interface.** It proves the paths it
  contains; it never proves a menu has no other children. Where it is silent,
  the honest answer is to say so and ask for a screenshot.
- **Classic and latest both count.** Classic has no published end-of-life date,
  and a migrated tenant carries both layers at once. The skill is built to
  answer for whichever one you are actually looking at, or to ask which.

## Licence

MIT for the skill, references and evaluation data in this repository. The short
quoted passages inside `references/` are attributed to the page they came from
and remain the property of their author. See `LICENSE`.
