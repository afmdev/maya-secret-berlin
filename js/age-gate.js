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

	// El velo va aquí y no en la hoja: nace con el script, antes de que ninguna
	// hoja haya llegado, así que tapa aunque una tarde o falle.
	var velo = document.createElement('style');
	// El velo tapa hasta que la puerta existe; a partir de ahi tapa el panel,
	// que es opaco y cubre la ventana entera. Asi el contenido sigue en pie
	// para quien renderiza la pagina (buscadores, asistentes) sin que nadie
	// lo vea antes de responder: lo mismo que ve quien ya ha entrado.
	velo.textContent = 'html.maya-agegate-on{overflow:hidden}' +
		'html.maya-agegate-on:not(.maya-agegate-ready) body>*:not(.maya-agegate){visibility:hidden}' +
		'.maya-agegate{position:fixed;inset:0;z-index:2147483000;background:#0D0A0C}';
	document.head.appendChild(velo);

	// La puerta es lo primero que se ve, asi que habla el idioma de la pagina:
	// el <html lang> ya lo pone scripts/i18n_build.py. Aleman por defecto.
	var TEXTOS = {
		de: {
			titulo: 'Nur für Personen ab 18 Jahren',
			texto: 'Diese Website enthält erotische Inhalte ausschließlich für Erwachsene. Mit dem Eintreten bestätigen Sie, dass Sie 18 Jahre oder älter sind und die Inhalte sehen möchten.',
			entrar: 'Ich bin 18 oder älter',
			salir: 'Verlassen',
			nota: 'Maya gibt Massagen in Berlin nur nach Vereinbarung. Hier werden keine sexuellen Dienstleistungen angeboten.'
		},
		en: {
			titulo: 'For adults 18 and over only',
			texto: 'This website contains erotic content intended for adults only. By entering you confirm that you are 18 or older and that you wish to see it.',
			entrar: 'I am 18 or older',
			salir: 'Leave',
			nota: 'Maya gives massages in Berlin by appointment only. No sexual services are offered here.'
		},
		es: {
			titulo: 'Solo para mayores de 18 años',
			texto: 'Esta web contiene contenido erótico dirigido exclusivamente a personas adultas. Al entrar confirma que tiene 18 años o más y que desea verlo.',
			entrar: 'Tengo 18 años o más',
			salir: 'Salir',
			nota: 'Maya solo ofrece masajes con cita previa en Berlín. Aquí no se ofrecen servicios sexuales.'
		},
		it: {
			titulo: 'Solo per maggiori di 18 anni',
			texto: 'Questo sito contiene contenuti erotici destinati esclusivamente a persone adulte. Entrando conferma di avere 18 anni o più e di volerli vedere.',
			entrar: 'Ho 18 anni o più',
			salir: 'Esci',
			nota: 'Maya offre massaggi a Berlino solo su appuntamento. Qui non si offrono servizi sessuali.'
		}
	};

	function montar() {
		var t = TEXTOS[(html.getAttribute('lang') || 'de').slice(0, 2)] || TEXTOS.de;
		var gate = document.createElement('div');
		gate.className = 'maya-agegate';
		gate.setAttribute('role', 'dialog');
		gate.setAttribute('aria-modal', 'true');
		gate.setAttribute('tabindex', '-1');
		gate.setAttribute('aria-labelledby', 'maya-agegate-title');
		gate.innerHTML = [
			'<div class="maya-agegate__panel">',
			'<p class="maya-agegate__brand">- Maya Erotik Massage Berlin -</p>',
			'<p class="maya-agegate__title" id="maya-agegate-title">' + t.titulo + '</p>',
			'<div class="hero-rule" aria-hidden="true">&#9670;</div>',
			'<p class="maya-agegate__text">' + t.texto + '</p>',
			'<div class="maya-agegate__actions">',
			'<button type="button" class="maya-agegate__btn" data-agegate="in">' + t.entrar + '</button>',
			'<button type="button" class="maya-agegate__btn maya-agegate__btn--out" data-agegate="out">' + t.salir + '</button>',
			'</div>',
			'<p class="maya-agegate__note">' + t.nota + '</p>',
			'</div>'
		].join('');
		document.body.appendChild(gate);
		// La puerta ya tapa por si misma: se levanta el velo.
		html.classList.add('maya-agegate-ready');

		// El velo tapaba tambien para el lector de pantalla; la capa opaca no,
		// asi que el resto de la pagina se marca inerte: fuera del foco, del
		// raton y del arbol de accesibilidad, pero presente en el documento.
		// La puerta se monta nada mas abrirse el <body>, cuando aun no hay
		// hermanos que tapar, asi que esto espera a que el <body> este entero.
		var tapado = [];
		var abierta = true;
		function tapar() {
			if (!abierta) return;           // ya entro: no hay nada que tapar
			tapado = [].slice.call(document.body.children).filter(function (el) {
				return el !== gate;
			});
			tapado.forEach(function (el) { el.inert = true; });
		}
		if (document.readyState === 'loading') {
			document.addEventListener('DOMContentLoaded', tapar);
		} else {
			tapar();
		}

		var entrar = gate.querySelector('[data-agegate="in"]');
		var salir = gate.querySelector('[data-agegate="out"]');

		entrar.addEventListener('click', function () {
			try { localStorage.setItem(KEY, Date.now()); } catch (e) { /* modo privado: vuelve a preguntar */ }
			abierta = false;
			html.classList.remove('maya-agegate-on', 'maya-agegate-ready');
			tapado.forEach(function (el) { el.inert = false; });
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

	// Desde el <head> no se puede tocar el <body>: todavia no existe. La
	// llamada la hace un <script> nada mas abrirse el <body> (lo mete
	// scripts/i18n_build.py), que es el primer instante en el que la puerta
	// puede pintarse. Esperar al DOMContentLoaded significaba esperar a todo
	// el JS diferido de la pagina, y la puerta es lo primero que se ve.
	window.mayaPuerta = function () {
		window.mayaPuerta = null;
		montar();
	};
	// Red de seguridad: si una pagina no lleva esa llamada, la puerta sale
	// igual (tarde, pero sale). Sin esto un olvido en el HTML la quita.
	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', function () {
			if (window.mayaPuerta) window.mayaPuerta();
		});
	} else {
		window.mayaPuerta();
	}
})();
