#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fern Canopy Theme — promo tiles (440x280 + 1400x560), all English.

Colours are read from manifest.json. Each canvas has its own geometry and font
scale; the layout is redrawn from scratch every run, with bounds assertions so
overflow fails loudly at generation time.
"""
import json
import os
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(ROOT))                      # relative paths only (non-ASCII path safety)

OUT_DIR = "store-assets/promo"


def save_png(img, path, tries=5):
    """PIL intermittently raises OSError [Errno 22] on this non-ASCII project path.

    Observed on Windows: the very same save() succeeds on one run and fails on the
    next, so retry a few times instead of crashing the whole generation.
    """
    last = None
    for i in range(tries):
        try:
            img.save(path)
            return
        except OSError as exc:            # pragma: no cover - environment specific
            last = exc
            time.sleep(0.35 * (i + 1))
    raise last


def rgb(vals):
    return tuple(vals)


def font(size, bold=False):
    for name in (("segoeuib.ttf", "seguisb.ttf") if bold else ("segoeui.ttf", "segoeuisl.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def bg_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=lerp(top, bottom, y / max(1, h - 1)))
    return img


def draw_chip(d, x, y, h, label, f, fill, txt, pad=18):
    w = text_w(d, label, f) + pad * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill)
    d.text((x + pad, y + (h - f.size) // 2 - 3), label, font=f, fill=txt)
    return w


def compose(size, geom, colors, props):
    W, H = size
    M = geom["margin"]
    RIGHT = W - M

    img = bg_gradient(size, rgb(colors["ntp_background"]), rgb(colors["button_background"]))
    d = ImageDraw.Draw(img)

    ink = rgb(colors["ntp_text"])
    sub = lerp(ink, rgb(colors["ntp_background"]), 0.34)
    chip_bg = rgb(colors["ntp_header"])
    cta_bg = rgb(colors["frame"])
    cta_txt = rgb(colors["tab_text"])

    # palette tiles: a 3x2 grid of rounded swatches with a soft shadow
    # (replaces the old vertical paint bars — user request 2026-10-20)
    tile_colors = [rgb(colors["ntp_background"]), rgb(colors["button_background_secondary"]),
                   rgb(colors["button_background"]), rgb(props["ntp_button_background"]),
                   rgb(colors["toolbar"]), rgb(colors["frame"])]
    cols = 3
    block_w = geom["block_w"]
    tgap = block_w * 0.05
    tw = (block_w - tgap * (cols - 1)) / cols
    th = tw * geom["tile_ratio"]
    block_h = th * 2 + tgap
    bx, by = int(round(RIGHT - block_w)), geom["bar_y"]
    assert bx + block_w <= RIGHT, "palette tiles overflow the right margin"
    assert by + block_h <= H - 12, "palette tiles too close to the canvas bottom"

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for i in range(len(tile_colors)):
        r, c = divmod(i, cols)
        x0 = bx + c * (tw + tgap)
        y0 = by + r * (th + tgap)
        sd.rounded_rectangle([x0, y0 + 4, x0 + tw, y0 + th + 4],
                             radius=tw * 0.26, fill=(22, 38, 26, 24))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    d = ImageDraw.Draw(img)
    for i, col in enumerate(tile_colors):
        r, c = divmod(i, cols)
        x0 = bx + c * (tw + tgap)
        y0 = by + r * (th + tgap)
        d.rounded_rectangle([x0, y0, x0 + tw, y0 + th], radius=tw * 0.26, fill=col)

    lsize = geom["logo"]
    logo = Image.open("logo/logo.png").convert("RGBA").resize((lsize, lsize), Image.LANCZOS)
    img.paste(logo, (M, geom["logo_y"]), logo)

    f_title, f_sub = font(geom["title_size"], True), font(geom["sub_size"])
    tx = M + (lsize + geom["logo_gap"] if geom["title_beside_logo"] else 0)
    ty = geom["title_y"] if geom["title_beside_logo"] else geom["logo_y"] + lsize + geom["logo_gap"]
    d.text((tx, ty), geom["title"], font=f_title, fill=ink)
    sub_y = ty + geom["title_size"] + geom["title_sub_gap"]
    d.text((tx if geom["title_beside_logo"] else M, sub_y), geom["subtitle"], font=f_sub, fill=sub)
    assert geom["title_sub_gap"] >= 8, "title/subtitle gap too tight"

    f_chip = font(geom["chip_size"])
    cx, cy = (tx if geom["title_beside_logo"] else M), sub_y + geom["sub_size"] + geom["chip_gap"]
    for label in geom["chips"]:
        w = draw_chip(d, cx, cy, geom["chip_h"], label, f_chip, chip_bg, ink)
        cx += w + geom["chip_gap_x"]
    assert cx - geom["chip_gap_x"] <= bx - 24, "chips collide with the palette bars"

    f_cta = font(geom["cta_size"], True)
    btn_w, btn_h = geom["cta_w"], geom["cta_h"]
    btn_x = M
    btn_y = geom["cta_y"] if geom["cta_beside"] else cy + geom["chip_h"] + geom["cta_gap"]
    d.rounded_rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], radius=btn_h // 2, fill=cta_bg)
    tw = text_w(d, geom["cta"], f_cta)
    d.text((btn_x + (btn_w - tw) // 2, btn_y + (btn_h - f_cta.size) // 2 - 3),
           geom["cta"], font=f_cta, fill=cta_txt)
    assert btn_y + btn_h <= H - 12, "CTA button too close to the canvas bottom"
    assert btn_x + btn_w <= RIGHT, "CTA button overflows the right margin"
    assert btn_x + btn_w <= bx - 20, "CTA button collides with the palette bars"
    return img, {"btn": (btn_x, btn_y, btn_w, btn_h), "tiles": (bx, by, block_w, round(block_h))}


LARGE = {
    "margin": 70,
    "logo": 104, "logo_y": 82, "logo_gap": 26, "title_beside_logo": True,
    "title": "Fern Canopy", "title_size": 58, "title_y": 98,
    "title_sub_gap": 14, "subtitle": "A verdant green Chrome theme", "sub_size": 21,
    "chips": ["Solid colors", "Verdant palette", "Easy on the eyes"],
    "chip_size": 15, "chip_h": 34, "chip_gap": 34, "chip_gap_x": 12,
    "cta": "Try It Now", "cta_size": 20, "cta_w": 210, "cta_h": 54,
    "cta_y": 366, "cta_beside": True,
    "block_w": 300, "tile_ratio": 1.44, "bar_y": 130,
}

SMALL = {
    "margin": 28,
    "logo": 46, "logo_y": 22, "logo_gap": 10, "title_beside_logo": False,
    "title": "Fern Canopy", "title_size": 26, "title_y": 0,
    "title_sub_gap": 8, "subtitle": "A verdant green Chrome theme", "sub_size": 12,
    "chips": ["Solid colors", "Verdant palette"],
    "chip_size": 10, "chip_h": 22, "chip_gap": 12, "chip_gap_x": 8,
    "cta": "Try It Now", "cta_size": 13, "cta_w": 118, "cta_h": 36,
    "cta_y": 0, "cta_gap": 16, "cta_beside": False,
    "block_w": 132, "tile_ratio": 1.44, "bar_y": 68,
}


def main():
    with open("manifest.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        c = data["theme"]["colors"]
        p = data["theme"]["properties"]
    os.makedirs(OUT_DIR, exist_ok=True)
    for size, geom in (((1400, 560), LARGE), ((440, 280), SMALL)):
        img, boxes = compose(size, geom, c, p)
        out = "%s/%dx%d.png" % (OUT_DIR, size[0], size[1])
        save_png(img, out)
        print("saved:", out, img.size, img.mode, "cta:", boxes["btn"], "tiles:", boxes["tiles"])


if __name__ == "__main__":
    main()
