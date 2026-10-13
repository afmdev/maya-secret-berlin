/* Lupa al pasar por encima de las fotos (masajes y galería de "Sobre Maya").
   El <dialog> se crea aquí y reusa los estilos de .maya-modal, así que la
   caída, el ::backdrop, Esc y el foco ya vienen dados. */
(() => {
	const photos = document.querySelectorAll('.svc-side-photo, .svc-gal-slide');
	if (!photos.length) return;

	const dialog = document.createElement('dialog');
	dialog.className = 'maya-modal svc-lightbox';
	dialog.innerHTML = '<div class="maya-modal__inner svc-lightbox__inner">'
		+ '<button type="button" class="maya-modal__close" aria-label="Cerrar">&#215;</button>'
		+ '<img alt=""></div>';
	// fuera del panel o en la X: se cierra
	dialog.addEventListener('click', e => {
		if (e.target === dialog || e.target.closest('.maya-modal__close')) dialog.close();
	});
	document.body.append(dialog);
	const full = dialog.querySelector('img');

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
		btn.addEventListener('click', () => {
			full.src = img.currentSrc || img.src;
			full.alt = img.alt;
			dialog.showModal();
		});
		photo.append(btn);
	});
})();
