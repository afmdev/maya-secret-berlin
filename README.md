# Maya Secret — Erotic Massage Berlin

Website of **Maya Secret**, an independent erotic and tantric massage practice in Berlin. Home and hotel visits, by appointment only.

Live: **[www.mayaerotikmassage.com](https://www.mayaerotikmassage.com)**

![Maya Secret — home page](docs/screenshot.png)

## What it is

A static, multi-page site in four languages — German (primary, at the root), English, Spanish and Italian. Plain HTML, a handful of stylesheets and vanilla JS: **no bundler, no framework, no dependencies to install**. The only build step is a Python script that stamps the four language trees out of `src/` plus the string tables in `i18n/`. The markup started life as an Elementor theme and was flattened into static files; the CSS and JS written for this project sit on top of it.

- **Zero third-party requests.** No analytics, no CDN, no embeds, no cookies. Fonts, images, jQuery, GSAP, Lenis and Swiper are all self-hosted.
- **18+ age gate (JMStV).** `js/age-gate.js` runs from `<head>` and veils the page before first paint; the visitor self-declares and the answer is stamped in `localStorage` for 30 days. Paired with the `age-de-meta-label` meta tag German filters read. It is a §5 self-declaration, not an identity-checking AVS.
- **Nine service pages × four languages.** One folder per massage, named in its own language (`/massagen/nuru-massage/`, `/en/massages/nuru-massage/`, `/es/servicios/masaje-erotico-nuru/`, `/it/servizi/massaggio-nuru/`), all sharing `css/service.css`, the only stylesheet written from scratch.
- **`hreflang` across all 52 pages,** with German as `x-default`, a `DE · EN · ES · IT` switcher in the header, and `LocalBusiness`, `Service` and `FAQPage` JSON-LD generated from the visible HTML of each page.
- **Motion that respects the visitor.** Lenis smooth scroll plus GSAP `ScrollTrigger`/`SplitText` for per-character text reveals and image wipes; the whole module returns early under `prefers-reduced-motion: reduce`.
- **CSS instead of JS where possible.** The "Masajes" mega menu with its hover photo panel is pure CSS, and so is the spotlight effect that restores colour under the pointer on grayscale photos (`@property` + a masked `backdrop-filter`).
- **Clean URLs.** `/about`, `/masajes`, `/servicios/masaje-erotico-nuru/` — the `.html` files stay on disk and Cloudflare resolves them extensionless.

## Layout

```
src/                    # templates: the 13 pages, Spanish text as translation keys
i18n/strings.es.json    # extracted strings (generated)
i18n/strings.{de,en,it}.tsv   # one translation per line, indexed
scripts/i18n_extract.py # src/ -> i18n/strings.es.json
scripts/i18n_build.py   # src/ + i18n/ -> the four language trees
scripts/schema.py       # JSON-LD (business, service, FAQ) from each page's visible HTML
scripts/imgs_build.py   # imgs/<photo>.jpg -> imgs/<photo>-<width>.webp (480/960/1440 + original)

index.html              # German home (primary language, lives at the root)
ueber-maya.html         # erotische-massagen.html, faq.html
massagen/<massage>/     # nine German service pages
en/ · es/ · it/         # the other three trees, same shape, own file names
impressum.html          # legal pages: German only, shared by all languages
datenschutz.html
_redirects              # old Spanish root URLs -> /es/… (301) + per-language photo names (200, generated)
sitemap.xml             # all 52 URLs with hreflang alternates and their photos (generated)
css/app.css             # flattened theme CSS
css/theme-palettes.css  # "Noir Vino" palette — colour tokens only
css/service.css         # service page layout (hand-written)
css/mega-menu.css       # CSS-only mega menu
css/spotlight.css       # grayscale → colour under the cursor
css/app-late.css        # rest of the CSS, split out of app.css
js/age-gate.js          # 18+ gate
js/revoza-scroll.js     # Lenis + GSAP scroll choreography
js/svc-lightbox.js      # <dialog> lightbox for service photos
js/vendor/              # gsap, ScrollTrigger, SplitText, lenis
fonts/                  # self-hosted woff2 (Cinzel Decorative, Ovo, Manrope, Bricolage Grotesque)
imgs/                   # photography, favicons, open graph
wrangler.jsonc          # Cloudflare Workers Static Assets config
scripts/hooks/post-commit  # commit on main → npx wrangler deploy
.github/workflows/      # push to main → pings a deploy hook that deploys nothing (see Deployment)
```

## Building the four languages

Edit copy in `src/` (Spanish — it doubles as the translation key) or in the language tables, then regenerate:

```bash
python3 scripts/i18n_extract.py   # only after adding or changing Spanish text
python3 scripts/i18n_build.py     # writes /, /en, /es, /it, _redirects, sitemap.xml
```

`i18n_build.py` runs `imgs_build.py` first (it only re-encodes a WebP when the JPEG is newer), wraps every content photo in a `<picture>` with the WebP variants, and renames the photo per language: `maya-masaje-erotico-berlin-suite-camera.jpg` is `maya-erotische-massage-berlin-suite-schlafzimmer.jpg` on the German pages. **There is still one file on disk** — the translated names are served by `200` proxy rules in `_redirects`, so adding a photo means adding its line to `IMG_SUFFIX` in `i18n_build.py`.

`i18n/strings.{de,en,it}.tsv` holds one `index<TAB>translation` line per string, in the order of `i18n/strings.es.json`; the build refuses to run if a line is missing or out of order. **Never edit the generated pages directly** — the next build overwrites them. `impressum.html` and `datenschutz.html` are hand-maintained and outside the build.

## Running it locally

No install:

```bash
python3 -m http.server 8080
```

That serves `index.html` but not the extensionless `/about`. For real clean-URL testing use `npx wrangler dev`, which applies the same `html_handling` rule as production.

The age gate stores its answer per origin — clear `localStorage` (or open a private window) to see it again.

## Deployment

Hosted on **Cloudflare Workers Static Assets**: no Worker script, no hosting plan — `wrangler.jsonc` serves the repository root as assets and claims both `mayaerotikmassage.com` and `www.mayaerotikmassage.com` as custom domains, creating the DNS records on deploy.

```bash
npx wrangler deploy
```

`.assetsignore` keeps repository-only files (`.git`, `inspiration/`, `wrangler.jsonc`, `docs/`, caches) out of the published bundle.

Every commit on `main` deploys, through `scripts/hooks/post-commit`. Activate it once per clone:

```bash
git config core.hooksPath scripts/hooks
```

Commits on any other branch are skipped. Note that `wrangler deploy` publishes **what is on disk**, not what you just committed — uncommitted changes go live too.

`.github/workflows/deploy.yml` pings the Cloudflare deploy hook in the `CF_DEPLOY_HOOK` secret on every push to `main`. **It does not actually deploy**: the `curl` returns 200 and the Action goes green, but no deployment of this Worker originates from it — every deployment on record has `source: wrangler`. On 2026-10-17 that silently left the live site four commits behind for two hours. The local hook is the workaround; fixing the workflow (a `CLOUDFLARE_API_TOKEN` secret and `cloudflare/wrangler-action`) would replace it.

Redirecting `www` to the apex is **not** in `_redirects` — Workers Static Assets rejects any rule carrying a hostname and fails the whole deploy. It lives as a zone Single Redirect rule (`http_request_dynamic_redirect`), which is Cloudflare dashboard configuration and not in this repository.
