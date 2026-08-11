# Install

Three steps. Copy a directory, set two variables, ask one question.

## 1. Copy the skill

```bash
cp -r skills/dynatrace ~/.claude/skills/
```

Windows PowerShell:

```powershell
Copy-Item -Recurse skills\dynatrace "$env:USERPROFILE\.claude\skills\"
```

That is the whole installation. Claude Code picks the skill up on the next
session and triggers it on any Dynatrace question.

## 2. Point it at a corpus, if you have one

The skill answers from its own references first. For anything they do not
cover, it greps a local Markdown copy of the Dynatrace documentation that
**you** build — this repository does not ship one and does not fetch one.

Two shell variables tell it where that copy lives:

```bash
export DT_DOCS=/path/to/your/docs.dynatrace.com/corpus
export DT_DEV=/path/to/your/developer.dynatrace.com/corpus
```

```powershell
$env:DT_DOCS = "E:/some/path/docs"
$env:DT_DEV  = "E:/some/path/developer"
```

Put them in your shell profile so they survive a new terminal. They are also
documented at the top of `references/corpus-map.md`, which is where the skill
looks for them.

**Skip this step if you have no corpus.** The skill still works — it just says
when an answer would need one, instead of inventing it.

## 3. Check it took

Ask Claude something narrow enough that only the skill knows it:

> In Dynatrace DQL, what is the default length limit on the `LD` matcher?

A correct answer names 4096 and the `{1,8192}` quantifier workaround. A vague
one means the skill did not load — check that
`~/.claude/skills/dynatrace/SKILL.md` exists and start a fresh session.

## What the corpus should look like

If you build one, the skill expects:

- a directory tree mirroring the site's URL paths
- one `.md` per page
- the page's source URL in YAML frontmatter

Roughly 4 400 pages for docs.dynatrace.com, 205 for developer.dynatrace.com.
Any HTML-to-Markdown pipeline that produces that shape will do.

Building a local copy of public documentation for your own reference is
ordinary. Redistributing it is not — see `README.md`.

## Uninstall

```bash
rm -rf ~/.claude/skills/dynatrace
```

That is the only place the skill lives.
