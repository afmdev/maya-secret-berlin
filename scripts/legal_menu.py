#!/usr/bin/env python3
"""Pone el selector de idioma de impressum.html y datenschutz.html al dia.

Esas dos paginas se mantienen a mano y quedan fuera de scripts/i18n_build.py
(son alemanas y las comparten los cuatro idiomas), asi que cada vez que cambia
la cabecera se quedan con la version anterior. El 17/10/2026 el selector paso
de la cabecera movil al interior del menu en las 52 paginas generadas y estas
dos se quedaron con el desplegable descuadrado.

Hace lo mismo que lang_switcher() en la cabecera movil: saca el <details> de
la fila del boton de contacto y deja las cuatro banderas en fila al final del
<nav> que abre la hamburguesa. Es idempotente: pasarlo dos veces no cambia nada.

    python3 scripts/legal_menu.py
"""
import re, sys

sys.path.insert(0, 'scripts')
from i18n_build import PICK  # el rotulo del selector, en el idioma de la pagina

PAGINAS = ['impressum.html', 'datenschutz.html']
# La cabecera movil es la ultima del bloque: lo de antes son la pegajosa y su
# espaciador, que se esconden en tablet y movil.
MARCA_MOVIL = 'elementor-element-ae335e5'
CAJA = re.compile(r'<div class="maya-lang"><details class="maya-lang__box">.*?</details></div>', re.S)
ENLACE = re.compile(r'<a class="maya-lang__link.*?</a>', re.S)
NAV = re.compile(r'(<nav class="elementor-nav-menu--dropdown[^"]*"[^>]*>(?:(?!</nav>).)*?)</nav>', re.S)


def arregla(src):
    """Devuelve (html, cambiado)."""
    corte = src.index(MARCA_MOVIL)
    arriba, movil = src[:corte], src[corte:]
    caja = CAJA.search(movil)
    if not caja:
        return src, False  # ya estaba hecho
    enlaces = ''.join(ENLACE.findall(caja.group(0)))
    lang = (re.search(r'<html lang="([a-z]{2})', src) or [None, 'de'])[1]
    fila = (f'<div class="maya-lang maya-lang--flat" role="group" aria-label="{PICK[lang]}">'
            f'{enlaces}</div>')
    movil = movil[:caja.start()] + movil[caja.end():]
    movil, n = NAV.subn(lambda m: m.group(1) + fila + '</nav>', movil, count=1)
    if n != 1:
        raise SystemExit('no se encontro el <nav> desplegable de la cabecera movil')
    return arriba + movil, True


def main():
    for p in PAGINAS:
        src = open(p, encoding='utf-8').read()
        nuevo, cambiado = arregla(src)
        if cambiado:
            open(p, 'w', encoding='utf-8').write(nuevo)
        print(f'{p}: {"actualizado" if cambiado else "ya estaba al dia"}')


def demo():
    """Comprobacion: mueve la caja una vez y la segunda pasada no toca nada."""
    muestra = (f'<html lang="de-DE"><div class="{MARCA_MOVIL}">'
               '<div class="maya-lang"><details class="maya-lang__box">'
               '<a class="maya-lang__link" href="/">DE</a>'
               '<a class="maya-lang__link" href="/en/">EN</a>'
               '</details></div><div class="elementor-element-bb9f07a"></div>'
               '<nav class="elementor-nav-menu--dropdown x"><ul><li>a</li></ul></nav></div></html>')
    una, c1 = arregla(muestra)
    assert c1
    assert 'maya-lang__box' not in una, 'el desplegable sigue en la cabecera movil'
    assert una.index('maya-lang--flat') > una.index('elementor-nav-menu--dropdown'), 'la fila no entro en el nav'
    assert una.count('maya-lang__link') == 2, 'se perdio algun idioma'
    assert una.index('maya-lang--flat') < una.index('</nav>'), 'la fila quedo fuera del nav'
    dos, c2 = arregla(una)
    assert not c2 and dos == una, 'no es idempotente'
    print('ok')


if __name__ == '__main__':
    demo() if '--demo' in sys.argv else main()
