#!/usr/bin/env python3
"""Lagert Inline-Styles und <style>-Blöcke aller HTML-Seiten in externe CSS-Dateien aus."""
import collections
import glob
import html as htmlmod
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
FILES = sorted(glob.glob(str(ROOT / '*.html')))
STYLE_ATTR = re.compile(r'\sstyle\s*=\s*("([^"]*)"|\'([^\']*)\')')
TAG = re.compile(r'<[a-zA-Z][^>]*>')
CLASS_D = re.compile(r'(?<![\w-])class\s*=\s*"([^"]*)"')
CLASS_S = re.compile(r"(?<![\w-])class\s*=\s*'([^']*)'")

def attr_value(m):
    return (m.group(2) if m.group(2) is not None else m.group(3)).strip()

# Pass 1: alle einzigartigen Inline-Style-Werte sammeln (Häufigkeit -> stabile Namen)
counter = collections.Counter()
for f in FILES:
    for m in STYLE_ATTR.finditer(open(f, encoding='utf-8').read()):
        v = attr_value(m)
        if v:
            counter[v] += 1
classmap = {v: f'iw-{i+1:03d}' for i, (v, _) in enumerate(counter.most_common())}

def split_decls(css):
    parts, depth, cur = [], 0, ''
    for ch in css:
        if ch == '(': depth += 1
        elif ch == ')': depth = max(0, depth - 1)
        if ch == ';' and depth == 0:
            parts.append(cur); cur = ''
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]

def to_rule(cls, raw):
    decls = split_decls(htmlmod.unescape(raw))
    body = ' '.join(d + ' !important;' for d in decls)
    return f'.{cls} {{ {body} }}'

def fix_tag(tag):
    m = STYLE_ATTR.search(tag)
    if not m:
        return tag
    v = attr_value(m)
    tag = tag[:m.start()] + tag[m.end():]
    if not v:
        return tag
    cls = classmap[v]
    for rx in (CLASS_D, CLASS_S):
        cm = rx.search(tag)
        if cm:
            sep = ' ' if cm.group(1).strip() else ''
            return tag[:cm.end(1)] + sep + cls + tag[cm.end(1):]
    nm = re.match(r'<[a-zA-Z][a-zA-Z0-9]*', tag)
    return tag[:nm.end()] + f' class="{cls}"' + tag[nm.end():]

APP_LINK = '<link rel="stylesheet" href="assets/app.css">'
IW_LINK = '<link rel="stylesheet" href="assets/legacy-inline.css">'

changed, style_blocks_moved = 0, 0
for f in FILES:
    h = open(f, encoding='utf-8').read()
    orig = h
    # <style>-Blöcke auslagern (aktuell nur 404.html)
    for sm in re.finditer(r'([ \t]*)<style[^>]*>(.*?)</style>\n?', h, re.S | re.I):
        css = sm.group(2).strip()
        name = f.rsplit('/', 1)[-1].replace('.html', '') + '.css'
        (ASSETS / name).write_text(css + '\n', encoding='utf-8')
        h = h.replace(sm.group(0), f'{sm.group(1)}<link rel="stylesheet" href="assets/{name}">\n')
        style_blocks_moved += 1
    # Inline-Styles -> Klassen
    h = TAG.sub(lambda m: fix_tag(m.group(0)), h)
    # Stylesheet einbinden (nur wenn Seite iw-Klassen nutzt)
    if re.search(r'class="[^"]*\biw-\d', h) and IW_LINK not in h:
        if APP_LINK in h:
            h = h.replace(APP_LINK, APP_LINK + '\n' + IW_LINK, 1)
        else:
            h = h.replace('</head>', IW_LINK + '\n</head>', 1)
    if h != orig:
        open(f, 'w', encoding='utf-8').write(h)
        changed += 1

# CSS-Datei schreiben
header = """/* ============================================================
   legacy-inline.css — automatisch extrahierte Inline-Styles
   Jeder ehemalige style="…"-Wert wurde dedupliziert und als
   Klasse .iw-NNN ausgelagert (sortiert nach Häufigkeit).
   !important erhält die ursprüngliche Inline-Style-Priorität
   gegenüber den Regeln in app.css (kein visueller Unterschied).
   ============================================================ */
"""
rules = [to_rule(cls, raw) for raw, cls in classmap.items()]
(ASSETS / 'legacy-inline.css').write_text(header + '\n'.join(rules) + '\n', encoding='utf-8')

# Map für Verifikation (temporär)
(ASSETS / 'iw-map.json').write_text(
    json.dumps({cls: htmlmod.unescape(raw) for raw, cls in classmap.items()}),
    encoding='utf-8',
)

rest = sum(len(STYLE_ATTR.findall(open(f, encoding='utf-8').read())) for f in FILES)
print(f'classes={len(classmap)} files_changed={changed} style_blocks_moved={style_blocks_moved} remaining_style_attrs={rest}')
