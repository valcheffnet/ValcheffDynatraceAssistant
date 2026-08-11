# -*- coding: utf-8 -*-
"""Build a greppable section index for a corpus.

The measured problem: an agent greps, learns that page X mentions the term, and
then Reads page X whole. Median page 1779 words; median section 65. So the
Read step throws away roughly 27 words for every one it needed.

The index is one row per H2/H3: doc_path, start line, end line, word count,
heading. It is meant to be **grepped, never read** — 50 000 rows is far too big
to load, which is exactly why it is a TSV and not prose. Grep returns the rows
that match, each row carries a line range, and the agent Reads that range.

Zero model tokens to build or maintain: one pass over the corpus.
"""
import glob
import io
import os
import re
import sys

ROOT = sys.argv[1]
DEST = sys.argv[2]
H = re.compile(r'^(#{2,3})\s+(.*?)\s*$')

rows = []
for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)):
    rel = os.path.relpath(p, ROOT).replace("\\", "/")
    if rel.startswith("_"):
        continue
    lines = io.open(p, encoding="utf-8", errors="ignore").read().split("\n")
    marks = [(i, m.group(1), m.group(2)) for i, l in enumerate(lines)
             for m in [H.match(l)] if m]
    if not marks:
        continue
    bounds = [i for i, _, _ in marks] + [len(lines)]
    for (start, level, title), end in zip(marks, bounds[1:]):
        body = " ".join(lines[start:end])
        # strip the anchor markers the corpus injects, they are not content
        title = re.sub(r'<a id="[^"]*"></a>', "", title).strip()
        if not title:
            continue
        rows.append((rel, start + 1, end, len(body.split()),
                     len(level), title))

with io.open(DEST, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("doc_path\tstart\tend\twords\tlevel\theading\n")
    for r in rows:
        fh.write("%s\t%d\t%d\t%d\th%d\t%s\n" % r)

kb = os.path.getsize(DEST) / 1024
print("%s: %d sections from %s  (%.0f KB)" % (DEST, len(rows), ROOT, kb))
