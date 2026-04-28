#!/usr/bin/env python3
"""GSC Indexing Audit for fitover35.com.

One-shot diagnostic that produces under data/gsc-audit/:
  crawl-results.csv  — raw per-URL crawl data
  canonical-diagnosis.md, noindex-diagnosis.md, redirect-diagnosis.md
  SUMMARY.md         — bucket totals and proposed actions

Run from repo root: python3 scripts/gsc_audit.py
"""

import csv
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPLOY_DIR = REPO_ROOT / "outputs" / "fitover35-website"
AUDIT_DIR = REPO_ROOT / "data" / "gsc-audit"
SITE_ROOT = "https://fitover35.com"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
CRAWL_BUDGET = 50
SLEEP_BETWEEN = 1.0

PROTECTED_NOINDEX_PATTERNS = [
    r"/404(\.html)?$", r"/500(\.html)?$",
    r"/admin/", r"/api/", r"/preview/", r"/draft/",
    r"/tag/page/", r"/search($|/)",
    r"/thank-?you($|/)", r"/confirmation($|/)",
]


def static_pass():
    rows = []
    for path in sorted(DEPLOY_DIR.rglob("*.html")):
        rel = path.relative_to(DEPLOY_DIR)
        try:
            soup = BeautifulSoup(
                path.read_text(encoding="utf-8", errors="replace"),
                "html.parser",
            )
        except Exception as e:
            rows.append({
                "file": str(rel), "robots": "<parse-error>",
                "canonical": "", "error": str(e),
            })
            continue
        rt = soup.find("meta", attrs={"name": "robots"})
        ct = soup.find("link", attrs={"rel": "canonical"})
        rows.append({
            "file": str(rel),
            "robots": (rt.get("content", "") if rt else ""),
            "canonical": (ct.get("href", "") if ct else ""),
        })
    return rows


def sitemap_urls():
    sitemap_path = DEPLOY_DIR / "sitemap.xml"
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for url_el in root.findall("sm:url", ns):
        loc = url_el.find("sm:loc", ns)
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    return urls


def vercel_config():
    return json.loads((DEPLOY_DIR / "vercel.json").read_text())


def pick_crawl_targets(sitemap, extras):
    chosen, seen = [], set()

    def add(u):
        if u not in seen:
            chosen.append(u)
            seen.add(u)

    for u in extras:
        add(u)

    root_urls = [u for u in sitemap if urlparse(u).path in ("/", "")]
    article_urls = [u for u in sitemap if "/articles/" in u]
    other_urls = [u for u in sitemap if u not in root_urls and u not in article_urls]

    for u in root_urls[:2]:
        add(u)
    for u in other_urls[:8]:
        add(u)
    for u in article_urls[:20]:
        add(u)
        if len(chosen) >= CRAWL_BUDGET:
            break

    paired = []
    for u in article_urls[:5]:
        alt = u[:-5] if u.endswith(".html") else u + ".html"
        paired.append(alt)
    for u in paired:
        if len(chosen) >= CRAWL_BUDGET:
            break
        add(u)

    return chosen[:CRAWL_BUDGET]


def crawl_one(session, url):
    try:
        resp = session.get(url, allow_redirects=True, timeout=20)
    except Exception as e:
        return {
            "url": url, "final_url": "", "chain": [], "hops": 0,
            "final_status": -1, "robots_meta": "", "canonical": "",
            "x_robots_tag": "", "error": str(e),
        }

    chain = [(h.status_code, h.url, h.headers.get("Location", "")) for h in resp.history]
    chain.append((resp.status_code, resp.url, ""))

    robots_meta = canonical = ""
    ctype = resp.headers.get("Content-Type", "")
    if "html" in ctype.lower():
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            rt = soup.find("meta", attrs={"name": "robots"})
            ct = soup.find("link", attrs={"rel": "canonical"})
            if rt:
                robots_meta = rt.get("content", "")
            if ct:
                canonical = ct.get("href", "")
        except Exception:
            pass

    return {
        "url": url,
        "final_url": resp.url,
        "chain": chain,
        "hops": len(resp.history),
        "final_status": resp.status_code,
        "robots_meta": robots_meta,
        "canonical": canonical,
        "x_robots_tag": resp.headers.get("X-Robots-Tag", ""),
        "error": "",
    }


def classify_canonical(rec):
    canonical = rec["canonical"]
    final_url = rec["final_url"]
    if not canonical:
        return "NO_CANONICAL", "no canonical tag"
    norm_canon = canonical.rstrip("/")
    norm_final = (final_url or "").rstrip("/")
    if norm_canon == norm_final:
        return "EXPECTED", "canonical = final URL (self)"
    if rec["hops"] > 0 and rec["url"].rstrip("/") == norm_canon:
        return "BUG", f"canonical {canonical} itself redirects (final {final_url})"
    return "BUG", f"canonical {canonical} ≠ final URL {final_url}"


def classify_noindex(rec):
    has_meta = "noindex" in (rec["robots_meta"] or "").lower()
    has_hdr = "noindex" in (rec["x_robots_tag"] or "").lower()
    if not (has_meta or has_hdr):
        return "NO_NOINDEX", ""
    path = urlparse(rec["url"]).path
    final_path = urlparse(rec["final_url"] or "").path
    for pat in PROTECTED_NOINDEX_PATTERNS:
        if re.search(pat, path) or re.search(pat, final_path):
            return "INTENTIONAL", f"matches protected pattern {pat}"
    return "BUG", f"unexpected noindex (meta={rec['robots_meta']!r}, header={rec['x_robots_tag']!r})"


def classify_redirect(rec):
    if rec["final_status"] >= 400:
        return "BUG", f"final status {rec['final_status']}"
    if rec["hops"] == 0:
        return "NO_REDIRECT", ""
    if rec["hops"] == 1:
        from_u, to_u = rec["url"], rec["final_url"] or ""
        if from_u.endswith(".html") and to_u == from_u[:-5]:
            return "EXPECTED", "cleanUrls strips .html"
        if from_u.rstrip("/") == to_u.rstrip("/"):
            return "EXPECTED", "trailing-slash normalization"
        if from_u.startswith("http://") and to_u.startswith("https://") and from_u[7:] == to_u[8:]:
            return "EXPECTED", "http→https"
        return "REVIEW", f"single redirect {from_u} → {to_u}"
    return "BUG", f"chain length {rec['hops']}"


def find_source_file(url, static_rows):
    path = urlparse(url).path
    if path in ("", "/"):
        candidates = ["index.html"]
    elif path.endswith(".html"):
        candidates = [path.lstrip("/")]
    else:
        candidates = [path.lstrip("/") + ".html", path.lstrip("/") + "/index.html"]
    file_index = {r["file"] for r in static_rows}
    for c in candidates:
        if c in file_index:
            return c
    return ""


def write_table(filename, headers, rows):
    with open(AUDIT_DIR / filename, "w", encoding="utf-8") as f:
        title = filename.replace(".md", "").replace("-", " ").title()
        f.write(f"# {title}\n\n")
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
        for row in rows:
            cells = [str(c).replace("|", "\\|").replace("\n", " ") for c in row]
            f.write("| " + " | ".join(cells) + " |\n")


def main():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Phase 2: GSC Audit ===")
    print(f"Repo : {REPO_ROOT}")
    print(f"Deploy: {DEPLOY_DIR}")
    print(f"Audit : {AUDIT_DIR}")

    print("\n[1/5] Static HTML pass…")
    static_rows = static_pass()
    n_articles = sum(1 for r in static_rows if "articles/" in r["file"])
    n_html_canon = sum(1 for r in static_rows if r["canonical"].endswith(".html"))
    n_meta_noindex = sum(1 for r in static_rows if "noindex" in (r["robots"] or "").lower())
    print(f"  files={len(static_rows)} articles={n_articles} html-canonicals={n_html_canon} meta-noindex={n_meta_noindex}")

    print("\n[2/5] Sitemap pass…")
    sm = sitemap_urls()
    sm_html = [u for u in sm if u.endswith(".html")]
    print(f"  urls={len(sm)} ending-in-.html={len(sm_html)}")

    print("\n[3/5] Vercel config pass…")
    vc = vercel_config()
    print(f"  cleanUrls={vc.get('cleanUrls')} trailingSlash={vc.get('trailingSlash')} "
          f"redirects={len(vc.get('redirects', []))} headers={len(vc.get('headers', []))}")

    print("\n[4/5] Live crawl…")
    extras = [
        f"{SITE_ROOT}/", f"{SITE_ROOT}/about", f"{SITE_ROOT}/contact",
        f"{SITE_ROOT}/privacy", f"{SITE_ROOT}/terms", f"{SITE_ROOT}/disclaimer",
        f"{SITE_ROOT}/gear", f"{SITE_ROOT}/dashboard", f"{SITE_ROOT}/404",
        f"{SITE_ROOT}/nutrition", f"{SITE_ROOT}/workouts", f"{SITE_ROOT}/supplements",
        f"{SITE_ROOT}/meal-plan", f"{SITE_ROOT}/blog", f"{SITE_ROOT}/resources",
        f"{SITE_ROOT}/12-week-program",
    ]
    targets = pick_crawl_targets(sm, extras)
    print(f"  queued {len(targets)} URLs")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    crawl = []
    for i, u in enumerate(targets, 1):
        rec = crawl_one(session, u)
        crawl.append(rec)
        marker = "OK" if rec["final_status"] == 200 else f"!{rec['final_status']}"
        print(f"  [{i:>2}/{len(targets)}] {marker:<5} hops={rec['hops']} {u}")
        time.sleep(SLEEP_BETWEEN)

    print("\n[5/5] Classify and emit reports…")

    with open(AUDIT_DIR / "crawl-results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url", "final_url", "hops", "final_status", "robots_meta",
                    "x_robots_tag", "canonical", "chain", "error"])
        for r in crawl:
            chain_str = " → ".join(f"{s} {u}" for s, u, _ in r["chain"])
            w.writerow([r["url"], r["final_url"], r["hops"], r["final_status"],
                        r["robots_meta"], r["x_robots_tag"], r["canonical"],
                        chain_str, r["error"]])

    canon_b, noindex_b, redirect_b = [], [], []
    for r in crawl:
        ccls, creason = classify_canonical(r)
        ncls, nreason = classify_noindex(r)
        rcls, rreason = classify_redirect(r)
        src = find_source_file(r["url"], static_rows)
        canon_b.append((r, ccls, creason, src))
        noindex_b.append((r, ncls, nreason, src))
        redirect_b.append((r, rcls, rreason, src))

    write_table(
        "canonical-diagnosis.md",
        ["URL", "Canonical", "Final URL", "Hops", "Class", "Source", "Reason"],
        [(r["url"], r["canonical"] or "—", r["final_url"], r["hops"], cls, src or "—", reason)
         for (r, cls, reason, src) in canon_b if cls != "NO_CANONICAL"],
    )
    write_table(
        "noindex-diagnosis.md",
        ["URL", "Robots Meta", "X-Robots-Tag", "Class", "Source", "Reason"],
        [(r["url"], r["robots_meta"] or "—", r["x_robots_tag"] or "—", cls, src or "—", reason)
         for (r, cls, reason, src) in noindex_b if cls != "NO_NOINDEX"],
    )
    write_table(
        "redirect-diagnosis.md",
        ["URL", "Hops", "Chain", "Final Status", "Class", "Source", "Reason"],
        [(r["url"], r["hops"],
          " → ".join(str(s) for s, u, _ in r["chain"]),
          r["final_status"], cls, src or "—", reason)
         for (r, cls, reason, src) in redirect_b if cls != "NO_REDIRECT"],
    )

    def cnt(buckets, key):
        return sum(1 for (_r, c, _x, _y) in buckets if c == key)

    canon_bug = cnt(canon_b, "BUG")
    canon_ok = cnt(canon_b, "EXPECTED")
    canon_none = cnt(canon_b, "NO_CANONICAL")
    nidx_bug = cnt(noindex_b, "BUG")
    nidx_int = cnt(noindex_b, "INTENTIONAL")
    nidx_none = cnt(noindex_b, "NO_NOINDEX")
    rd_bug = cnt(redirect_b, "BUG")
    rd_ok = cnt(redirect_b, "EXPECTED")
    rd_review = cnt(redirect_b, "REVIEW")

    with open(AUDIT_DIR / "SUMMARY.md", "w", encoding="utf-8") as f:
        f.write("# GSC Indexing Audit — Summary (2026-04-27)\n\n")
        f.write(f"- Repo: `{REPO_ROOT}`\n")
        f.write(f"- Deploy dir: `outputs/fitover35-website/` ({len(static_rows)} HTML files, {n_articles} articles)\n")
        f.write(f"- Sitemap: {len(sm)} URLs total, {len(sm_html)} ending in `.html`\n")
        f.write(f"- Static `.html` canonicals: **{n_html_canon} of {len(static_rows)}** files\n")
        f.write(f"- Static `noindex` meta tags: **{n_meta_noindex} of {len(static_rows)}** files\n")
        f.write(f"- Crawl: {len(crawl)} URLs sampled @ {SLEEP_BETWEEN}s between requests\n")
        f.write(f"- Vercel config: cleanUrls={vc.get('cleanUrls')} trailingSlash={vc.get('trailingSlash')} "
                f"redirects={len(vc.get('redirects', []))} headers={len(vc.get('headers', []))}\n\n")

        f.write("## Bucket totals (in crawl sample)\n\n")
        f.write("| Bucket | EXPECTED/INTENTIONAL | BUG | Other |\n")
        f.write("|---|---|---|---|\n")
        f.write(f"| canonical | {canon_ok} | **{canon_bug}** | NO_CANONICAL={canon_none} |\n")
        f.write(f"| noindex   | {nidx_int} | **{nidx_bug}** | NO_NOINDEX={nidx_none} |\n")
        f.write(f"| redirect  | {rd_ok} | **{rd_bug}** | REVIEW={rd_review} |\n\n")

        f.write("## Proposed actions\n\n")
        if canon_bug or n_html_canon:
            f.write(
                f"- **Canonical fix (mechanical sed)**: {canon_bug} crawled URLs flagged BUG. "
                f"Static check shows **{n_html_canon}/{len(static_rows)}** deployed files have a `.html` canonical. "
                f"Fix: sed all article HTML + sitemap.xml + 1-line generator change. "
                f"Estimated files modified: **{n_html_canon} HTML files + 1 sitemap + 1 generator script**.\n"
            )
        if nidx_bug:
            f.write(
                f"- **Noindex fix**: {nidx_bug} URLs flagged BUG. See `noindex-diagnosis.md` for source files. "
                f"Manual review required before any tag is removed.\n"
            )
        else:
            f.write(f"- **Noindex**: no BUG-classified noindex in crawl sample (n={n_meta_noindex} static occurrences total — likely intentional pages like 404).\n")
        if rd_bug or rd_review:
            f.write(
                f"- **Redirect fix**: {rd_bug} BUG + {rd_review} REVIEW. See `redirect-diagnosis.md`. "
                f"Single-hop `.html→clean` redirects are EXPECTED and need no fix.\n"
            )
        else:
            f.write("- **Redirect**: no chains >1 hop or 4xx final statuses observed in crawl.\n")

        f.write("\n## Internal-link cleanup (deferred)\n\n")
        f.write("Internal `<a href=\"/foo.html\">` links across the site still produce 1-hop "
                "redirects via `cleanUrls`. This is EXPECTED behavior, but the redirect bucket "
                "in GSC may not fully empty until those links are also cleaned up. Out of scope "
                "for this PR; track as a follow-up if the bucket remains noisy after re-crawl.\n")

        f.write("\n## Next step\n\n")
        f.write("Review the three `*-diagnosis.md` files and `crawl-results.csv`, then explicitly "
                "approve Phase 4 fixes.\n")

    print(f"\nDone. Artifacts in {AUDIT_DIR}/")


if __name__ == "__main__":
    main()
