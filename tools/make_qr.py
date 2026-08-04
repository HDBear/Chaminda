#!/usr/bin/env python3
"""Generate the QR code and print-ready A4 poster for the catalogue page.

Usage: python3 tools/make_qr.py <SITE_URL> [short-label]
Example: python3 tools/make_qr.py https://hdbear.github.io/Chaminda/
Outputs into qr/: qr.svg, qr.png, poster-a4.svg, poster-a4.pdf, poster-a4.png
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

# --- standalone QR assets -------------------------------------------------
qr = segno.make(URL, error="m")
qr.save(QR_DIR / "qr.svg", kind="svg", scale=8, border=4)
qr.save(QR_DIR / "qr.png", kind="png", scale=16, border=4, dpi=300)
print(f"  qr.svg + qr.png for {URL}")

# QR as embedded base64 PNG for the poster

def b64_png(scale):
    from io import BytesIO
    buf = BytesIO()
    qr.save(buf, kind="png", scale=scale, border=2)
    return base64.b64encode(buf.getvalue()).decode()

qr_b64 = b64_png(24)

# --- A4 poster (210 x 297 mm), viewBox in px at 96 dpi --------------------
W, H = 794, 1123
poster = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="mast" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b3c5d"/>
      <stop offset="1" stop-color="#1a517d"/>
    </linearGradient>
  </defs>

  <rect width="{W}" height="{H}" fill="#ffffff"/>

  <!-- brand band -->
  <rect width="{W}" height="150" fill="url(#mast)"/>
  <text x="{W/2}" y="72" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="44" font-weight="bold" fill="#ffffff">CRB<tspan fill="#e8641b">Techs</tspan></text>
  <text x="{W/2}" y="112" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="20" fill="#c9d7e4">Authorised partner of James Heal</text>

  <!-- headline -->
  <text x="{W/2}" y="245" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="46" font-weight="bold" fill="#0b3c5d">Scan to view &amp; download</text>
  <text x="{W/2}" y="292" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="30" fill="#4c5a69">our product catalogues</text>

  <!-- QR frame -->
  <rect x="{(W-560)/2 - 26}" y="330" width="612" height="612" rx="28"
        fill="#ffffff" stroke="#e8641b" stroke-width="6"/>
  <image x="{(W-560)/2}" y="356" width="560" height="560"
         xlink:href="data:image/png;base64,{qr_b64}"/>

  <!-- short link -->
  <rect x="{(W-470)/2}" y="985" width="470" height="58" rx="29" fill="#0b3c5d"/>
  <text x="{W/2}" y="1024" text-anchor="middle" font-family="Courier New, monospace"
        font-size="26" font-weight="bold" fill="#ffffff">{SHORT}</text>

  <!-- footer -->
  <text x="{W/2}" y="1082" text-anchor="middle" font-family="Arial, Helvetica, sans-serif"
        font-size="17" fill="#4c5a69">James Heal textile testing instruments — brochures &amp; flyers</text>
</svg>
"""
(QR_DIR / "poster-a4.svg").write_text(poster, encoding="utf-8")
print("  poster-a4.svg written")

# --- raster + pdf versions ------------------------------------------------
try:
    subprocess.run(["magick", "-density", "300", str(QR_DIR / "poster-a4.svg"),
                    "-background", "white", "-alpha", "remove",
                    str(QR_DIR / "poster-a4.png")], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["magick", "-density", "300", str(QR_DIR / "poster-a4.svg"),
                    "-background", "white", "-alpha", "remove",
                    str(QR_DIR / "poster-a4.pdf")], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("  poster-a4.png + poster-a4.pdf written (300 dpi)")
except (subprocess.CalledProcessError, FileNotFoundError) as e:
    print(f"  !! magick conversion failed: {e} — print poster-a4.svg from a browser instead")
