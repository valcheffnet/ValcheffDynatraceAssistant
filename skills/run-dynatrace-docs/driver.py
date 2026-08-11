"""Driver for the docs.dynatrace.com Markdown corpus.

The "app" here is a corpus, not a process, so driving it means asking it
questions and getting answers you can act on:

    check    what changed upstream since the snapshot (read-only, network)
    devcheck same, for the developer.dynatrace.com corpus, by content hash
    indexes  rebuild the section index and the UI map (offline)
    verify   is the corpus internally consistent (offline)
    anchors  do #anchors in cross-page links resolve (offline)
    images   have any images changed (network, ~50s)
    stats    per-section file/word/image counts (offline)

Run everything through the markitdown venv python, because `check` and the
conversion step import url2md, which needs requests + bs4:

    {{VENV_PYTHON}} \
        .claude/skills/run-dynatrace-docs/driver.py <subcommand>

Exit codes: 0 = clean, 1 = drift or integrity failure, 2 = usage error.
`check` returning 1 is normal and expected - upstream moves. `verify`
returning 1 is not; it means the corpus is damaged.
"""
import collections
import hashlib
import io
import os
import shutil
import tempfile
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = "{{DOCS_CORPUS}}"
TOOLS = "{{MD_WORKFLOW}}"
VENV = "{{VENV_PYTHON}}"
SITEMAP = "https://docs.dynatrace.com/sitemap.xml"

# Second corpus: developer.dynatrace.com. Flat sitemap, no lastmod, so drift is
# detected by hashing rather than by date. Only these subtrees are mirrored;
# design/ (364 pages of the Strato design system) is deliberately excluded.
DEV_ROOT = "{{DEV_CORPUS}}"
DEV_SITEMAP = "https://developer.dynatrace.com/sitemap.xml"
DEV_SUBTREES = ("develop/", "quickstart/", "plan/", "release-notes/")
DEV_HASHES = DEV_ROOT + "/_reports/page-hashes.tsv"

# How many URLs to list per category. A truncated report reads as a complete
# one; raise this rather than trusting "... and N more".
LIMIT = 500

# docs.dynatrace.com serves 403 to anything that looks like a bot.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

FM_RE = re.compile(r'^---\r?\n(.*?)\r?\n---', re.S)
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+\.md)(?:#[^)]*)?\)')


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def sitemap_urls():
    """Return {url: lastmod}. The top-level sitemap is an index, not a list."""
    out = {}
    root = ET.fromstring(fetch(SITEMAP))
    children = [e.text for e in root.iter(NS + "loc")]
    if root.tag.endswith("sitemapindex"):
        for child in children:
            # /managed/ is the on-prem product, deliberately not in the corpus.
            if "/managed/" in child:
                continue
            sub = ET.fromstring(fetch(child))
            for url in sub.iter(NS + "url"):
                loc = url.find(NS + "loc").text.strip()
                lm = url.find(NS + "lastmod")
                out[loc] = (lm.text.strip()[:10] if lm is not None else "")
    return out


def corpus_pages():
    """Return {source_url: (lastmod, relpath)} from the frontmatter."""
    out = {}
    for dp, _, fs in os.walk(ROOT):
        if "_reports" in dp:
            continue
        for fn in fs:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            head = open(p, encoding="utf-8").read(1200)
            m = FM_RE.match(head)
            if not m:
                continue
            fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', m.group(1), re.M))
            if fm.get("source_url"):
                out[fm["source_url"]] = (fm.get("lastmod", ""), rel)
    return out


def cmd_check():
    up = sitemap_urls()
    have = corpus_pages()
    print("upstream sitemap: %d pages" % len(up))
    print("local corpus:     %d pages" % len(have))

    new = sorted(set(up) - set(have))
    # _external/ holds pages deliberately captured from outside the sitemap
    # (product blog posts). They are permanently "missing" upstream and would
    # otherwise show up as removed on every single run.
    gone = sorted(u for u in set(have) - set(up)
                  if not have[u][1].startswith("_external/"))
    changed = sorted(u for u in set(up) & set(have)
                     if up[u] and up[u] > have[u][0])

    print("\nNEW upstream:     %d" % len(new))
    for u in new[:LIMIT]:
        print("   ", u)
    if len(new) > LIMIT:
        print("    ... and %d more" % (len(new) - LIMIT))

    print("\nCHANGED upstream: %d" % len(changed))
    for u in changed[:LIMIT]:
        print("    %s  %s -> %s" % (u, have[u][0], up[u]))
    if len(changed) > LIMIT:
        print("    ... and %d more" % (len(changed) - LIMIT))

    # Removed-page detection: a local file whose source_url left the sitemap.
    # Nothing else reports this - the corpus never shrinks on its own.
    print("\nREMOVED upstream (local file is now stale): %d" % len(gone))
    for u in gone[:LIMIT]:
        print("    %s  <- %s" % (u, have[u][1]))
    if len(gone) > LIMIT:
        print("    ... and %d more" % (len(gone) - LIMIT))

    return 1 if (new or changed or gone) else 0


def cmd_verify():
    sys.path.insert(0, TOOLS)
    import url2md as U

    bad_key = bad_fence = bad_pair = crlf = orphan = 0
    blocks = files = 0
    bodies = collections.defaultdict(set)
    texts = {}

    for dp, _, fs in os.walk(ROOT):
        if "_reports" in dp:      # its own prose quotes the sentinels
            continue
        for fn in fs:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, ROOT).replace("\\", "/")
            raw = open(p, "rb").read()
            if b"\r\n" in raw:
                crlf += 1
                print("CRLF:", rel)
            t = raw.decode("utf-8")
            texts[rel] = t
            if "stage4:orphaned" in t:
                orphan += 1
                print("ORPHANED:", rel)
            s, e = t.count("stage4:start"), t.count("stage4:end")
            if s != e:
                bad_pair += 1
                print("UNPAIRED:", rel, s, e)
            if not s:
                continue
            files += 1
            blocks += s
            imgs = {m.group(2) for m in U.IMG_RE.finditer(t)}
            for m in U.STAGE4_RE.finditer(t):
                u = m.group("url")
                if u not in imgs:
                    bad_key += 1
                    print("KEY WITHOUT IMAGE:", rel, u)
                bodies[u].add(m.group("body").strip())
                if m.group("body").count("```") % 2:
                    bad_fence += 1
                    print("ODD FENCES:", rel, u)

    dangling = 0
    total_links = 0
    for rel, t in texts.items():
        base = os.path.dirname(os.path.join(ROOT, rel))
        for m in LINK_RE.finditer(t):
            href = m.group(1)
            if href.startswith(("http://", "https://")):
                continue
            total_links += 1
            if not os.path.exists(os.path.normpath(os.path.join(base, href))):
                dangling += 1
                if dangling <= 20:
                    print("DANGLING:", rel, "->", href)

    multi = {u: v for u, v in bodies.items() if len(v) > 1}
    print("\nfiles: %d   stage4 blocks: %d in %d files   unique image URLs: %d"
          % (len(texts), blocks, files, len(bodies)))
    print("internal .md links: %d   dangling: %d" % (total_links, dangling))
    print("bad keys: %d   odd fences: %d   unpaired: %d   CRLF: %d   orphaned: %d"
          % (bad_key, bad_fence, bad_pair, crlf, orphan))
    print("URLs with more than one distinct transcription: %d" % len(multi))
    for u in list(multi)[:5]:
        print("   ", u.rsplit("/", 1)[-1], len(multi[u]))

    bad = bad_key + bad_fence + bad_pair + crlf + orphan + dangling + len(multi)
    print("\nVERDICT:", "CLEAN" if not bad else "FAILED (%d problems)" % bad)
    return 1 if bad else 0


def cmd_images():
    # imgindex.py takes no subcommands and ignores unknown flags; a bare run
    # is the drift report, `--write` rewrites the baseline.
    args = [VENV, "imgindex.py"] + [a for a in sys.argv[2:] if a == "--write"]
    return subprocess.call(args, cwd=TOOLS)


def cmd_stats():
    rows = []
    # Section landing pages live at the corpus root, not inside the section
    # directory, so walking only the directories loses 14 files.
    top = [f for f in os.listdir(ROOT) if f.endswith(".md")]
    if top:
        w = img = 0
        for f in top:
            txt = open(os.path.join(ROOT, f), encoding="utf-8").read()
            w += len(txt.split())
            img += txt.count("stage4:start")
        rows.append(("(section landing pages)", len(top), w, img))
    for name in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, name)
        if not os.path.isdir(d) or name == "_reports":
            continue
        n = w = img = 0
        for dp, _, fs in os.walk(d):
            for fn in fs:
                if not fn.endswith(".md"):
                    continue
                n += 1
                t = open(os.path.join(dp, fn), encoding="utf-8").read()
                w += len(t.split())
                img += t.count("stage4:start")
        rows.append((name, n, w, img))
    rows.sort(key=lambda r: -r[1])
    print("%-28s %6s %10s %8s" % ("section", "files", "words", "img"))
    for name, n, w, img in rows:
        print("%-28s %6d %10d %8d" % (name, n, w, img))
    print("%-28s %6d %10d %8d" % ("TOTAL", sum(r[1] for r in rows),
                                  sum(r[2] for r in rows),
                                  sum(r[3] for r in rows)))
    return 0


def cmd_anchors():
    """Do `foo.md#bar` links land on something that exists in foo.md?

    Two things can satisfy an anchor: a heading whose slug matches, or an
    explicit `<a id="bar">` carried over from the site. Dynatrace assigns short
    custom heading ids that the heading text cannot reproduce, so without the
    second kind roughly half of all anchored links point at nothing.
    """
    sys.path.insert(0, TOOLS)
    import url2md as U

    anchored = re.compile(r'\]\(([^)\s]+\.md)#([^)\s]+)\)')
    explicit = re.compile(r'<a\s+id="([^"]+)"')
    cache = {}

    def targets(path):
        if path not in cache:
            try:
                txt = open(path, encoding="utf-8").read()
            except OSError:
                txt = ""
            ids = {m.group(1).lower() for m in explicit.finditer(txt)}
            ids |= {U.slugify_heading(m.group(2))
                    for m in U.HEADING_RE.finditer(txt)}
            cache[path] = ids
        return cache[path]

    total = miss = 0
    per_file = collections.Counter()
    for dp, _, fs in os.walk(ROOT):
        if "_reports" in dp:
            continue
        for fn in fs:
            if not fn.endswith(".md"):
                continue
            src = os.path.join(dp, fn)
            txt = open(src, encoding="utf-8").read()
            for m in anchored.finditer(txt):
                tgt = os.path.normpath(os.path.join(dp, m.group(1)))
                if not os.path.exists(tgt):
                    continue        # file-level breakage is verify's job
                total += 1
                if m.group(2).lower() not in targets(tgt):
                    miss += 1
                    per_file[os.path.relpath(tgt, ROOT).replace("\\", "/")] += 1

    print("anchored internal links: %d" % total)
    print("anchor not found in target: %d (%.1f%%)"
          % (miss, 100.0 * miss / max(total, 1)))
    if per_file:
        print("\nworst targets:")
        for path, n in per_file.most_common(15):
            print("  %4d  %s" % (n, path))
    return 1 if miss else 0



def _dev_urls():
    req = urllib.request.Request(DEV_SITEMAP, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        xml = r.read()
    out = []
    for loc in ET.fromstring(xml).iter(NS + "loc"):
        u = (loc.text or "").strip()
        p = u.replace("https://developer.dynatrace.com/", "").strip("/")
        if any((p + "/").startswith(s) for s in DEV_SUBTREES):
            out.append((p, u))
    return sorted(set(out))


def _md_body(path):
    """Markdown minus frontmatter and minus our own stage4 blocks.

    `converted:` changes on every run and stage4 blocks are authored here, not
    upstream; including either would report a change on every comparison.
    """
    try:
        txt = io.open(path, encoding="utf-8").read()
    except OSError:
        return None
    txt = FM_RE.sub("", txt, count=1)
    txt = re.sub(r'<!--[ \t]*stage4:start.*?<!--[ \t]*stage4:end[ \t]*-->',
                 "", txt, flags=re.S)
    txt = re.sub(r'<!--[ \t]*stage4:(skip|orphaned).*?-->', "", txt)
    return hashlib.md5(re.sub(r'\s+', ' ', txt).strip().encode("utf-8")).hexdigest()


def _fetch_hash(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            return hashlib.md5(r.read()).hexdigest()
    except Exception as e:
        return "ERROR:" + type(e).__name__


def cmd_devcheck():
    """Drift for the developer corpus. `--baseline` rewrites the stored hashes."""
    write_baseline = "--baseline" in sys.argv

    urls = _dev_urls()
    print("sitemap pages in scope: %d" % len(urls))

    have = {}
    if os.path.exists(DEV_HASHES):
        for n, line in enumerate(io.open(DEV_HASHES, encoding="utf-8")):
            parts = line.rstrip("\n").split("\t")
            # Row 0 is the column header. Without this the header lands in the
            # baseline as a page called "doc_path" and is reported as removed
            # upstream on the very next run.
            if n == 0 and parts[0] == "doc_path":
                continue
            if len(parts) == 3:
                have[parts[0]] = (parts[1], parts[2])

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as ex:
        html = dict(zip([p for p, _ in urls],
                        ex.map(_fetch_hash, [u for _, u in urls])))

    errors = sorted(p for p, h in html.items() if h.startswith("ERROR:"))
    on_disk = {p for p, _ in urls
               if os.path.exists(os.path.join(DEV_ROOT, *p.split("/")) + ".md")}

    new = [p for p, _ in urls if p not in on_disk]
    removed = sorted(set(have) - {p for p, _ in urls})
    suspect = [p for p, _ in urls
               if p in have and p in on_disk and html.get(p) != have[p][0]
               and not html.get(p, "").startswith("ERROR:")]

    # Tier 2 — only the pages tier 1 flagged, so a site rebuild that renames a
    # bundled asset costs one conversion pass, not a false "everything changed".
    changed = []
    if suspect and not write_baseline:
        print("tier 1 flagged %d page(s); converting them to compare content"
              % len(suspect))
        rx = "|".join(re.escape(p) + "/?$" for p in suspect)
        # Outside the corpus, and removed in `finally`. Written inside it, a run
        # that reported drift left a full shadow copy behind — every corpus walk
        # then counted 409 files instead of 205, and every grep hit twice.
        tmp = tempfile.mkdtemp(prefix="devcheck-")
        try:
            subprocess.run([VENV, os.path.join(TOOLS, "url2md.py"), DEV_SITEMAP,
                            "--sitemap", "--mirror", "--frontmatter", "--docsite",
                            "--absolutize-links", "--inline-assets",
                            "--link-prefix=", "--link-origin",
                            "https://developer.dynatrace.com",
                            "--generation", "latest", "--filter", rx,
                            "-o", tmp], capture_output=True, text=True)
            for p in suspect:
                a = _md_body(os.path.join(DEV_ROOT, *p.split("/")) + ".md")
                b = _md_body(os.path.join(tmp, *p.split("/")) + ".md")
                if b is not None and a != b:
                    changed.append(p)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("\nnew      : %d" % len(new))
    for p in new[:LIMIT]:
        print("   +", p)
    print("changed  : %d" % len(changed))
    for p in changed[:LIMIT]:
        print("   ~", p)
    print("removed  : %d" % len(removed))
    for p in removed[:LIMIT]:
        print("   -", p)
    if errors:
        print("fetch errors: %d" % len(errors))
        for p in errors[:LIMIT]:
            print("   !", p, html[p])
    if suspect and not changed and not write_baseline:
        print("\n%d page(s) differed in raw HTML but not in content "
              "(site rebuild, nav or footer churn)." % len(suspect))

    if write_baseline:
        os.makedirs(os.path.dirname(DEV_HASHES), exist_ok=True)
        with io.open(DEV_HASHES, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("doc_path\thtml_md5\tbody_md5\n")
            for p, _ in urls:
                body = _md_body(os.path.join(DEV_ROOT, *p.split("/")) + ".md")
                fh.write("%s\t%s\t%s\n" % (p, html.get(p, ""), body or ""))
        print("\nbaseline written: %s (%d pages)" % (DEV_HASHES, len(urls)))
        return 0

    return 1 if (new or changed or removed or errors) else 0



def cmd_indexes():
    """Rebuild the derived indexes. Offline, no model tokens, safe to re-run.

    Run this after any refresh: both indexes carry line numbers and `lastmod`
    values that a re-converted page invalidates. A stale section index sends a
    reader to the wrong line; a stale UI map misdates a menu path, which is the
    one thing the map exists to get right.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    steps = [
        ("section index (docs)", [VENV, os.path.join(here, "scripts",
         "build_section_index.py"), ROOT, ROOT + "/_reports/section-index.tsv"]),
        ("section index (developer)", [VENV, os.path.join(here, "scripts",
         "build_section_index.py"), DEV_ROOT,
         DEV_ROOT + "/_reports/section-index.tsv"]),
        ("ui paths -> raw", [VENV, os.path.join(here, "scripts",
         "extract_ui_paths.py"), ROOT + "/_reports/_ui-paths-raw.json"]),
        ("ui map", [VENV, os.path.join(here, "scripts", "build_ui_map.py"),
         ROOT + "/_reports/_ui-paths-raw.json", ROOT + "/_reports/ui-map.tsv"]),
    ]
    bad = 0
    for label, cmd in steps:
        r = subprocess.run(cmd, capture_output=True, text=True)
        tail = [x for x in (r.stdout or "").strip().split("\n") if x.strip()]
        if r.returncode:
            bad += 1
            print("[FAIL] %-26s %s" % (label, (r.stderr or "").strip()[:120]))
        else:
            print("[OK]   %-26s %s" % (label, tail[0] if tail else ""))
    raw = ROOT + "/_reports/_ui-paths-raw.json"
    if os.path.exists(raw):
        os.remove(raw)          # intermediate, not part of the corpus
    return 1 if bad else 0


CMDS = {"check": cmd_check, "devcheck": cmd_devcheck, "verify": cmd_verify,
        "anchors": cmd_anchors, "images": cmd_images, "stats": cmd_stats,
        "indexes": cmd_indexes}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__)
        print("subcommands:", ", ".join(CMDS))
        sys.exit(2)
    sys.exit(CMDS[sys.argv[1]]())
