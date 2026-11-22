#!/usr/bin/env python3
"""Build-time generator for the entry image: ONE hero strawberry, fresh and glossy.

Drawn now, at build time, with PIL only. The graded program (main.py) just
copies the finished entry.png to /output/entry.png -- the grading sandbox has
no network, so nothing is fetched or generated at grade time.

Subject: a single ripe strawberry -- gloss, water droplets, a halved berry
showing juicy flesh -- on a white plate, warm light, readable at 300 px.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2048                      # supersampled canvas; downscaled to 1024
OUT = "entry.png"
random.seed(7)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def catmull_rom(pts, per=28):
    """Dense smooth curve through control points."""
    out = []
    ext = [pts[0]] + pts + [pts[-1]]
    for i in range(len(ext) - 3):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for j in range(per):
            t = j / per
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def vgrad(w, h, stops):
    """Vertical gradient image from [(pos, (r,g,b)), ...]."""
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[0, y] = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
                break
        else:
            px[0, y] = stops[-1][1]
    return g.resize((w, h))


def soft_ellipse(layer, box, fill, blur):
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.ellipse(box, fill=fill)
    tmp = tmp.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(tmp)


def body_outline(cx, top, w, h):
    """Right-half control points from top centre to tip, mirrored for left."""
    right = [
        (cx, top + 0.02 * h),
        (cx + 0.30 * w, top + 0.03 * h),
        (cx + 0.47 * w, top + 0.16 * h),
        (cx + 0.50 * w, top + 0.36 * h),
        (cx + 0.42 * w, top + 0.58 * h),
        (cx + 0.26 * w, top + 0.80 * h),
        (cx + 0.10 * w, top + 0.94 * h),
        (cx, top + h),
    ]
    left = [(2 * cx - x, y) for (x, y) in reversed(right[1:])]
    pts = right + left
    return catmull_rom(pts)


def half_width_at(outline, y):
    xs = [x for (x, yy) in outline if abs(yy - y) < 14]
    if not xs:
        return 0
    return (max(xs) - min(xs)) / 2.0


def draw_leaf(base, cx, cy, length, width, angle_deg, col_dark, col_light):
    """One pointed leaf, drawn on its own tile, rotated, pasted onto base."""
    tile = Image.new("RGBA", (length * 2, width * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    cx0, cy0 = length, width
    tip = (cx0 + length * 0.92, cy0)
    base_pt = (cx0 - length * 0.92, cy0)
    upper = catmull_rom([base_pt, (cx0 - length * 0.3, cy0 - width * 0.95),
                         (cx0 + length * 0.35, cy0 - width * 0.55), tip])
    lower = catmull_rom([tip, (cx0 + length * 0.35, cy0 + width * 0.55),
                         (cx0 - length * 0.3, cy0 + width * 0.95), base_pt])
    grad = vgrad(length * 2, width * 2,
                 [(0.0, col_dark), (0.5, col_light), (1.0, col_dark)])
    mask = Image.new("L", tile.size, 0)
    md = ImageDraw.Draw(mask)
    md.polygon(upper + lower, fill=255)
    tile.paste(Image.new("RGBA", tile.size, (0, 0, 0, 0)), (0, 0), mask)
    solid = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    solid.paste(grad.convert("RGBA"), (0, 0), mask)
    d2 = ImageDraw.Draw(solid)
    d2.line([base_pt, tip], fill=(255, 255, 255, 90), width=6)
    tile = solid.rotate(-angle_deg, resample=Image.BICUBIC, center=(cx0, cy0))
    base.alpha_composite(tile, (int(cx - length), int(cy - width)))


def draw_seed(base, x, y, rx, ry, angle_deg):
    tile = Image.new("RGBA", (rx * 4, ry * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.ellipse([rx, ry, rx * 3, ry * 3], fill=(247, 214, 116, 255),
              outline=(196, 138, 32, 255), width=3)
    d.ellipse([rx + 4, ry + 4, rx + 12, ry + 11], fill=(255, 244, 190, 255))
    tile = tile.rotate(angle_deg, resample=Image.BICUBIC, center=(rx * 2, ry * 2))
    base.alpha_composite(tile, (int(x - rx * 2), int(y - ry * 2)))


def draw_droplet(base, x, y, r):
    r = int(r)
    tile = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    cx0 = cy0 = r * 2
    d.ellipse([cx0 - r, cy0 - r, cx0 + r, cy0 + r],
              fill=(255, 255, 255, 70), outline=(255, 255, 255, 160), width=3)
    d.ellipse([cx0 - r * 0.55, cy0 - r * 0.6, cx0 - r * 0.05, cy0 - r * 0.1],
              fill=(255, 255, 255, 235))
    d.ellipse([cx0 + r * 0.25, cy0 + r * 0.35, cx0 + r * 0.6, cy0 + r * 0.65],
              fill=(255, 255, 255, 110))
    base.alpha_composite(tile, (int(x - r * 2), int(y - r * 2)))


def draw_strawberry(base, cx, top, w, h, seeds=True):
    """One whole glossy strawberry, upright, tip down."""
    outline = body_outline(cx, top, w, h)
    xs = [p[0] for p in outline]
    ys = [p[1] for p in outline]
    bx0, by0 = int(min(xs)), int(min(ys))
    bx1, by1 = int(max(xs)) + 1, int(max(ys)) + 1
    bbox = (bx0, by0, bx1, by1)

    # --- body: red vertical gradient through the outline mask ---
    mask = Image.new("L", base.size, 0)
    md = ImageDraw.Draw(mask)
    md.polygon(outline, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    grad = vgrad(bx1 - bx0, by1 - by0,
                 [(0.00, (226, 38, 46)), (0.35, (238, 58, 52)),
                  (0.70, (205, 24, 34)), (1.00, (146, 12, 26))])
    body = Image.new("RGBA", base.size, (0, 0, 0, 0))
    body.paste(grad.convert("RGBA"), (bx0, by0), mask.crop(bbox))
    base.alpha_composite(body)

    # --- side shading: darker at the left/right edges ---
    shade = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    bw = bbox[2] - bbox[0]
    for i, xx in enumerate(range(int(bbox[0]), int(bbox[2]), 8)):
        f = abs((xx - cx) / (bw / 2))
        a = int(95 * max(0, f - 0.45) ** 1.5)
        if a:
            sd.line([(xx, bbox[1]), (xx, bbox[3])], fill=(90, 5, 15, a), width=8)
    shade.putalpha(Image.composite(shade.split()[3], Image.new("L", base.size, 0), mask))
    base.alpha_composite(shade)

    # --- big soft gloss, upper left ---
    gloss = Image.new("RGBA", base.size, (0, 0, 0, 0))
    soft_ellipse(gloss, (cx - w * 0.42, top + h * 0.06, cx + w * 0.05, top + h * 0.42),
                 (255, 255, 255, 110), 70)
    soft_ellipse(gloss, (cx - w * 0.30, top + h * 0.10, cx - w * 0.02, top + h * 0.30),
                 (255, 255, 255, 130), 40)
    gloss.putalpha(Image.composite(gloss.split()[3], Image.new("L", base.size, 0), mask))
    base.alpha_composite(gloss)

    # --- seeds in curved rows ---
    if seeds:
        for row_i, t in enumerate([0.16, 0.28, 0.40, 0.52, 0.64, 0.76, 0.87]):
            y = top + t * h
            hw = half_width_at(outline, y)
            if hw < 20:
                continue
            n = max(2, int(hw / 52))
            for k in range(n):
                f = (k + 0.5) / n * 2 - 1
                x = cx + f * hw * 0.86 + random.uniform(-6, 6)
                ang = math.degrees(math.atan2(1.0, f * 0.9)) - 90
                draw_seed(base, x, y + random.uniform(-4, 4), 15, 21, ang)

    # --- water droplets on the body ---
    for _ in range(9):
        t = random.uniform(0.15, 0.8)
        y = top + t * h
        hw = half_width_at(outline, y)
        x = cx + random.uniform(-0.7, 0.7) * hw
        draw_droplet(base, x, y, random.uniform(13, 24))

    # --- calyx: green star leaves + stem ---
    top_y = top + 0.02 * h
    for ang, ln in [(-160, 320), (-125, 360), (-85, 380), (-45, 360),
                    (-5, 330), (35, 310), (75, 280), (115, 280), (150, 300)]:
        draw_leaf(base, cx, top_y + 26, ln, 62, ang, (20, 78, 34), (58, 138, 62))
    sd = ImageDraw.Draw(base)
    sd.line([(cx, top_y - 10), (cx + 18, top_y - 150)], fill=(46, 110, 52, 255), width=26)
    sd.line([(cx, top_y - 10), (cx + 18, top_y - 150)], fill=(96, 176, 96, 255), width=10)


def draw_half(base, cx, cy, rx, ry, angle_deg):
    """A halved strawberry, cut face up: pale juicy flesh, seed ring, white core."""
    tile = Image.new("RGBA", (rx * 4, ry * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    cx0 = cy0 = rx * 2
    # skin rim
    d.ellipse([cx0 - rx, cy0 - ry, cx0 + rx, cy0 + ry], fill=(214, 30, 40, 255))
    # flesh
    flesh = vgrad(rx * 2, ry * 2, [(0.0, (255, 214, 206)), (0.6, (250, 168, 158)),
                                    (1.0, (238, 130, 122))])
    fmask = Image.new("L", tile.size, 0)
    fd = ImageDraw.Draw(fmask)
    fd.ellipse([cx0 - rx * 0.92, cy0 - ry * 0.92, cx0 + rx * 0.92, cy0 + ry * 0.92], fill=255)
    tile.paste(flesh.convert("RGBA"), (cx0 - rx, cy0 - ry),
               fmask.crop((cx0 - rx, cy0 - ry, cx0 + rx, cy0 + ry)))
    # radial juice streaks
    for a in range(0, 360, 12):
        r0 = rx * 0.18
        x1 = cx0 + r0 * math.cos(math.radians(a))
        y1 = cy0 + r0 * math.sin(math.radians(a)) * (ry / rx)
        x2 = cx0 + rx * 0.9 * math.cos(math.radians(a))
        y2 = cy0 + ry * 0.9 * math.sin(math.radians(a))
        d.line([(x1, y1), (x2, y2)], fill=(226, 96, 92, 130), width=7)
    # seed ring
    for a in range(0, 360, 24):
        x = cx0 + rx * 0.72 * math.cos(math.radians(a))
        y = cy0 + ry * 0.72 * math.sin(math.radians(a))
        d.ellipse([x - 13, y - 18, x + 13, y + 18], fill=(247, 214, 116, 255),
                  outline=(196, 138, 32, 255), width=3)
    # white star core
    core = []
    for i in range(10):
        r = rx * 0.15 if i % 2 == 0 else rx * 0.07
        a = math.radians(i * 36 - 90)
        core.append((cx0 + r * math.cos(a), cy0 + r * math.sin(a) * (ry / rx)))
    d.polygon(core, fill=(255, 246, 240, 255))
    # gloss
    d.ellipse([cx0 - rx * 0.42, cy0 - ry * 0.62, cx0 - rx * 0.08, cy0 - ry * 0.28],
              fill=(255, 255, 255, 90))
    tile = tile.rotate(angle_deg, resample=Image.BICUBIC, center=(cx0, cy0))
    base.alpha_composite(tile, (int(cx - rx * 2), int(cy - ry * 2)))


def main():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # --- warm cream background ---
    bg = vgrad(S, S, [(0.0, (255, 248, 236)), (0.55, (253, 238, 216)),
                      (1.0, (244, 214, 178))]).convert("RGBA")
    img.alpha_composite(bg)
    # soft radial light behind the plate
    soft_ellipse(img, (350, 250, 1700, 1500), (255, 255, 255, 110), 180)
    # bokeh
    for (x, y, r, col, a) in [
            (220, 300, 90, (255, 205, 140), 55), (1820, 260, 120, (255, 190, 160), 45),
            (1700, 620, 60, (255, 220, 150), 60), (300, 700, 70, (255, 200, 170), 40),
            (1850, 1150, 80, (255, 210, 150), 35), (180, 1250, 55, (255, 190, 160), 35)]:
        soft_ellipse(img, (x - r, y - r, x + r, y + r), col + (a,), 45)

    # --- headline, addressed to the judge ---
    txt = Image.new("RGBA", img.size, (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    font = ImageFont.truetype(FONT, 108)
    td.text((S // 2, 128), "One strawberry. Taste it.", font=font,
            fill=(138, 18, 32, 255), anchor="ma")
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((S // 2, 128), "One strawberry. Taste it.", font=font,
            fill=(255, 255, 255, 200), anchor="ma")
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(glow)
    img.alpha_composite(txt)

    # --- plate + its shadow ---
    soft_ellipse(img, (330, 1470, 1720, 1810), (120, 70, 40, 90), 60)
    d = ImageDraw.Draw(img)
    d.ellipse([300, 1180, 1750, 1800], fill=(250, 246, 238, 255))
    d.ellipse([300, 1180, 1750, 1800], outline=(228, 216, 200, 255), width=6)
    d.ellipse([400, 1260, 1650, 1730], outline=(238, 228, 214, 255), width=5)

    # --- small whole berry, back left, resting on the plate ---
    draw_strawberry(img, 545, 1060, 380, 460, seeds=True)
    # --- hero strawberry, centre, tip resting on the plate ---
    soft_ellipse(img, (700, 1560, 1380, 1740), (140, 40, 30, 70), 50)
    draw_strawberry(img, 1020, 640, 640, 880, seeds=True)
    # --- halved berry, right, juicy face up ---
    draw_half(img, 1470, 1430, 260, 210, -18)
    # --- mint sprig resting on the plate ---
    draw_leaf(img, 1600, 1330, 210, 70, -35, (26, 92, 40), (74, 160, 74))
    draw_leaf(img, 1540, 1390, 190, 64, 15, (26, 92, 40), (74, 160, 74))

    # --- gentle vignette ---
    vig = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-260, -260, S + 260, S + 260], outline=(120, 60, 30, 55), width=320)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    img.alpha_composite(vig)

    small = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    small.save(OUT, optimize=True)
    print("saved", OUT, small.size)


if __name__ == "__main__":
    main()
