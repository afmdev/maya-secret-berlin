/* Puerta de edad 18+ (JMStV). Autodeclaración: el visitante confirma que es
   mayor de edad. Vale para contenido "entwicklungsbeeinträchtigend" (§5
   JMStV) junto a la etiqueta age-de-meta-label; NO sustituye a un AVS con
   comprobación de identidad, que el §4 exige para pornografía.

   Corre desde <head>: marca el <html> antes de que se pinte nada y el CSS
   tapa la página hasta que el visitante responde. */
(function () {
	'use strict';

	var KEY = 'maya-age-ok';
	var VIGENCIA = 30 * 24 * 60 * 60 * 1000; // 30 días
	var SALIDA = 'https://www.google.de/';
	var html = document.documentElement;

	var sello = 0;
	try { sello = +localStorage.getItem(KEY) || 0; } catch (e) { /* modo privado */ }
	if (sello && Date.now() - sello < VIGENCIA) return;

	html.classList.add('maya-agegate-on');

	// El velo va aquí y no en la hoja: theme-palettes.css se carga al final del
	// body y para entonces la página ya habría asomado.
	var velo = document.createElement('style');
	velo.textContent = 'html.maya-agegate-on{overflow:hidden}' +
		'html.maya-agegate-on body>*:not(.maya-agegate){visibility:hidden}';
	document.head.appendChild(velo);

	function montar() {
		var gate = document.createElement('div');
		gate.className = 'maya-agegate';
		gate.setAttribute('role', 'dialog');
		gate.setAttribute('aria-modal', 'true');
		gate.setAttribute('tabindex', '-1');
		gate.setAttribute('aria-labelledby', 'maya-agegate-title');
		gate.innerHTML = [
			'<div class="maya-agegate__panel">',
			'<p class="maya-agegate__brand">- Maya Erotik Massage Berlin -</p>',
			'<h1 class="maya-agegate__title" id="maya-agegate-title">Solo para mayores de 18 años</h1>',
			'<div class="hero-rule" aria-hidden="true">&#9670;</div>',
			'<p class="maya-agegate__text">Esta web contiene contenido erótico dirigido exclusivamente a personas adultas. Al entrar confirmas que tienes 18 años o más y que deseas verlo.</p>',
			'<div class="maya-agegate__actions">',
			'<button type="button" class="maya-agegate__btn" data-agegate="in">Tengo 18 años o más</button>',
			'<button type="button" class="maya-agegate__btn maya-agegate__btn--out" data-agegate="out">Salir</button>',
			'</div>',
			'<p class="maya-agegate__note">Maya solo ofrece masajes con cita previa en Berlin. Aquí no se ofrecen servicios sexuales.</p>',
			'</div>'
		].join('');
		document.body.appendChild(gate);

		var entrar = gate.querySelector('[data-agegate="in"]');
		var salir = gate.querySelector('[data-agegate="out"]');

		entrar.addEventListener('click', function () {
			try { localStorage.setItem(KEY, Date.now()); } catch (e) { /* modo privado: vuelve a preguntar */ }
			html.classList.remove('maya-agegate-on');
			gate.remove();
		});

		salir.addEventListener('click', function () {
			location.replace(SALIDA);
		});

		// El foco no sale de la puerta: solo hay dos botones, se turnan.
		gate.addEventListener('keydown', function (e) {
			if (e.key !== 'Tab') return;
			e.preventDefault();
			(document.activeElement === entrar ? salir : entrar).focus();
		});

		// El foco entra por el diálogo, no por el botón: el lector de pantalla lee
		// el aviso entero y ningún navegador dibuja su anillo sobre el oro.
		gate.focus();
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', montar);
	} else {
		montar();
	}
})();
