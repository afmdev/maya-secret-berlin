#!/usr/bin/env python3
"""Genera las cuatro versiones del sitio desde src/ y los diccionarios de i18n/.

    src/index.html  ->  /index.html        (aleman, idioma principal)
                        /en/index.html
                        /es/index.html
                        /it/index.html

El aleman vive en la raiz: es el idioma oficial y el x-default de hreflang.
Cada idioma lleva sus propias rutas (massagen/, massages/, servicios/, servizi/)
y sus propios nombres de archivo. Las rutas de css/js/imgs se pasan a absolutas
para que no dependan de la profundidad de la carpeta.

    python3 scripts/i18n_build.py
"""
import html, json, os, posixpath, re, subprocess, sys
from urllib.parse import quote

SITE = 'https://mayaerotikmassage.com'
SRC = 'src'
PAGES = ['index.html', 'about.html', 'masajes.html', 'faq.html']
RITUALS = ['clasico', 'tantrico', 'cuerpo-a-cuerpo', 'nuru', 'lingam', 'yoni',
           'sensual', 'oriental', 'mutuo']
SRC_RITUAL = 'servicios/masaje-erotico-{}/index.html'
ASSET_DIRS = ('css', 'js', 'imgs', 'fonts', 'lib')

LANGS = {
    'de': {
        'label': 'DE', 'lang': 'de-DE', 'locale': 'de_DE', 'prefix': '',
        'pages': {'index.html': 'index.html', 'about.html': 'ueber-maya.html',
                  'masajes.html': 'erotische-massagen.html', 'faq.html': 'faq.html'},
        'dir': 'massagen',
        'slugs': {'clasico': 'klassische-erotische-massage', 'tantrico': 'erotische-tantra-massage',
                  'cuerpo-a-cuerpo': 'body-to-body-massage', 'nuru': 'nuru-massage',
                  'lingam': 'lingam-massage', 'yoni': 'yoni-massage',
                  'sensual': 'sinnliche-massage', 'oriental': 'orientalische-massage',
                  'mutuo': 'gegenseitige-massage'},
    },
    'en': {
        'label': 'EN', 'lang': 'en', 'locale': 'en_US', 'prefix': 'en',
        'pages': {'index.html': 'index.html', 'about.html': 'about-maya.html',
                  'masajes.html': 'erotic-massages.html', 'faq.html': 'faq.html'},
        'dir': 'massages',
        'slugs': {'clasico': 'classic-erotic-massage', 'tantrico': 'tantric-erotic-massage',
                  'cuerpo-a-cuerpo': 'body-to-body-massage', 'nuru': 'nuru-massage',
                  'lingam': 'lingam-massage', 'yoni': 'yoni-massage',
                  'sensual': 'sensual-massage', 'oriental': 'oriental-massage',
                  'mutuo': 'mutual-massage'},
    },
    'es': {
        'label': 'ES', 'lang': 'es-ES', 'locale': 'es_ES', 'prefix': 'es',
        'pages': {'index.html': 'index.html', 'about.html': 'sobre-maya.html',
                  'masajes.html': 'masajes.html', 'faq.html': 'preguntas-frecuentes.html'},
        'dir': 'servicios',
        'slugs': {r: 'masaje-erotico-' + r for r in RITUALS},
    },
    'it': {
        'label': 'IT', 'lang': 'it-IT', 'locale': 'it_IT', 'prefix': 'it',
        'pages': {'index.html': 'index.html', 'about.html': 'chi-e-maya.html',
                  'masajes.html': 'massaggi-erotici.html', 'faq.html': 'domande-frequenti.html'},
        'dir': 'servizi',
        'slugs': {'clasico': 'massaggio-erotico-classico', 'tantrico': 'massaggio-tantrico',
                  'cuerpo-a-cuerpo': 'massaggio-corpo-a-corpo', 'nuru': 'massaggio-nuru',
                  'lingam': 'massaggio-lingam', 'yoni': 'massaggio-yoni',
                  'sensual': 'massaggio-sensuale', 'oriental': 'massaggio-orientale',
                  'mutuo': 'massaggio-reciproco'},
    },
}
ORDER = ['de', 'en', 'es', 'it']
# Nombre del idioma en su propio idioma: lo que espera ver quien no entiende
# el idioma de la pagina en la que esta.
NATIVE = {'de': 'Deutsch', 'en': 'English', 'es': 'Español', 'it': 'Italiano'}
# Rotulo del boton: en el menu solo se ve la bandera, asi que el nombre del
# idioma vive en el aria-label (lector de pantalla) y en el title (raton).
PICK = {'de': 'Sprache wählen', 'en': 'Choose language',
        'es': 'Elegir idioma', 'it': 'Scegli lingua'}
# Rotulo del boton +/- del menu movil: el icono no dice nada a un lector de
# pantalla y el nombre del masaje ya lo lleva el enlace de al lado.
SUBMENU = {'de': 'Untermenü anzeigen', 'en': 'Show submenu',
           'es': 'Mostrar submenú', 'it': 'Mostra sottomenu'}

# Banderas: cuatro SVG propios en imgs/flags/ (los emoji de bandera no se
# dibujan en Windows). Van como <img> para que el navegador las cachee en vez
# de repetir el trazado en cada pagina.
def flag(l):
    return (f'<img class="maya-lang__flag" src="/imgs/flags/{l}.svg" alt="" '
            'width="20" height="15" decoding="async">')


# Paginas legales: una sola version, en aleman, compartida por los cuatro idiomas.
LEGAL = {'Impressum': '/impressum.html', 'Datenschutz': '/datenschutz.html'}

# Mensaje con el que se abre WhatsApp: deja claro el limite antes del primer
# mensaje, asi que va en el idioma de la pagina.
WA_TEXT = {
    'de': 'Hallo, ich habe Ihre Website gesehen und würde gern eine erotische Massage buchen. '
          'Mir ist klar, dass es ein sinnliches Erlebnis ist und kein sexueller Service. '
          'Welche Termine haben Sie frei?',
    'en': 'Hello, I saw your website and would like to book an erotic massage. I understand it is '
          'a sensual experience and not a sexual service. What availability do you have?',
    'es': 'Hola, he visto su web y me gustaría reservar un masaje erótico. Tengo claro que es una '
          'experiencia sensorial y no un servicio sexual. ¿Qué disponibilidad tiene?',
    'it': 'Salve, ho visto il suo sito e vorrei prenotare un massaggio erotico. So che è '
          'un\'esperienza sensoriale e non un servizio sessuale. Che disponibilità ha?',
}

SKIP = re.compile(r'<(script|style|svg)\b.*?</\1>|<!--.*?-->', re.S)
META = re.compile(r'(<meta\s+(?:name="(?:description|keywords)"|property="(?:og:title|og:description|og:image:alt|twitter:title|twitter:description)")[^>]*?content=")([^"]*)(")', re.I)
TAG_ATTR = re.compile(r'(<(?!link\b)[a-z][^>]*?\b(?:title|alt|aria-label|placeholder)=")([^"]*)(")', re.I)


def norm(s):
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def src_pages():
    return PAGES + [SRC_RITUAL.format(r) for r in RITUALS]


def out_path(page, lang):
    """Ruta de salida (relativa a la raiz del repo) de una pagina en un idioma."""
    cfg = LANGS[lang]
    m = re.match(r'servicios/masaje-erotico-(.+)/index\.html$', page)
    name = f"{cfg['dir']}/{cfg['slugs'][m.group(1)]}/index.html" if m else cfg['pages'][page]
    return posixpath.join(cfg['prefix'], name) if cfg['prefix'] else name


def url_of(page, lang):
    p = out_path(page, lang)
    return SITE + '/' + (p[:-len('index.html')] if p.endswith('index.html') else p)


def skip_ranges(src):
    return [(m.start(), m.end()) for m in SKIP.finditer(src)]


def in_skip(pos, ranges):
    return any(a <= pos < b for a, b in ranges)


def translate(src, dic):
    """Sustituye nodos de texto y atributos visibles usando el diccionario."""
    ranges = skip_ranges(src)
    out, last = [], 0
    for m in re.finditer(r'>([^<>]+)<', src):
        if in_skip(m.start(), ranges):
            continue
        raw = m.group(1)
        key = norm(raw)
        if key in dic and dic[key]:
            lead = raw[:len(raw) - len(raw.lstrip())]
            trail = raw[len(raw.rstrip()):]
            out.append(src[last:m.start(1)])
            out.append(lead + dic[key] + trail)
            last = m.end(1)
    out.append(src[last:])
    src = ''.join(out)

    def attr(m):
        key = norm(m.group(2))
        return m.group(1) + dic.get(key, m.group(2)) + m.group(3) if dic.get(key) else m.group(0)

    src = META.sub(attr, src)
    src = TAG_ATTR.sub(attr, src)
    src = re.sub(r'(<title>)(.*?)(</title>)',
                 lambda m: m.group(1) + dic.get(norm(m.group(2)), m.group(2)) + m.group(3),
                 src, flags=re.S)
    return src


def rewrite_urls(src, page, lang):
    """Enlaces internos al idioma destino; assets a ruta absoluta."""
    base = posixpath.dirname(page)
    pagemap = {p: url_of(p, lang)[len(SITE):] for p in src_pages()}

    def resolve(ref):
        if re.match(r'^(?:[a-z]+:|//|#|/)', ref, re.I):
            return None
        target = posixpath.normpath(posixpath.join(base, ref.split('#')[0].split('?')[0]))
        frag = ref[len(ref.split('#')[0]):]
        if target in pagemap:
            return pagemap[target] + frag
        if target.split('/')[0] in ASSET_DIRS:
            return '/' + target + frag
        return None

    def sub_attr(m):
        new = resolve(m.group(2))
        return m.group(1) + new + m.group(3) if new else m.group(0)

    src = re.sub(r'\b((?:href|src|data-src)=")([^"]+)(")', sub_attr, src)
    src = re.sub(r'(url\()([^)\'"]+)(\))', sub_attr, src)
    # Rutas de assets dentro de la configuracion JS: el regex de atributos no las
    # ve, y al ser relativas se resuelven contra la carpeta de la pagina. En
    # /en/ o /massagen/x/ eso es un 404 por cada chunk de Elementor (cientos de
    # errores en consola y el menu o el acordeon sin montar).
    src = re.sub(r'"jspath": "[^"]*"', '"jspath": "/js/"', src)
    src = re.sub(r'"assets": "[^"]*"', '"assets": "/"', src)
    src = re.sub(r'(https://wa\.me/\d+\?text=)[^"&]*',
                 lambda m: m.group(1) + quote(WA_TEXT[lang]), src)
    for label, href in LEGAL.items():
        src = re.sub(r'href="#"(\s*(?:class="[^"]*")?\s*>)(\s*)' + label,
                     f'href="{href}"\\1\\2{label}', src)
    return src


def head_meta(src, page, lang):
    cfg = LANGS[lang]
    url = url_of(page, lang)
    src = re.sub(r'<html lang="[^"]*"', f'<html lang="{cfg["lang"]}"', src, count=1)
    src = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>' + url + r'\2', src, count=1)
    src = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>' + url + r'\2', src, count=1)
    src = re.sub(r'(<meta property="og:locale" content=")[^"]*(")', r'\g<1>' + cfg['locale'] + r'\2', src, count=1)
    alts = ''.join(
        f'\n\t<link rel="alternate" hreflang="{LANGS[l]["lang"].split("-")[0]}" href="{url_of(page, l)}" />'
        for l in ORDER)
    alts += f'\n\t<link rel="alternate" hreflang="x-default" href="{url_of(page, "de")}" />'
    src = re.sub(r'(<link rel="canonical" href="[^"]*"\s*/?>)', lambda m: m.group(1) + alts, src, count=1)
    return src


def lang_switcher(src, page, lang):
    """Un desplegable de banderas junto al boton de contacto, en cada cabecera.

    <details> nativo: abre con teclado y sin JS; js/lang-switch.js solo anade
    cerrar al pulsar fuera o con Escape. El panel es un <div> y no un <ul>
    porque SmartMenus toma cualquier <ul> de la cabecera por sub-menu suyo,
    busca el enlace padre que no existe y deja el menu a medio montar.
    """
    options = ''.join(
        '<a class="maya-lang__link{}" href="{}" hreflang="{}" lang="{}" '
        'title="{}" aria-label="{}"{}>{}</a>'.format(
            ' is-current' if l == lang else '', url_of(page, l)[len(SITE):], l, l,
            NATIVE[l], NATIVE[l], ' aria-current="page"' if l == lang else '', flag(l))
        for l in ORDER)
    box = ('<div class="maya-lang"><details class="maya-lang__box">'
           f'<summary class="maya-lang__toggle" aria-label="{PICK[lang]}" title="{PICK[lang]}">'
           f'{flag(lang)}<span class="maya-lang__caret" aria-hidden="true"></span></summary>'
           f'<div class="maya-lang__panel">{options}</div>'
           '</details></div>')
    # El boton de contacto (widget bb9f07a) solo esta en las cabeceras, una por
    # maquetacion (escritorio, pegajosa y movil): el selector entra a su lado en
    # las tres y en ningun otro sitio de la pagina.
    btn = re.compile(r'<div class="[^"]*elementor-element-bb9f07a[^"]*"[^>]*>')
    src = btn.sub(lambda m: box + m.group(0), src)
    if 'lang-switch.js' not in src:
        src = src.replace('</body>', '\t<script src="/js/lang-switch.js" defer></script>\n'
                          '\t<script src="/js/mobile-menu.js" defer></script>\n</body>', 1)
    return src


def mobile_submenu(src, page, lang):
    """Boton +/- en los items con submenu del menu movil.

    El menu movil lo monta SmartMenus, que se queda el primer toque del enlace
    padre para desplegar: quien pulsa "Erotische Massagen" espera la pagina de
    masajes, no un acordeon. El boton separa las dos cosas (abrir y navegar) y
    usa el mismo par de iconos que el acordeon del FAQ; el resto lo hace
    js/mobile-menu.js. Solo en los <nav> desplegables: en escritorio manda el
    mega menu, que se abre al pasar el raton.
    """
    boton = ('<button class="maya-sub" type="button" aria-expanded="false" '
             f'aria-label="{SUBMENU[lang]}">'
             '<i aria-hidden="true" class="mayaerotikmassagetheme- mayaerotikmassage-theme-plus"></i>'
             '<i aria-hidden="true" class="mayaerotikmassagetheme- mayaerotikmassage-theme-minus"></i>'
             '</button>')
    masajes = url_of('masajes.html', lang)[len(SITE):]
    # El texto del enlace puede traer la flechita de SmartMenus, asi que el
    # cierre se busca con un (?!</a>) en vez de con [^<]*.
    padre = re.compile(r'(<a\s[^>]*class="[^"]*elementor-item[^"]*"[^>]*)'
                       r'(>(?:(?!</a>).)*?</a>)(\s*<ul class="sub-menu)', re.S)

    def en_nav(m):
        visto = [0]

        def marca(a):
            visto[0] += 1
            tag = a.group(1)
            href = re.search(r'href="([^"]*)"', tag)
            destino = href.group(1) if href else ''
            # La plantilla del menu movil deja el padre en href="#"; el primero
            # es el de masajes, asi que se le pone su pagina. Los demas padres
            # sin destino se quedan solo como desplegable.
            if destino in ('', '#') and visto[0] == 1:
                destino = masajes
            if destino in ('', '#'):
                return tag + a.group(2) + boton + a.group(3)
            return tag + f' data-maya-href="{destino}"' + a.group(2) + boton + a.group(3)

        return padre.sub(marca, m.group(0))

    return re.sub(r'<nav class="elementor-nav-menu--dropdown[^"]*"[^>]*>.*?</nav>',
                  en_nav, src, flags=re.S)


def build_page(page, lang, dic):
    src = open(posixpath.join(SRC, page), encoding='utf-8').read()
    src = translate(src, dic) if lang != 'es' else src
    src = rewrite_urls(src, page, lang)
    src = head_meta(src, page, lang)
    src = lang_switcher(src, page, lang)
    src = mobile_submenu(src, page, lang)
    dest = out_path(page, lang)
    os.makedirs(os.path.dirname(dest) or '.', exist_ok=True)
    open(dest, 'w', encoding='utf-8').write(src)
    return dest


def redirects():
    """URLs españolas antiguas (estaban en la raiz) -> su sitio en /es/."""
    lines = ['# Generado por scripts/i18n_build.py: las URLs españolas vivian en la raiz.',
             '# index.html y faq.html se omiten: esas rutas las ocupa ahora el aleman,',
             '# que es el idioma principal. El hreflang lleva al visitante a /es/.']
    taken = {out_path(p, 'de') for p in src_pages()}
    for page in src_pages():
        if page in taken:
            continue
        new = url_of(page, 'es')[len(SITE):]
        lines.append(f'/{page} {new} 301')
        if page.endswith('/index.html'):
            lines.append(f'/{page[:-len("index.html")]} {new} 301')
    open('_redirects', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


def sitemap():
    rows = []
    for page in src_pages():
        for lang in ORDER:
            alts = ''.join(
                f'\n\t\t<xhtml:link rel="alternate" hreflang="{LANGS[l]["lang"].split("-")[0]}" href="{url_of(page, l)}" />'
                for l in ORDER)
            rows.append(f'\t<url>\n\t\t<loc>{url_of(page, lang)}</loc>{alts}\n\t</url>')
    open('sitemap.xml', 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n')


def load_dict(lang):
    """i18n/strings.<lang>.tsv: una linea "<indice>\t<traduccion>" por cadena.

    El indice es el orden de i18n/strings.es.json y se valida, asi que una
    linea de mas o de menos se nota al construir en vez de en la web.
    """
    keys = list(json.load(open('i18n/strings.es.json', encoding='utf-8')))
    dic = {}
    for n, line in enumerate(open(f'i18n/strings.{lang}.tsv', encoding='utf-8')):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        idx, _, text = line.partition('\t')
        i = int(idx)
        if i != n:
            raise SystemExit(f'{lang}.tsv linea {n}: indice {i} no coincide')
        dic[keys[i]] = text.strip()
    if len(dic) != len(keys):
        raise SystemExit(f'{lang}.tsv: {len(dic)} cadenas, se esperaban {len(keys)}')
    return dic


def main():
    built = []
    for lang in ORDER:
        dic = {}
        if lang != 'es':
            try:
                dic = load_dict(lang)
            except FileNotFoundError:
                print(f'FALTA i18n/strings.{lang}.tsv: {lang} omitido'); continue
        for page in src_pages():
            built.append(build_page(page, lang, dic))
        print(f'{lang}: {len(src_pages())} paginas')
    redirects()
    sitemap()
    subprocess.run([sys.executable, 'scripts/faqjson.py', '--write'] + built, check=True)
    print(f'{len(built)} paginas, _redirects y sitemap.xml generados')


if __name__ == '__main__':
    main()
