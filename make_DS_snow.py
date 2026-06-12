#!/usr/bin/env python3
"""
make_DS_snow.py - wrap a static image in a light-blue + animated-snow panel
for a GitHub profile README (snow falls *over* the picture).

    python3 make_DS_snow.py            # uses DS.png -> DS_snow.svg
    python3 make_DS_snow.py pic.png out.svg
    

Pillow is optional: if installed, the image is auto-shrunk so the SVG stays small.
If not, it still works but pre-resize your PNG to ~500-600px wide to keep it light.
"""

import sys
import base64
import struct
import random

src = sys.argv[1] if len(sys.argv) > 1 else "DS.png"
out = sys.argv[2] if len(sys.argv) > 2 else "DS_snow.svg"

data = open(src, "rb").read()
mime = "image/jpeg" if src.lower().endswith((".jpg", ".jpeg")) else "image/png"


def png_size(b):
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    return None


dim = png_size(data)

# shrink with Pillow if available (keeps the embedded file small)
try:
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    if im.width > 600:
        im = im.resize((600, round(im.height * 600 / im.width)))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    data, dim, mime = buf.getvalue(), im.size, "image/png"
except Exception:
    pass

iw, ih = dim if dim else (3, 4)        # assume portrait if size unknown

IMG_W = 300
IMG_H = round(IMG_W * ih / iw)
PAD = 22
W, H = IMG_W + 2 * PAD, IMG_H + 2 * PAD

rng = random.Random(7)
flakes = []
for _ in range(int(W * H / 2600)):
    x = rng.uniform(0, W); r = rng.uniform(1.4, 3.6); op = rng.uniform(0.5, 0.95)
    dur = rng.uniform(6, 13); beg = -rng.uniform(0, dur)
    flakes.append(
        f'    <circle cx="{x:.1f}" cy="-6" r="{r:.1f}" fill="#fff" opacity="{op:.2f}">'
        f'<animate attributeName="cy" values="-6;{H + 6}" dur="{dur:.1f}s" '
        f'begin="{beg:.1f}s" repeatCount="indefinite"/></circle>')

b64 = base64.b64encode(data).decode()
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="DORO">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dcefff"/><stop offset="1" stop-color="#b8ddfb"/></linearGradient>
    <clipPath id="panel"><rect width="{W}" height="{H}" rx="18"/></clipPath>
    <clipPath id="photo"><rect x="{PAD}" y="{PAD}" width="{IMG_W}" height="{IMG_H}" rx="12"/></clipPath>
  </defs>
  <g clip-path="url(#panel)">
    <rect width="{W}" height="{H}" fill="url(#sky)"/>
    <image x="{PAD}" y="{PAD}" width="{IMG_W}" height="{IMG_H}" clip-path="url(#photo)" href="data:{mime};base64,{b64}"/>
{chr(10).join(flakes)}
  </g>
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="none" stroke="#9cc9ef" stroke-width="1.5"/>
</svg>
'''
open(out, "w").write(svg)
kb = len(svg) // 1024
print(f"wrote {out}  ({W}x{H}px panel, image {iw}x{ih}, svg ~{kb} KB)")
if kb > 800:
    print("NOTE: SVG is large - install Pillow (pip install pillow) or pre-resize the PNG to ~500px wide.")
