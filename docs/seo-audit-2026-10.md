# Auditoría SEO · Maya Secret (mayaerotikmassage.com)

**Fecha:** 17 de octubre de 2026 · **Alcance:** SEO técnico, on-page, local y GEO · **Idiomas:** DE (principal) · EN · ES · IT
**Base analizada:** repositorio `maya-secret` (52 páginas generadas) + comprobaciones en vivo sobre el dominio en producción.

---

## 0. Estado de implementación (17 oct 2026)

Aplicado en el repositorio y verificado sobre las 52 páginas generadas:

| Hallazgo | Qué se hizo | Verificación |
|---|---|---|
| 1, 2 | Puerta de edad: el velo `visibility:hidden` solo vive hasta que la puerta se monta; a partir de ahí tapa el panel opaco (`position:fixed`, `#0D0A0C`). El resto de la página queda `inert` (fuera del foco y del lector de pantalla) y su `<h1>` pasa a `<p>` | `js/age-gate.js`, sintaxis comprobada. **Falta QA visual en navegador** |
| 3, 14 | `url_of()` devuelve URLs finales sin `.html`: canónicas, hreflang, enlaces internos, `_redirects` y sitemap. Páginas legales incluidas | 0 canónicas con `.html`, 0 enlaces internos con `.html` |
| 6 | `scripts/faqjson.py` → `scripts/schema.py`: genera un `@graph` por página desde el HTML visible | 4 `HealthAndBeautyBusiness` + 4 `Person` + 4 `WebSite` + 36 `Service` + 36 `BreadcrumbList` + 44 `FAQPage`, todos parsean |
| 7 | `/llms.txt` creado y referenciado desde `robots.txt` | Precios de los 9 rituales contrastados con sus páginas |
| 8, 9 | `<h1>` en el hub (antes empezaba en `<h6>`); en la home la marca pasa a `<p>` y el `<h1>` es "Erotische Massage in Berlin" | 52/52 páginas con exactamente un `<h1>` |
| 10 | `_headers` con caché de un año para `/imgs/`, `/fonts/`, `/js/vendor/`, HSTS, `nosniff` y `Referrer-Policy` | Comprobar cabeceras tras el despliegue |
| 13 | Twitter Cards y `og:image:alt` en las 52 páginas, traducidos por el build | 52/52 con `twitter:card`. La imagen OG sigue siendo la misma (1200×600): recortarla a 1200×630 y hacerla neutra queda pendiente (hallazgo 12) |
| 14 | Sitemap con `lastmod`, `x-default` y URLs finales | 52 `<loc>`, 52 `lastmod`, 52 `x-default`, 0 `.html` |
| 16, 18 | Fuera los restos de WordPress/Elementor (`rss+xml`, oEmbed, `api.w.org`, `EditURI`, `shortlink`, `generator`) y `meta keywords`, también en las páginas legales | 0 coincidencias en las 54 páginas |

Pendiente, y por qué:

- **Hallazgo 4 (hosts duplicados)** — requiere el panel de Cloudflare: `_redirects` solo casa rutas, no nombres de host. Hace falta una Redirect Rule `www` → apex y activar "Always Use HTTPS".
- **Hallazgo 5 (Impressum)** — faltan datos legales reales (nombre, dirección, correo); no se pueden inventar.
- **Hallazgos 11, 19 (imágenes)** — WebP y `srcset` requieren `cwebp` y tocar el marcado de las galerías; no se ha ejecutado.
- **Hallazgos 15, 21 (página de contacto, landings de barrio)** — contenido nuevo, decisión del negocio.
- **Hallazgo 17 (jQuery)** — Elementor depende de él; aplazarlo sin probar el menú y el acordeón en navegador es arriesgar la navegación por un LCP.

---

## 1. Resumen ejecutivo

El sitio está **técnicamente muy por encima de la media del sector**: estático sobre Cloudflare Workers, TTFB de 66 ms, cero peticiones a terceros, `hreflang` completo en las 52 URLs, canónicas en todas las páginas, FAQ en JSON-LD y etiquetado de edad (`age-de-meta-label` + `rating: adult`) correcto para el JMStV alemán.

Lo que frena la visibilidad no es la arquitectura, son **seis fallos concretos**:

1. **La puerta de edad oculta el `<body>` con `visibility:hidden`** y, además, inyecta un `<h1>` propio. Googlebot renderiza con `localStorage` vacío → ve una página cuyo contenido está oculto y cuyo único `<h1>` visible es "Nur für Personen ab 18 Jahren". Es el problema de indexación más serio del sitio.
2. **Las canónicas apuntan a URLs que redirigen.** `…/ueber-maya.html` devuelve un **307** hacia `/ueber-maya`. Lo mismo en el sitemap y en los enlaces internos: cada rastreo paga un salto y la señal canónica se contradice con la respuesta del servidor.
3. **`www` y el dominio raíz devuelven ambos 200**, y **`http://` también responde 200** (sin redirección forzada a HTTPS ni HSTS). Tres versiones rastreables del mismo sitio.
4. **No hay `LocalBusiness`/`HealthAndBeautyBusiness` en ninguna página.** Solo hay `FAQPage`, que desde 2023 ya no genera rich results para negocios. Sin schema de negocio no hay panel de entidad, ni datos de precio/horario legibles por máquina.
5. **El Impressum tiene marcadores `[PENDIENTE]`** en nombre legal, dirección y correo. En Alemania es una obligación legal (§5 DDG) y, para Google, es el documento que acredita quién está detrás del sitio (E-E-A-T). Es, además, la base de cualquier citación NAP.
6. **No existe `llms.txt`** (404 confirmado) ni ninguna fuente estructurada que un asistente de IA pueda citar con precios y condiciones correctos. → **Resuelto en esta entrega:** `/llms.txt` ya está en el repositorio.

Hipótesis sobre el estado actual: el sitio probablemente está indexado pero con **contenido devaluado por el velo de la puerta de edad** y con señales de entidad local prácticamente nulas. No se ha podido confirmar la cobertura real de indexación sin acceso a Search Console; es la primera comprobación a hacer (ver §9).

---

## 2. Tabla de diagnóstico

| # | Elemento | Estado actual detectado | Severidad | Solución recomendada |
|---|---|---|---|---|
| 1 | Puerta de edad vs. renderizado | `js/age-gate.js` aplica `body>*:not(.maya-agegate){visibility:hidden}` hasta que se pulsa el botón. Googlebot nunca pulsa | **Alta** | Sustituir el velo por una capa superpuesta (`position:fixed;inset:0;z-index:9999` + `inert` en el contenido) que tape visualmente sin ocultar el contenido al renderizador. Mismo efecto legal, contenido indexable, sin cloaking |
| 2 | `<h1>` de la puerta de edad | El diálogo inyecta `<h1>Nur für Personen ab 18 Jahren</h1>` en todas las páginas | **Alta** | Cambiar a `<p class="maya-agegate__title">` + `aria-labelledby` (la accesibilidad no exige `h1`) |
| 3 | Canónicas hacia URLs con redirección | `ueber-maya.html`, `erotische-massagen.html`, `faq.html` y sus traducciones: canónica con `.html` → 307 a la versión sin extensión | **Alta** | Canónicas, enlaces internos y sitemap siempre en forma final (`/ueber-maya`, `/faq`, `/es/masajes`). Cambiar en `src/` y en `scripts/i18n_build.py` |
| 4 | Duplicación de host | `https://www.` y `https://` devuelven 200; `http://` también 200 | **Alta** | Regla de redirección en Cloudflare: `www` → apex 301 y "Always Use HTTPS" activo. Añadir HSTS |
| 5 | Impressum incompleto | 5 campos `[PENDIENTE]`: nombre legal, calle, CP, correo, responsable §18 MStV | **Alta** (legal + confianza) | Completarlo antes que cualquier otra acción SEO. Sin él no hay NAP ni citación posible |
| 6 | Schema de negocio | No existe `LocalBusiness`/`HealthAndBeautyBusiness` en ninguna de las 52 páginas | **Alta** | Insertar el bloque `@graph` de §5.1 en la home y el de `Service` de §5.2 en las nueve páginas de servicio |
| 7 | `llms.txt` | 404 | **Media** | Hecho: `/llms.txt` creado. Desplegar y enlazarlo desde `robots.txt` (ya actualizado) |
| 8 | `<h1>` ausente en el hub de servicios | `erotische-massagen.html` y sus 3 traducciones empiezan en `<h6>` y siguen con dos `<h2>`. Cero `h1` | **Alta** | `<h1>Erotische Massagen in Berlin</h1>` como primer encabezado; el `h6` decorativo pasa a `<p class="eyebrow">` |
| 9 | `<h1>` de la home | `<h1>Maya Secret</h1>`: marca sin keyword ni ciudad | **Media** | `<h1>Erotische Massage in Berlin</h1>` con la marca como línea superior en `<p>` |
| 10 | Caché de estáticos | Todo sirve `cache-control: public, max-age=0, must-revalidate`, incluidos fuentes, CSS, JS e imágenes | **Media** | Añadir `_headers` (§5.4): un año e `immutable` para `/imgs/`, `/fonts/`, `/js/vendor/` |
| 11 | Peso e formato de imágenes | 6,0 MB en `imgs/`, sin WebP/AVIF, sin `srcset`. Mayores: 596 KB, 480 KB, 433 KB; una se sirve a 2744 px | **Media** | Generar WebP (calidad 78-82) + `<picture>` o `srcset` a 640/960/1440. Ahorro estimado 65-75 % |
| 12 | `og:image` | 1200×600 (el estándar es 1200×630) y es una foto sensual: riesgo de bloqueo de previsualización en Meta/WhatsApp | **Media** | Nueva `open-graph.jpg` 1200×630, sin cuerpo en primer plano (detalle de camilla, aceites, luz cálida). Ver §6 |
| 13 | Twitter Cards | Cero etiquetas `twitter:*` en las 52 páginas | **Media** | Añadir `twitter:card`, `title`, `description`, `image` (§5.3) |
| 14 | Sitemap | 52 URLs, pero con `.html` (redirigen), sin `lastmod` y sin `x-default` en los bloques `xhtml:link` | **Media** | Regenerar desde `scripts/i18n_build.py` con URLs finales, `lastmod` y `x-default` |
| 15 | Página de contacto / reserva | No existe. La conversión depende de botones repartidos por el contenido | **Media** | Crear `/kontakt` (+ `/en/contact`, `/es/contacto`, `/it/contatti`): WhatsApp, teléfono, horario, zona, qué indicar al reservar |
| 16 | Restos de WordPress/Elementor | `href="#"` en RSS, oEmbed, EditURI, `api.w.org`, `shortlink`; `meta generator: Elementor 4.2.3` | **Baja** | Eliminarlos de `src/`: enlaces rotos en el `<head>` y huella de CMS inexistente |
| 17 | jQuery bloqueante | `jquery.min.js` sin `defer` en `<head>` + `jquery-migrate` | **Media** | Comprobar si algo lo usa; si no, eliminar. Si sí, `defer` |
| 18 | `meta keywords` | Presente con 14 términos | **Baja** | Eliminar: ningún buscador la usa y delata automatización |
| 19 | Nombres de archivo de imagen | `maya-masaje-erotico-berlin-*.jpg` (español) en un sitio cuyo idioma principal es el alemán | **Baja** | Renombrar a `erotische-massage-berlin-*.jpg` en el próximo lote de optimización |
| 20 | Enlace saliente del pie | "Webdesign Berlin" enlazado en las 52 páginas sin `rel` | **Baja** | `rel="nofollow"` para que no parezca un enlace de pago sitewide |
| 21 | Páginas de barrio / hotel | Mitte, Charlottenburg, Prenzlauer Berg, Kreuzberg solo aparecen como texto dentro de otras páginas | **Media** (oportunidad) | 3-4 landings de barrio y una de "Massage im Hotel Berlin". Ver §4.3 |
| 22 | `FAQPage` en las 52 páginas | Correcto y válido, pero Google ya no da rich results de FAQ a negocios | **Baja** | Mantener: ahora su valor es GEO (los LLM lo leen muy bien), no rich results |
| 23 | Google Business Profile | Sin perfil detectado | **Media** | **No crear un GBP de "masaje erótico"**: el contenido para adultos está prohibido y se arriesga suspensión del perfil y de la cuenta. Alternativas en §4.2 |
| 24 | Señales de reputación | Sin testimonios ni reseñas | **Media** | Testimonios en la web **sin** marcado `Review` (Google prohíbe reseñas autoalojadas marcadas) + reseñas en directorios del sector |

---

## 3. Contenido listo para implementar

> Importante: todo se edita en `src/` y se regenera (`python3 scripts/i18n_extract.py && python3 scripts/i18n_build.py`). Las páginas de `/`, `/en`, `/es`, `/it` son generadas; editarlas directamente se pierde en el siguiente build.

### 3.1 Home (DE) — actual: `Erotische Massage Berlin | Maya Secret – Élite Massage` (54)

| # | Title | Meta description |
|---|---|---|
| A | `Erotische Massage Berlin – Hausbesuch & Hotel \| Maya` (52) | `Erotische und tantrische Massage in Berlin, bei Ihnen zu Hause oder im Hotel. Diskret, nur nach Vereinbarung, täglich 11–23 Uhr. Keine sexuellen Dienste.` (153) |
| B | `Erotische & Tantra Massage Berlin \| Maya Secret` (47) | `Sinnliche Ganzkörpermassage von Maya, unabhängige Masseurin in Berlin. Hausbesuch und Hotel, 60 bis 120 Minuten, ab 120 €. Termine nur nach Vereinbarung.` (153) |
| C | `Sinnliche Massage Berlin bei Ihnen \| Maya Secret` (48) | `Neun erotische Rituale in Berlin: Tantra, Nuru, Body-to-Body, Lingam, Yoni. Ich komme zu Ihnen, diskret und ohne Eile. WhatsApp-Buchung, ab 18 Jahren.` (150) |

**Recomendada: A.** Añade las dos modalidades reales de consumo ("Hausbesuch", "Hotel"), que son términos de búsqueda con intención alta y poca competencia, y suelta "Élite Massage", que no aporta nada.

### 3.2 Hub de servicios (`/erotische-massagen`)

| # | Title | Meta description |
|---|---|---|
| A | `Erotische Massagen in Berlin: 9 Rituale \| Maya Secret` (53) | `Die neun Rituale von Maya in Berlin im Vergleich: klassisch, tantrisch, Nuru, Body-to-Body, Lingam, Yoni. Dauer, Preise und was zu wem passt.` (141) |
| B | `Erotische Massage Berlin: Arten & Preise \| Maya Secret` (54) | `Welche erotische Massage passt zu Ihnen? Neun Rituale in Berlin, 60 bis 120 Minuten, ab 120 €, als Hausbesuch oder im Hotel. Nur nach Vereinbarung.` (147) |
| C | `Alle Massagen in Berlin – Nuru, Tantra, Yoni \| Maya` (51) | `Erotische Massage in Berlin Mitte, Charlottenburg, Prenzlauer Berg und Kreuzberg: neun Rituale, Preise je Dauer und Buchung per WhatsApp. Ab 18 Jahren.` (151) |

**Recomendada: B** — "Arten & Preise" captura la búsqueda comparativa, que es la intención real de un hub.

### 3.3 Nuru (`/massagen/nuru-massage/`)

| # | Title | Meta description |
|---|---|---|
| A | `Nuru-Massage Berlin – Hausbesuch ab 160 € \| Maya Secret` (55) | `Echte Nuru-Massage in Berlin mit warmem Algengel, Haut an Haut. Hausbesuch und Hotel, 60 Min. 160 €, 90 Min. 210 €, 120 Min. 280 €. Nur nach Vereinbarung.` (154) |
| B | `Erotische Nuru-Massage Berlin \| Hotel & Hausbesuch` (50) | `Schwereloser Body-to-Body-Kontakt auf warmem Algengel, bei Ihnen zu Hause oder im Hotel in Berlin. Ab 160 €, absolute Diskretion, Buchung per WhatsApp.` (151) |
| C | `Nuru-Massage Berlin: echtes Algengel, 60–120 Min.` (49) | `Nuru-Massage als Hausbesuch in Berlin: warmes Algengel, ganzer Körper, ohne Eile. 60, 90 oder 120 Minuten ab 160 €. Keine sexuellen Dienstleistungen.` (149) |

**Recomendada: A** — el precio en el title filtra clics y sube el CTR cualificado; en este sector la primera pregunta siempre es el precio.

### 3.4 Tantra (`/massagen/erotische-tantra-massage/`)

| # | Title | Meta description |
|---|---|---|
| A | `Tantra-Massage Berlin – erotisch, bei Ihnen \| Maya` (50) | `Erotische Tantra-Massage in Berlin: Atem, Rhythmus und Berührung ohne Eile, bei Ihnen zu Hause oder im Hotel. 60–120 Minuten ab 140 €, nur nach Vereinbarung.` (157) |
| B | `Erotische Tantra-Massage Berlin ab 140 € \| Maya Secret` (54) | `Tantrische Ganzkörpermassage von Maya in Berlin. Ein ruhiges Ritual für Körper und Atem, diskret, als Hausbesuch. Ab 140 €, Buchung per WhatsApp, ab 18.` (152) |
| C | `Tantrische Massage Berlin: Hausbesuch & Hotel \| Maya` (52) | `Tantra-Massage in Berlin Mitte, Charlottenburg und Kreuzberg: 90 Minuten für 190 €, Hausbesuch oder Hotel. Sinnlich, achtsam, ohne sexuelle Dienstleistungen.` (157) |

**Recomendada: B.** Nota: "Tantra Massage Berlin" es la keyword más competida del nicho (estudios con presupuesto); el camino realista es la cola larga de la variante A/C ("bei Ihnen", "Hausbesuch").

### 3.5 Patrón para EN / ES / IT

Mismo esqueleto, traducido en `i18n/strings.{en,es,it}.tsv` (no reescribir las páginas generadas):

```
[Servicio] [ciudad local] – [modalidad] | Maya Secret
Erotic massage Berlin – outcall & hotel | Maya Secret
Masaje erótico Berlín – a domicilio y hotel | Maya Secret
Massaggio erotico Berlino – a domicilio e hotel | Maya
```

La ciudad siempre en el idioma de la página (`Berlin` / `Berlín` / `Berlino`): es como escribe quien busca en ese idioma.

### 3.6 Estructura de encabezados sugerida

**Home**

```
H1  Erotische Massage in Berlin                 (hoy: "Maya Secret")
  H2  Die Kunst der Berührung ohne Eile          (propuesta de valor)
  H2  Neun Rituale, eines für jede Art zu fragen
    H3  Klassische erotische Massage … (×9, cada uno enlaza a su página)
  H2  Wie eine Sitzung abläuft
    H3  Vor dem Termin  /  H3  Während  /  H3  Danach
  H2  Hausbesuch und Hotel in Berlin
    H3  Bezirke   /   H3  Hotels
  H2  Häufige Fragen
    H3  (una por pregunta del acordeón)
  H2  Termin vereinbaren
```

**Hub de servicios** (hoy sin `h1`)

```
H1  Erotische Massagen in Berlin: neun Rituale
  H2  Neun Rituale, ein Anspruch
    H3  (uno por ritual: nombre + a quién le va + precio desde)
  H2  Preise und Dauer im Überblick        (tabla comparativa, hoy inexistente)
  H2  Bezirke und Hotels in Berlin
  H2  Buchung und Bedingungen
```

**Página de servicio** (ya correcta; mantener el patrón)

```
H1  Erotische Nuru-Massage in Berlin
  H2  Was die Nuru-Massage ist
  H2  Wie die Sitzung abläuft
  H2  Für wen sie geeignet ist
  H2  Preise            (60 / 90 / 120 Min. + Pakete)
  H2  Hausbesuch oder Hotel in Berlin
  H2  Häufige Fragen
    H3  (una por pregunta)
  H2  Termin vereinbaren
```

Regla única: un solo `h1` por página, con servicio + ciudad, y nunca saltar de `h2` a `h4`.

---

## 4. SEO local y conversión

### 4.1 Coherencia NAP

| Dato | Estado | Acción |
|---|---|---|
| **N**ame | "Maya Secret" en la web, "Maya Erotik Massage Berlin" en el Impressum y en la puerta de edad | Elegir **uno** como nombre comercial y usar el mismo en web, Impressum, schema (`name`) y directorios. El otro va en `alternateName` |
| **A**ddress | Sin dirección pública (solo salidas) + `[PENDIENTE]` en el Impressum | El Impressum **debe** llevar dirección real (obligación legal; se puede usar un domicilio profesional). En la web pública y en el schema basta `addressLocality: Berlin` + `areaServed`. Un negocio sin local no debe publicar una dirección falsa |
| **P**hone | `+49 1578 8814749` consistente en `tel:` y `wa.me` | Correcto. Usar siempre el mismo formato E.164 (`+4915788814749`) en schema y directorios |
| **E**mail | `[PENDIENTE]` | Crear un buzón del dominio (`kontakt@mayaerotikmassage.com`) y publicarlo en Impressum y contacto |

### 4.2 Google Business Profile y alternativas

**No abrir un GBP para este negocio.** Las políticas de Google para perfiles de empresa excluyen el contenido y los servicios sexualmente explícitos; un perfil de "erotische Massage" acaba suspendido y la suspensión salpica a la cuenta de Google asociada (incluida la Search Console si comparte cuenta). Riesgo mayor que el beneficio.

Lo que sí construye señal local en este sector:

1. **Directorios alemanes del nicho** — Kaufmich, Ladies.de, Erobella, Massage-Anzeigen, Hobbyhuren-Portale regionales. Mismo NAP exacto, mismo nombre, enlace a la web. Son además la principal fuente de tráfico cualificado del sector.
2. **Bing Places** — políticas algo menos restrictivas, pero revisar antes de invertir tiempo.
3. **Apple Business Connect** — útil para "masaje cerca de mí" en iPhone; revisar sus condiciones para adultos.
4. **Perfil de marca propio**: una página "Über Maya" fuerte (ya existe) + Impressum completo + `Person` en schema. Para Google, esto es la entidad.
5. **Menciones no enlazadas**: foros de Berlín, Reddit (r/berlin no admite promoción; r/berlinsocialclub sí tolera hilos de servicios), directorios de wellness independientes.

Regla para todos: **NAP idéntico carácter a carácter**. Una variación de nombre entre portales rompe la consolidación de entidad.

### 4.3 Oportunidad local sin explotar

Los barrios ya se nombran en el texto del hub, pero no existen como páginas. Con 9 servicios × 4 idiomas ya cubiertos, el siguiente eje de crecimiento es geográfico:

- `/erotische-massage-berlin-mitte`
- `/erotische-massage-charlottenburg`
- `/erotische-massage-prenzlauer-berg`
- `/massage-im-hotel-berlin` ← la de mayor intención comercial: quien busca eso ya tiene la habitación reservada

Cada una: 500-700 palabras propias (hoteles y calles reales de la zona, tiempos de desplazamiento, particularidades), nunca un calco con la ciudad cambiada. Cuatro páginas débiles y duplicadas hacen más daño que una buena.

### 4.4 Llamadas a la acción

Estado: 8 enlaces `wa.me` + 8 `tel:` por página, con mensaje predefinido en alemán que ya fija expectativas ("…es un servicio sensual, no sexual") — excelente decisión, filtra solicitudes inadecuadas antes del primer mensaje.

Mejoras:

1. **Botón flotante de WhatsApp** persistente en móvil (una sola etiqueta `<a>`, sin librerías). Hoy el usuario debe volver a buscar un botón al terminar de leer.
2. **El mensaje predefinido debe decir el ritual**: en cada página de servicio, `?text=…Nuru-Massage…` en lugar del texto genérico. Convierte mejor y ahorra una ida y vuelta.
3. **Una página `/kontakt`** con horario, zona, qué indicar al reservar y los dos canales. Es la URL que un asistente de IA citará cuando le pidan "cómo reservar", y la que se enlaza desde los directorios.
4. **Mapa: no incrustar Google Maps.** Rompería la promesa de cero terceros y no hay local que mostrar. Basta una lista de barrios en texto + `areaServed` en el schema.

---

## 5. Bloque técnico de código

### 5.1 JSON-LD de negocio — para la **home** (uno por idioma, cambiando `inLanguage`, `url` y `@id`)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "HealthAndBeautyBusiness",
      "@id": "https://mayaerotikmassage.com/#business",
      "name": "Maya Secret",
      "alternateName": "Maya Erotik Massage Berlin",
      "additionalType": "http://www.productontology.org/id/Erotic_massage",
      "description": "Unabhängige Masseurin in Berlin. Erotische, tantrische und sinnliche Massage als Haus- oder Hotelbesuch, nur nach Vereinbarung. Keine sexuellen Dienstleistungen.",
      "url": "https://mayaerotikmassage.com/",
      "telephone": "+4915788814749",
      "email": "kontakt@mayaerotikmassage.com",
      "image": "https://mayaerotikmassage.com/imgs/open-graph.jpg",
      "logo": "https://mayaerotikmassage.com/imgs/logo-maya.svg",
      "priceRange": "120 € – 1800 €",
      "currenciesAccepted": "EUR",
      "paymentAccepted": "Bargeld",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Berlin",
        "addressRegion": "Berlin",
        "addressCountry": "DE"
      },
      "areaServed": {
        "@type": "City",
        "name": "Berlin",
        "sameAs": "https://www.wikidata.org/wiki/Q64"
      },
      "serviceArea": {
        "@type": "GeoCircle",
        "geoMidpoint": {
          "@type": "GeoCoordinates",
          "latitude": 52.5200,
          "longitude": 13.4050
        },
        "geoRadius": "15000"
      },
      "openingHoursSpecification": [{
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        "opens": "11:00",
        "closes": "23:00"
      }],
      "audience": {
        "@type": "PeopleAudience",
        "suggestedMinAge": 18
      },
      "founder": { "@id": "https://mayaerotikmassage.com/#maya" },
      "employee": { "@id": "https://mayaerotikmassage.com/#maya" },
      "availableLanguage": ["de","en","es","it"],
      "potentialAction": {
        "@type": "ReserveAction",
        "name": "Termin per WhatsApp vereinbaren",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "https://wa.me/4915788814749",
          "inLanguage": "de-DE",
          "actionPlatform": [
            "http://schema.org/DesktopWebPlatform",
            "http://schema.org/MobileWebPlatform"
          ]
        }
      },
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Rituale",
        "itemListElement": [
          { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Klassische erotische Massage", "url": "https://mayaerotikmassage.com/massagen/klassische-erotische-massage/" }, "price": "120", "priceCurrency": "EUR" },
          { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Sinnliche Massage", "url": "https://mayaerotikmassage.com/massagen/sinnliche-massage/" }, "price": "125", "priceCurrency": "EUR" },
          { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Lingam-Massage", "url": "https://mayaerotikmassage.com/massagen/lingam-massage/" }, "price": "130", "priceCurrency": "EUR" },
          { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Yoni-Massage", "url": "https://mayaerotikmassage.com/massagen/yoni-massage/" }, "price": "130", "priceCurrency": "EUR" },
          { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Orientalische Massage", "url": "https://mayaerotikmassage.com/massagen/orientalische-massage/" }, "price": "130", "priceCurrency": "EUR" },
          { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Erotische Tantra-Massage", "url": "https://mayaerotikmassage.com/massagen/erotische-tantra-massage/" }, "price": "140", "priceCurrency": "EUR" },
          { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Body-to-Body-Massage", "url": "https://mayaerotikmassage.com/massagen/body-to-body-massage/" }, "price": "140", "priceCurrency": "EUR" },
          { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Gegenseitige Massage", "url": "https://mayaerotikmassage.com/massagen/gegenseitige-massage/" }, "price": "140", "priceCurrency": "EUR" },
          { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Nuru-Massage", "url": "https://mayaerotikmassage.com/massagen/nuru-massage/" }, "price": "160", "priceCurrency": "EUR" }
        ]
      }
    },
    {
      "@type": "Person",
      "@id": "https://mayaerotikmassage.com/#maya",
      "name": "Maya",
      "jobTitle": "Masseurin",
      "image": "https://mayaerotikmassage.com/imgs/maya-masajista-erotica-berlin-retrato.jpg",
      "url": "https://mayaerotikmassage.com/ueber-maya",
      "worksFor": { "@id": "https://mayaerotikmassage.com/#business" },
      "knowsLanguage": ["de","en","es","it"]
    },
    {
      "@type": "WebSite",
      "@id": "https://mayaerotikmassage.com/#website",
      "url": "https://mayaerotikmassage.com/",
      "name": "Maya Secret",
      "inLanguage": "de-DE",
      "publisher": { "@id": "https://mayaerotikmassage.com/#business" }
    }
  ]
}
</script>
```

**Antes de publicar, verificar tres campos:** `email` (crear el buzón), `knowsLanguage` / `availableLanguage` (confirmar qué idiomas habla Maya realmente) y `priceRange`. Un dato inventado en schema es peor que no tener schema.

Para EN/ES/IT: mismo bloque con `"@id": "…/en/#business"`, `inLanguage` y `url` del árbol correspondiente, apuntando `sameAs` al `@id` alemán.

### 5.2 JSON-LD de servicio — para cada página de masaje (ejemplo: Nuru)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Service",
      "@id": "https://mayaerotikmassage.com/massagen/nuru-massage/#service",
      "name": "Erotische Nuru-Massage in Berlin",
      "serviceType": "Nuru-Massage",
      "description": "Warmes Algengel, schwereloser Body-to-Body-Kontakt. Nuru-Massage als Haus- oder Hotelbesuch in Berlin, nur nach Vereinbarung.",
      "url": "https://mayaerotikmassage.com/massagen/nuru-massage/",
      "image": "https://mayaerotikmassage.com/imgs/maya-masaje-erotico-berlin-banador-rosa-terraza.jpg",
      "provider": { "@id": "https://mayaerotikmassage.com/#business" },
      "areaServed": { "@type": "City", "name": "Berlin" },
      "audience": { "@type": "PeopleAudience", "suggestedMinAge": 18 },
      "offers": [
        { "@type": "Offer", "name": "60 Minuten",  "price": "160",  "priceCurrency": "EUR", "availability": "https://schema.org/InStock" },
        { "@type": "Offer", "name": "90 Minuten",  "price": "210",  "priceCurrency": "EUR", "availability": "https://schema.org/InStock" },
        { "@type": "Offer", "name": "120 Minuten", "price": "280",  "priceCurrency": "EUR", "availability": "https://schema.org/InStock" },
        { "@type": "Offer", "name": "Paket 5 × 90 Minuten",  "price": "950",  "priceCurrency": "EUR" },
        { "@type": "Offer", "name": "Paket 10 × 90 Minuten", "price": "1800", "priceCurrency": "EUR" }
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://mayaerotikmassage.com/massagen/nuru-massage/#breadcrumb",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Start", "item": "https://mayaerotikmassage.com/" },
        { "@type": "ListItem", "position": 2, "name": "Erotische Massagen", "item": "https://mayaerotikmassage.com/erotische-massagen" },
        { "@type": "ListItem", "position": 3, "name": "Nuru-Massage" }
      ]
    }
  ]
}
</script>
```

Las otras ocho páginas son el mismo bloque con su tabla de precios (está en §3 de `/llms.txt`). Encaja bien como tercera función de `scripts/faqjson.py`, que ya genera el `FAQPage` desde el HTML visible: misma idea, leyendo la tabla de precios.

### 5.3 Etiquetas sociales que faltan

```html
<meta property="og:image:height" content="630" />   <!-- hoy 600 -->
<meta property="og:image:alt" content="Maya Secret – erotische Massage in Berlin" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Erotische Massage Berlin – Hausbesuch & Hotel | Maya" />
<meta name="twitter:description" content="Erotische und tantrische Massage in Berlin, bei Ihnen zu Hause oder im Hotel. Diskret, nur nach Vereinbarung." />
<meta name="twitter:image" content="https://mayaerotikmassage.com/imgs/open-graph.jpg" />
```

### 5.4 `_headers` (raíz del repositorio, lo sirve Cloudflare Workers Assets)

```
/imgs/*
  Cache-Control: public, max-age=31536000, immutable

/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/js/vendor/*
  Cache-Control: public, max-age=31536000, immutable

/css/*
  Cache-Control: public, max-age=604800

/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
```

Comprobar tras el despliegue (`curl -sI https://mayaerotikmassage.com/css/app.css | grep -i cache`) que la cabecera se aplica; si Workers Assets la ignorase en esta configuración, la alternativa es una Cache Rule en el panel de Cloudflare. Nota: con `max-age` largo, cualquier cambio en una imagen exige renombrarla.

### 5.5 `robots.txt` (ya aplicado)

```
User-agent: *
Allow: /

# Resumen legible por asistentes de IA (GEO):
# https://mayaerotikmassage.com/llms.txt

Sitemap: https://mayaerotikmassage.com/sitemap.xml
```

No hace falta nada más. Enumerar `GPTBot`, `PerplexityBot`, `ClaudeBot` o `Google-Extended` con `Allow: /` es redundante: ya están cubiertos por `User-agent: *`, y añadir bloques por bot solo crea sitio donde equivocarse. **Lo que sí hay que vigilar es no bloquearlos nunca**: en este sector la cita en un asistente de IA sustituye al Google Business Profile que no se puede tener.

### 5.6 Sitemap

Cambios en `scripts/i18n_build.py`, función `sitemap()`:

1. URLs finales sin `.html` (`url_of()` debe devolver la forma canónica).
2. `<lastmod>` por página (`git log -1 --format=%cI -- <archivo>` o la fecha del build).
3. `x-default` en cada bloque de alternates, como ya hace el `<head>`.

```xml
<url>
  <loc>https://mayaerotikmassage.com/ueber-maya</loc>
  <lastmod>2026-10-17</lastmod>
  <xhtml:link rel="alternate" hreflang="de" href="https://mayaerotikmassage.com/ueber-maya" />
  <xhtml:link rel="alternate" hreflang="en" href="https://mayaerotikmassage.com/en/about-maya" />
  <xhtml:link rel="alternate" hreflang="es" href="https://mayaerotikmassage.com/es/sobre-maya" />
  <xhtml:link rel="alternate" hreflang="it" href="https://mayaerotikmassage.com/it/chi-e-maya" />
  <xhtml:link rel="alternate" hreflang="x-default" href="https://mayaerotikmassage.com/ueber-maya" />
</url>
```

### 5.7 `llms.txt`

Creado en la raíz del repositorio: `/llms.txt`. Incluye descripción, los nueve rituales con su tabla de precios completa, horario, zona de servicio, método de reserva, límites explícitos ("keine sexuellen Dienstleistungen", 18+) y un resumen en inglés. Se despliega solo con el siguiente `wrangler deploy` (no está en `.assetsignore`).

**Mantenerlo vivo:** cada vez que cambie un precio o el horario, actualizarlo. Un `llms.txt` desactualizado hace que los asistentes citen precios incorrectos, que es peor que no existir. Lo ideal es generarlo desde `scripts/i18n_build.py` leyendo las mismas tablas de precios que publican las páginas.

---

## 6. Multimedia y SafeSearch

**Estado:** 20 fotografías, 6,0 MB en total, JPEG exclusivamente, sin `srcset`, con `width`/`height` siempre presentes (bien: cero CLS) y con `alt` descriptivos y geolocalizados en alemán (muy bien). Las banderas del selector de idioma llevan `alt=""`, que es lo correcto para un elemento decorativo.

**Optimización:**

1. **WebP** a calidad 80 con el JPEG como respaldo. Ahorro esperado: de 6,0 MB a ~1,5-2,0 MB.
   ```bash
   for f in imgs/*.jpg; do cwebp -q 80 -resize 1440 0 "$f" -o "${f%.jpg}.webp"; done
   ```
2. **`srcset` a 640/960/1440**: hoy se sirve una imagen de 2744 px a móviles.
3. **`open-graph.jpg`**: 416 KB y 1200×600 → regenerar a 1200×630 y ~150 KB.
4. **`loading="lazy"`** en todo lo que esté bajo el pliegue; el `preload` + `fetchpriority="high"` de la imagen LCP ya está bien puesto.

**SafeSearch y redes sociales.** Google no penaliza por ser un sitio para adultos: lo clasifica. `rating: adult` + `age-de-meta-label` hacen que el sitio quede filtrado con SafeSearch activo, lo cual es la decisión **correcta** aquí (cumplimiento del JMStV) y no impide posicionar ante consultas de intención adulta con SafeSearch desactivado. No las quites.

Lo que sí conviene vigilar:

- **Sin desnudos ni pezones ni genitales**, ni siquiera insinuados o cubiertos por un objeto. Las fotos actuales (lencería, bañador) están dentro de lo aceptable para Meta/Instagram; cualquier escalada implica bloqueo de cuenta, no solo del post.
- **Nada de "sex", "escort", "happy ending" ni "Sexdienstleistung"** en `alt`, nombres de archivo, titles ni URLs. Esos términos son los que activan clasificadores de contenido comercial sexual, que es otra categoría —mucho peor tratada— que "erótico/sensual". El sitio ya lo hace bien, incluso lo niega explícitamente; mantenerlo.
- **Imagen OG neutra**: la previsualización del enlace es lo que ven WhatsApp, Telegram y Meta. Una foto de la camilla, los aceites, una toalla doblada y luz cálida no se bloquea nunca y sigue vendiendo el servicio. Guarda las fotos sensuales para dentro de la página, donde el usuario ya pasó la puerta de edad.
- **Nombres de archivo descriptivos y no explícitos**: el patrón actual (`maya-masaje-erotico-berlin-*`) es correcto, solo convendría pasarlo al alemán.

---

## 7. GEO — visibilidad en motores de IA

En un sector sin Google Business Profile, la cita en ChatGPT, Perplexity, Copilot o Gemini es la vía de descubrimiento con mejor retorno. Lo que esos sistemas necesitan es lo mismo que un humano apurado: **datos concretos, en texto plano, fáciles de extraer y de atribuir**.

Lo que ya juega a favor: HTML estático sin JS para el contenido, `FAQPage` en las 52 páginas, precios en texto visible, cuatro idiomas y cero bloqueos en `robots.txt`.

Lo que faltaba y se ha añadido: `/llms.txt`.

Lo que queda por hacer, por orden de impacto:

1. **Desbloquear el renderizado** (puerta de edad, §2.1). Varios rastreadores de IA **no ejecutan JavaScript**; esos ven el HTML completo sin problema. Pero los que sí lo ejecutan ven una página velada. Arreglarlo sirve igual a Google y a los asistentes.
2. **Schema de negocio y de servicio** (§5.1, §5.2): es la fuente preferida para extraer precio, horario y zona sin alucinar.
3. **Respuestas directas en el texto.** Un bloque "In einem Satz" al principio de cada página de servicio —qué es, cuánto dura, cuánto cuesta, dónde— es lo que un LLM cita literalmente. Ya está casi logrado en las FAQ.
4. **Tabla de precios comparativa** en el hub: hoy los precios están dispersos en nueve páginas. Una tabla es la unidad que mejor se extrae.
5. **Presencia externa verificable.** Los asistentes dan más peso a lo que pueden corroborar en una segunda fuente. Los directorios del sector (§4.2) cumplen aquí una función doble: tráfico y corroboración.
6. **Fecha de actualización visible** ("Preise Stand: Oktober 2026") en las páginas de precios: los modelos prefieren citar lo que pueden datar.

---

## 8. Plan de prioridades — esta semana

### Top 3 técnico

| | Cambio | Dónde | Por qué primero |
|---|---|---|---|
| **1** | Quitar el velo `visibility:hidden` de la puerta de edad (capa superpuesta + `inert`) y cambiar su `<h1>` por `<p>` | `js/age-gate.js`, `css/theme-palettes.css` | Es lo que impide que el contenido cuente plenamente. Cualquier otra mejora se apoya en esto |
| **2** | Canónicas, enlaces internos y sitemap a URLs finales sin `.html` + `www`→apex 301 + "Always Use HTTPS" | `src/`, `scripts/i18n_build.py`, panel de Cloudflare | Consolida en una sola URL la autoridad que hoy se reparte entre tres variantes y una cadena de 307 |
| **3** | Insertar el `@graph` de negocio en las cuatro homes y el `Service` en las 36 páginas de servicio | `src/` + `scripts/` | Sin esto no hay entidad local reconocible, ni en Google ni en los asistentes |

### Top 3 de contenido

| | Cambio | Dónde | Por qué primero |
|---|---|---|---|
| **1** | Completar el Impressum (nombre legal, dirección, correo, responsable) | `impressum.html` | Obligación legal del §5 DDG y, a la vez, el documento que acredita la entidad ante Google. Bloquea el alta en directorios |
| **2** | `<h1>` en el hub de servicios + `<h1>` con keyword en la home (§3.6) | `src/masajes.html`, `src/index.html` | Cuatro páginas importantes sin `h1`; es el arreglo on-page de mejor relación esfuerzo/resultado |
| **3** | Titles y descriptions nuevos de home, hub y las dos páginas de servicio principales (§3.1-3.4) | `src/` + `i18n/strings.*.tsv` | Sube el CTR sobre las impresiones que ya se tienen, sin esperar a que nada se reindexe |

Orden de ejecución sugerido: Impressum (10 min) → encabezados y metadatos (1 h) → puerta de edad (1 h) → URLs canónicas y redirecciones (2 h) → schema (2 h). Un solo `wrangler deploy` al final de cada bloque.

---

## 9. Verificación y seguimiento

Lo que no se ha podido medir desde fuera y hay que comprobar en cuanto haya acceso:

1. **Search Console** (propiedad de dominio, no de URL): cobertura real de indexación, consultas actuales, estado de `hreflang`. Es el dato que falta para cerrar el diagnóstico.
2. **Prueba de resultados enriquecidos** sobre home y una página de servicio tras publicar el schema.
3. **Inspección de URL → "Ver página rastreada"**: confirma si el contenido llega al renderizador una vez corregida la puerta de edad. Es la prueba decisiva del cambio nº 1.
4. **PageSpeed Insights** móvil (no se pudo ejecutar en la auditoría: cuota de la API agotada). Con 6 MB de imágenes sin WebP y jQuery bloqueante, el LCP móvil es el sospechoso principal.
5. **Bing Webmaster Tools**: alimenta a Copilot y a parte del ecosistema de IA; dar de alta el sitemap.
6. **Comprobación mensual de citas en IA**: preguntar en ChatGPT, Perplexity y Gemini "erotische Massage Berlin Hausbesuch" y anotar si aparece, con qué datos y si son correctos. Es la métrica GEO que sí se puede seguir sin herramientas de pago.
