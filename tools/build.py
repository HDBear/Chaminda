#!/usr/bin/env python3
"""Build the CRBTechs x James Heal catalogue landing page.

Reads catalogue.json next to this script's parent folder, copies + renames the
PDFs into pdfs/, renders first-page cover thumbnails into thumbs/, compresses
any document flagged "compress" with ghostscript, and regenerates index.html.

Usage:  python3 tools/build.py          (run from the site folder or anywhere)
Only python3 stdlib + system tools (pdftoppm, magick, gs) are required.
"""
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
SRC_ROOT = SITE.parent  # the "Catalogs for Download" folder holding Brochures/ Flyers/
PDFS = SITE / "pdfs"
THUMBS = SITE / "thumbs"

THUMB_WIDTH = 440  # px, rendered as webp (jpg fallback)


def sh(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def human_size(n):
    if n < 1024 ** 2:
        return f"{round(n / 1024):d} KB"
    return f"{n / 1024**2:.1f} MB"


def build_pdfs(docs):
    PDFS.mkdir(exist_ok=True)
    for d in docs:
        src = SRC_ROOT / d["source"]
        dst = PDFS / d["file"]
        if not src.exists():
            print(f"  !! missing source: {src}", file=sys.stderr)
            continue
        if d.get("compress") and (not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime):
            tmp = dst.with_suffix(".gs.pdf")
            try:
                sh(["gs", "-q", "-dBATCH", "-dNOPAUSE", "-sDEVICE=pdfwrite",
                    "-dPDFSETTINGS=/ebook", "-dColorImageResolution=110",
                    f"-sOutputFile={tmp}", str(src)])
                if tmp.stat().st_size < src.stat().st_size:
                    tmp.replace(dst)
                    print(f"  compressed {d['file']}: "
                          f"{human_size(src.stat().st_size)} -> {human_size(dst.stat().st_size)}")
                else:
                    tmp.unlink()
                    shutil.copy2(src, dst)
                    print("  (compression no help, copied original)")
            except FileNotFoundError:
                print("  ghostscript not found, copying original")
                shutil.copy2(src, dst)
        elif not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
            shutil.copy2(src, dst)
        d["size"] = human_size(dst.stat().st_size)


def magick_supports_webp():
    try:
        out = subprocess.run(["magick", "-list", "format"],
                             capture_output=True, text=True).stdout
        return "WEBP" in out.upper()
    except FileNotFoundError:
        return False


def build_thumbs(docs):
    THUMBS.mkdir(exist_ok=True)
    webp = magick_supports_webp()
    ext = "webp" if webp else "jpg"
    for d in docs:
        pdf = PDFS / d["file"]
        if not pdf.exists():
            continue
        out = THUMBS / (Path(d["file"]).stem + "." + ext)
        if out.exists() and out.stat().st_mtime >= pdf.stat().st_mtime:
            d["thumb"] = f"thumbs/{out.name}"
            continue
        tmp = THUMBS / ".tmpcover"
        sh(["pdftoppm", "-f", "1", "-l", "1", "-r", "110", "-png", "-singlefile",
            str(pdf), str(tmp)])
        sh(["magick", str(tmp) + ".png", "-resize", f"{THUMB_WIDTH}x>",
            "-strip", "-quality", "84", str(out)])
        (THUMBS / ".tmpcover.png").unlink(missing_ok=True)
        d["thumb"] = f"thumbs/{out.name}"
        print(f"  thumb {out.name}")
    stale = {p for p in THUMBS.iterdir() if p.is_file()} - {
        THUMBS / Path(d["file"]).with_suffix("." + ext).name for d in docs
    }
    for p in stale:
        p.unlink()
        print(f"  removed stale {p.name}")


ICONS = {
    "featured": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6L3.3 9.3l6.1-.7z"/></svg>',
    "abrasion": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/></svg>',
    "strength": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8v8M3 10v4M18 8v8M21 10v4M6 12h12"/></svg>',
    "colour": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3s6 6.5 6 11a6 6 0 1 1-12 0c0-4.5 6-11 6-11z"/></svg>',
    "washing": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 10h16v9H4zM4 10l2-5h12l2 5M8 15c1.3 1 2.7 1 4 0s2.7-1 4 0"/></svg>',
    "comfort": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 8h12a3 3 0 1 0-3-3M3 12h16a3 3 0 1 1-3 3M3 16h8a2.5 2.5 0 1 1-2.5 2.5"/></svg>',
}


def card_html(d):
    t = html.escape(d["title"])
    search = html.escape(f'{d["title"]} {d["type"]} {d["blurb"]}'.lower())
    tag = f'<span class="tag">{html.escape(d["tag"])}</span>' if d.get("tag") else ""
    return f"""      <article class="card" data-group="{d['group']}" data-search="{search}">
        <a class="thumb" href="pdfs/{d['file']}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true">
          <img src="{d['thumb']}" width="440" height="311" loading="lazy" decoding="async" alt="Cover of {t}">
        </a>
        <div class="info">
          <h3>{t}</h3>
          <p class="meta"><span class="badge">{html.escape(d['type'])}</span><span class="size">{d['size']}</span>{tag}</p>
          <p class="blurb">{html.escape(d['blurb'])}</p>
          <div class="actions">
            <a class="btn primary" href="pdfs/{d['file']}" target="_blank" rel="noopener">View</a>
            <a class="btn" href="pdfs/{d['file']}" download>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m0 0l-4.5-4.5M12 15l4.5-4.5M4 20h16"/></svg>Download</a>
          </div>
        </div>
      </article>"""


def build_html(cfg, docs):
    site = cfg["site"]
    counts = {}
    for d in docs:
        counts[d["group"]] = counts.get(d["group"], 0) + 1
    total = len(docs)

    chips = [f'<button class="chip" type="button" data-group="all" aria-pressed="true">All <span class="n">{total}</span></button>']
    sections = []
    for g in cfg["groups"]:
        gid, gtitle = g["id"], html.escape(g["title"])
        chips.append(f'<button class="chip" type="button" data-group="{gid}" aria-pressed="false">{gtitle} <span class="n">{counts.get(gid, 0)}</span></button>')
        cards = "\n".join(card_html(d) for d in docs if d["group"] == gid)
        icon = ICONS.get(gid, "")
        sections.append(f"""    <section class="group" id="{gid}" data-group="{gid}">
      <header class="grouphead">{icon}<h2>{gtitle}</h2><span class="count">{counts.get(gid, 0)}</span></header>
      <div class="cards">
{cards}
      </div>
    </section>""")

    doc_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0b3c5d">
<meta name="description" content="{html.escape(site['company'])} x {html.escape(site['partner'])} — browse and download product catalogues, brochures and flyers.">
<title>{html.escape(site['title'])} — {html.escape(site['company'])} × {html.escape(site['partner'])}</title>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="styles.css">
<script src="app.js" defer></script>
</head>
<body>
<header class="mast">
  <div class="wrap">
    <div class="brandrow">
      <span class="logo company">CRB<em>Techs</em></span>
      <span class="rule" aria-hidden="true"></span>
      <span class="logo partner">James&nbsp;Heal</span>
    </div>
    <p class="assoc">Authorised partner of James Heal textile testing instruments</p>
    <h1>{html.escape(site['title'])}</h1>
    <p class="intro">{html.escape(site['intro'])}</p>
  </div>
</header>

<nav class="filterbar" aria-label="Filter documents">
  <div class="wrap">
    <div class="searchbox">
      <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20.5 20.5L16 16"/></svg>
      <input type="search" id="q" placeholder="Search catalogues…" aria-label="Search catalogues" autocomplete="off">
    </div>
    <div class="chips" role="group" aria-label="Categories">
      {' '.join(chips)}
    </div>
  </div>
</nav>

<main class="wrap" id="main">
{chr(10).join(sections)}
  <p class="noresults" id="noresults" hidden>No documents match your search — <button type="button" id="clearq">clear filter</button></p>
</main>

<footer class="foot">
  <div class="wrap">
    <p>© {__import__('datetime').date.today().year} {html.escape(site['company'])}. Documents © {html.escape(site['partner'])} (PPT Group).</p>
    <p class="dim">All documents are provided in PDF format.</p>
  </div>
</footer>
<button id="totop" type="button" aria-label="Back to top" hidden>↑</button>
</body>
</html>
"""
    (SITE / "index.html").write_text(doc_html, encoding="utf-8")
    print(f"  index.html written ({total} documents)")


def main():
    cfg = json.loads((SITE / "catalogue.json").read_text(encoding="utf-8"))
    docs = cfg["documents"]
    print("Copying PDFs...")
    build_pdfs(docs)
    print("Rendering thumbnails...")
    build_thumbs(docs)
    print("Generating HTML...")
    build_html(cfg, docs)
    print("Done.")


if __name__ == "__main__":
    main()
