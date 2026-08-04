#!/usr/bin/env python3
"""Generate branded QR assets for the catalogue page (CRB Techs x James Heal template).

Usage: python3 tools/make_qr.py [SITE_URL] [short-label]
Outputs into qr/: qr.svg, qr.png, poster-a4.svg/png/pdf, handout-a6.svg/png/pdf

Logos: assets/logo-jamesheal.png is embedded. If assets/crbtechs-logo.png exists
it is used; otherwise an SVG stand-in of the CRB Techs mark is drawn.
"""
import base64
import subprocess
import sys
from pathlib import Path

import segno

SITE = Path(__file__).resolve().parent.parent
QR_DIR = SITE / "qr"
QR_DIR.mkdir(exist_ok=True)

URL = sys.argv[1].rstrip("/") + "/" if len(sys.argv) > 1 else "https://hdbear.github.io/Chaminda/"
SHORT = sys.argv[2] if len(sys.argv) > 2 else URL.replace("https://", "").rstrip("/")

NAVY = "#1d2b49"
HEAD_NAVY = "#29385e"
RED = "#e8442b"
CREAM = "#f4ede1"
GRAY = "#4c5158"
BG = "#ffffff"


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()

# --- standalone QR --------------------------------------------------------
qr = segno.make(URL, error="m")
qr.save(QR_DIR / "qr.svg", kind="svg", scale=8, border=4)
qr.save(QR_DIR / "qr.png", kind="png", scale=16, border=4, dpi=300)
print(f"  qr.svg + qr.png for {URL}")


def qr_png_b64(border=1) -> str:
    from io import BytesIO
    buf = BytesIO()
    qr.save(buf, kind="png", scale=24, border=border)
    return base64.b64encode(buf.getvalue()).decode()


QR_B64 = qr_png_b64()
JH_B64 = base64.b64encode((SITE / "assets" / "logo-jamesheal.png").read_bytes())
CRB_B64 = base64.b64encode((SITE / "assets" / "crbtechs-logo.png").read_bytes())


def crb_logo(x, y, scale=1.0) -> str:
    """Embed the real CRB Techs logo PNG (1357x568 incl. tagline)."""
    h = 104 * scale
    w = h * (1357 / 568)
    return (f'<image x="{x}" y="{y}" width="{w:.0f}" height="{h:.0f}" '
            f'xlink:href="data:image/png;base64,{CRB_B64}"/>')


ICONS = {
    "scan": '<rect x="7.5" y="2.5" width="9" height="19" rx="2"/>'
            '<path d="M10 7h1.8v1.8H10zM12.2 7H14v1.8h-1.8zM10 8.8h1.8v1.8H10zM12.2 8.8H14v1.8h-1.8z" fill="currentColor" stroke="none"/>'
            '<path d="M9.8 12.5h4.4M9.8 15.5h4.4"/>',
    "download": '<path d="M12 4v8.5m0 0l-3.2-3.2M12 12.5l3.2-3.2"/>'
                '<path d="M5.5 15.5h4.5l1 1.8h2.8l1-1.8h3.7v4H5.5z"/>',
    "thanks": '<circle cx="12" cy="9" r="4.2"/>'
              '<path d="M10 12.5L8.5 20l3.5-2.2L15.5 20 14 12.5"/>'
              '<path d="M10.6 9l1.1 1.1 2-2.1"/>',
}


def icon_strip(y) -> str:
    cols = [(166, "SCAN THE CODE", "scan"), (397, "BROWSE &amp; DOWNLOAD", "download"), (628, "THANK YOU!", "thanks")]
    out = []
    for cx, label, icon in cols:
        out.append(f'<circle cx="{cx}" cy="{y}" r="29" fill="{NAVY}"/>')
        out.append(f'<g transform="translate({cx-14},{y-14}) scale(1.167)" fill="none" stroke="#ffffff" '
                   f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" color="#ffffff">{ICONS[icon]}</g>')
        out.append(f'<text x="{cx}" y="{y+52}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" '
                   f'font-size="12.5" font-weight="bold" fill="{NAVY}" letter-spacing="0.8">{label}</text>')
    return "\n  ".join(out)


# --- A4 poster --------------------------------------------------------------
W, H = 794, 1123
poster = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <pattern id="geo" width="46" height="46" patternUnits="userSpaceOnUse">
      <rect width="46" height="46" fill="{BG}"/>
      <path d="M0 46L46 0M-11 11L11 -11M35 57L57 35" stroke="#f4f5f8" stroke-width="1.1" fill="none"/>
    </pattern>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#geo)"/>

  <!-- header: logos -->
  <image x="88" y="54" width="265" height="47" xlink:href="data:image/png;base64,{JH_B64}"/>
  <line x1="397" y1="46" x2="397" y2="108" stroke="#d4d7dc" stroke-width="1.5"/>
  {crb_logo(486, 42, 0.68)}

  <!-- headline -->
  <text x="{W/2}" y="252" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="42" font-weight="bold" fill="{HEAD_NAVY}">CRB Techs (Pvt) Ltd.</text>
  <text x="{W/2}" y="298" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="33" font-weight="bold" fill="{RED}">Product Catalogue Library</text>
  <line x1="200" y1="326" x2="594" y2="326" stroke="#c7cbd1" stroke-width="1.2"/>
  <line x1="372" y1="326" x2="422" y2="326" stroke="{RED}" stroke-width="4"/>

  <!-- QR frame -->
  <rect x="170" y="356" width="470" height="470" rx="26" fill="#e3e6ea"/>
  <rect x="162" y="348" width="470" height="470" rx="26" fill="#ffffff" stroke="{NAVY}" stroke-width="10"/>
  <image x="206" y="392" width="382" height="382" xlink:href="data:image/png;base64,{QR_B64}"/>

  <!-- short link -->
  <text x="{W/2}" y="858" text-anchor="middle" font-family="Courier New, monospace"
        font-size="20" font-weight="bold" fill="{NAVY}">{SHORT}</text>

  <!-- icon strip -->
  <line x1="281" y1="894" x2="281" y2="972" stroke="#d4d7dc" stroke-width="1"/>
  <line x1="513" y1="894" x2="513" y2="972" stroke="#d4d7dc" stroke-width="1"/>
  {icon_strip(922)}

  <!-- footer band -->
  <rect x="0" y="1036" width="{W}" height="87" fill="{NAVY}"/>
  <text x="{W/2}" y="1068" text-anchor="middle" font-family="Georgia, serif"
        font-size="17" font-style="italic" fill="{CREAM}">We value your time and interest.</text>
  <text x="{W/2}" y="1102" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="24" font-weight="bold" fill="{RED}" letter-spacing="1">THANK YOU FOR VISITING!</text>

  <!-- outer border (drawn last, overlays band edges) -->
  <rect x="11" y="11" width="{W-22}" height="{H-22}" rx="22" fill="none" stroke="{RED}" stroke-width="2.5"/>
</svg>
"""
(QR_DIR / "poster-a4.svg").write_text(poster, encoding="utf-8")
print("  poster-a4.svg written (CRB x James Heal template)")

# --- A6 handout (landscape 148x105mm) --------------------------------------
HW, HH = 559, 397
handout = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{HW}" height="{HH}" viewBox="0 0 {HW} {HH}">
  <rect width="{HW}" height="{HH}" fill="{BG}"/>
  <image x="34" y="30" width="186" height="33" xlink:href="data:image/png;base64,{JH_B64}"/>
  {crb_logo(36, 84, 0.85)}
  <text x="34" y="212" font-family="Arial, Helvetica, sans-serif" font-size="19"
        font-weight="bold" fill="{HEAD_NAVY}">Product Catalogue Library</text>
  <text x="34" y="238" font-family="Arial, Helvetica, sans-serif" font-size="12.5"
        fill="{GRAY}">Scan to browse &amp; download</text>
  <text x="34" y="256" font-family="Arial, Helvetica, sans-serif" font-size="12.5"
        fill="{GRAY}">25 brochures &amp; flyers</text>
  <text x="34" y="330" font-family="Courier New, monospace" font-size="14"
        font-weight="bold" fill="{NAVY}">{SHORT}</text>
  <rect x="334" y="52" width="196" height="196" rx="18" fill="#ffffff" stroke="{NAVY}" stroke-width="7"/>
  <image x="350" y="68" width="164" height="164" xlink:href="data:image/png;base64,{QR_B64}"/>
  <rect x="0" y="356" width="{HW}" height="41" fill="{NAVY}"/>
  <text x="{HW/2}" y="381" text-anchor="middle" font-family="Georgia, serif"
        font-size="13" font-style="italic" fill="{CREAM}">Thank you for visiting CRB Techs!</text>
  <rect x="8" y="8" width="{HW-16}" height="{HH-16}" rx="14" fill="none" stroke="{RED}" stroke-width="1.8"/>
</svg>
"""
(QR_DIR / "handout-a6.svg").write_text(handout, encoding="utf-8")
print("  handout-a6.svg written")

# --- raster + pdf -----------------------------------------------------------
for name, density in (("poster-a4", 300), ("handout-a6", 300)):
    svg = QR_DIR / f"{name}.svg"
    for ext, extra in (("png", []), ("pdf", [])):
        try:
            subprocess.run(["magick", "-density", str(density), str(svg),
                            "-background", "white", "-alpha", "remove", *extra,
                            str(QR_DIR / f"{name}.{ext}")],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"  {name}.{ext} written")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"  !! {name}.{ext} failed: {e}")
