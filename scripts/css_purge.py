#!/usr/bin/env python3
"""Quita de app.css las reglas que ninguna pagina usa.

    src/css/app.css  (volcado de Elementor, 575 KB)  ->  css/app.css

El criterio es el de PurgeCSS y es deliberadamente conservador: un selector
sobrevive si TODAS sus clases e ids aparecen sueltos en algun HTML construido.
No se mira el estado (hover, focus, clases que pone el JS): para eso esta
SALVADAS, y las pseudo-clases se recortan antes de comparar, asi que
".foo:hover" vive o muere con ".foo".

    python3 scripts/css_purge.py            # construye css/app.css
    python3 scripts/css_purge.py --informe  # ademas lista lo que se va

Lo llama scripts/i18n_build.py al final, cuando las 52 paginas ya existen.
"""
import glob, os, re, sys

FUENTE = 'src/css/app.css'
DESTINO = 'css/app.css'

# Clases que el JS pone en marcha y que por tanto no estan en el HTML servido.
SALVADAS = re.compile(r'''^(
    animated|animated-fast|fadeIn|fadeInUp|zoomIn|slideInUp|slideInDown|
    elementor-invisible|elementor-active|elementor-sticky.*|e-lazyloaded|
    maya-menu-open|maya-agegate.*|is-open|lenis.*|split-line|no-js|
    elementor-animation-.*|mayaerotikmassage-sticky-header--.*|
    elementor-motion-effects.*|swiper.*|elementor-lightbox.*|dialog-.*
)$''', re.X)

# Etiquetas que siempre pueden aparecer (las pinta el navegador o el JS).
ETIQUETAS_BASE = {'html', 'body', ':root', 'a', 'div', 'span', 'p', 'img', 'ul', 'li',
                  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'button', 'input', 'form', 'svg',
                  'picture', 'source', 'section', 'header', 'footer', 'nav', 'main',
                  'aside', 'article', 'figure', 'figcaption', 'details', 'summary',
                  'dialog', 'label', 'table', 'tr', 'td', 'th', 'code', 'pre', 'strong',
                  'em', 'b', 'i', 'small', 'hr', 'br', 'iframe', 'video', 'audio',
                  'select', 'textarea', 'option', 'fieldset', 'legend', 'blockquote',
                  'ol', 'dl', 'dt', 'dd', 'canvas', 'template', 'noscript', '*'}

# At-rules que se quedan enteras: definen recursos o variables, no estilan nada
# que se pueda rastrear por selector.
AT_INTOCABLES = ('@font-face', '@keyframes', '@-webkit-keyframes', '@charset',
                 '@import', '@property', '@page', '@counter-style')


def sin_comentarios(css):
    """Fuera los /* */ (respetando cadenas): si no, el comentario que precede a
    una regla viaja pegado al selector y lo manda a la basura por error."""
    fuera, i, n = [], 0, len(css)
    while i < n:
        c = css[i]
        # El comentario va primero: dentro de uno, un apostrofo ("Maya's") no
        # abre ninguna cadena, y tratarlo como tal se come el resto del fichero.
        if css.startswith('/*', i):
            fin = css.find('*/', i + 2)
            i = (fin + 2) if fin > 0 else n
            fuera.append(' ')
        elif c in '"\'':
            fin = css.find(c, i + 1)
            while fin > 0 and css[fin - 1] == '\\':
                fin = css.find(c, fin + 1)
            fin = fin if fin > 0 else n
            fuera.append(css[i:fin + 1])
            i = fin + 1
        else:
            fuera.append(c)
            i += 1
    return ''.join(fuera)


def trocear(css):
    """[(prefijo, cuerpo_o_None)] en orden. prefijo es el selector o la at-rule."""
    fuera, prof, ini, i = [], 0, 0, 0
    n = len(css)
    while i < n:
        c = css[i]
        if c in '"\'':                      # cadena: saltarla entera
            fin = css.find(c, i + 1)
            while fin > 0 and css[fin - 1] == '\\':
                fin = css.find(c, fin + 1)
            i = (fin if fin > 0 else n) + 1
            continue
        if css.startswith('/*', i):
            i = css.find('*/', i + 2)
            i = (i + 2) if i > 0 else n
            continue
        if c == '{':
            if prof == 0:
                prefijo, cuerpo_ini = css[ini:i].strip(), i + 1
            prof += 1
        elif c == '}':
            prof -= 1
            if prof == 0:
                fuera.append((prefijo, css[cuerpo_ini:i]))
                ini = i + 1
        elif c == ';' and prof == 0:        # at-rule sin cuerpo (@charset, @import)
            suelta = css[ini:i].strip()
            if suelta:
                fuera.append((suelta, None))
            ini = i + 1
        i += 1
    return fuera


def candidatos(paginas):
    """Clases, ids y etiquetas que aparecen en el HTML construido."""
    vistos = set(ETIQUETAS_BASE)
    for p in paginas:
        s = open(p, encoding='utf-8', errors='ignore').read()
        for m in re.finditer(r'class="([^"]*)"', s):
            vistos.update(m.group(1).split())
        for m in re.finditer(r'\bid="([^"]*)"', s):
            vistos.add(m.group(1))
        vistos.update(t.lower() for t in re.findall(r'<([a-zA-Z][\w-]*)', s))
    return vistos


FICHAS = re.compile(r'[.#]([-\w]+)')          # .clase / #id
PSEUDO = re.compile(r'::?[-\w]+(\([^)]*\))?')  # :hover, ::before, :not(...)
ATRIBUTO = re.compile(r'\[([-\w]+)[^\]]*\]')


def sobrevive(sel, vistos):
    nombres_attr = ATRIBUTO.findall(sel)
    limpio = ATRIBUTO.sub(' ', PSEUDO.sub(' ', sel))
    fichas = FICHAS.findall(limpio)
    if any(SALVADAS.match(f) for f in fichas):
        return True
    if not all(f in vistos for f in fichas):
        return False
    # Etiquetas sueltas: solo se descartan si son un nombre que no existe aqui.
    for etiqueta in re.findall(r'(?:^|[\s>+~])([a-zA-Z][\w-]*)', limpio):
        if etiqueta.lower() not in vistos:
            return False
    # Un selector que solo filtra por atributo se queda: el atributo puede
    # llevar valores que el HTML no muestra literalmente.
    if not fichas and nombres_attr:
        return True
    return True


def separar_selectores(prefijo):
    """Parte por las comas de primer nivel. Dentro de :is(), :not() o [attr]
    la coma no separa nada, y cortar ahi deja selectores rotos que el navegador
    arrastra hasta el final del fichero."""
    partes, actual, prof = [], [], 0
    for c in prefijo:
        if c in '([':
            prof += 1
        elif c in ')]':
            prof -= 1
        if c == ',' and prof == 0:
            partes.append(''.join(actual))
            actual = []
        else:
            actual.append(c)
    partes.append(''.join(actual))
    return [p.strip() for p in partes if p.strip()]


def purgar(nodos, vistos, fuera):
    salida = []
    for prefijo, cuerpo in nodos:
        if cuerpo is None:
            salida.append(prefijo + ';')
            continue
        # Un "{}" sin selector o sin declaraciones es un error de sintaxis: el
        # navegador descarta desde ahi hasta que logra resincronizar y se lleva
        # por delante reglas buenas.
        if not prefijo.strip() or not cuerpo.strip():
            continue
        if prefijo.startswith('@'):
            if prefijo.split()[0].lower() in AT_INTOCABLES:
                salida.append(f'{prefijo}{{{cuerpo}}}')
                continue
            dentro = purgar(trocear(cuerpo), vistos, fuera)   # @media, @supports
            if dentro.strip():
                salida.append(f'{prefijo}{{{dentro}}}')
            continue
        selectores = separar_selectores(prefijo)
        vivos = [s for s in selectores if sobrevive(s, vistos)]
        muertos = len(selectores) - len(vivos)
        if muertos:
            fuera.append((prefijo, muertos))
        if vivos:
            salida.append(f'{",".join(vivos)}{{{cuerpo}}}')
    return ''.join(salida)


def main():
    paginas = [p for p in glob.glob('**/*.html', recursive=True)
               if not p.startswith(('src/', 'inspiration/', 'docs/'))]
    if len(paginas) < 50:
        raise SystemExit(f'solo {len(paginas)} paginas construidas: ejecuta antes i18n_build.py')
    vistos = candidatos(paginas)
    css = open(FUENTE, encoding='utf-8').read()
    fuera = []
    limpio = purgar(trocear(sin_comentarios(css)), vistos, fuera)
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    open(DESTINO, 'w', encoding='utf-8').write(limpio)
    antes, ahora = len(css) / 1024, len(limpio) / 1024
    print(f'app.css: {antes:.0f} KB -> {ahora:.0f} KB ({100 - ahora / antes * 100:.0f}% menos), '
          f'{len(paginas)} paginas, {len(vistos)} nombres en uso')
    if '--informe' in sys.argv:
        for sel, n in fuera[:60]:
            print(f'  -{n:3d}  {sel[:150]}')


if __name__ == '__main__':
    main()
