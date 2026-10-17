/* Desplegable de idioma. El <details> abre y cierra solo, pero de golpe: aqui
   se le pone la animacion (al abrir, la clase llega un fotograma despues; al
   cerrar, el panel se va antes de plegar el <details>), cerrar al pulsar
   fuera, cerrar con Escape y no dejar dos abiertos a la vez (hay uno por
   cabecera). */
(() => {
	const boxes = document.querySelectorAll('.maya-lang__box');
	if (!boxes.length) return;

	const suave = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

	const abrir = box => {
		box.open = true;
		// Con la clase puesta en el mismo fotograma no hay transicion: el panel
		// nacería ya en su sitio.
		requestAnimationFrame(() => box.classList.add('is-open'));
	};

	const cerrar = box => {
		if (!box.open) return;
		box.classList.remove('is-open');
		if (!suave) {
			box.open = false;
			return;
		}
		// El <details> se pliega cuando el panel ha terminado de subir; el
		// temporizador es el plan B si la transicion no llega a dispararse.
		const panel = box.querySelector('.maya-lang__panel');
		let plegado = false;
		const plegar = () => {
			if (plegado) return;
			plegado = true;
			box.open = false;
		};
		panel.addEventListener('transitionend', e => {
			if (e.propertyName === 'opacity') plegar();
		}, { once: true });
		setTimeout(plegar, 300);
	};

	const cerrarTodos = excepto => boxes.forEach(b => {
		if (b !== excepto) cerrar(b);
	});

	boxes.forEach(box => {
		box.querySelector('summary').addEventListener('click', e => {
			e.preventDefault(); // el <details> abriria de golpe
			if (box.open) {
				cerrar(box);
			} else {
				cerrarTodos(box);
				abrir(box);
			}
		});
	});

	document.addEventListener('click', e => {
		if (!e.target.closest('.maya-lang__box')) cerrarTodos(null);
	});

	document.addEventListener('keydown', e => {
		if (e.key !== 'Escape') return;
		const abierto = document.querySelector('.maya-lang__box[open]');
		if (!abierto) return;
		cerrar(abierto);
		abierto.querySelector('summary').focus();
	});
})();
