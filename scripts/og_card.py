#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Front-page OG cards (1200x630), one per language: og-card.png (en), og-card-<lang>.png."""
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
HN = "/System/Library/Fonts/HelveticaNeue.ttc"
L = {
    # lang: (font path, bold idx, regular idx, tagline lines, sub lines, output)
    "en":    (HN, 1, 0, ["The feel of FTP.", "The world of S3."],
              ["Dual-pane file transfers for S3, R2, B2 & MinIO —", "sandboxed on your Mac, keys in the Keychain."], "og-card.png"),
    "zh":    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2, 0, ["FTP 的手感，", "S3 的世界。"],
              ["給 S3、R2、B2 與 MinIO 的雙欄檔案傳輸工具——", "跑在 Apple 沙盒裡，金鑰存於 Keychain。"], "og-card-zh.png"),
    "zh-cn": ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2, 0, ["FTP 的手感，", "S3 的世界。"],
              ["给 S3、R2、B2 与 MinIO 的双栏文件传输工具——", "运行在 Apple 沙盒里，密钥存于 Keychain。"], "og-card-zh-cn.png"),
    "ja":    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2, 0, ["FTP の手ざわり、", "S3 の世界。"],
              ["S3・R2・B2・MinIO のためのデュアルペイン転送アプリ——", "Apple サンドボックスで動作、キーは Keychain に。"], "og-card-ja.png"),
    "ko":    ("/System/Library/Fonts/AppleSDGothicNeo.ttc", 6, 0, ["FTP의 손맛,", "S3의 세계."],
              ["S3, R2, B2, MinIO를 위한 듀얼 페인 전송 앱 —", "Apple 샌드박스에서 실행, 키는 Keychain에."], "og-card-ko.png"),
}
CHIPS = ["Amazon S3", "Cloudflare R2", "Backblaze B2", "MinIO"]

def base():
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
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

def fit(d, lines, path, idx, start, floor):
    size = start
    while size > floor:
        f = ImageFont.truetype(path, size, index=idx)
        if all(d.textlength(l, font=f) <= 744 for l in lines):   # text must end before x=824
            return f
        size -= 2
    return ImageFont.truetype(path, floor, index=idx)

for lang, (path, bi, ri, tag, sub, out) in L.items():
    img = base(); d = ImageDraw.Draw(img)
    d.text((80, 150), "RocketBucket", font=ImageFont.truetype(HN, 76, index=1), fill=(244, 241, 234))
    tf = fit(d, tag, path, bi, 34, 26)
    d.text((80, 262), tag[0], font=tf, fill=(255, 138, 61))
    d.text((80, 262 + int(tf.size * 1.4)), tag[1], font=tf, fill=(255, 138, 61))
    sf = fit(d, sub, path, ri, 26, 20)
    d.text((80, 392), sub[0], font=sf, fill=(150, 165, 190))
    d.text((80, 392 + int(sf.size * 1.4)), sub[1], font=sf, fill=(150, 165, 190))
    small = ImageFont.truetype(HN, 26, index=0)
    x, cy = 80, 505
    for c in CHIPS:
        tw = d.textlength(c, font=small)
        d.rounded_rectangle([x, cy, x + tw + 36, cy + 46], radius=23, outline=(80, 95, 120), width=2)
        d.text((x + 18, cy + 8), c, font=small, fill=(244, 241, 234))
        x += tw + 36 + 16
    img.save(out); print(out, img.size)
