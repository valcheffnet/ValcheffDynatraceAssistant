# -*- coding: utf-8 -*-
"""Build the UI map: a destination-keyed navigation index, split by generation.

Shape, because it decides everything else: this is a **graph, not a tree**. One
destination is reachable by several paths, and one parent leads to many
destinations. So the index is keyed on (generation, destination) and carries a
list of paths, rather than pretending there is a single canonical route.

Confidence, because the extraction is heuristic. A bold run preceded by "go to"
is a menu path; a bold run in the middle of a sentence may be emphasis. Roots
are scored by how often they appear behind such an opener, and each row carries
the verdict rather than being silently dropped — a dropped path cannot be
argued with later.

Provenance, because on a tenant running both layers an unlabelled path is worse
than none. Every row carries generation, the newest lastmod among its sources,
and how many pages attest it.
"""
import collections
import io
import json
import sys

RAW, TSV = sys.argv[1], sys.argv[2]
rows = json.load(io.open(RAW, encoding="utf-8"))

# --- score roots by how often they sit behind an explicit opener -----------
tot = collections.Counter()
opened = collections.Counter()
for r in rows:
    tot[r["root"]] += 1
    if r["explicit_entry"]:
        opened[r["root"]] += 1
ENTRY_ROOTS = {k for k in tot
               if tot[k] >= 3 and opened[k] / tot[k] >= 0.5}

# Pages about spreadsheets, IDEs and other vendors' UIs contribute bold runs
# that look like menus. Named rather than pattern-matched: the list is short and
# a wrong pattern would silently delete real Dynatrace paths.
FOREIGN = {"Data", "File", "Insert", "Format", "Tools", "View", "Help",
           "Edit", "Window", "Run", "Build", "Terminal"}


def confidence(r):
    if r["root"] in FOREIGN and not r["explicit_entry"]:
        return "foreign"
    if r["explicit_entry"] and r["root"] in ENTRY_ROOTS:
        return "high"
    if r["explicit_entry"] or r["root"] in ENTRY_ROOTS:
        return "medium"
    return "low"


# --- collapse duplicates, keep every distinct path per destination ---------
agg = {}
for r in rows:
    key = (r["generation"], r["dest"], " > ".join(r["path"]))
    a = agg.setdefault(key, {
        "generation": r["generation"], "dest": r["dest"],
        "path": " > ".join(r["path"]), "depth": len(r["path"]),
        "root": r["root"], "files": set(), "lastmod": "",
        "screenshot": False, "conf": "low", "corpus": r["corpus"]})
    a["files"].add(r["file"])
    a["lastmod"] = max(a["lastmod"], r["lastmod"] or "")
    a["screenshot"] = a["screenshot"] or r["from_screenshot"]
    order = {"high": 3, "medium": 2, "low": 1, "foreign": 0}
    c = confidence(r)
    if order[c] > order[a["conf"]]:
        a["conf"] = c

out = [a for a in agg.values() if a["conf"] != "foreign"]
out.sort(key=lambda a: (a["generation"], a["dest"].lower(), -a["depth"]))

with io.open(TSV, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("generation\tconfidence\tdestination\tpath\tdepth\t"
             "attested_by\tnewest_lastmod\tfrom_screenshot\texample_source\n")
    for a in out:
        fh.write("%s\t%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\n" % (
            a["generation"], a["conf"], a["dest"], a["path"], a["depth"],
            len(a["files"]), a["lastmod"] or "-",
            "yes" if a["screenshot"] else "no", sorted(a["files"])[0]))

# --- what the reference needs to say --------------------------------------
by_dest = collections.defaultdict(list)
for a in out:
    by_dest[(a["generation"], a["dest"])].append(a)
multi = {k: v for k, v in by_dest.items() if len(v) > 1}

print("rows written        : %d" % len(out))
print("distinct destinations: %d" % len(by_dest))
print("reachable >1 way    : %d" % len(multi))
print("confidence          :", dict(collections.Counter(a["conf"] for a in out)))
print("generation          :", dict(collections.Counter(a["generation"] for a in out)))
print()
print("destinations with the most alternative routes:")
for k, v in sorted(multi.items(), key=lambda kv: -len(kv[1]))[:8]:
    print("  [%s] %s  — %d routes" % (k[0][:7], k[1][:44], len(v)))
    for a in v[:3]:
        print("        %s   (%s, %s)" % (a["path"][:74], a["conf"], a["lastmod"] or "-"))
