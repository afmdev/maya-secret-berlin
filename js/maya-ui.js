/* Lo poco que hacia en esta web el stack de jQuery + Elementor (~330 KB),
   en vanilla: la entrada de los bloques, la hamburguesa, la cabecera que se
   esconde al bajar y el boton de subir.

   El resto no lo necesitaba: el acordeon del FAQ y el selector de idioma son
   <details>, el contacto es <dialog>, el mega menu abre por :hover en CSS y
   los reveals de texto e imagen los hace js/revoza-scroll.js con GSAP. */
(() => {
	'use strict';

	/* 1. Entrada de los bloques ------------------------------------------
	   Elementor deja .elementor-invisible{visibility:hidden} y al entrar en
	   pantalla lo cambia por "animated <nombre>"; los @keyframes (fadeIn,
	   zoomIn, slideInUp) ya viven en css/app.css. */
	const ocultos = document.querySelectorAll('.elementor-invisible');
	if (ocultos.length) {
		const mostrar = el => {
			let cfg = {};
			try { cfg = JSON.parse(el.dataset.settings || '{}'); } catch (e) { /* sin ajustes */ }
			const entrada = () => {
				el.classList.add('animated', cfg._animation || 'fadeIn');
				el.classList.remove('elementor-invisible');
			};
			const espera = cfg._animation_delay || 0;
			espera ? setTimeout(entrada, espera) : entrada();
		};
		const ojo = new IntersectionObserver((entradas, obs) => {
			entradas.forEach(e => {
				if (!e.isIntersecting) return;
				mostrar(e.target);
				obs.unobserve(e.target);
			});
		}, { rootMargin: '0px 0px -8% 0px' });
		ocultos.forEach(el => ojo.observe(el));
	}

	/* 2. Hamburguesa: el panel lo abre y lo cierra el CSS del tema con
	   .elementor-active sobre el boton (selector hermano en app.css). El panel
	   va en absoluto bajo un widget estrecho; con --stretch Elementor lo abria
	   a lo ancho de la ventana, que es lo que hace ensanchar(). */
	document.querySelectorAll('.elementor-menu-toggle').forEach(boton => {
		const panel = boton.nextElementSibling;
		const estira = panel && boton.closest('.elementor-nav-menu--stretch');
		const ensanchar = () => {
			const origen = panel.offsetParent ? panel.offsetParent.getBoundingClientRect().left : 0;
			panel.style.left = `${-origen}px`;
			panel.style.width = `${document.documentElement.clientWidth}px`;
		};
		boton.addEventListener('click', () => {
			const abierto = boton.classList.toggle('elementor-active');
			boton.setAttribute('aria-expanded', String(abierto));
			if (estira && abierto) ensanchar();
		});
		if (estira) {
			addEventListener('resize', () => {
				if (boton.classList.contains('elementor-active')) ensanchar();
			});
		}
	});

	/* 3. Cabecera: fija por CSS; estas dos clases la esconden al bajar y la
	   devuelven (con el fondo difuminado) al subir. */
	const cabecera = document.querySelector(
		'.mayaerotikmassage-sticky-header:not(.mayaerotikmassage-sticky-header--spacer)');
	if (cabecera) {
		const OCULTA = 'mayaerotikmassage-sticky-header--fixed-hidden';
		const VISIBLE = 'mayaerotikmassage-sticky-header--fixed-shown';
		let ultimo = window.scrollY;
		let pedido = false;
		const pintar = () => {
			pedido = false;
			const y = window.scrollY;
			if (y < 10) {
				cabecera.classList.remove(OCULTA, VISIBLE);
			} else if (Math.abs(y - ultimo) > 4) {
				const baja = y > ultimo;
				cabecera.classList.toggle(OCULTA, baja);
				cabecera.classList.toggle(VISIBLE, !baja);
			}
			ultimo = y;
		};
		addEventListener('scroll', () => {
			if (pedido) return;
			pedido = true;
			requestAnimationFrame(pintar);
		}, { passive: true });
		pintar();
	}

	/* 4. Subir arriba (lo hacia js/low-priority.js). */
	const subir = document.getElementById('scroll-to-top');
	if (subir) {
		const colocar = () => {
			const visible = window.scrollY > innerHeight / 2;
			subir.style.opacity = visible ? '1' : '';
			subir.style.transform = `translate3d(0, ${visible ? '0' : '100%'}, 0)`;
		};
		addEventListener('scroll', colocar, { passive: true });
		colocar();
		subir.addEventListener('click', e => {
			e.preventDefault();
			scrollTo({ top: 0, behavior: 'smooth' });
		});
	}
})();
