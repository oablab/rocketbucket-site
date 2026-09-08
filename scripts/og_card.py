#!/usr/bin/env python3
"""Generate og-card.png (1200x630) for rocketbucket.app."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)

# Vertical gradient: deep space navy -> darker
top = (27, 37, 54)     # 1B2536
bot = (14, 20, 32)     # 0E1420
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))

# Stars
import random
random.seed(7)
for _ in range(70):
    x, y = random.randint(0, W), random.randint(0, H)
    r = random.choice([1, 1, 1, 2])
    a = random.randint(70, 150)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(143 + a // 8, 163 + a // 8, 196, ))

# Icon on the right
icon = Image.open("icon.png").convert("RGBA").resize((300, 300), Image.LANCZOS)
img.paste(icon, (830, 165), icon)

bold = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 76, index=1)
med = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 34, index=0)
small = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 26, index=0)

ink = (244, 241, 234)
orange = (255, 138, 61)
muted = (150, 165, 190)

d.text((80, 150), "RocketBucket", font=bold, fill=ink)
d.text((80, 262), "The feel of FTP.", font=med, fill=orange)
d.text((80, 310), "The world of S3.", font=med, fill=orange)
d.text((80, 392), "Dual-pane file transfers for S3, R2, B2 & MinIO —", font=small, fill=muted)
d.text((80, 428), "sandboxed on your Mac, keys in the Keychain.", font=small, fill=muted)

# Endpoint chips
chips = ["Amazon S3", "Cloudflare R2", "Backblaze B2", "MinIO"]
x = 80
cy = 505
for c in chips:
    tw = d.textlength(c, font=small)
    d.rounded_rectangle([x, cy, x + tw + 36, cy + 46], radius=23, outline=(80, 95, 120), width=2)
    d.text((x + 18, cy + 8), c, font=small, fill=ink)
    x += tw + 36 + 16

img.save("og-card.png")
print("og-card.png", img.size)
