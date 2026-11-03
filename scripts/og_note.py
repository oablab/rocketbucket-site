#!/usr/bin/env python3
"""Per-language OG cards for a dev note.

usage: og_note.py <notes/<slug>> — reads NOTES[slug] below, writes og-card.png
for every language that note has copy for.
"""
import glob, random, sys
from PIL import Image, ImageDraw, ImageFont

SLUG_DIR = sys.argv[1]
W, H = 1200, 630
TEXT_MAX_X = 824   # artwork starts at 830

TITLES_500 = {
    "en": ["500 GB to R2, stopped,", "and started again."],
    "zh": ["500 GB 傳上 R2，", "中斷，再接著傳"],
    "ja": ["500 GB を R2 へ、止めて、", "また続ける"],
    "ko": ["500 GB를 R2로, 멈추고,", "다시 이어가기"],
}
SUBS_500 = {
    "en": "Multipart upload & resume · peak memory ~900 MB–1 GB",
    "zh": "分段上傳與續傳 · 記憶體峰值約 900 MB–1 GB",
    "ja": "マルチパート再開 · ピークメモリ約 900 MB–1 GB",
    "ko": "멀티파트 이어올리기 · 최대 메모리 약 900 MB–1 GB",
}
NOTES = {
    "500-gb-not-sure": (TITLES_500, SUBS_500),
    "one-byte-at-a-time": (
        {
            "en": ["One byte at a time:", "28× slower downloads,", "small files waiting in line"],
            "zh": ["一次一個位元組：", "下載慢 28 倍，小檔排隊"],
            "ja": ["1 バイトずつ：", "28 倍遅いダウンロードと", "順番待ちの小さなファイル"],
            "ko": ["한 번에 한 바이트:", "28배 느린 다운로드와", "줄 서는 작은 파일들"],
        },
        {
            "en": "1 GiB download 31.3 → 0.48 s",
            "zh": "1 GiB 下載 31.3 → 0.48 秒",
            "ja": "1 GiB ダウンロード 31.3 → 0.48 秒",
            "ko": "1 GiB 다운로드 31.3 → 0.48초",
        },
        # zh: PingFang TC puts ：and ，in the centre of the em box (Traditional
        # Chinese convention); Hiragino Sans GB sets them bottom-left, so the
        # full-width colon read as a half-width one.
        # ja borrows PingFang TC too: same centred ：, and it covers the kana and
        # 遅. Hiragino Sans (ja) has no bold cut installed on this Mac.
        {"zh": ("PINGFANG", 10, 2), "ja": ("PINGFANG", 10, 2)},
    ),
}
NOTE = NOTES[SLUG_DIR.rstrip("/").split("/")[-1]]
TITLES, SUBS = NOTE[0], NOTE[1]
NEXT = {  # one-byte only: the release-status line under the subtitle
    "en": "Ships in the next release, 0.3.0",
    "zh": "下一個版本 0.3.0 生效",
    "ja": "次のリリース 0.3.0 で反映",
    "ko": "다음 릴리스 0.3.0부터 적용",
}
FONTS = {  # (path, bold index, regular index)
    "en": ("/System/Library/Fonts/HelveticaNeue.ttc", 1, 0),
    "zh": ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2, 0),
    "ja": ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2, 0),  # borrow GB W6 for kana+Latin headline
    "ko": ("/System/Library/Fonts/AppleSDGothicNeo.ttc", 6, 0),
}
for lang, (path, bi, ri) in (NOTE[2] if len(NOTE) > 2 else {}).items():
    if path == "PINGFANG":  # a MobileAsset font; its directory name is a hash
        hits = glob.glob("/System/Library/AssetsV2/com_apple_MobileAsset_Font*/*/AssetData/PingFang.ttc")
        if not hits: sys.exit("PingFang.ttc not found")
        path = hits[0]
    FONTS[lang] = (path, bi, ri)

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

FALLBACK = ("/System/Library/Fonts/SFNS.ttf", 0)  # → is missing from Helvetica Neue

def missing(f, c):
    g, nd = f.getmask(c), f.getmask("\uffff")
    return c != " " and (g.size, bytes(g)) == (nd.size, bytes(nd))

def runs(f, text):
    """Split text into (string, font) runs; glyphs the font lacks use FALLBACK at the same size."""
    fb = ImageFont.truetype(FALLBACK[0], f.size, index=FALLBACK[1])
    out = []
    for c in text:
        cf = fb if missing(f, c) else f
        if out and out[-1][1] is cf: out[-1][0] += c
        else: out.append([c, cf])
    return out

def textlen(d, text, f):
    return sum(d.textlength(t, font=rf) for t, rf in runs(f, text))

def draw(d, xy, text, f, fill):
    x, y = xy
    base = y + f.getmetrics()[0]  # share the main font's baseline across runs
    for t, rf in runs(f, text):
        d.text((x, base), t, font=rf, fill=fill, anchor="ls")
        x += d.textlength(t, font=rf)

def fit(d, lines, path, idx, start, step=-4, floor=40, reserve=80):
    size = start
    while size > floor:
        f = ImageFont.truetype(path, size, index=idx)
        if all(textlen(d, l, f) <= TEXT_MAX_X - reserve for l in lines):
            return f
        size += step
    return ImageFont.truetype(path, floor, index=idx)

for lang, lines in TITLES.items():
    img = base(); d = ImageDraw.Draw(img)
    path, bi, ri = FONTS[lang]
    small = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 26, index=0)
    d.text((80, 120), "RocketBucket · Notes", font=small, fill=(150, 165, 190))
    # one-byte titles keep 40 px clear of the icon (ja line 3 touched it at 80)
    hf = fit(d, lines, path, bi, 64, reserve=120 if NOTE is NOTES["one-byte-at-a-time"] else 80)
    y = 190
    for l in lines:
        draw(d, (80, y), l, hf, (244, 241, 234))
        y += int(hf.size * 1.3)
    sf = fit(d, [SUBS[lang]], path, ri, 30, floor=24)
    for l in lines:
        if 80 + textlen(d, l, hf) > TEXT_MAX_X: sys.exit(f"{lang}: title overflows: {l}")
    if 80 + textlen(d, SUBS[lang], sf) > TEXT_MAX_X: sys.exit(f"{lang}: subtitle overflows")
    draw(d, (80, y + 30), SUBS[lang], sf, (255, 138, 61))
    if NOTE is NOTES["one-byte-at-a-time"]:  # 500 GB card stays unchanged
        nf = fit(d, [NEXT[lang]], path, ri, 26, floor=20)
        if 80 + textlen(d, NEXT[lang], nf) > TEXT_MAX_X: sys.exit(f"{lang}: next-release line overflows")
        draw(d, (80, y + 30 + sf.size + 26), NEXT[lang], nf, (150, 165, 190))
    out = f"{SLUG_DIR}/og-card.png" if lang == "en" else f"{lang}/{SLUG_DIR}/og-card.png"
    img.save(out); print(out, img.size)
