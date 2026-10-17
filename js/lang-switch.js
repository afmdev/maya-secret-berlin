/* Desplegable de idioma. El <details> ya abre y cierra solo; esto añade lo que
   no trae de serie: cerrar al pulsar fuera, cerrar con Escape y no dejar dos
   abiertos a la vez (hay un menu por cabecera). */
(() => {
	const boxes = document.querySelectorAll('.maya-lang__box');
	if (!boxes.length) return;

	const cerrar = excepto => boxes.forEach(b => {
		if (b !== excepto) b.open = false;
	});

	boxes.forEach(box => {
		box.addEventListener('toggle', () => {
			if (box.open) cerrar(box);
		});
	});

	document.addEventListener('click', e => {
		if (!e.target.closest('.maya-lang__box')) cerrar(null);
	});

	document.addEventListener('keydown', e => {
		if (e.key !== 'Escape') return;
		const abierto = document.querySelector('.maya-lang__box[open]');
		if (!abierto) return;
		abierto.open = false;
		abierto.querySelector('summary').focus();
	});
})();
