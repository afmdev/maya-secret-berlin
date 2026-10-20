#!/usr/bin/env python3
"""Construye css/site.css desde src/css/: purga, minifica y une.

    src/css/app.css  (volcado de Elementor, 575 KB)
    src/css/*.css    (las cinco hojas escritas a mano)   ->  css/site.css

Una sola hoja porque cinco <link> son cinco peticiones que bloquean el
render, y en movil cada una cuesta ~300 ms de latencia aunque pese 1 KB.
Todo sale minificado: los comentarios y la indentacion viven en src/.

El criterio es el de PurgeCSS y es deliberadamente conservador: un selector
sobrevive si TODAS sus clases e ids aparecen sueltos en algun HTML construido.
No se mira el estado (hover, focus, clases que pone el JS): para eso esta
SALVADAS, y las pseudo-clases se recortan antes de comparar, asi que
".foo:hover" vive o muere con ".foo".

    python3 scripts/css_purge.py            # construye css/
    python3 scripts/css_purge.py --informe  # ademas lista lo que se va
    python3 scripts/css_purge.py --test     # autocomprobacion del minificador

Lo llama scripts/i18n_build.py al final, cuando las 52 paginas ya existen.
"""
import glob, os, re, sys

DESTINO = 'css/site.css'

# (origen, podar) EN EL ORDEN DE LA CASCADA: es el mismo en el que iban los
# <link>, y cambiarlo cambia quien gana. Solo app.css se poda: es el volcado
# de Elementor y sobra el 60%. Las hojas escritas a mano se escribieron para
# esta web, asi que ahi podar solo seria una forma rebuscada de romper algo.
FUENTES = [
    ('src/css/app.css',            True),
    ('src/css/app-late.css',       False),
    ('src/css/theme-palettes.css', False),
    ('src/css/mega-menu.css',      False),
    ('src/css/spotlight.css',      False),
    # service.css solo la usaban las 36 paginas de ritual, pero pesa 2,6 KB
    # comprimida: menos que la peticion extra que costaba servirla aparte.
    ('src/css/service.css',        False),
]

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


def minificar(texto, declaraciones):
    """Colapsa el espacio en blanco, sin tocar el interior de las cadenas.

    En declaraciones el espacio junto a ':', ';', ',' y los parentesis no
    significa nada y se va; en selectores el espacio ES el combinador de
    descendencia, asi que solo se reduce a uno."""
    fuera, i, n = [], 0, len(texto)
    while i < n:
        c = texto[i]
        if c in '"\'':                      # cadena: entera y sin mirar
            fin = texto.find(c, i + 1)
            while fin > 0 and texto[fin - 1] == '\\':
                fin = texto.find(c, fin + 1)
            fin = fin if fin > 0 else n
            fuera.append(texto[i:fin + 1])
            i = fin + 1
            continue
        if c.isspace():
            while i < n and texto[i].isspace():
                i += 1
            if not fuera or i >= n:          # ni al principio ni al final
                continue
            pega = declaraciones and (fuera[-1][-1] in ':;,(' or texto[i] in ':;,)')
            if not pega:
                fuera.append(' ')
            continue
        fuera.append(c)
        i += 1
    salida = ''.join(fuera)
    # El ultimo ';' de un bloque no separa nada.
    return salida[:-1] if declaraciones and salida.endswith(';') else salida


def purgar(nodos, vistos, fuera, podar=True):
    salida = []
    for prefijo, cuerpo in nodos:
        if cuerpo is None:
            salida.append(minificar(prefijo, False) + ';')
            continue
        # Un "{}" sin selector o sin declaraciones es un error de sintaxis: el
        # navegador descarta desde ahi hasta que logra resincronizar y se lleva
        # por delante reglas buenas.
        if not prefijo.strip() or not cuerpo.strip():
            continue
        if prefijo.startswith('@'):
            corto = minificar(prefijo, False)
            if prefijo.split()[0].lower() in AT_INTOCABLES:
                # @keyframes lleva reglas dentro ('0%', 'from'); @font-face solo
                # declaraciones. Ninguno se poda: sus selectores no son del HTML.
                dentro = (purgar(trocear(cuerpo), vistos, fuera, False)
                          if '{' in cuerpo else minificar(cuerpo, True))
                if dentro:
                    salida.append(f'{corto}{{{dentro}}}')
                continue
            dentro = purgar(trocear(cuerpo), vistos, fuera, podar)  # @media, @supports
            if dentro.strip():
                salida.append(f'{corto}{{{dentro}}}')
            continue
        selectores = separar_selectores(prefijo)
        vivos = [s for s in selectores if not podar or sobrevive(s, vistos)]
        muertos = len(selectores) - len(vivos)
        if muertos:
            fuera.append((prefijo, muertos))
        cuerpo = minificar(cuerpo, True)
        if vivos and cuerpo:
            salida.append(f'{",".join(minificar(s, False) for s in vivos)}{{{cuerpo}}}')
    return ''.join(salida)


def autocomprobacion():
    """Lo unico que puede romper la web aqui es el minificador: un espacio de
    mas o de menos cambia el significado. Estos son los sitios donde duele."""
    assert minificar('\n\tcolor : red ;\n', True) == 'color:red'
    assert minificar('margin: calc(100% - 10px) 0;', True) == 'margin:calc(100% - 10px) 0'
    assert minificar('transform: translate( -50% , 0 )', True) == 'transform:translate(-50%,0)'
    assert minificar('color: red !important;', True) == 'color:red !important'
    assert minificar('content: "a  ,  b";', True) == 'content:"a  ,  b"'
    assert minificar('.a\n\t.b', False) == '.a .b'          # descendencia: el espacio manda
    assert minificar('a\n:hover', False) == 'a :hover'
    nodos = trocear(sin_comentarios('a /* x */ {  color : red ; }  @media (min-width: 9px){'
                                    '.a{top:0}}  @keyframes k{from{opacity:0}}'
                                    '  .no-existe{top:0}'))
    hecho = purgar(nodos, {'a'}, [], True)
    assert hecho == 'a{color:red}@media (min-width: 9px){.a{top:0}}@keyframes k{from{opacity:0}}', hecho
    assert purgar(trocear('.no-existe{top:0}'), {'a'}, [], False) == '.no-existe{top:0}'
    print('minificador ok')


def main():
    if '--test' in sys.argv:
        return autocomprobacion()
    paginas = [p for p in glob.glob('**/*.html', recursive=True)
               if not p.startswith(('src/', 'inspiration/', 'docs/'))]
    if len(paginas) < 50:
        raise SystemExit(f'solo {len(paginas)} paginas construidas: ejecuta antes i18n_build.py')
    vistos = candidatos(paginas)
    print(f'{len(paginas)} paginas, {len(vistos)} nombres en uso')
    trozos, total = [], 0
    for origen, podar in FUENTES:
        css = open(origen, encoding='utf-8').read()
        fuera = []
        limpio = purgar(trocear(sin_comentarios(css)), vistos, fuera, podar)
        if not limpio.strip():
            raise SystemExit(f'{origen} se ha quedado vacio: algo va mal')
        trozos.append(limpio)
        total += len(css)
        antes, ahora = len(css) / 1024, len(limpio) / 1024
        print(f'  {os.path.basename(origen):<20} {antes:6.0f} KB -> {ahora:5.0f} KB '
              f'({100 - ahora / antes * 100:2.0f}% menos){"" if podar else "  [solo minificado]"}')
        if '--informe' in sys.argv and podar:
            for sel, n in fuera[:60]:
                print(f'    -{n:3d}  {sel[:150]}')
    # @charset solo vale al principio del fichero: unido va al medio y el
    # navegador se lo salta con un aviso. El HTML ya declara UTF-8.
    unido = re.sub(r'@charset [^;]+;', '', ''.join(trozos))
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    open(DESTINO, 'w', encoding='utf-8').write(unido)
    print(f'  {"-" * 20} {total / 1024:6.0f} KB -> {len(unido) / 1024:5.0f} KB  {DESTINO}')


if __name__ == '__main__':
    main()
