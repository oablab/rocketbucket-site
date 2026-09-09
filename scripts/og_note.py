#!/usr/bin/env python3
"""Per-language OG cards for a dev note.

usage: og_note.py <notes/<slug>> — reads TITLES below, writes og-<lang>.png
"""
import random, sys
from PIL import Image, ImageDraw, ImageFont

SLUG_DIR = sys.argv[1]
W, H = 1200, 630
TEXT_MAX_X = 824   # artwork starts at 830

TITLES = {
    "en": ["500 GB to R2, stopped,", "and started again."],
    "zh": ["500 GB 傳上 R2，", "中斷，再接著傳"],
    "ja": ["500 GB を R2 へ、止めて、", "また続ける"],
    "ko": ["500 GB를 R2로, 멈추고,", "다시 이어가기"],
}
SUBS = {
    "en": "Multipart upload & resume · peak memory ~900 MB–1 GB",
    "zh": "分段上傳與續傳 · 記憶體峰值約 900 MB–1 GB",
    "ja": "マルチパート再開 · ピークメモリ約 900 MB–1 GB",
    "ko": "멀티파트 이어올리기 · 최대 메모리 약 900 MB–1 GB",
}
FONTS = {  # (path, bold index, regular index)
    "en": ("/System/Library/Fonts/HelveticaNeue.ttc", 1, 0),
    "zh": ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2, 0),
    "ja": ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2, 0),  # borrow GB W6 for kana+Latin headline
    "ko": ("/System/Library/Fonts/AppleSDGothicNeo.ttc", 6, 0),
}

def base():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    top, bot = (27, 37, 54), (14, 20, 32)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))
    random.seed(7)
    for _ in range(70):
        x, y = random.randint(0, W), random.randint(0, H)
        r = random.choice([1, 1, 1, 2]); a = random.randint(70, 150)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(143 + a // 8, 163 + a // 8, 196))
    icon = Image.open("icon.png").convert("RGBA").resize((300, 300), Image.LANCZOS)
    img.paste(icon, (830, 165), icon)
    return img

def fit(d, lines, path, idx, start, step=-4, floor=40):
    size = start
    while size > floor:
        f = ImageFont.truetype(path, size, index=idx)
        if all(d.textlength(l, font=f) <= TEXT_MAX_X - 80 for l in lines):
            return f
        size += step
    return ImageFont.truetype(path, floor, index=idx)

for lang, lines in TITLES.items():
    img = base(); d = ImageDraw.Draw(img)
    path, bi, ri = FONTS[lang]
    small = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 26, index=0)
    d.text((80, 120), "RocketBucket · Notes", font=small, fill=(150, 165, 190))
    hf = fit(d, lines, path, bi, 64)
    y = 190
    for l in lines:
        d.text((80, y), l, font=hf, fill=(244, 241, 234))
        y += int(hf.size * 1.3)
    sf = fit(d, [SUBS[lang]], path, ri, 30, floor=24)
    d.text((80, y + 30), SUBS[lang], font=sf, fill=(255, 138, 61))
    out = f"{SLUG_DIR}/og-card.png" if lang == "en" else f"{lang}/{SLUG_DIR}/og-card.png"
    img.save(out); print(out, img.size)
