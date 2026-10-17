#!/usr/bin/env python3
"""Regenera el JSON-LD de FAQPage a partir del acordeon visible de cada pagina.

El marcado debe coincidir con lo que se ve en pantalla, asi que las preguntas y
respuestas se extraen del HTML, no se escriben a mano. Desde la raiz del repo:

    python3 scripts/faqjson.py            # dry-run: imprime lo que encuentra
    python3 scripts/faqjson.py --write    # reescribe el bloque en cada pagina
"""
import glob, html, json, re, sys

TITLE = re.compile(r'e-n-accordion-item-title-text">(.*?)</div>', re.S)
PARA  = re.compile(r'<p>(.*?)</p>', re.S)

def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()

def faqs(src):
    out = []
    for m in TITLE.finditer(src):
        end = src.find('</details>', m.end())
        body = src[m.end():end if end != -1 else len(src)]
        ans = ' '.join(clean(p) for p in PARA.findall(body))
        out.append((clean(m.group(1)), ans))
    return out

def block(path, src, items):
    canonical = re.search(r'rel="canonical" href="(.*?)"', src).group(1)
    title = clean(re.search(r'<title>(.*?)</title>', src, re.S).group(1))
    lang = re.search(r'<html lang="([^"]+)"', src).group(1)
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "@id": canonical + "#faq",
        "inLanguage": lang,
        "name": title,
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in items
        ],
    }
    body = json.dumps(data, ensure_ascii=False, indent=2).replace('\n', '\n\t')
    return ('\t<!-- Preguntas frecuentes en schema.org: el mismo acordeon, legible para\n'
            '\t     buscadores (rich results). Si cambia una respuesta, cambiela aqui tambien. -->\n'
            '\t<script type="application/ld+json">\n\t' + body + '\n\t</script>\n')

OLD = re.compile(r'\t*(?:<!--(?:(?!-->).)*?rich results.*?-->\s*)?<script type="application/ld\+json">.*?</script>\n', re.S)

dry = '--write' not in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('--')]
targets = args or ['index.html', 'faq.html'] + sorted(glob.glob('servicios/*/index.html'))
for path in targets:
    src = open(path, encoding='utf-8').read()
    items = faqs(src)
    if not items:
        print(f'{path}: sin FAQ, omitido'); continue
    new = block(path, src, items)
    if OLD.search(src):
        src2 = OLD.sub(lambda _: new, src, count=1)
    else:
        src2 = src.replace('</head>', new + '</head>', 1)
    print(f'--- {path}: {len(items)} preguntas')
    if dry:
        for q, a in items:
            print(f'  Q: {q}\n  A: {a[:160]}{"..." if len(a) > 160 else ""}')
    else:
        open(path, 'w', encoding='utf-8').write(src2)
