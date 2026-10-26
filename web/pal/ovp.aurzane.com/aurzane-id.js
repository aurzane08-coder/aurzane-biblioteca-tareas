/*
 * AURZANE ID — sesión compartida entre todos los subdominios de aurzane.com
 * ---------------------------------------------------------------------
 * Este archivo resuelve la limitación detectada antes en el proyecto de
 * Universidades: un login guardado con localStorage NO se comparte entre
 * subdominios (aurzane.com, mind.aurzane.com, ovp.aurzane.com, etc.) porque
 * cada subdominio es un "origen" distinto para el navegador.
 *
 * La solución: en vez de localStorage, la sesión de Supabase se guarda en
 * una cookie con `domain=.aurzane.com` — esa sí la puede leer cualquier
 * subdominio. Así, si alguien inicia sesión en aurzane.com, esa misma
 * sesión ya está disponible en mind.aurzane.com, ovp.aurzane.com, etc. sin
 * que tenga que volver a loguearse en cada uno (una vez que este script se
 * incluya también en esas páginas — ver guía de entrega).
 *
 * Uso en cualquier página del ecosistema:
 *
 *   <script src="https://unpkg.com/@supabase/supabase-js@2"></script>
 *   <script src="/aurzane-id.js"></script>
 *   <script>
 *     const sbId = crearClienteAurzaneID(SUPABASE_URL, SUPABASE_ANON_KEY);
 *     const { data: { session } } = await sbId.auth.getSession();
 *   </script>
 *
 * Nota honesta: las cookies de sesión tienen un límite práctico de tamaño
 * (~4KB por cookie). El token de Supabase normalmente entra sin problema,
 * pero por si acaso, este storage parte el valor en varias cookies
 * numeradas si hace falta, y las vuelve a unir al leer.
 */

(function (global) {
  "use strict";

  const DOMINIO_COOKIE = ".aurzane.com";
  const TAMANO_MAXIMO_TROZO = 3180; // margen de seguridad bajo el límite de ~4KB

  function escaparNombre(nombre) {
    return nombre.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function leerCookie(nombre) {
    const m = document.cookie.match(
      new RegExp("(?:^|; )" + escaparNombre(nombre) + "=([^;]*)")
    );
    return m ? decodeURIComponent(m[1]) : null;
  }

  function escribirCookie(nombre, valor) {
    const treintaDias = 60 * 60 * 24 * 30;
    const esLocal = location.hostname === "localhost";
    document.cookie =
      `${nombre}=${encodeURIComponent(valor)}; ` +
      (esLocal ? "" : `domain=${DOMINIO_COOKIE}; `) +
      `path=/; max-age=${treintaDias}; ` +
      (esLocal ? "" : "secure; ") +
      "samesite=lax";
  }

  function borrarCookie(nombre) {
    const esLocal = location.hostname === "localhost";
    document.cookie =
      `${nombre}=; ` +
      (esLocal ? "" : `domain=${DOMINIO_COOKIE}; `) +
      "path=/; max-age=0";
  }

  // Storage compatible con la interfaz que espera supabase-js (getItem/
  // setItem/removeItem), pero respaldado por cookies en vez de localStorage,
  // con troceo automático si el valor no entra en una sola cookie.
  const cookieStorage = {
    getItem(clave) {
      const directo = leerCookie(clave);
      if (directo !== null) return directo;
      const trozos = [];
      let i = 0;
      while (true) {
        const trozo = leerCookie(`${clave}.${i}`);
        if (trozo === null) break;
        trozos.push(trozo);
        i++;
      }
      return trozos.length ? trozos.join("") : null;
    },
    setItem(clave, valor) {
      this.removeItem(clave);
      const codificado = encodeURIComponent(valor);
      if (codificado.length <= TAMANO_MAXIMO_TROZO) {
        escribirCookie(clave, valor);
        return;
      }
      // Trocear: se codifica y decodifica trozo a trozo para no cortar
      // un carácter escapado (%XX) por la mitad.
      let restante = valor;
      let i = 0;
      while (restante.length > 0) {
        let corte = TAMANO_MAXIMO_TROZO;
        let trozo = "";
        while (corte > 0) {
          trozo = restante.slice(0, corte);
          if (encodeURIComponent(trozo).length <= TAMANO_MAXIMO_TROZO) break;
          corte -= 50;
        }
        escribirCookie(`${clave}.${i}`, trozo);
        restante = restante.slice(trozo.length);
        i++;
      }
    },
    removeItem(clave) {
      borrarCookie(clave);
      let i = 0;
      while (leerCookie(`${clave}.${i}`) !== null) {
        borrarCookie(`${clave}.${i}`);
        i++;
      }
    },
  };

  // Crea (o reutiliza) el cliente Supabase compartido de AURZANE ID.
  // storageKey es fijo ("aurzane-id-auth") a propósito: así todas las
  // páginas del ecosistema que incluyan este script leen la MISMA sesión.
  function crearClienteAurzaneID(supabaseUrl, supabaseAnonKey) {
    if (global.__aurzaneIdClient) return global.__aurzaneIdClient;
    if (!global.supabase || !global.supabase.createClient) {
      throw new Error(
        "aurzane-id.js necesita que supabase-js ya esté cargado antes (ver comentario de uso arriba)."
      );
    }
    const cliente = global.supabase.createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        storage: cookieStorage,
        storageKey: "aurzane-id-auth",
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    });
    global.__aurzaneIdClient = cliente;
    return cliente;
  }

  /* ------------------------------------------------------------------
   * Cierre de sesión por inactividad (OVP)
   * ------------------------------------------------------------------
   * La sesión vive en una cookie de 30 días, así que sin esto quien abre
   * su cuenta en una computadora compartida (colegio, cyber) queda
   * conectado. Regla: 30 minutos sin actividad (teclado, ratón, toque,
   * desplazamiento) cierran la sesión, con aviso 2 minutos antes.
   * La última actividad se guarda en una cookie del dominio, así que
   * varias pestañas abiertas cuentan como una sola persona activa.
   * Si alguien vuelve después de más de 30 minutos (por ejemplo, al día
   * siguiente), la sesión vieja se descarta antes de que la página la use.
   */
  const MINUTOS_INACTIVIDAD = 30;
  const MINUTOS_AVISO = 2;
  const COOKIE_ACTIVIDAD = "aurzane-ultima-actividad";
  const CLAVE_SESION = "aurzane-id-auth";

  function escribirActividad(ms) {
    const esLocal = location.hostname === "localhost";
    document.cookie =
      `${COOKIE_ACTIVIDAD}=${ms}; ` +
      (esLocal ? "" : `domain=${DOMINIO_COOKIE}; `) +
      "path=/; max-age=2592000; " + (esLocal ? "" : "secure; ") + "samesite=lax";
  }
  function leerActividad() {
    const v = Number(leerCookie(COOKIE_ACTIVIDAD));
    return Number.isFinite(v) && v > 0 ? v : 0;
  }
  // Momento en que se emitió el token actual (iat): un inicio de sesión
  // recién hecho nunca se considera inactivo.
  function emisionToken() {
    try {
      const crudo = cookieStorage.getItem(CLAVE_SESION);
      if (!crudo) return null;
      const ses = JSON.parse(crudo);
      const tok = ses && (ses.access_token || (ses.currentSession && ses.currentSession.access_token));
      if (!tok) return null;
      const carga = tok.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
      const json = JSON.parse(decodeURIComponent(escape(atob(carga))));
      return { iat: (json.iat || 0) * 1000, exp: (json.exp || 0) * 1000 };
    } catch (e) {
      return null;
    }
  }
  function hayCookieSesion() {
    return cookieStorage.getItem(CLAVE_SESION) !== null;
  }


  // Al cargar: si la sesión guardada lleva más de 30 minutos sin uso, se
  // descarta en este navegador antes de crear el cliente de Supabase.
  function descartarSesionVieja() {
    if (!hayCookieSesion()) return false;
    // Se descarta solo si el token ya venció (nadie lo mantuvo vivo en otra
    // página del ecosistema) y además no hubo actividad en 30 minutos.
    const tok = emisionToken();
    const vencido = !tok || (tok.exp && Date.now() > tok.exp);
    const ultima = Math.max(leerActividad(), tok ? tok.iat : 0);
    if (vencido && Date.now() - ultima > MINUTOS_INACTIVIDAD * 60000) {
      cookieStorage.removeItem(CLAVE_SESION);
      return true;
    }
    // Abrir o recargar una página cuenta como actividad.
    escribirActividad(Date.now());
    return false;
  }

  let vigilanciaIniciada = false;
  function iniciarVigilancia(cliente) {
    if (vigilanciaIniciada) return;
    vigilanciaIniciada = true;
    let ultimaEscritura = 0;
    let aviso = null;
    let cerrando = false;

    function registrar() {
      const ahora = Date.now();
      if (ahora - ultimaEscritura > 15000) {
        ultimaEscritura = ahora;
        if (hayCookieSesion()) escribirActividad(ahora);
      }
      if (aviso) ocultarAviso();
    }
    ["pointerdown", "keydown", "wheel", "touchstart", "scroll", "mousemove"].forEach((ev) =>
      window.addEventListener(ev, registrar, { passive: true, capture: true })
    );
    document.addEventListener("visibilitychange", () => { if (!document.hidden) revisar(); });

    function mostrarAviso(segundos) {
      if (!aviso) {
        aviso = document.createElement("div");
        aviso.setAttribute("role", "alertdialog");
        aviso.setAttribute("aria-live", "assertive");
        aviso.style.cssText =
          "position:fixed;inset:0;z-index:2147483000;background:rgba(4,6,14,.72);display:flex;align-items:center;justify-content:center;padding:20px;font-family:'Instrument Sans',system-ui,sans-serif;";
        aviso.innerHTML =
          '<div style="background:#0F1530;color:#F5F3EE;border:1px solid rgba(201,162,75,.45);border-radius:14px;max-width:420px;width:100%;padding:26px 24px;text-align:center;box-shadow:0 20px 50px -20px rgba(0,0,0,.6);">' +
          '<h2 style="font-family:\'Bodoni Moda\',Georgia,serif;font-weight:500;font-size:1.35rem;margin:0 0 10px;">¿Sigues ahí?</h2>' +
          '<p style="margin:0 0 18px;color:#C7CDD6;font-size:.92rem;line-height:1.55;">Por seguridad, tu sesión se cerrará en <b data-seg></b> por inactividad. Tus respuestas guardadas no se pierden.</p>' +
          '<button type="button" data-seguir style="background:linear-gradient(135deg,#EACF92,#C9A24B);color:#080B17;border:none;border-radius:8px;padding:12px 22px;font-weight:700;font-size:.9rem;cursor:pointer;">Seguir conectado</button>' +
          "</div>";
        aviso.querySelector("[data-seguir]").addEventListener("click", () => {
          escribirActividad(Date.now());
          ultimaEscritura = Date.now();
          ocultarAviso();
        });
        document.body.appendChild(aviso);
        aviso.querySelector("[data-seguir]").focus();
      }
      const m = Math.floor(segundos / 60), s = segundos % 60;
      aviso.querySelector("[data-seg]").textContent = m + ":" + String(s).padStart(2, "0");
    }
    function ocultarAviso() {
      if (aviso) { aviso.remove(); aviso = null; }
    }

    async function cerrar() {
      if (cerrando) return;
      cerrando = true;
      try { await cliente.auth.signOut(); } catch (e) { cookieStorage.removeItem(CLAVE_SESION); }
      const destino = "https://aurzane.com/mi-aurzane.html?inactividad=1&next=" + encodeURIComponent(location.href);
      location.replace(location.hostname === "localhost" ? location.pathname : destino);
    }

    function revisar() {
      if (cerrando) return;
      if (!hayCookieSesion()) { ocultarAviso(); return; }
      const inactivo = Date.now() - (leerActividad() || Date.now());
      const limite = MINUTOS_INACTIVIDAD * 60000;
      if (inactivo >= limite) { cerrar(); return; }
      if (inactivo >= limite - MINUTOS_AVISO * 60000) {
        mostrarAviso(Math.ceil((limite - inactivo) / 1000));
      } else if (aviso) {
        ocultarAviso();
      }
    }
    setInterval(revisar, 1000);
  }

  const crearClienteBase = crearClienteAurzaneID;
  function crearClienteConInactividad(supabaseUrl, supabaseAnonKey) {
    if (!global.__aurzaneIdClient) descartarSesionVieja();
    const cliente = crearClienteBase(supabaseUrl, supabaseAnonKey);
    if (document.body) iniciarVigilancia(cliente);
    else document.addEventListener("DOMContentLoaded", () => iniciarVigilancia(cliente));
    return cliente;
  }

  global.crearClienteAurzaneID = crearClienteConInactividad;
  global.__aurzaneIdCookieStorage = cookieStorage; // expuesto por si hace falta depurar
})(window);

/* Paleta de color compartida del ecosistema (también en las páginas de tests). */
;(function () {
  if (window.AurzanePaleta || document.querySelector('script[src*="aurzane-paleta.js"]')) return;
  var s = document.createElement('script');
  s.src = 'https://aurzane.com/aurzane-paleta.js';
  (document.head || document.documentElement).appendChild(s);
})();
