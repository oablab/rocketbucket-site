#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split a 4-language note (data-lang-page blocks) into standalone per-language pages:
   /notes/<slug>/            en
   /<lang>/notes/<slug>/     zh ja ko
Also splits /notes/index.html the same way. Old /notes/<slug>/<lang>/ share pages
become redirects to the new URLs."""
import io, re, os, shutil, sys

SLUG = sys.argv[1] if len(sys.argv) > 1 else '500-gb-not-sure'
SITE = 'https://rocketbucket.app'
LANGS = ['en', 'zh', 'ja', 'ko']
HTML_LANG = {'en': 'en', 'zh': 'zh-Hant', 'ja': 'ja', 'ko': 'ko'}
OG_LOCALE = {'en': 'en_US', 'zh': 'zh_TW', 'ja': 'ja_JP', 'ko': 'ko_KR'}
PREFIX = {'en': '', 'zh': '/zh', 'ja': '/ja', 'ko': '/ko'}
LABEL = {'en': 'EN', 'zh': '中文', 'ja': '日本語', 'ko': '한국어'}
NOTES_WORD = {'en': 'Notes', 'zh': '開發筆記', 'ja': '開発ノート', 'ko': '개발 노트'}
PRIVACY = {'en': 'Privacy', 'zh': '隱私權政策', 'ja': 'プライバシー', 'ko': '개인정보 처리방침'}
SUPPORT = {'en': 'Support', 'zh': '支援', 'ja': 'サポート', 'ko': '지원'}

def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8').write(s)

def blocks(t):
    out = {}
    for l in LANGS:
        m = re.search(r'  <main data-lang-page="%s"( hidden)?>\n(.*?)\n  </main>' % l, t, re.S)
        assert m, l
        out[l] = m.group(2)
    return out

def hreflang(path_after_prefix):
    lines = []
    for l in LANGS:
        lines.append('  <link rel="alternate" hreflang="%s" href="%s%s%s">' % (HTML_LANG[l], SITE, PREFIX[l], path_after_prefix))
    lines.append('  <link rel="alternate" hreflang="x-default" href="%s%s">' % (SITE, path_after_prefix))
    return '\n'.join(lines)

def nav(lang, path_after_prefix):
    links = ''.join('<a href="%s%s"%s>%s</a>' % (PREFIX[l], path_after_prefix, ' aria-current="page"' if l == lang else '', LABEL[l]) for l in LANGS)
    return ('  <nav>\n    <a class="brand" href="%s/"><img src="/icon.png" alt="" width="28" height="28">RocketBucket</a>\n'
            '    <div class="lang-switch" aria-label="Language">%s</div>\n  </nav>\n') % (PREFIX[lang] or '', links)

def footer(lang):
    return ('  <footer>\n    © 2026 RocketBucket · <a href="%s/">rocketbucket.app</a> · <a href="%s/notes/">%s</a> · <a href="/privacy/">%s</a> · <a href="mailto:tautiu.dev@gmail.com">%s</a>\n  </footer>\n'
            % (PREFIX[lang] or '', PREFIX[lang], NOTES_WORD[lang], PRIVACY[lang], SUPPORT[lang]))

# ---------------- the note ----------------
SRC = 'notes/%s/index.html' % SLUG
t = rd(SRC)
style = re.search(r'  <style>\n.*?\n  </style>\n', t, re.S).group(0)
# switcher was buttons; make anchors look the same
style = style.replace('.lang-switch button {', '.lang-switch a, .lang-switch button {') \
             .replace('.lang-switch button[aria-selected="true"] {', '.lang-switch a[aria-current="page"], .lang-switch button[aria-selected="true"] {') \
             .replace('cursor: pointer;\n      padding: 0.3rem 0.75rem;', 'cursor: pointer; text-decoration: none;\n      padding: 0.3rem 0.75rem;')
titles = dict(re.findall(r'^\s+(en|zh|ja|ko): "(.*?)",$', t, re.M))
assert len(titles) == 4, titles
bl = blocks(t)

# per-language description: from the share pages (zh/ja/ko) and the EN meta
desc = {'en': re.search(r'<meta name="description" content="([^"]*)"', t).group(1)}
for l in ('zh', 'ja', 'ko'):
    s = rd('notes/%s/%s/index.html' % (SLUG, l))
    desc[l] = re.search(r'og:description" content="([^"]*)"', s).group(1)

for l in LANGS:
    path = '/notes/%s/' % SLUG
    url = SITE + PREFIX[l] + path
    h1 = re.search(r'<h1>(.*?)</h1>', bl[l], re.S).group(1)
    og_img = '%s%s%sog-card.png' % (SITE, PREFIX[l], path)
    body = bl[l].replace('<a class="back" href="/notes/">', '<a class="back" href="%s/notes/">' % PREFIX[l])
    page = ('<!DOCTYPE html>\n<html lang="%(hl)s">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '  <title>%(title)s</title>\n  <meta name="description" content="%(desc)s">\n'
            '  <meta property="og:type" content="article">\n  <meta property="og:title" content="%(h1)s">\n  <meta property="og:description" content="%(desc)s">\n'
            '  <meta property="og:url" content="%(url)s">\n  <meta property="og:image" content="%(img)s">\n  <meta property="og:image:width" content="1200">\n  <meta property="og:image:height" content="630">\n  <meta property="og:image:type" content="image/png">\n'
            '  <meta property="og:site_name" content="RocketBucket">\n  <meta property="og:locale" content="%(loc)s">\n'
            '  <meta name="twitter:card" content="summary_large_image">\n  <meta name="twitter:title" content="%(h1)s">\n  <meta name="twitter:description" content="%(desc)s">\n  <meta name="twitter:image" content="%(img)s">\n'
            '  <link rel="canonical" href="%(url)s">\n%(hreflang)s\n  <link rel="icon" type="image/png" href="/icon.png">\n  <link rel="apple-touch-icon" href="/icon.png">\n'
            '%(style)s</head>\n<body>\n%(nav)s\n  <main>\n%(body)s\n  </main>\n\n%(footer)s</body>\n</html>\n') % dict(
        hl=HTML_LANG[l], title=titles[l], desc=desc[l], h1=h1, url=url, img=og_img, loc=OG_LOCALE[l],
        hreflang=hreflang(path), style=style, nav=nav(l, path), body=body, footer=footer(l))
    out = ('%s%s' % (PREFIX[l].lstrip('/') + '/' if PREFIX[l] else '', 'notes/%s/index.html' % SLUG))
    # keep old share dirs for now (rewritten below); write the new page
    if l == 'en':
        wr(SRC + '.new', page)
    else:
        wr(out, page)
    # OG card into the page's own directory as og-card.png
    src_card = 'notes/%s/og-%s.png' % (SLUG, l)
    dst_card = os.path.join(os.path.dirname(out), 'og-card.png')
    shutil.copyfile(src_card, dst_card)
    print('wrote', out if l != 'en' else SRC, '+', dst_card)

# Old /notes/<slug>/<lang>/ share pages -> redirect to the new per-language URL
for l in ('zh', 'ja', 'ko'):
    new = '%s/notes/%s/' % (PREFIX[l], SLUG)
    wr('notes/%s/%s/index.html' % (SLUG, l),
       '<!DOCTYPE html>\n<html lang="%s">\n<head>\n  <meta charset="utf-8">\n  <meta name="robots" content="noindex">\n  <link rel="canonical" href="%s%s">\n'
       '  <meta http-equiv="refresh" content="0; url=%s">\n  <script>location.replace("%s");</script>\n</head>\n<body><a href="%s">%s</a></body>\n</html>\n'
       % (HTML_LANG[l], SITE, new, new, new, new, new))
# Root EN page: honour legacy ?lang= by redirecting to the per-language URL, then install
en_page = rd(SRC + '.new')
en_page = en_page.replace('</head>', '  <script>\n    (function () {\n      var l = new URLSearchParams(location.search).get("lang");\n      if (l === "zh" || l === "ja" || l === "ko") location.replace("/" + l + "/notes/%s/");\n    })();\n  </script>\n</head>' % SLUG, 1)
wr(SRC, en_page); os.remove(SRC + '.new')
for l in LANGS: os.remove('notes/%s/og-%s.png' % (SLUG, l))

# ---------------- the notes index ----------------
IDX = 'notes/index.html'
i = rd(IDX)
ib = blocks(i)
istyle = re.search(r'  <style>\n.*?\n  </style>\n', i, re.S).group(0)
istyle = istyle.replace('.lang-switch button {', '.lang-switch a, .lang-switch button {') \
               .replace('.lang-switch button[aria-selected="true"] {', '.lang-switch a[aria-current="page"], .lang-switch button[aria-selected="true"] {') \
               .replace('cursor: pointer; padding: 0.3rem 0.75rem;', 'cursor: pointer; text-decoration: none; padding: 0.3rem 0.75rem;')
ititles = dict(re.findall(r'(en|zh|ja|ko): "([^"]*)"', re.search(r'var TITLES = \{(.*?)\};', i, re.S).group(1)))
idesc = {'en': re.search(r'<meta name="description" content="([^"]*)"', i).group(1),
         'zh': '做 RocketBucket 的過程中學到的事，趁還記得的時候寫下來。',
         'ja': 'RocketBucket を作りながら学んだことを、まだ新しいうちに書き留めたもの。',
         'ko': 'RocketBucket을 만들며 배운 것들을, 아직 생생할 때 적어 둔 기록.'}
for l in LANGS:
    path = '/notes/'
    url = SITE + PREFIX[l] + path
    body = ib[l].replace('href="/notes/%s/?lang=%s"' % (SLUG, l), 'href="%s/notes/%s/"' % (PREFIX[l], SLUG))
    assert '?lang=' not in body, l
    page = ('<!DOCTYPE html>\n<html lang="%(hl)s">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '  <title>%(title)s</title>\n  <meta name="description" content="%(desc)s">\n'
            '  <meta property="og:type" content="website">\n  <meta property="og:title" content="RocketBucket %(nw)s">\n  <meta property="og:description" content="%(desc)s">\n  <meta property="og:url" content="%(url)s">\n'
            '  <meta property="og:image" content="%(site)s/og-card%(sfx)s.png">\n  <meta property="og:image:width" content="1200">\n  <meta property="og:image:height" content="630">\n  <meta property="og:site_name" content="RocketBucket">\n  <meta property="og:locale" content="%(loc)s">\n'
            '  <link rel="canonical" href="%(url)s">\n%(hreflang)s\n  <link rel="icon" type="image/png" href="/icon.png">\n  <link rel="stylesheet" href="/site.css">\n%(style)s</head>\n<body>\n%(nav)s\n  <main>\n%(body)s\n  </main>\n\n%(footer)s</body>\n</html>\n') % dict(
        hl=HTML_LANG[l], title=ititles[l], desc=idesc[l], nw=NOTES_WORD[l], url=url, site=SITE, sfx=('' if l == 'en' else '-' + l),
        loc=OG_LOCALE[l], hreflang=hreflang(path), style=istyle, nav=nav(l, path), body=body, footer=footer(l))
    out = IDX if l == 'en' else '%s/notes/index.html' % l
    wr(out, page); print('wrote', out)
print('done')
