# -*- coding: utf-8 -*-
"""Extract UI navigation paths from both corpora, with provenance.

A destination is reachable by more than one path, and one parent leads to many
destinations, so this is a graph and not a tree. The extraction therefore keys
on (destination, full path) pairs and lets both sides repeat.

Provenance is the point. Every path carries the page it came from, that page's
`generation` (classic or latest) and its `lastmod`, because on a tenant that
runs both layers an unlabelled path is worse than none — it looks authoritative
and sends the reader to a menu they do not have.

Sources scanned: prose, and Stage 4 transcription blocks. The blocks matter:
menu paths are routinely shown in a screenshot while the prose says only
"go to Settings".
"""
import glob
import io
import json
import os
import re
import sys

# **A** > **B** > **C**  — the doc-site's own convention for a menu path.
BOLD_PATH = re.compile(
    r'\*\*([^*\n]{1,45}?)\*\*'
    r'((?:\s*(?:>|›|→)\s*\*\*[^*\n]{1,45}?\*\*){1,5})')
SEG = re.compile(r'\*\*([^*\n]{1,45}?)\*\*')
FM = re.compile(r'^---\n(.*?)\n---', re.S)
S4 = re.compile(r'<!--\s*stage4:start.*?<!--\s*stage4:end\s*-->', re.S)

# Openers that mark the first segment as a UI entry point rather than emphasis.
ENTRY = re.compile(r'(?i)\b(go to|navigate to|open|select|choose|from)\s*$')

NOISE = re.compile(
    r'(?i)^(note|tip|important|warning|caution|example|required|optional|'
    r'yes|no|true|false|new|preview|early access|deprecated|latest dynatrace|'
    r'dynatrace classic)$')


def clean(s):
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'^[\s>›→]+|[\s>›→:.,]+$', '', s)
    s = re.sub(r'\s*\((?:latest|new|preview|early access)\)\s*$', '', s, flags=re.I)
    return s.strip()


def scan(root, corpus):
    rows = []
    for p in glob.glob(os.path.join(root, "**", "*.md"), recursive=True):
        rel = os.path.relpath(p, root).replace("\\", "/")
        if rel.startswith("_"):
            continue
        t = io.open(p, encoding="utf-8", errors="ignore").read()
        m = FM.match(t)
        fm = m.group(1) if m else ""
        gen = (re.search(r'^generation: "(.*?)"', fm, re.M) or [None, "unknown"])
        gen = gen[1] if isinstance(gen, list) else gen.group(1)
        lm = re.search(r'^lastmod: "(.*?)"', fm, re.M)
        lm = lm.group(1) if lm else ""
        in_s4 = set()
        for b in S4.finditer(t):
            in_s4.update(range(b.start(), b.end()))
        for mm in BOLD_PATH.finditer(t):
            segs = [clean(mm.group(1))] + [clean(x) for x in SEG.findall(mm.group(2))]
            segs = [s for s in segs if s and not NOISE.match(s)]
            if len(segs) < 2:
                continue
            before = t[max(0, mm.start() - 30):mm.start()]
            rows.append({
                "corpus": corpus, "file": rel, "generation": gen, "lastmod": lm,
                "path": segs, "dest": segs[-1], "root": segs[0],
                "from_screenshot": mm.start() in in_s4,
                "explicit_entry": bool(ENTRY.search(before)),
            })
    return rows


def main():
    rows = scan("{{DOCS_CORPUS}}", "docs")
    rows += scan("{{DEV_CORPUS}}", "developer")
    out = sys.argv[1]
    io.open(out, "w", encoding="utf-8", newline="\n").write(
        json.dumps(rows, ensure_ascii=False))
    import collections
    print("raw paths        : %d" % len(rows))
    print("distinct paths   : %d" % len({tuple(r["path"]) for r in rows}))
    print("distinct dests   : %d" % len({r["dest"] for r in rows}))
    print("from screenshots : %d" % sum(1 for r in rows if r["from_screenshot"]))
    print()
    print("by generation:", dict(collections.Counter(r["generation"] for r in rows)))
    print()
    print("top roots:")
    for k, v in collections.Counter(r["root"] for r in rows).most_common(15):
        print("  %-34s %4d" % (k[:34], v))


main()
