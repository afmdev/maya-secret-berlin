/* Menu movil: las dos cosas que la plantilla no trae.

   1. Entrada escalonada. El panel ya desliza, pero los items estan a plena
      opacidad desde el primer fotograma y el contenido aparece de golpe: la
      clase maya-menu-open los va soltando uno detras de otro (el retardo lo
      pone el CSS).
   2. El item con submenu. SmartMenus se queda el primer toque del enlace
      padre para desplegar, asi que "Erotische Massagen" no llevaba a ninguna
      parte. Aqui el enlace navega y el boton +/- (lo pone scripts/i18n_build.py)
      abre y cierra el submenu, como el acordeon del FAQ. */
(() => {
	const navs = document.querySelectorAll('.elementor-nav-menu--dropdown.elementor-nav-menu__container');
	if (!navs.length) return;

	// --- 1. Entrada escalonada ------------------------------------------
	// El panel no avisa de que se abre: quien lleva la cuenta es la hamburguesa,
	// que recibe la clase elementor-active.
	document.querySelectorAll('.elementor-menu-toggle').forEach(hamburguesa => {
		const nav = hamburguesa.parentElement
			&& hamburguesa.parentElement.querySelector('.elementor-nav-menu--dropdown.elementor-nav-menu__container');
		if (!nav) return;
		new MutationObserver(() => {
			nav.classList.toggle('maya-menu-open', hamburguesa.classList.contains('elementor-active'));
		}).observe(hamburguesa, { attributes: true, attributeFilter: ['class'] });
	});

	// --- 2. Submenu con boton -------------------------------------------
	const submenu = li => li.querySelector(':scope > ul');

	const desplegar = (li, abrir) => {
		const ul = submenu(li);
		const boton = li.querySelector(':scope > .maya-sub');
		if (!ul) return;

		ul.style.display = 'block';
		ul.style.height = abrir ? '0px' : ul.scrollHeight + 'px';
		ul.getBoundingClientRect(); // fuerza el calculo: sin esto no hay transicion
		ul.style.height = abrir ? ul.scrollHeight + 'px' : '0px';
		li.classList.toggle('is-open', abrir);
		if (boton) boton.setAttribute('aria-expanded', String(abrir));

		ul.addEventListener('transitionend', e => {
			if (e.propertyName !== 'height') return;
			// Abierto queda en auto para que crezca si cambia el contenido;
			// cerrado se limpia y vuelve a mandar el CSS del tema.
			ul.style.height = abrir ? 'auto' : '';
			if (!abrir) ul.style.display = '';
		}, { once: true });
	};

	navs.forEach(nav => {
		// En captura y sobre el <nav>: asi corre antes que los manejadores que
		// SmartMenus engancha en el propio enlace.
		nav.addEventListener('click', e => {
			const boton = e.target.closest('.maya-sub');
			if (boton) {
				e.preventDefault();
				e.stopPropagation();
				const li = boton.parentElement;
				desplegar(li, !li.classList.contains('is-open'));
				return;
			}
			const enlace = e.target.closest('a[data-maya-href]');
			if (enlace) {
				// SmartMenus deja el href en "#": se devuelve y se le corta el
				// paso para que el navegador haga lo suyo, ir a la pagina.
				e.stopPropagation();
				enlace.setAttribute('href', enlace.dataset.mayaHref);
			}
		}, true);
	});
})();
