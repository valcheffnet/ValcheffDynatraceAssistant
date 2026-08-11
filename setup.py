# -*- coding: utf-8 -*-
"""Substitute the {{PLACEHOLDER}} paths and install the skills.

The repository ships templated paths because Claude Code resolves none at load
time — an installed skill needs real absolute paths. So the substitution happens
here, once, and the result is written into ~/.claude/skills/.

Writes only to the Claude skills directory and to config.json beside this file.
Run with --dry-run to see what it would do.
"""
import argparse
import io
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "config.json")

KEYS = [
    ("CLAUDE_HOME", "Your Claude home", "~/.claude"),
    ("SKILL_DIR", "Where the dynatrace skill will be installed",
     "{CLAUDE_HOME}/skills/dynatrace"),
    ("PROJECT_ROOT", "Directory holding your corpora", ""),
    ("DOCS_CORPUS", "Your docs.dynatrace.com corpus", "{PROJECT_ROOT}/docs"),
    ("DEV_CORPUS", "Your developer.dynatrace.com corpus",
     "{PROJECT_ROOT}/developer"),
]


def norm(p):
    return os.path.abspath(os.path.expanduser(p)).replace("\\", "/")


def ask(existing):
    cfg = dict(existing)
    for key, prompt, default in KEYS:
        d = default.format(**cfg) if default and "{" in default else default
        cur = cfg.get(key, d)
        try:
            v = input("%s\n  [%s]: " % (prompt, cur or "required")).strip()
        except EOFError:
            v = ""
        cfg[key] = norm(v or cur) if (v or cur) else ""
        if not cfg[key]:
            sys.exit("%s is required." % key)
    return cfg


def install(cfg, dry):
    pairs = [("skills/dynatrace", cfg["SKILL_DIR"])]
    text_ext = {".md", ".py", ".json", ".sh", ".txt", ".yml", ".yaml"}
    total = 0
    for rel, dest in pairs:
        src = os.path.join(HERE, rel)
        if not os.path.isdir(src):
            print("missing in repo: %s" % rel)
            continue
        for dp, dirs, fs in os.walk(src):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fn in fs:
                sp = os.path.join(dp, fn)
                out = os.path.join(dest, os.path.relpath(sp, src))
                total += 1
                if dry:
                    continue
                os.makedirs(os.path.dirname(out), exist_ok=True)
                if os.path.splitext(fn)[1].lower() in text_ext:
                    t = io.open(sp, encoding="utf-8", errors="ignore").read()
                    for k, v in cfg.items():
                        t = t.replace("{{%s}}" % k, v)
                    io.open(out, "w", encoding="utf-8",
                            newline="\n").write(t)
                else:
                    shutil.copy2(sp, out)
        print("%s -> %s" % (rel, dest))
    print("%s %d file(s)" % ("would install" if dry else "installed", total))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    existing = {}
    if os.path.exists(CONFIG):
        existing = json.load(io.open(CONFIG, encoding="utf-8"))
        print("Using %s as defaults.\n" % CONFIG)

    cfg = ask(existing)
    missing = [k for k in ("DOCS_CORPUS", "DEV_CORPUS")
               if not os.path.exists(cfg[k])]
    if missing:
        print("\nNot there yet: %s" % ", ".join(missing))
        print("Fine before you build a corpus. The skill loads either way and "
              "says when an answer would need one.\n")

    if not args.dry_run:
        io.open(CONFIG, "w", encoding="utf-8", newline="\n").write(
            json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
        print("wrote %s (git-ignored)\n" % CONFIG)
    install(cfg, args.dry_run)

    if not args.dry_run:
        print("\nNext: build a corpus at %s, then ask Claude a Dynatrace\n"
              "question — the skill triggers on its own."
              % cfg["DOCS_CORPUS"])


main()
