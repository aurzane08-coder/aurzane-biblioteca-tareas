# Marketing automático de AURZANE

Presupuesto: 0 €. Todo corre en GitHub Actions (`.github/workflows/marketing.yml`).

## Qué hace solo, cada día

| Hora (UTC) | Qué |
|---|---|
| 05:13 | Actualiza el catálogo: productos fijos, más de 700 libros abiertos, notas de corte y **cualquier página nueva del sitemap** (entra sola y sale primero). Planifica 14 días, crea las tarjetas 1080x1350 y las sube a `aurzane.com/marketing/img/`. Suma los clics. |
| 08:37 | Franja de mañana: tests, calculadoras y cursos. |
| 17:41 | Franja de tarde: rota entre libros, creatividades, notas de corte y secciones. |

- Cada red recibe un producto **distinto** en cada franja, y recorre todo el catálogo antes de repetir.
- Los textos cambian según la red (largo, gancho, hashtags) y los tests llevan siempre el aviso de que no son un diagnóstico.
- Solo se publica en **cuentas propias**. Nunca en grupos, foros ni comunidades de terceros: eso se hace a mano siguiendo `comunidades` (ver el tracker).
- Enlaces cortos `aurzane.com/ir/xxxxxx`: cuentan los clics de personas (sin bots ni datos personales) y llevan `utm_source` a la página.
- Resultado en `marketing/INFORME.md` (publicaciones y clics por red y por producto), `registro.csv` y `clics.csv`.
- Pinterest se alimenta del feed `https://aurzane.com/marketing/feed.xml` (una pieza al día).

## Activar cada red (una sola vez)

Crea la cuenta tú y añade los secretos en GitHub: repositorio `aurzane-biblioteca-tareas` > Settings > Secrets and variables > Actions > New repository secret. La red empieza a publicar en la siguiente franja.

| Red | Secretos | Cómo conseguirlos |
|---|---|---|
| Telegram | `TELEGRAM_TOKEN`, `TELEGRAM_CANAL` | Crea un canal público. Habla con @BotFather, `/newbot`, copia el token. Añade el bot como administrador del canal. Canal = `@nombre_del_canal`. |
| Bluesky | `BSKY_USUARIO`, `BSKY_CLAVE_APP` | Usuario = `aurzane.bsky.social` (o el tuyo). Settings > Privacy and security > App passwords > Add. |
| Mastodon | `MASTODON_SERVIDOR`, `MASTODON_TOKEN` | Servidor, p. ej. `mastodon.social`. Preferencias > Desarrollo > Nueva aplicación con permisos `write:statuses` y `write:media`. Copia el token de acceso. |
| Facebook | `FB_PAGINA_ID`, `FB_PAGINA_TOKEN` | Página de Facebook. En developers.facebook.com crea una app, en Graph API Explorer pide `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`, cambia a token largo y saca el token de la página (no caduca). |
| Instagram | `IG_USUARIO_ID` (+ `FB_PAGINA_TOKEN`) | Cuenta profesional de Instagram vinculada a la página. El ID sale en Graph API Explorer: `me/accounts?fields=instagram_business_account`. |
| Threads | `THREADS_TOKEN` | App de Meta con el caso de uso Threads API, permisos `threads_basic` y `threads_content_publish`. El token largo dura 60 días: hay que renovarlo. |
| X | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET` | developer.x.com, plan gratuito, app con permisos Read and write. Solo texto con enlace (la tarjeta sale de la página). |
| Pinterest | ninguno | Cuenta de empresa > Ajustes > Publicación masiva > Conectar RSS: `https://aurzane.com/marketing/feed.xml`. |

## Fotos de las tarjetas

Con el secreto `PEXELS_API_KEY` (gratis en pexels.com/api), cada tarjeta usa una foto de [Pexels](https://www.pexels.com) elegida por el tema del producto, con la publicidad compuesta encima y el crédito del fotógrafo. La licencia de Pexels permite el uso comercial gratis. La foto elegida para cada producto queda en `fotos.json`; para cambiarla, borra su línea y se busca otra. Pinterest no se usa como fuente de imágenes: sus imágenes son de sus autores.

## Añadir o cambiar productos

- Productos fijos y textos: `marketing/fijos.py`.
- Creatividades propias: deja la imagen en `marketing/img/` y añádela en la lista `C` de `fijos.py`.
- Páginas nuevas de la web: no hay que hacer nada si están en `aurzane.com/sitemap.xml`.
