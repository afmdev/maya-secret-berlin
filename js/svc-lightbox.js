/* Retoques de las páginas de servicio: lupa sobre las fotos (masajes y galería
   de "Sobre Maya") y, en una columna, la foto del masaje subida junto a la intro.
   El <dialog> se crea aquí y reusa los estilos de .maya-modal, así que la
   caída, el ::backdrop, Esc y el foco ya vienen dados. */
(() => {
	const photos = document.querySelectorAll('.svc-side-photo, .svc-gal-slide');
	if (!photos.length) return;

	const dialog = document.createElement('dialog');
	dialog.className = 'maya-modal svc-lightbox';
	dialog.innerHTML = '<div class="maya-modal__inner svc-lightbox__inner">'
		+ '<div class="svc-lightbox__frame">'
		+ '<button type="button" class="maya-modal__close" aria-label="Cerrar">&#215;</button>'
		+ '<img alt=""></div></div>';
	const full = dialog.querySelector('img');
	// el dialog cubre la ventana: cualquier clic que no sea la foto, cierra
	dialog.addEventListener('click', e => {
		if (e.target !== full) dialog.close();
	});
	document.body.append(dialog);

	photos.forEach(photo => {
		const img = photo.querySelector('img');
		if (!img) return;
		const btn = document.createElement('button');
		btn.type = 'button';
		btn.className = 'svc-zoom';
		btn.setAttribute('aria-label', 'Ver la foto en grande');
		btn.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true">'
			+ '<circle cx="11" cy="11" r="6.5"/><path d="M15.8 15.8 21 21"/>'
			+ '<path d="M8.5 11h5M11 8.5v5"/></svg>';
		photo.append(btn);
		// toda la foto abre el visor; el botón solo da la pista visual y el teclado
		photo.addEventListener('click', () => {
			full.src = img.currentSrc || img.src;
			full.alt = img.alt;
			dialog.showModal();
		});
	});

	// al cerrar, el navegador devuelve el foco a la lupa y se quedaba encendida
	dialog.addEventListener('close', () => {
		const activo = document.activeElement;
		if (activo && activo.classList.contains('svc-zoom')) activo.blur();
	});
})();

/* En una columna la foto del aside caía después de todo el texto: se coloca
   tras la entradilla, justo antes del primer separador. */
(() => {
	const foto = document.querySelector('.svc-side-photo');
	const aside = document.querySelector('.svc-side');
	const corte = document.querySelector('.svc-main .hero-rule');
	if (!foto || !aside || !corte) return;

	const titulo = document.querySelector('.svc-main h1');

	// En tableta el texto de entrada y la foto van a dos columnas dentro de un
	// mismo bloque: así la foto mide lo que el texto y no deja hueco debajo.
	const marco = document.createElement('div');
	marco.className = 'svc-intro';
	const columnaTexto = document.createElement('div');
	columnaTexto.className = 'svc-intro__texto';
	marco.append(columnaTexto);

	const parte = () => {
		if (!marco.parentElement) return;
		while (columnaTexto.firstChild) marco.before(columnaTexto.firstChild);
		marco.before(foto);
		marco.remove();
	};
	const junta = () => {
		if (marco.parentElement) return;
		titulo.after(marco);
		let n = marco.nextElementSibling;
		while (n && !n.classList.contains('hero-rule')) {
			const sig = n.nextElementSibling;
			if (n !== foto) columnaTexto.append(n);
			n = sig;
		}
		marco.append(foto);
	};

	const tableta = matchMedia('(min-width:768px) and (max-width:1024px)');
	const movil = matchMedia('(max-width:767px)');
	const coloca = () => {
		if (tableta.matches && titulo) return junta();
		parte();
		if (movil.matches) corte.before(foto);
		else aside.prepend(foto);
	};
	coloca();
	tableta.addEventListener('change', coloca);
	movil.addEventListener('change', coloca);
})();
