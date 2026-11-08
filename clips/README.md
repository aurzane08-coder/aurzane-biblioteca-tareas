# Fábrica de clips (Clips-All)

Canal de YouTube **Clips-All** (@Clips-All-g1n) y una cuenta de TikTok aparte, separados de AURZANE.

## Regla de oro
Solo se recortan vídeos **autorizados**: de campañas de clipping (Clipeamos, Whop, Vyro…) o de creadores que lo permiten por escrito.
Subir clips de otros sin permiso trae reclamaciones de copyright y el cierre del canal.

## Cómo añadir un vídeo
En `clips/fuentes.json`, una entrada por vídeo de la campaña:

```json
{"url": "https://enlace-del-video-de-la-campaña", "titulo": "Nombre del vídeo", "creador": "Nombre del creador",
 "campana": "Clipeamos: nombre de la campaña", "reglas": "lo que pida la campaña (hashtags, mención…)",
 "original": "https://enlace al canal del creador", "max_clips": 5, "autorizado": true}
```

## Secretos de GitHub
- `CLIPS_YT_REFRESH_TOKEN`: permiso del canal Clips-All (OAuth Playground, permiso `youtube.upload`, eligiendo el canal Clips-All).
- Opcional `CLIPS_YT_CLIENT_ID` y `CLIPS_YT_CLIENT_SECRET`: un proyecto de Google Cloud propio para los clips, así tiene su propio cupo (unas 6 subidas al día) y no le quita a AURZANE.
- Opcional `CLIPS_TIKTOK_REFRESH_TOKEN`: la cuenta de TikTok de clips conectada a la app.

El registro de lo publicado (para declarar las vistas en cada campaña) queda en `clips/hechos.json`.
