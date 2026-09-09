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
    "en": ["500 GB went up.", "The app said it wasn't sure."],
    "zh": ["500 GB 傳完了，", "App 卻說它不確定"],
    "ja": ["500 GB は上がった。", "アプリは「確信がない」と言った"],
    "ko": ["500 GB는 올라갔다.", "앱은 확신이 없다고 했다"],
}
SUBS = {
    "en": "Resumable uploads to S3 & R2, at 9,847 parts",
    "zh": "S3 與 R2 的斷點續傳，9,847 個分段",
    "ja": "S3 と R2 への再開可能アップロード、9,847 パート",
    "ko": "S3와 R2로의 이어올리기, 9,847개 파트",
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
    out = f"{SLUG_DIR}/og-{lang}.png"
    img.save(out); print(out, img.size)
