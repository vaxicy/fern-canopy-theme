#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fern Canopy Theme — vector logo candidates (SVG rendered by headless Chromium).

Each candidate is inline SVG in its own 512px cell; Playwright screenshots every
cell with omit_background=True (true transparency) and PIL only composes the
contact sheets, the inline strip and the official logo/logo.png exported from
the SELECTED candidate.

Colours come from manifest.json. Change SELECTED and re-run; never hand-copy PNGs.
"""
import json
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(ROOT))                      # relative paths only (non-ASCII path safety)

SIZE = 128
CELL = 512
PREVIEW = 256
SELECTED = "01"
CAND_DIR = Path("logo/candidates")
LOGO_OUT = Path("logo/logo.png")

with open("manifest.json", "r", encoding="utf-8") as f:
    _m = json.load(f)
_C, _P = _m["theme"]["colors"], _m["theme"]["properties"]


def hx(vals):
    return "#%02X%02X%02X" % tuple(vals)


DEEP = hx(_C["frame"])                    # #3F6B4C
TOOLBAR = hx(_C["toolbar"])               # #47724F
PALE = hx(_C["ntp_background"])           # #E4F1D6
PALE2 = hx(_C["button_background"])       # #D4E9BD
PALE3 = hx(_C["button_background_secondary"])  # #C5E1A5
SAGE = hx(_P["ntp_button_background"])    # #90A479
INK = hx(_C["ntp_text"])                  # #2F4A38


def svg_open(body, defs=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 256 256">%s%s</svg>' % (CELL, CELL, defs, body))


def bezier(p0, p1, p2, p3, t):
    mt = 1 - t
    x = mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0]
    y = mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]
    return x, y


def tangent_deg(p0, p1, p2, p3, t):
    mt = 1 - t
    dx = 3 * mt * mt * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0])
    dy = 3 * mt * mt * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1])
    return math.degrees(math.atan2(dy, dx))


def leaflet(x, y, angle, length, fill, vein=None, width_k=0.20):
    w = length * width_k
    d = ('M0 0 C %.1f %.1f %.1f %.1f %.1f 0 C %.1f %.1f %.1f %.1f 0 0 Z'
         % (length * 0.30, -w, length * 0.76, -w * 0.92, length,
            length * 0.76, w * 0.92, length * 0.30, w))
    out = '<g transform="translate(%.2f %.2f) rotate(%.2f)"><path d="%s" fill="%s"/>' % (
        x, y, angle, d, fill)
    if vein:
        out += ('<path d="M%.1f 0 H%.1f" stroke="%s" stroke-opacity=".35" '
                'stroke-width="%.2f" stroke-linecap="round" fill="none"/>' % (
                    length * 0.06, length * 0.88, vein, max(1.6, length * 0.05)))
    return out + '</g>'


def frond(p0, p1, p2, p3, n=9, base_len=52, decay=0.55, spread=54,
          fill=PALE2, vein=DEEP, stroke=DEEP):
    parts = ['<path d="M%.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" stroke="%s" '
             'stroke-width="0.06" stroke-linecap="round" fill="none" '
             'transform="scale(1)" stroke-opacity="0"/>' % (0, 0, 0, 0, 0, 0, 0, 0, stroke)]
    for i in range(n):
        t = 0.10 + 0.84 * i / (n - 1)
        x, y = bezier(p0, p1, p2, p3, t)
        ang = tangent_deg(p0, p1, p2, p3, t)
        length = base_len * (1 - decay * i / (n - 1))
        for side in (1, -1):
            parts.append(leaflet(x, y, ang + side * spread, length, fill, vein))
    return "".join(parts)


def rachis(p0, p1, p2, p3, width=7.0, color=DEEP):
    d = ("M%.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f"
         % (p0[0], p0[1], p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]))
    return ('<path d="%s" stroke="%s" stroke-width="%.1f" stroke-linecap="round" fill="none"/>'
            % (d, color, width))


def spiral_path(cx, cy, r0, r1, turns, steps=300):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        th = 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        pts.append("%.2f %.2f" % (cx + r * math.cos(th), cy - r * math.sin(th)))
    return "M" + " L".join(pts)


# ------------------------------------------------------------------ candidates
FROND = ((74, 216), (92, 150), (140, 96), (198, 52))
SVG_01 = svg_open(rachis(*FROND) + frond(*FROND, n=9, base_len=56, fill=SAGE, vein=DEEP),
                  defs="")

SVG_02 = svg_open("""
<defs>
  <linearGradient id="fc2" x1="0" y1="1" x2="1" y2="0">
    <stop offset="0" stop-color="%s"/>
    <stop offset="0.55" stop-color="%s"/>
    <stop offset="1" stop-color="%s"/>
  </linearGradient>
</defs>
<path d="%s" fill="none" stroke="url(#fc2)" stroke-width="19" stroke-linecap="round"
      stroke-linejoin="round"/>
<circle cx="%d" cy="%d" r="9" fill="%s" opacity=".9"/>
""" % (DEEP, SAGE, PALE3, spiral_path(128, 128, 30, 96, 1.65), 128, 128, PALE))

SVG_03 = svg_open("""
<path d="M22 168 Q128 96 234 168" fill="none" stroke="%s" stroke-width="17" stroke-linecap="round"/>
<path d="M40 202 Q128 142 216 202" fill="none" stroke="%s" stroke-width="17" stroke-linecap="round"/>
<path d="M58 232 Q128 186 198 232" fill="none" stroke="%s" stroke-width="17" stroke-linecap="round"/>
<circle cx="128" cy="82" r="17" fill="%s"/>
""" % (SAGE, hx(_P["ntp_button_hover"]), DEEP, SAGE))

SVG_04 = svg_open("""
<path d="M128 214 V104" stroke="%s" stroke-width="7" stroke-linecap="round" fill="none"/>
%s
%s
%s
%s
%s
""" % (DEEP,
       leaflet(128, 106, -128, 62, SAGE, DEEP),
       leaflet(128, 106, -52, 62, SAGE, DEEP),
       leaflet(128, 140, -90, 78, PALE3, DEEP),
       leaflet(128, 172, -150, 56, PALE2, DEEP),
       leaflet(128, 172, -30, 56, PALE2, DEEP)))

SVG_05 = svg_open("""
<circle cx="128" cy="128" r="102" fill="%s"/>
<circle cx="128" cy="128" r="102" fill="none" stroke="%s" stroke-opacity=".28" stroke-width="4"/>
<g transform="translate(128 132) scale(0.62) translate(-128 -132)">
  %s
  %s
</g>
""" % (DEEP, PALE,
       rachis(*FROND, width=10, color=PALE),
       frond(*FROND, n=8, base_len=56, fill=PALE2, vein=None)))

SVG_06 = svg_open("""
<defs>
  <linearGradient id="cp6" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="%s"/>
    <stop offset="1" stop-color="%s"/>
  </linearGradient>
</defs>
<path d="M128 46 C186 76 214 126 214 168 C214 202 178 224 128 224 C78 224 42 202 42 168 C42 126 70 76 128 46 Z"
      fill="url(#cp6)"/>
<path d="M128 224 V182" stroke="%s" stroke-opacity=".55" stroke-width="9" stroke-linecap="round"/>
<path d="M96 168 Q128 148 160 168" fill="none" stroke="%s" stroke-opacity=".45" stroke-width="7"
      stroke-linecap="round"/>
""" % (PALE3, SAGE, DEEP, DEEP))

CANDIDATES = [
    ("01", "fern-frond", "Fern frond — leaves on a curved rachis, most literal", SVG_01),
    ("02", "fern-curl", "Fiddlehead spiral — most iconic, reads at 16px", SVG_02),
    ("03", "canopy-arcs", "Three canopy arcs — abstract, layered value ladder", SVG_03),
    ("04", "leaf-cluster", "Five-leaf sprig — lightest and most botanical", SVG_04),
    ("05", "fern-badge", "Frond in a forest badge — boldest at 32px", SVG_05),
    ("06", "canopy-dome", "Canopy dome — soft and structural", SVG_06),
]


def font(size, bold=False):
    for name in (("segoeuib.ttf", "seguisb.ttf") if bold else ("segoeui.ttf", "segoeuisl.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_cells():
    cells = "".join('<div id="cell%s" style="width:%dpx;height:%dpx">%s</div>' % (num, CELL, CELL, svg)
                    for num, _n, _d, svg in CANDIDATES)
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>'
            'html,body{margin:0;padding:0;background:transparent}'
            '#grid{display:flex;flex-wrap:wrap;width:%dpx}div[id^=cell]{display:block}'
            '</style></head><body><div id="grid">%s</div></body></html>' % (CELL * 3, cells))
    out = {}
    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            # Playwright's bundled headless shell may be missing after an update;
            # fall back to the locally installed Chrome instead of a 150MB download.
            b = p.chromium.launch(channel="chrome")
        pg = b.new_page(viewport={"width": CELL * 3, "height": CELL * 2})
        pg.set_content(html)
        for num, name, _d, _svg in CANDIDATES:
            path = CAND_DIR / ("%s-%s.png" % (num, name))
            pg.locator("#cell" + num).screenshot(path=str(path), omit_background=True)
            img = Image.open(path).convert("RGBA").resize((PREVIEW, PREVIEW), Image.LANCZOS)
            img.save(path)
            bbox = img.split()[3].getbbox()
            assert bbox, "candidate %s rendered empty" % name
            assert bbox[0] > 8 and bbox[1] > 8 and bbox[2] < PREVIEW - 8 and bbox[3] < PREVIEW - 8, \
                "candidate %s touches the canvas edge: %s" % (name, bbox)
            out[num] = img
            print("candidate %s %s -> alpha bbox %s" % (num, name, bbox))
        b.close()
    return out


def contact_sheet(rendered, bg, txt, sub, path, title):
    cols, rows = 3, 2
    cw, ch = 384, 374
    gap, margin = 28, 40
    W = margin * 2 + cols * cw + (cols - 1) * gap
    H = margin * 2 + 34 + rows * ch + (rows - 1) * gap
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    f_title, f_name, f_desc, f_file = font(24, True), font(21, True), font(15), font(14)
    d.text((margin, margin), title, font=f_title, fill=txt)
    y0 = margin + 34
    for i, (num, name, desc, _svg) in enumerate(CANDIDATES):
        r, c = divmod(i, cols)
        x = margin + c * (cw + gap)
        y = y0 + r * (ch + gap)
        big = rendered[num].resize((220, 220), Image.LANCZOS)
        sheet.paste(big, (x + (cw - 220) // 2, y + 14), big)
        d.text((x + 18, y + 250), "%s · %s" % (num, name), font=f_name, fill=txt)
        d.text((x + 18, y + 280), desc, font=f_desc, fill=sub)
        thumb = rendered[num].resize((32, 32), Image.LANCZOS)
        sheet.paste(thumb, (x + 18, y + 330), thumb)
        d.text((x + 60, y + 339), "%s.png  256x256" % name, font=f_file, fill=sub)
        assert y + 300 <= y + 322, "text block collides with the thumbnail row"
    sheet.save(path)
    print("saved:", path, sheet.size)


def inline_strip(rendered, path):
    n, cell, gap, margin = len(CANDIDATES), 108, 22, 30
    W = margin * 2 + n * cell + (n - 1) * gap
    H = margin * 2 + cell + 30
    strip = Image.new("RGB", (W, H), (240, 247, 233))
    d = ImageDraw.Draw(strip)
    f = font(15, True)
    for i, (num, _n, _d, _s) in enumerate(CANDIDATES):
        x = margin + i * (cell + gap)
        img = rendered[num].resize((cell, cell), Image.LANCZOS)
        strip.paste(img, (x, margin), img)
        d.text((x + cell // 2 - 8, margin + cell + 8), num, font=f, fill=(47, 74, 56))
    strip.save(path)
    print("saved:", path, strip.size)


def main():
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    rendered = render_cells()
    contact_sheet(rendered, (240, 247, 233), (47, 74, 56), (110, 128, 98),
                  CAND_DIR / "contact-light.png", "Fern Canopy — vector logo candidates (light)")
    contact_sheet(rendered, (37, 56, 43), (228, 241, 214), (160, 184, 146),
                  CAND_DIR / "contact-dark.png", "Fern Canopy — vector logo candidates (dark)")
    inline_strip(rendered, CAND_DIR / "inline-strip.png")
    sel = [c for c in CANDIDATES if c[0] == SELECTED][0]
    icon = rendered[sel[0]].resize((SIZE, SIZE), Image.LANCZOS)
    icon.save(LOGO_OUT)
    print("official icon from SELECTED=%s (%s):" % (sel[0], sel[1]), LOGO_OUT, icon.size)


if __name__ == "__main__":
    main()
