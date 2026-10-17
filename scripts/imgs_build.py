#!/usr/bin/env python3
"""Genera las variantes WebP de las fotos: imgs/<foto>-<ancho>.webp.

Las fotos del set miden entre 1000 y 2700 px de ancho y se servian tal cual a
un movil de 390: medio megabyte para pintar 390 px. scripts/i18n_build.py
envuelve cada foto en <picture> y tira de estas variantes; el JPEG original se
queda como respaldo del <img>.

Las miniaturas de imgs/menu/ (533 px, 66 KB) y los iconos no entran: ya pesan
lo que tienen que pesar.

    python3 scripts/imgs_build.py [--force]
"""
import glob, os, sys
from PIL import Image

WIDTHS = (480, 960, 1440)
QUALITY = 78
SOURCES = sorted(glob.glob('imgs/maya-*.jpg'))


def variants(width):
    """Anchos a generar: los de WIDTHS que reduzcan la foto, mas el original."""
    return sorted({w for w in WIDTHS if w < width} | {width})


def build(force=False):
    hechas = 0
    for src in SOURCES:
        im = Image.open(src)
        im = im.convert('RGB')
        for w in variants(im.width):
            dest = f'{src[:-len(".jpg")]}-{w}.webp'
            # El WebP solo se rehace si falta o si la foto es mas nueva: una
            # construccion normal no debe reescribir 50 ficheros binarios.
            if not force and os.path.exists(dest) \
                    and os.path.getmtime(dest) >= os.path.getmtime(src):
                continue
            h = round(im.height * w / im.width)
            im.resize((w, h), Image.LANCZOS).save(dest, 'WEBP', quality=QUALITY, method=6)
            hechas += 1
    return hechas


def demo():
    """Comprobacion: los anchos no suben del original y el original siempre esta."""
    assert variants(1080) == [480, 960, 1080]
    assert variants(2744) == [480, 960, 1440, 2744]
    assert variants(480) == [480], 'una foto justo en el limite no se duplica'
    assert variants(300) == [300], 'una foto pequena no se agranda'
    print('ok')


if __name__ == '__main__':
    if '--demo' in sys.argv:
        demo()
    else:
        n = build('--force' in sys.argv)
        print(f'{n} variantes WebP generadas ({len(SOURCES)} fotos)')
