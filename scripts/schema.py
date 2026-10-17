#!/usr/bin/env python3
"""Regenera el JSON-LD de cada pagina a partir de lo que se ve en pantalla.

Un solo bloque por pagina, con un @graph dentro:

    FAQPage         si la pagina tiene acordeon (preguntas y respuestas visibles)
    LocalBusiness   en las cuatro portadas, con horario, telefono y catalogo
    Person          Maya, en las portadas
    WebSite         en las portadas
    Service         en las 36 paginas de ritual, con sus cinco precios
    BreadcrumbList  en las 36 paginas de ritual

Nada se escribe a mano: las preguntas salen del acordeon, los precios de la
tabla de precios y el nombre del servicio del h1, asi que el marcado no puede
desviarse de lo que lee el visitante. Desde la raiz del repo:

    python3 scripts/schema.py            # dry-run: imprime lo que encuentra
    python3 scripts/schema.py --write    # reescribe el bloque en cada pagina
"""
import glob, html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n_build as B

TITLE = re.compile(r'e-n-accordion-item-title-text">(.*?)</div>', re.S)
PARA = re.compile(r'<p>(.*?)</p>', re.S)
PRICE = re.compile(r'>€(\d+)<')
H1 = re.compile(r'<h1[^>]*>(.*?)</h1>', re.S)
HERO_IMG = re.compile(r'<img[^>]+src="(/imgs/[^"]+\.jpg)"', re.I)

PHONE = '+4915788814749'
WHATSAPP = 'https://wa.me/4915788814749'
LOGO = B.SITE + '/imgs/logo-maya.svg'
OG = B.SITE + '/imgs/open-graph.jpg'
PORTRAIT = B.SITE + '/imgs/maya-masajista-erotica-berlin-retrato.jpg'
# Horario y zona: lo mismo que dice el texto de las paginas.
OPENS, CLOSES = '11:00', '23:00'
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Textos del marcado, uno por idioma. No pasan por i18n/: no se ven en pantalla.
L10N = {
    'de': {
        'desc': 'Unabhängige Masseurin in Berlin. Erotische, tantrische und sinnliche Massage '
                'als Haus- oder Hotelbesuch, nur nach Vereinbarung. Keine sexuellen Dienstleistungen.',
        'job': 'Masseurin', 'book': 'Termin per WhatsApp vereinbaren',
        'min': '{} Minuten', 'pack': 'Paket {} × 90 Minuten',
        'home': 'Start', 'hub': 'Erotische Massagen', 'cash': 'Bargeld',
    },
    'en': {
        'desc': 'Independent masseuse in Berlin. Erotic, tantric and sensual massage as a home '
                'or hotel visit, by appointment only. No sexual services.',
        'job': 'Masseuse', 'book': 'Book an appointment on WhatsApp',
        'min': '{} minutes', 'pack': 'Package {} × 90 minutes',
        'home': 'Home', 'hub': 'Erotic massages', 'cash': 'Cash',
    },
    'es': {
        'desc': 'Masajista independiente en Berlín. Masaje erótico, tántrico y sensual a domicilio '
                'o en hotel, solo con cita previa. Sin servicios sexuales.',
        'job': 'Masajista', 'book': 'Reservar cita por WhatsApp',
        'min': '{} minutos', 'pack': 'Paquete de {} × 90 minutos',
        'home': 'Inicio', 'hub': 'Masajes eróticos', 'cash': 'Efectivo',
    },
    'it': {
        'desc': 'Massaggiatrice indipendente a Berlino. Massaggio erotico, tantrico e sensuale a '
                'domicilio o in hotel, solo su appuntamento. Nessun servizio sessuale.',
        'job': 'Massaggiatrice', 'book': 'Prenotare un appuntamento su WhatsApp',
        'min': '{} minuti', 'pack': 'Pacchetto {} × 90 minuti',
        'home': 'Home', 'hub': 'Massaggi erotici', 'cash': 'Contanti',
    },
}

BIZ_ID = B.SITE + '/#business'
MAYA_ID = B.SITE + '/#maya'


def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def routes():
    """{ruta en disco: (plantilla, idioma)} de las 52 paginas generadas."""
    return {B.out_path(p, l): (p, l)
            for p in B.src_pages() for l in B.ORDER}


def faqs(src):
    out = []
    for m in TITLE.finditer(src):
        end = src.find('</details>', m.end())
        body = src[m.end():end if end != -1 else len(src)]
        ans = ' '.join(clean(p) for p in PARA.findall(body))
        out.append((clean(m.group(1)), ans))
    return out


def faq_node(url, lang, title, items):
    return {
        "@type": "FAQPage",
        "@id": url + "#faq",
        "inLanguage": lang,
        "name": title,
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in items
        ],
    }


def catalog(lang):
    """Los nueve rituales con su precio mas bajo, leidos de sus propias paginas."""
    items = []
    for r in B.RITUALS:
        page = B.SRC_RITUAL.format(r)
        path = B.out_path(page, lang)
        if not os.path.exists(path):
            continue
        src = open(path, encoding='utf-8').read()
        prices = PRICE.findall(src)
        name = clean(H1.search(src).group(1)) if H1.search(src) else r
        offer = {"@type": "Offer",
                 "itemOffered": {"@type": "Service", "name": name,
                                 "url": B.url_of(page, lang)}}
        if prices:
            offer["price"] = prices[0]
            offer["priceCurrency"] = "EUR"
        items.append(offer)
    return items


def business_node(lang):
    t = L10N[lang]
    return {
        "@type": "HealthAndBeautyBusiness",
        "@id": BIZ_ID,
        "name": "Maya Secret",
        "alternateName": "Maya Erotik Massage Berlin",
        "additionalType": "http://www.productontology.org/id/Erotic_massage",
        "description": t['desc'],
        "url": B.url_of('index.html', lang),
        "telephone": PHONE,
        "image": OG,
        "logo": LOGO,
        "priceRange": "120 € – 280 €",
        "currenciesAccepted": "EUR",
        "paymentAccepted": t['cash'],
        "address": {"@type": "PostalAddress", "addressLocality": "Berlin",
                    "addressRegion": "Berlin", "addressCountry": "DE"},
        "areaServed": {"@type": "City", "name": "Berlin",
                       "sameAs": "https://www.wikidata.org/wiki/Q64"},
        "serviceArea": {"@type": "GeoCircle",
                        "geoMidpoint": {"@type": "GeoCoordinates",
                                        "latitude": 52.52, "longitude": 13.405},
                        "geoRadius": "15000"},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": DAYS,
                                       "opens": OPENS, "closes": CLOSES}],
        "audience": {"@type": "PeopleAudience", "suggestedMinAge": 18},
        "founder": {"@id": MAYA_ID},
        "employee": {"@id": MAYA_ID},
        "potentialAction": {
            "@type": "ReserveAction",
            "name": t['book'],
            "target": {"@type": "EntryPoint", "urlTemplate": WHATSAPP,
                       "actionPlatform": ["http://schema.org/DesktopWebPlatform",
                                          "http://schema.org/MobileWebPlatform"]},
        },
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": L10N[lang]['hub'],
                            "itemListElement": catalog(lang)},
    }


def person_node(lang):
    return {
        "@type": "Person",
        "@id": MAYA_ID,
        "name": "Maya",
        "jobTitle": L10N[lang]['job'],
        "image": PORTRAIT,
        "url": B.url_of('about.html', lang),
        "worksFor": {"@id": BIZ_ID},
    }


def website_node(url, lang, title):
    return {
        "@type": "WebSite",
        "@id": url + "#website",
        "url": url,
        "name": "Maya Secret",
        "inLanguage": lang,
        "publisher": {"@id": BIZ_ID},
    }


def service_nodes(src, url, lang, page, desc):
    """Service + BreadcrumbList de una pagina de ritual.

    Los precios salen de la tabla visible, en el orden en que estan: 60, 90 y
    120 minutos y los dos paquetes. Si la tabla cambia, cambia el marcado.
    """
    t = L10N[lang]
    name = clean(H1.search(src).group(1)) if H1.search(src) else ''
    prices = PRICE.findall(src)
    offers = []
    for mins, price in zip(('60', '90', '120'), prices):
        offers.append({"@type": "Offer", "name": t['min'].format(mins),
                       "price": price, "priceCurrency": "EUR",
                       "availability": "https://schema.org/InStock"})
    for packs, price in zip(('5', '10'), prices[3:]):
        offers.append({"@type": "Offer", "name": t['pack'].format(packs),
                       "price": price, "priceCurrency": "EUR"})

    img = HERO_IMG.search(src)
    service = {
        "@type": "Service",
        "@id": url + "#service",
        "name": name,
        "description": desc,
        "url": url,
        "provider": {"@id": BIZ_ID},
        "areaServed": {"@type": "City", "name": "Berlin"},
        "audience": {"@type": "PeopleAudience", "suggestedMinAge": 18},
    }
    if img:
        service["image"] = B.SITE + img.group(1)
    if offers:
        service["offers"] = offers

    crumbs = {
        "@type": "BreadcrumbList",
        "@id": url + "#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t['home'],
             "item": B.url_of('index.html', lang)},
            {"@type": "ListItem", "position": 2, "name": t['hub'],
             "item": B.url_of('masajes.html', lang)},
            {"@type": "ListItem", "position": 3, "name": name},
        ],
    }
    return [service, crumbs]


def graph(path, src, page, lang):
    url = re.search(r'rel="canonical" href="(.*?)"', src).group(1)
    title = clean(re.search(r'<title>(.*?)</title>', src, re.S).group(1))
    htmllang = re.search(r'<html lang="([^"]+)"', src).group(1)
    desc = re.search(r'<meta name="description"\s*\n?\s*content="([^"]*)"', src)
    desc = html.unescape(desc.group(1)) if desc else title

    nodes = []
    if page == 'index.html':
        nodes += [business_node(lang), person_node(lang), website_node(url, htmllang, title)]
    if page.startswith('servicios/'):
        nodes += service_nodes(src, url, lang, page, desc)
    items = faqs(src)
    if items:
        nodes.append(faq_node(url, htmllang, title, items))
    return nodes, items


def block(nodes):
    data = {"@context": "https://schema.org", "@graph": nodes}
    body = json.dumps(data, ensure_ascii=False, indent=2).replace('\n', '\n\t')
    return ('\t<!-- Datos estructurados: salen del HTML visible (acordeon, tabla de precios,\n'
            '\t     h1), asi que no hay que tocarlos a mano. Los regenera scripts/schema.py. -->\n'
            '\t<script type="application/ld+json">\n\t' + body + '\n\t</script>\n')


OLD = re.compile(r'\t*(?:<!--(?:(?!-->).)*?(?:rich results|scripts/schema\.py).*?-->\s*)?'
                 r'<script type="application/ld\+json">.*?</script>\n', re.S)


def main():
    dry = '--write' not in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    known = routes()
    targets = args or sorted(known)
    for path in targets:
        if path not in known:
            print(f'{path}: no es una pagina generada, omitido'); continue
        page, lang = known[path]
        src = open(path, encoding='utf-8').read()
        nodes, items = graph(path, src, page, lang)
        if not nodes:
            print(f'{path}: nada que marcar, omitido'); continue
        new = block(nodes)
        src2 = OLD.sub(lambda _: new, src, count=1) if OLD.search(src) \
            else src.replace('</head>', new + '</head>', 1)
        types = ', '.join(n['@type'] for n in nodes)
        print(f'--- {path}: {types}' + (f' ({len(items)} preguntas)' if items else ''))
        if not dry:
            open(path, 'w', encoding='utf-8').write(src2)


if __name__ == '__main__':
    main()
