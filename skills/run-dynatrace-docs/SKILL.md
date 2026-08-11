---
name: run-dynatrace-docs
description: Build, refresh, verify and inspect the two local Dynatrace Markdown corpora - docs.dynatrace.com at {{DOCS_CORPUS}} and developer.dynatrace.com at {{DEV_CORPUS}}. Use when asked to run or check a corpus, see what changed upstream, refresh or re-convert pages, detect new/changed/removed pages, verify corpus integrity, check whether images changed, or get per-section file/word/image counts.
---

The unit is a **corpus, not a process** — 4403 Markdown pages converted from
`docs.dynatrace.com`, plus a second corpus of 205 pages from
`developer.dynatrace.com` at `{{DEV_CORPUS}}`, plus the tooling
that produced them. There is nothing to
launch; driving it means asking it questions. The handle is
`.claude/skills/run-dynatrace-docs/driver.py`, run under the markitdown venv.

All paths below are relative to `{{PROJECT_ROOT}}/`.

## Prerequisites

No install step. Two things must already exist:

```bash
{{VENV_PYTHON}} --version
# → Python 3.13.14
ls {{MD_WORKFLOW}}/url2md.py {{MD_WORKFLOW}}/imgindex.py
```

**Use that interpreter, not `python`.** The system Python is 3.14.4 and has no
`requests`:

```bash
python -c "import bs4, requests"
# → ModuleNotFoundError: No module named 'requests'
```

## Run (agent path)

```bash
cd {{PROJECT_ROOT}}
{{VENV_PYTHON}} .claude/skills/run-dynatrace-docs/driver.py <subcommand>
```

| subcommand | what it does | network | time |
|---|---|---|---|
| `stats` | per-section file / word / stage4-block counts | no | ~10s |
| `verify` | full integrity check, exits 1 on any problem | no | ~90s |
| `anchors` | do `page.md#anchor` links land on something | no | ~90s |
| `check` | new / changed / removed pages vs the live sitemap | yes | ~15s |
| `devcheck` | same for the **developer** corpus, by content hash | yes | ~15s |
| `images` | MD5 drift over all 3296 image URLs | yes | ~40s |

Exit codes: 0 clean, 1 drift or integrity failure, 2 unknown subcommand.
`check` exiting 1 is normal — upstream moves. `verify` exiting 1 is not; it
means the corpus is damaged.

### stats

```bash
{{VENV_PYTHON}} .claude/skills/run-dynatrace-docs/driver.py stats
```

Last run (2026-08-05, after the refresh) ended:

```
TOTAL                          4403    7834100     2750
```

### verify

```bash
{{VENV_PYTHON}} .claude/skills/run-dynatrace-docs/driver.py verify
```

Checks every invariant the corpus build established. Last run:

```
files: 4403   stage4 blocks: 2750 in 949 files   unique image URLs: 2265
internal .md links: 30568   dangling: 0
bad keys: 0   odd fences: 0   unpaired: 0   CRLF: 0   orphaned: 0
URLs with more than one distinct transcription: 0

VERDICT: CLEAN
```

The load-bearing line is the last one. A URL carrying two different
transcriptions means an image was described twice and inconsistently — the
corpus then contradicts itself and greps return whichever copy they hit first.

### check

```bash
{{VENV_PYTHON}} .claude/skills/run-dynatrace-docs/driver.py check
```

Compares the live sitemap's `lastmod` against each local page's frontmatter.
Run on 2026-08-05 *before* the refresh, against the 2026-08-04 snapshot:

```
upstream sitemap: 4402 pages
local corpus:     4390 pages

NEW upstream:     13
CHANGED upstream: 26
REMOVED upstream (local file is now stale): 0
```

Those 39 pages have since been converted, so a run today reports 0/0/0.

Removed-page detection exists nowhere else. The corpus never shrinks on its
own, so a page deleted upstream stays on disk and keeps answering greps with
content Dynatrace has withdrawn.

### anchors

```bash
{{VENV_PYTHON}} .claude/skills/run-dynatrace-docs/driver.py anchors
```

Separate from `verify` on purpose: a missing anchor is a navigation nuisance,
not corpus damage, and most of what is left is Dynatrace's own dead links.
Last run:

```
anchored internal links: 8992
anchor not found in target: 1128 (12.5%)
```

It was 46.3% before the ids were backfilled. Of the 436 distinct
(page, anchor) pairs still unresolved, **311 do not exist on the live page
either** - checked by fetching each target - and 125 are ours to fix, never
more than 5 on any one page.

To refill after adding pages:

```bash
{{VENV_PYTHON}} {{MD_WORKFLOW}}/anchorfill.py {{DOCS_CORPUS}} --apply --workers 16
```

Idempotent, one GET per page, inserts only `<a id="...">` lines. Omit
`--apply` for a dry run. `url2md.py --docsite` now does the same during
conversion, so this is only needed for pages converted before 2026-08-05.

### images

```bash
{{VENV_PYTHON}} .claude/skills/run-dynatrace-docs/driver.py images
```

Wraps `imgindex.py`. Bare run reports drift against
`docs/_reports/image-index.tsv`; pass `--write` to adopt the current state as
the new baseline. Last run: `new 0, no longer used 0, CONTENT CHANGED 0`.

### devcheck

Drift for the developer corpus. `check` cannot serve it: that sitemap has no
`lastmod`, so there is no date to compare. Hashing replaces it, in two tiers,
because neither works alone.

**Tier 1 hashes the raw HTML.** 204 threaded GETs, ~13 s, no conversion.
Measured byte-stable across repeated fetches (8/8 pages, 2026-08-06), so it is a
real signal — but it fires on things that never reach the Markdown. The one that
matters is a site rebuild renaming the hashed JS bundle every page references:
that flips all 204 hashes at once with no content change anywhere.

**Tier 2 converts only what tier 1 flagged** and compares a hash of the Markdown
body, with frontmatter and `stage4` blocks excluded — `converted:` changes every
run, and stage4 blocks are ours rather than upstream's, so including either
would report a change on every comparison. A page that fails both tiers has
genuinely changed.

```bash
# report drift
{{VENV_PYTHON}} .claude/skills/run-dynatrace-docs/driver.py devcheck

# adopt the current state as the baseline (after a deliberate refresh)
{{VENV_PYTHON}} .claude/skills/run-dynatrace-docs/driver.py devcheck --baseline
```

Baseline lives at `{{DEV_CORPUS}}/_reports/page-hashes.tsv`, one
row per page: `doc_path`, raw-HTML md5, body md5. Keeping it inside the corpus
means there is no side-car state to drift out of sync.

Output distinguishes the two outcomes explicitly. `changed: 0` alongside
"N page(s) differed in raw HTML but not in content" is the rebuild case and
exits 0 — nothing to do. Anything under `changed:` is real.

Verified 2026-08-06 by corrupting one stored tier-1 hash: tier 1 flagged the
page, tier 2 converted it, found the body identical, and reported the
false-positive line with exit 0.


## Refreshing pages

Not a driver subcommand — it writes to the corpus, so it stays an explicit
call. **`MSYS_NO_PATHCONV=1` is not optional under Git Bash**; see the first
gotcha.

```bash
cd {{MD_WORKFLOW}}
MSYS_NO_PATHCONV=1 {{VENV_PYTHON}} url2md.py \
  https://docs.dynatrace.com/sitemap.xml --sitemap --mirror \
  --strip-prefix /docs --frontmatter --skip-unchanged --docsite \
  --link-prefix /docs --link-origin https://docs.dynatrace.com \
  --external-index \
  -o "{{DOCS_CORPUS}}" \
  --filter 'grail/dynatrace-query-language$' \
  --report "{{DOCS_CORPUS}}/_reports/refresh.json"
```

Verified against the real corpus — with a filter matching an unchanged page it
prints `external index: 1 captured page(s)` and `[SKIP] ... (lastmod
2026-01-28)`, writing nothing. Swap the `--filter` for a page from `check`, or
drop it entirely to refresh everything `--skip-unchanged` finds stale. Always
run `verify` afterwards — see the orphan gotcha below.

Its output tells you what happened per page:

```
[OK] ...\services-app.md  (5930w, ..., stage4-7, latest) | 8 image(s) queued
     for Stage 4 (vision); 4 auto-skipped | 1 orphaned stage4 block(s)
```

## Gotchas

- **Git Bash rewrites `/docs` into `E:/Program Files/Git/docs`.** MSYS path
  conversion mangles any argument that starts with a slash, before Python sees
  it. `--strip-prefix` and `--link-prefix` then match nothing, and the run
  *succeeds* — with an extra `docs/` level in the tree and link rewriting
  silently disabled. Prove it to yourself:

  ```bash
  {{VENV_PYTHON}} -c "import sys; print(sys.argv[1:])" --link-prefix /docs
  # → ['--link-prefix', 'E:/Program Files/Git/docs']
  ```

  Prefix every `url2md.py` call with `MSYS_NO_PATHCONV=1`, or run it from
  PowerShell, which does not do this. `url2md.py` now refuses a mangled prefix
  outright rather than ignoring it, so a forgotten `MSYS_NO_PATHCONV=1` exits 1
  with an explanation instead of quietly producing a wrong corpus.

- **`--strip-prefix /docs` is required, and `-o` is the corpus directory.**
  `-o {{DOCS_CORPUS}} --strip-prefix /docs` gives
  `docs/platform/grail/...` and `doc_path: "platform/grail/..."`, matching what
  is already on disk. Dropping the strip adds a `docs/` level and writes
  `doc_path: "docs/platform/..."`, which does not match any existing page.

- **Refreshing a page whose upstream images changed orphans a transcription.**
  Observed on `services-app.md`: 8 stage4 markers went in, 7 survived, and the
  eighth became an orphan because its image URL
  (`services-app-filtering-3840-9fb2e6e569.png`) no longer appears on the
  page. The transcription is preserved rather than deleted — deliberately, it
  is expensive — but it now keys to nothing. `verify` reports it as both
  `ORPHANED` and `KEY WITHOUT IMAGE`. The fix is to re-transcribe the page's
  new images and drop the orphan, not to delete the marker and call it clean.

- **`imgindex.py --help` is not help.** It ignores unknown arguments and runs
  the full 40-second network scan. Its only real flag is `--write`.

- **`_external/` pages are permanently absent from the sitemap** — they were
  captured on purpose from outside it. `check` filters them out of the removed
  list; without that filter it reports a phantom removal on every run.

- **The site's heading ids are not derivable from the heading text.**
  "View health alerts and warning signals" is `#health-alerts`; "New Explorer
  view Early Access" is `#explorer-early-access` because the badge is markup,
  not words; collapsible section headers are `<span data-dt-component="Heading">`
  rather than `<h2>`. Markdown keeps the anchor in the link and loses the id,
  so before the backfill 46% of anchored cross-links pointed at nothing.
  17 643 `<a id="...">` markers now carry them. Do not delete those lines as
  noise - they are the only thing making `#anchor` navigation work locally.

- **Counting only the section directories loses 14 files.** The section
  landing pages (`analyze-explore-automate.md`, `deliver.md`, …) sit at the
  corpus root. 4376 + 14 = 4390. `stats` counts them as a separate row.

## Troubleshooting

- **`--strip-prefix='E:/Program Files/Git/docs' looks like an MSYS-mangled
  path`** — you forgot `MSYS_NO_PATHCONV=1`. That message is the fix working;
  before it existed the run silently produced a wrong tree.

- **`targets: 0` from `url2md.py`** — a `--filter` regex that matches nothing.
  The filter runs against the full URL; anchor it with `$` and copy the path
  from a `check` line. (`targets: 0` used to also mean "you passed the sitemap
  index" — `url2md.py` follows it now, so both
  `https://docs.dynatrace.com/sitemap.xml` and `/docs/sitemap.xml` work.)

- **`VERDICT: FAILED` with `ORPHANED` right after a refresh** — expected when
  upstream changed that page's images. Re-transcribe; do not just delete the
  block.

- **`ModuleNotFoundError: No module named 'requests'`** — you used the system
  `python`. Use `{{VENV_PYTHON}}`.

## Related

- `docs/_reports/RESUME.md` — how the corpus was built, full state
- `docs/_reports/UPDATE-PLAN.md` — the refresh procedure this driver implements
- `{{MD_WORKFLOW}}/WORKFLOW.md` — every lesson from the build,
  including the conversion bugs and their fixes
