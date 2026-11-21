#!/usr/bin/env python3
"""Render the AERTHYS travel poster to entry.png.

Build-time renderer (needs Pillow). The graded entrypoint is main.py,
which only copies the pre-rendered entry.png, because the grading sandbox
is plain python:3.13-slim with no Pillow.

Poster: "AERTHYS - The Islands Above the Clouds". A golden-hour sky over a
sea of clouds, three floating islands, one lit lighthouse as the single
landmark, and the invented place's name set in large serif type.
Deterministic: one fixed seed, no clock, no network.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "assets", "DejaVuSerif-Bold.ttf")
OUT_PATH = os.path.join(HERE, "entry.png")

# Final poster size; render at 2x and downscale for smooth edges.
W, H = 768, 1024
SS = 2
RW, RH = W * SS, H * SS
SEED = 20261121

# Palette (golden hour).
SKY_STOPS = [
    (0.00, (38, 32, 74)),    # deep indigo, top
    (0.30, (94, 62, 128)),   # violet
    (0.55, (186, 96, 122)),  # rose
    (0.75, (238, 164, 104)), # amber
    (1.00, (250, 205, 138)), # pale gold at the horizon
]
CREAM = (250, 240, 214)
GOLD = (212, 164, 74)
ROCK_DARK = (58, 44, 66)
ROCK_MID = (82, 62, 86)
ROCK_LIGHT = (108, 82, 104)
GRASS = (96, 122, 88)
CLOUD_HI = (252, 238, 220)
CLOUD_LO = (226, 178, 178)
SUN_CORE = (255, 226, 160)
SUN_EDGE = (244, 178, 96)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_color(y_frac):
    for i in range(len(SKY_STOPS) - 1):
        y0, c0 = SKY_STOPS[i]
        y1, c1 = SKY_STOPS[i + 1]
        if y0 <= y_frac <= y1:
            return lerp(c0, c1, (y_frac - y0) / (y1 - y0))
    return SKY_STOPS[-1][1]


def paint_sky(base):
    """Vertical gradient sky, drawn as one-pixel rows then stretched."""
    strip = Image.new("RGB", (1, RH))
    px = strip.load()
    for y in range(RH):
        px[0, y] = sky_color(y / RH)
    base.paste(strip.resize((RW, RH)), (0, 0))


def add_stars(img, rng):
    """Stars in the upper sky, fading out toward the horizon."""
    layer = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(170):
        x = rng.uniform(0.03, 0.97) * RW
        y = rng.uniform(0.02, 0.38) * RH
        r = rng.uniform(0.8, 2.4) * SS
        fade = max(0.0, 1.0 - y / (0.40 * RH))
        alpha = int(235 * fade * rng.uniform(0.5, 1.0))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 244, 220, alpha))
        if r > 1.8 * SS and rng.random() < 0.5:
            d.line([x - r * 2.2, y, x + r * 2.2, y], fill=(255, 244, 220, alpha // 3), width=1)
            d.line([x, y - r * 2.2, x, y + r * 2.2], fill=(255, 244, 220, alpha // 3), width=1)
    img.alpha_composite(layer)


def add_sun(img):
    """Low setting sun at the right, with a soft halo."""
    cx, cy = int(0.76 * RW), int(0.50 * RH)
    halo = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(halo)
    for frac, alpha in ((0.30, 46), (0.20, 70), (0.12, 110)):
        rr = int(150 * SS * frac / 0.30)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=SUN_EDGE + (alpha,))
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(18 * SS)))
    d = ImageDraw.Draw(img)
    r = int(46 * SS)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN_CORE + (255,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 240, 90), width=2 * SS)


def cloud_puff(layer, rng, cx, cy, rx, ry, tint, alpha):
    d = ImageDraw.Draw(layer)
    n = rng.randint(7, 11)
    for i in range(n):
        t = i / max(n - 1, 1)
        ox = (t - 0.5) * rx * 1.6
        oy = math.sin(t * math.pi) * -ry * 0.25 + rng.uniform(-4, 4) * SS
        ex = rx * rng.uniform(0.28, 0.45)
        ey = ry * rng.uniform(0.55, 0.8)
        d.ellipse([cx + ox - ex, cy + oy - ey, cx + ox + ex, cy + oy + ey],
                  fill=tint + (alpha,))


def paint_cloud_sea(img, rng):
    """Layered banks of soft cloud filling the lower third."""
    layer = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    base_y = int(0.68 * RH)
    for row, (tint, alpha, ry) in enumerate((
            (CLOUD_LO, 150, 34),
            (CLOUD_HI, 185, 44),
            (CLOUD_HI, 215, 52),
            (CLOUD_HI, 235, 60),
            (CLOUD_HI, 245, 64))):
        y = base_y + row * int(0.075 * RH)
        x = -int(0.05 * RW)
        while x < RW * 1.05:
            rx = rng.uniform(0.10, 0.17) * RW
            cloud_puff(layer, rng, x, y, rx, ry * SS, tint, alpha)
            x += int(rx * rng.uniform(0.9, 1.3))
    # A few detached puffs drifting higher, catching the light.
    for _ in range(6):
        cx = rng.uniform(0.05, 0.95) * RW
        cy = rng.uniform(0.55, 0.64) * RH
        cloud_puff(layer, rng, cx, cy, rng.uniform(0.05, 0.09) * RW,
                   20 * SS, CLOUD_HI, 120)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(7 * SS)))


def island_silhouette(cx, top, half_w, depth, rng, jag=0.12):
    """Rock outline: a jagged top edge tapering to a point below."""
    pts = []
    steps = 9
    for i in range(steps + 1):
        t = i / steps
        x = cx - half_w + 2 * half_w * t
        y = top + rng.uniform(-jag, jag) * half_w * 0.18
        pts.append((x, y))
    tip = (cx + rng.uniform(-0.08, 0.08) * half_w, top + depth)
    left = (cx - half_w * 0.82, top + depth * 0.55)
    right = (cx + half_w * 0.82, top + depth * 0.55)
    return pts + [right, tip, left]


def paint_island(img, rng, cx, top, half_w, depth, strata=4):
    """One floating island: rock body, strata bands, grassy rim."""
    poly = island_silhouette(cx, top, half_w, depth, rng)
    body = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.polygon(poly, fill=ROCK_MID + (255,))
    # Strata: horizontal bands clipped to the silhouette.
    mask = Image.new("L", (RW, RH), 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    bands = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bands)
    for i in range(strata):
        y0 = top + depth * (i + 0.6) / (strata + 0.4)
        tone = ROCK_DARK if i % 2 == 0 else ROCK_LIGHT
        bd.rectangle([cx - half_w, y0, cx + half_w, y0 + depth * 0.05], fill=tone + (210,))
    body = Image.alpha_composite(body, Image.composite(bands, Image.new("RGBA", (RW, RH), (0, 0, 0, 0)), mask))
    # Grassy rim along the top edge.
    rim = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    top_pts = poly[:10]
    rd.line(top_pts, fill=GRASS + (255,), width=int(7 * SS), joint="curve")
    rd.line(top_pts, fill=(126, 150, 110, 255), width=int(3 * SS), joint="curve")
    body = Image.alpha_composite(body, Image.composite(rim, Image.new("RGBA", (RW, RH), (0, 0, 0, 0)), mask))
    img.alpha_composite(body)
    return top_pts


def paint_pines(img, rng, top_pts, count):
    """Little pine silhouettes standing on an island's top edge."""
    layer = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        (x0, y0), (x1, y1) = rng.choice(list(zip(top_pts, top_pts[1:])))
        x = rng.uniform(x0, x1)
        y = (y0 + y1) / 2
        h = rng.uniform(16, 30) * SS
        w = h * 0.42
        d.polygon([(x, y - h), (x - w, y), (x + w, y)], fill=(38, 58, 46, 255))
        d.polygon([(x, y - h * 1.35), (x - w * 0.7, y - h * 0.45), (x + w * 0.7, y - h * 0.45)],
                  fill=(46, 68, 52, 255))
        d.rectangle([x - 1.5 * SS, y, x + 1.5 * SS, y + 5 * SS], fill=(52, 40, 34, 255))
    img.alpha_composite(layer)


def paint_lighthouse(img, x, base_y):
    """The poster's single landmark: a lit lighthouse on the main island."""
    s = SS
    tower_w, tower_h = 26 * s, 96 * s
    top_y = base_y - tower_h
    d = ImageDraw.Draw(img)
    # Warm light cone fanning out to the left.
    cone = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cone)
    cd.polygon([(x, top_y + 6 * s), (x - 190 * s, top_y - 26 * s),
                (x - 190 * s, top_y + 38 * s)], fill=(255, 226, 160, 90))
    img.alpha_composite(cone.filter(ImageFilter.GaussianBlur(6 * s)))
    d = ImageDraw.Draw(img)
    # Tower with two dark bands.
    d.polygon([(x - tower_w // 2, base_y), (x - tower_w // 2 + 3 * s, top_y),
               (x + tower_w // 2 - 3 * s, top_y), (x + tower_w // 2, base_y)],
              fill=(246, 236, 214, 255))
    d.rectangle([x - tower_w // 2, top_y + 30 * s, x + tower_w // 2, top_y + 42 * s],
                fill=(122, 62, 66, 255))
    d.rectangle([x - tower_w // 2, top_y + 62 * s, x + tower_w // 2, top_y + 74 * s],
                fill=(122, 62, 66, 255))
    # Gallery, lamp room, roof.
    d.rectangle([x - 17 * s, top_y - 8 * s, x + 17 * s, top_y], fill=(58, 44, 66, 255))
    d.rectangle([x - 10 * s, top_y - 22 * s, x + 10 * s, top_y - 8 * s],
                fill=(255, 214, 130, 255))
    d.polygon([(x - 13 * s, top_y - 22 * s), (x + 13 * s, top_y - 22 * s), (x, top_y - 34 * s)],
              fill=(122, 62, 66, 255))
    # Lamp glow.
    glow = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([x - 30 * s, top_y - 45 * s, x + 30 * s, top_y + 15 * s],
               fill=(255, 220, 140, 110))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10 * s)))


def paint_pavilion(img, x, base_y):
    """A small domed pavilion on the right island."""
    s = SS
    d = ImageDraw.Draw(img)
    # Columns and dome.
    d.rectangle([x - 20 * s, base_y - 26 * s, x + 20 * s, base_y], fill=(240, 228, 200, 255))
    for cx in (-14 * s, 0, 14 * s):
        d.rectangle([x + cx - 2 * s, base_y - 26 * s, x + cx + 2 * s, base_y],
                    fill=(96, 74, 92, 255))
    d.pieslice([x - 24 * s, base_y - 52 * s, x + 24 * s, base_y - 4 * s], 180, 360,
               fill=(150, 96, 96, 255))
    d.ellipse([x - 3 * s, base_y - 58 * s, x + 3 * s, base_y - 52 * s], fill=GOLD + (255,))
    # One warm window.
    d.rectangle([x - 5 * s, base_y - 18 * s, x + 5 * s, base_y - 4 * s],
                fill=(255, 206, 120, 255))


def paint_waterfalls(img, rng, spots):
    """Thin falls spilling off island edges, dissolving into mist."""
    layer = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y0, length in spots:
        w = rng.uniform(3, 6) * SS
        steps = 14
        for i in range(steps):
            t = i / steps
            alpha = int(200 * (1 - t) ** 1.6)
            d.rectangle([x - w / 2, y0 + t * length, x + w / 2, y0 + (t + 1 / steps) * length],
                        fill=(240, 244, 250, alpha))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(2 * SS)))
    # Mist where the falls end.
    mist = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for x, y0, length in spots:
        md.ellipse([x - 26 * SS, y0 + length - 10 * SS, x + 26 * SS, y0 + length + 16 * SS],
                   fill=(250, 240, 224, 110))
    img.alpha_composite(mist.filter(ImageFilter.GaussianBlur(9 * SS)))


def paint_birds(img, rng):
    """A few distant birds, simple chevrons in the open sky."""
    d = ImageDraw.Draw(img)
    for _ in range(9):
        x = rng.uniform(0.08, 0.55) * RW
        y = rng.uniform(0.28, 0.42) * RH
        s = rng.uniform(5, 10) * SS
        d.arc([x - s, y - s * 0.55, x, y + s * 0.55], 200, 340, fill=(52, 40, 58, 200), width=max(2, int(1.4 * SS)))
        d.arc([x, y - s * 0.55, x + s, y + s * 0.55], 200, 340, fill=(52, 40, 58, 200), width=max(2, int(1.4 * SS)))


def paint_title(img):
    """AERTHYS in large letterspaced serif, with a soft shadow, a rule
    and a gold diamond beneath it. No other copy on the poster."""
    d = ImageDraw.Draw(img)
    size = int(96 * SS)
    font = ImageFont.truetype(FONT_PATH, size)
    word = "AERTHYS"
    tracking = int(0.24 * size)
    widths = [d.textlength(ch, font=font) for ch in word]
    total = sum(widths) + tracking * (len(word) - 1)
    x = (RW - total) / 2
    y = int(0.135 * RH)
    shadow = Image.new("RGBA", (RW, RH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    cx = x
    for ch, wch in zip(word, widths):
        sd.text((cx, y + 5 * SS), ch, font=font, fill=(40, 28, 52, 160))
        cx += wch + tracking
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4 * SS)))
    cx = x
    for ch, wch in zip(word, widths):
        d.text((cx, y), ch, font=font, fill=CREAM + (255,))
        cx += wch + tracking
    # Thin rule with a gold diamond at its centre.
    ry = y + size + int(0.018 * RH)
    d.line([(RW - total) / 2, ry, (RW + total) / 2, ry], fill=CREAM + (230,), width=int(2 * SS))
    dia = 7 * SS
    cx0 = RW // 2
    d.polygon([(cx0, ry - dia), (cx0 + dia, ry), (cx0, ry + dia), (cx0 - dia, ry)],
              fill=GOLD + (255,))


def paint_frame(img):
    """Cream double-rule poster frame."""
    d = ImageDraw.Draw(img)
    m1, m2 = 26 * SS, 38 * SS
    d.rectangle([m1, m1, RW - m1, RH - m1], outline=CREAM + (255,), width=3 * SS)
    d.rectangle([m2, m2, RW - m2, RH - m2], outline=CREAM + (210,), width=int(1.5 * SS))


def main():
    rng = random.Random(SEED)
    img = Image.new("RGBA", (RW, RH), (0, 0, 0, 255))
    paint_sky(img)
    add_stars(img, rng)
    add_sun(img)
    paint_cloud_sea(img, rng)

    # Main island, centre-left, carrying the lighthouse.
    main_cx, main_top = int(0.38 * RW), int(0.545 * RH)
    main_half, main_depth = int(0.24 * RW), int(0.20 * RH)
    top_edge = paint_island(img, rng, main_cx, main_top, main_half, main_depth)
    paint_pines(img, rng, top_edge, 7)
    paint_lighthouse(img, int(0.34 * RW), main_top + int(0.004 * RH))

    # Right island with the domed pavilion.
    r_cx, r_top = int(0.76 * RW), int(0.625 * RH)
    r_half, r_depth = int(0.13 * RW), int(0.12 * RH)
    r_edge = paint_island(img, rng, r_cx, r_top, r_half, r_depth, strata=3)
    paint_pines(img, rng, r_edge, 3)
    paint_pavilion(img, r_cx, r_top + int(0.004 * RH))

    # Tiny far-left island.
    t_cx, t_top = int(0.11 * RW), int(0.685 * RH)
    t_half, t_depth = int(0.07 * RW), int(0.08 * RH)
    t_edge = paint_island(img, rng, t_cx, t_top, t_half, t_depth, strata=2)
    paint_pines(img, rng, t_edge, 2)

    # Waterfalls off the main and right islands.
    paint_waterfalls(img, rng, [
        (int(0.30 * RW), main_top + main_depth * 0.55, int(0.10 * RH)),
        (int(0.47 * RW), main_top + main_depth * 0.42, int(0.08 * RH)),
        (int(0.72 * RW), r_top + r_depth * 0.5, int(0.07 * RH)),
    ])

    paint_birds(img, rng)
    paint_title(img)
    paint_frame(img)

    img.convert("RGB").resize((W, H), Image.LANCZOS).save(OUT_PATH, "PNG", optimize=True)
    size = os.path.getsize(OUT_PATH)
    print(f"wrote {OUT_PATH} ({size} bytes, {W}x{H})")
    assert size <= 1_048_576, "entry.png exceeds the 1 MiB gate"


if __name__ == "__main__":
    main()
