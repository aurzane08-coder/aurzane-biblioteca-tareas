# Guía de lenguaje de AURZANE

Español de España con tuteo (tú) en todo el ecosistema. Nunca voseo. Sin rayas largas: comas, puntos o dos puntos.
Lo aplican solos `ai/parches/voseo.py` y `ai/parches/lenguaje.py` (cada día) y el generador de artículos (`ai/manager.py`).

## Botones (verbo + objeto, lo que pasa al pulsar)
| Acción | Texto | Evitar |
|---|---|---|
| Entrar en la cuenta | Iniciar sesión | Ingresar, Entrar, Acceder, Iniciá sesión |
| Salir de la cuenta | Cerrar sesión | Salir, Logout |
| Crear cuenta | Crear cuenta | Registrarse, Regístrate gratis |
| Guardar un elemento | Guardar / Guardado | Guardar ✓, Favorito |
| Lista guardada | Guardados | Mis favoritos, Mi lista |
| Empezar una prueba | Comenzar / Continuar | Iniciar test, Empezá |
| Abrir algo | Ver … (Ver mi informe, Ver el curso) | Click aquí, Más info |
| Descargar | Descargar PDF / Descargar Word | Bajar, Exportar |

## Navegación
Inicio, Evaluaciones, Mi informe, Dónde estudiar, Mi cuenta (OVP). Mundos con su nombre corto de `mundos/identidad.json`.

## Mensajes
- Carga: «Cargando…» (con puntos suspensivos de un carácter).
- Éxito: participio breve y concreto: «Guardado», «Cambios guardados», «Enlace enviado».
- Error: «No se pudo [acción]. [Qué hacer].» Nunca el texto técnico del servidor. Ej.: «No se pudo guardar. Revisa tu conexión e inténtalo de nuevo.»
- Vacío: qué falta + cómo conseguirlo. Ej.: «Todavía no has guardado nada. Pulsa Guardar en cualquier test, libro o curso.»
- Confirmación de algo que no se puede deshacer: pregunta concreta + botón con el verbo: «¿Quitar este curso de tu lista?» [Quitar] [Cancelar].
