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

  global.crearClienteAurzaneID = crearClienteAurzaneID;
  global.__aurzaneIdCookieStorage = cookieStorage; // expuesto por si hace falta depurar
})(window);
