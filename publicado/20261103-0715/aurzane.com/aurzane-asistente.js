/* Asistente de resultados de AURZANE (IA). Aparece al terminar un test de MIND o LIVE, o el test de personalidad,
   y responde dudas sobre ese resultado. Lo carga aurzane-paleta.js. La respuesta la genera Gemini en aurzane.com/ai/asistente.php. */
(function (w, d) {
  if (w.__azAsistente) return; w.__azAsistente = 1;
  if (!/^(mind|live)\.aurzane\.com$/.test(location.hostname)) return;
  var E = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  function datos() {
    var r = w.__res;
    if (r && d.body.classList.contains('hecho')) return { test: r.titulo || d.title, resultado: (r.valor + ' ' + (r.unidad || '')).trim() + (r.nivel ? ', nivel: ' + r.nivel : ''), sitio: d.getElementById('detalle'), tipo: 'escala' };
    var res = d.getElementById('resultados'), nom = d.getElementById('resNombre');
    if (res && !res.hidden && nom && nom.textContent.trim()) {
      var t = 'Perfil ' + nom.textContent.trim() + '. ' + ((d.getElementById('resLema') || {}).textContent || '') + ' Rasgos: ' + ((d.getElementById('listaRasgos') || {}).innerText || '').replace(/\s+/g, ' ').slice(0, 700);
      return { test: 'Test de personalidad (Cinco Grandes)', resultado: t, sitio: res, tipo: 'personalidad' };
    }
    if (!r && d.body.classList.contains('hecho')) {   // tests sin resumen (por ejemplo, TDAH): se usa el nivel que muestra la página
      var nv = d.getElementById('nivel'); if (nv && nv.textContent.trim()) return { test: d.title.split('|')[0].trim(), resultado: nv.textContent.trim(), sitio: d.getElementById('detalle'), tipo: 'escala' };
    }
    return null;
  }
  var SUG = { escala: ['¿Qué significa mi resultado?', '¿Qué puedo hacer esta semana para mejorar?', '¿Cuándo debería pedir ayuda profesional?'],
              personalidad: ['Explícame mi perfil en palabras sencillas', '¿Qué carreras o trabajos encajan conmigo?', '¿Cómo puedo aprovechar mis fortalezas?'] };
  function pintar(x) {
    if (d.getElementById('azAsis') || !x.sitio) return;
    var c = d.createElement('section'); c.id = 'azAsis';
    c.style.cssText = 'margin:22px 0;padding:18px 20px;border-radius:16px;border:1px solid rgba(127,127,127,.25);background:var(--surface,rgba(127,127,127,.06));font:inherit';
    c.innerHTML = '<h3 style="margin:0 0 4px;font-size:1.05rem">Pregúntale a la IA de AURZANE sobre tu resultado</h3>' +
      '<p style="margin:0 0 12px;font-size:.86rem;opacity:.75">Respuestas orientativas, no sustituyen a un profesional. Tu pregunta y tu resultado (sin datos personales) se envían a Google Gemini para generar la respuesta; no se guardan.</p>' +
      '<div id="azSug" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px">' + SUG[x.tipo].map(function (s) { return '<button type="button" style="border:1px solid rgba(127,127,127,.35);background:transparent;color:inherit;border-radius:99px;padding:7px 12px;font:inherit;font-size:.85rem;cursor:pointer">' + E(s) + '</button>'; }).join('') + '</div>' +
      '<form id="azForm" style="display:flex;gap:8px;flex-wrap:wrap"><input id="azPreg" maxlength="400" placeholder="Escribe tu pregunta" style="flex:1;min-width:200px;padding:11px 12px;border-radius:12px;border:1px solid rgba(127,127,127,.35);background:transparent;color:inherit;font:inherit">' +
      '<button style="border:0;border-radius:99px;padding:11px 18px;font:inherit;font-weight:700;cursor:pointer;background:var(--acento,#0F1530);color:var(--sobre-acento,#fff)">Preguntar</button></form>' +
      '<div id="azResp" aria-live="polite" style="margin-top:12px;line-height:1.6"></div>';
    x.sitio.parentNode.insertBefore(c, x.sitio.nextSibling);
    var resp = d.getElementById('azResp');
    function preguntar(q) {
      q = (q || '').trim(); if (q.length < 3) return;
      resp.innerHTML = '<p style="opacity:.7">Pensando…</p>';
      var act = datos() || x;
      fetch('https://aurzane.com/ai/asistente.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ test: act.test, resultado: act.resultado, pregunta: q }) })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j.error) { resp.innerHTML = '<p>' + E(j.error) + '</p>'; return; }
          resp.innerHTML = '<p style="margin:0 0 6px;font-weight:700">' + E(q) + '</p>' + E(j.respuesta).split(/\n+/).map(function (p) { return '<p style="margin:0 0 8px">' + p + '</p>'; }).join('') +
            '<p style="font-size:.8rem;opacity:.65">Si en algún momento piensas en hacerte daño, llama al <a href="tel:024">024</a> (España, gratis, 24 h) o al 112.</p>';
        })
        .catch(function () { resp.innerHTML = '<p>No se pudo conectar con el asistente. Prueba en un momento.</p>'; });
    }
    c.querySelectorAll('#azSug button').forEach(function (b) { b.addEventListener('click', function () { preguntar(b.textContent); }); });
    d.getElementById('azForm').addEventListener('submit', function (e) { e.preventDefault(); var i = d.getElementById('azPreg'); preguntar(i.value); i.value = ''; });
  }
  var n = 0, t = setInterval(function () { var x = datos(); if (x) { pintar(x); } if (++n > 2400) clearInterval(t); }, 1500);
})(window, document);
