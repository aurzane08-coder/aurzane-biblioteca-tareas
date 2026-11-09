/* =====================================================================
   informe-opciones.js — AURZANE OVP
   Membrete y firma del informe. Solo se ofrecen los membretes activos
   (hoy AURZANE y COMIL 12); si el cliente no tiene ninguno, se usa
   AURZANE. La firma por defecto es la del profesional predeterminado
   (Psi. Cl. Adrian Sánchez Samaniego) y se puede cambiar por otro.
   ===================================================================== */
(function(global){
  'use strict';

  var AURZANE_RESPALDO = { id: null, nombre_marca: 'AURZANE', subtitulo: 'MIND · Orientación Vocacional-Profesional', color_acento: '#C9A24B', activo: true };
  var FIRMA_RESPALDO = { id: null, nombre: 'Psi. Cl. Adrian Sánchez Samaniego', titulo: 'Psicólogo Clínico', registro: 'Registro SENESCYT N.º 1033-2023-2618464', es_predeterminado: true };

  var cache = null;

  async function cargar(sb, forzar){
    if(cache && !forzar) return cache;
    var r = await Promise.all([
      sb.from('membretes').select('*').eq('activo', true),
      sb.from('profesionales').select('*').eq('activo', true)
    ]);
    var membretes = (r[0] && r[0].data) || [];
    var profesionales = (r[1] && r[1].data) || [];
    // AURZANE primero, después el resto por nombre.
    membretes.sort(function(a, b){
      if(a.nombre_marca === 'AURZANE') return -1;
      if(b.nombre_marca === 'AURZANE') return 1;
      return String(a.nombre_marca).localeCompare(String(b.nombre_marca), 'es');
    });
    profesionales.sort(function(a, b){
      if(a.es_predeterminado !== b.es_predeterminado) return a.es_predeterminado ? -1 : 1;
      return String(a.nombre).localeCompare(String(b.nombre), 'es');
    });
    cache = { membretes: membretes, profesionales: profesionales };
    return cache;
  }

  function membretePorDefecto(op){
    return (op.membretes || []).filter(function(m){ return m.nombre_marca === 'AURZANE'; })[0] || AURZANE_RESPALDO;
  }
  function profesionalPorDefecto(op){
    var l = op.profesionales || [];
    return l.filter(function(p){ return p.es_predeterminado; })[0] || l[0] || FIRMA_RESPALDO;
  }

  // Devuelve { membrete, profesional } para un cliente. Un membrete
  // inactivo (p. ej. Rocket UP) o inexistente cae en AURZANE.
  async function resolver(sb, cliente){
    var op = await cargar(sb);
    var m = (op.membretes || []).filter(function(x){ return x.id === cliente.membrete_id; })[0] || membretePorDefecto(op);
    var p = (op.profesionales || []).filter(function(x){ return x.id === cliente.profesional_id; })[0] || profesionalPorDefecto(op);
    return { membrete: m, profesional: p, opciones: op };
  }

  function esc(s){
    return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]; });
  }
  function nombreMembrete(m){
    return m.nombre_marca + (m.subtitulo && m.nombre_marca !== 'AURZANE' ? ' (' + m.subtitulo + ')' : '');
  }

  // Pinta los dos selectores. onCambio({ membrete_id, profesional_id })
  // debe guardar y volver a generar el informe.
  function selector(cont, estado, onCambio){
    var op = estado.opciones;
    var defM = membretePorDefecto(op), defP = profesionalPorDefecto(op);
    cont.innerHTML =
      '<div class="opciones-informe">' +
        '<label class="oi-campo"><span>Membrete</span>' +
          '<select id="oiMembrete">' + op.membretes.map(function(m){
            return '<option value="' + esc(m.id) + '"' + (m.id === estado.membrete.id ? ' selected' : '') + '>' + esc(nombreMembrete(m)) + '</option>';
          }).join('') + '</select></label>' +
        '<label class="oi-campo"><span>Firma de responsabilidad</span>' +
          '<select id="oiFirma">' + op.profesionales.map(function(p){
            return '<option value="' + esc(p.id) + '"' + (p.id === estado.profesional.id ? ' selected' : '') + '>' + esc(p.nombre) + '</option>';
          }).join('') + '</select></label>' +
        '<span class="oi-estado" id="oiEstado" aria-live="polite"></span>' +
      '</div>';
    var sm = cont.querySelector('#oiMembrete'), sp = cont.querySelector('#oiFirma'), st = cont.querySelector('#oiEstado');
    if(op.profesionales.length < 2) sp.disabled = true;
    async function cambiar(){
      sm.disabled = sp.disabled = true;
      st.textContent = 'Guardando…';
      try{
        // AURZANE y el profesional predeterminado se guardan como "sin
        // asignar", así siguen siendo el valor por defecto.
        var mid = sm.value && sm.value !== String(defM.id) ? sm.value : null;
        var pid = sp.value && sp.value !== String(defP.id) ? sp.value : null;
        await onCambio({ membrete_id: mid, profesional_id: pid });
        st.textContent = 'Informe actualizado.';
      }catch(e){
        st.textContent = 'No se pudo guardar: ' + (e && e.message ? e.message : 'error');
      }finally{
        sm.disabled = false;
        sp.disabled = op.profesionales.length < 2;
      }
    }
    sm.addEventListener('change', cambiar);
    sp.addEventListener('change', cambiar);
  }

  global.OVPOpciones = {
    cargar: cargar, resolver: resolver, selector: selector,
    membretePorDefecto: membretePorDefecto, profesionalPorDefecto: profesionalPorDefecto,
    FIRMA_RESPALDO: FIRMA_RESPALDO, AURZANE_RESPALDO: AURZANE_RESPALDO
  };
})(window);
