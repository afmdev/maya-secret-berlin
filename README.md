# Maya Secret — Erotic Massage Berlin

Website of **Maya Secret**, an independent erotic and tantric massage practice in Berlin. Home and hotel visits, by appointment only.

Live: **[www.mayaerotikmassage.com](https://www.mayaerotikmassage.com)**

![Maya Secret — home page](docs/screenshot.png)

## What it is

A static, multi-page site in Spanish. Plain HTML, a handful of stylesheets and vanilla JS — **no build step, no bundler, no framework, no dependencies to install**. The markup started life as an Elementor theme and was flattened into static files; the CSS and JS written for this project sit on top of it.

- **Zero third-party requests.** No analytics, no CDN, no embeds, no cookies. Fonts, images, jQuery, GSAP, Lenis and Swiper are all self-hosted.
- **18+ age gate (JMStV).** `js/age-gate.js` runs from `<head>` and veils the page before first paint; the visitor self-declares and the answer is stamped in `localStorage` for 30 days. Paired with the `age-de-meta-label` meta tag German filters read. It is a §5 self-declaration, not an identity-checking AVS.
- **Nine service pages.** One folder per massage under `/servicios/` — classic, body-to-body, lingam, mutual, nuru, oriental, sensual, tantric and yoni — all sharing `css/service.css`, the only stylesheet written from scratch.
- **Motion that respects the visitor.** Lenis smooth scroll plus GSAP `ScrollTrigger`/`SplitText` for per-character text reveals and image wipes; the whole module returns early under `prefers-reduced-motion: reduce`.
- **CSS instead of JS where possible.** The "Masajes" mega menu with its hover photo panel is pure CSS, and so is the spotlight effect that restores colour under the pointer on grayscale photos (`@property` + a masked `backdrop-filter`).
- **Clean URLs.** `/about`, `/masajes`, `/servicios/masaje-erotico-nuru/` — the `.html` files stay on disk and Cloudflare resolves them extensionless.

## Layout

```
index.html              # home
about.html              # Sobre Maya
masajes.html            # index of the nine massages
faq.html
servicios/<massage>/    # one folder per service page
css/app.css             # flattened theme CSS
css/theme-palettes.css  # "Noir Vino" palette — colour tokens only
css/service.css         # service page layout (hand-written)
css/mega-menu.css       # CSS-only mega menu
css/spotlight.css       # grayscale → colour under the cursor
css/app-late.css        # non-critical CSS, loaded at the end of <body>
js/age-gate.js          # 18+ gate
js/revoza-scroll.js     # Lenis + GSAP scroll choreography
js/svc-lightbox.js      # <dialog> lightbox for service photos
js/vendor/              # gsap, ScrollTrigger, SplitText, lenis
fonts/                  # self-hosted woff2 (Cinzel Decorative, Ovo, Manrope, Bricolage Grotesque)
imgs/                   # photography, favicons, open graph
wrangler.jsonc          # Cloudflare Workers Static Assets config
.github/workflows/      # push to main → pings the Cloudflare deploy hook
```

## Running it locally

No install, no build:

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

A push to `main` runs `.github/workflows/deploy.yml`, which pings the Cloudflare deploy hook stored in the `CF_DEPLOY_HOOK` secret — so merging to `main` is all a deploy takes.
