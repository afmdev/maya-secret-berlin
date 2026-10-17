#!/usr/bin/env python3
"""Extrae cada cadena traducible de las paginas y escribe i18n/strings.es.json.

Una cadena = un nodo de texto o un atributo visible (title, alt, aria-label,
placeholder, meta content). La clave es el texto espanol normalizado, asi que
una cadena repetida en varias paginas se traduce una sola vez.

    python3 scripts/i18n_extract.py
"""
import glob, html, json, os, re, sys

PAGES = ['src/index.html', 'src/masajes.html', 'src/faq.html', 'src/about.html'] + sorted(glob.glob('src/servicios/*/index.html'))
SKIP = re.compile(r'<(script|style|svg)\b.*?</\1>|<!--.*?-->|<script\b[^>]*/?>', re.S)
# Solo estos meta llevan texto para humanos; el resto (viewport, generator,
# feeds, favicons) no se traduce.
META = re.compile(r'<meta\s+(?:name="(?:description|keywords|twitter:title|twitter:description)"|property="(?:og:title|og:description|og:image:alt)")[^>]*?content="([^"]*)"', re.I)
# title/alt/aria-label/placeholder, menos los de <link> (titulos de feeds).
TAG_ATTR = re.compile(r'<(?!link\b)[a-z][^>]*?\b(?:title|alt|aria-label|placeholder)="([^"]*)"', re.I)

def norm(s):
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def units(src):
    """(tipo, texto_normalizado) de cada unidad traducible."""
    masked = SKIP.sub(lambda m: ' ' * len(m.group(0)), src)
    out = []
    for m in re.finditer(r'>([^<>]+)<', masked):
        t = norm(m.group(1))
        if t and re.search(r'[A-Za-zÀ-ÿ]', t):
            out.append(('text', t))
    for rx in (META, TAG_ATTR):
        for m in rx.finditer(masked):
            t = norm(m.group(1))
            if t and re.search(r'[A-Za-zÀ-ÿ]{3}', t):
                out.append(('attr', t))
    for m in re.finditer(r'<title>(.*?)</title>', src, re.S):
        out.append(('title', norm(m.group(1))))
    return out

def main():
    strings = {}
    for p in PAGES:
        src = open(p, encoding='utf-8').read()
        for kind, t in units(src):
            e = strings.setdefault(t, {'kind': kind, 'pages': []})
            if p not in e['pages']:
                e['pages'].append(p)
    os.makedirs('i18n', exist_ok=True)
    out = {t: {'kind': v['kind'], 'pages': v['pages'], 'words': len(t.split())}
           for t, v in strings.items()}
    with open('i18n/strings.es.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"{len(out)} cadenas unicas, {sum(v['words'] for v in out.values())} palabras -> i18n/strings.es.json")

if __name__ == '__main__':
    main()
