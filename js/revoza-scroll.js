/* Efectos de scroll portados de Revoza (index-3): smooth scroll + reveal de texto por scrub + wipe de imagenes */
(function () {
	if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

	gsap.registerPlugin(ScrollTrigger, SplitText);

	/* Smooth Scroll (equivale a SmoothScroll.js de Revoza) */
	var lenis = new Lenis({ duration: 1.1, smoothWheel: true });
	lenis.on('scroll', ScrollTrigger.update);
	gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
	gsap.ticker.lagSmoothing(0);

	/* Texto: los caracteres pasan de opacidad .3 a 1 segun avanza el scroll.

	   Se cogen todos los h1 y h2 del contenido, no solo los de Elementor: las
	   paginas escritas a mano (sobre Maya y los nueve rituales, en los cuatro
	   idiomas) llevan <h1>/<h2> pelados y se quedaban sin efecto. En
	   ueber-maya.html no entraba ninguno de los ocho. La cabecera, el pie y
	   los menus quedan fuera por la guarda de abajo. */
	function textReveal() {
		document.querySelectorAll('h1, h2').forEach(function (el) {
			if (el.closest('header, footer, nav')) return;

			SplitText.create(el, {
				type: 'lines,words,chars',
				linesClass: 'split-line',
				/* re-parte las lineas al cambiar el ancho; sin esto quedan huecos al redimensionar */
				autoSplit: true,
				onSplit: function (self) {
					gsap.set(self.chars, { opacity: 0.3, x: -7 });
					return gsap.to(self.chars, {
						scrollTrigger: { trigger: el, start: 'top 92%', end: 'top 60%', scrub: 1 },
						x: 0,
						opacity: 1,
						duration: 0.7,
						stagger: 0.02
					});
				}
			});
		});
	}

	/* Imagenes: barrido lateral + micro zoom al entrar en pantalla */
	function imageReveal() {
		document.querySelectorAll('.elementor-widget-image img').forEach(function (img) {
			gsap.from(img, {
				scrollTrigger: { trigger: img, start: 'top 88%', toggleActions: 'play none none none' },
				clipPath: 'inset(0 100% 0 0)',
				scale: 1.12,
				duration: 1.1,
				ease: 'power2.out',
				/* sin esto el transform inline de GSAP anula el :hover de .maya-secret-animation-grow */
				onComplete: function () { gsap.set(img, { clearProps: 'transform,clipPath,scale,translate,rotate' }); }
			});
		});
	}

	/* SplitText mide mal si las fuentes aun no cargaron */
	(document.fonts ? document.fonts.ready : Promise.resolve()).then(function () {
		textReveal();
		imageReveal();
		ScrollTrigger.refresh();
	});
})();

/* Spotlight: el puntero devuelve el color a las imágenes .spotlight (ver css/spotlight.css) */
(function () {
	document.querySelectorAll('.spotlight').forEach(function (el) {
		el.addEventListener('pointermove', function (e) {
			var r = el.getBoundingClientRect();
			el.style.setProperty('--sx', (e.clientX - r.left) + 'px');
			el.style.setProperty('--sy', (e.clientY - r.top) + 'px');
		});
	});
})();
