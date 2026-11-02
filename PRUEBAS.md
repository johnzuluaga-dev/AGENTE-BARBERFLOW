# Pruebas, hallazgos y métricas de BarberFlow

Pruebas hechas el **2 de noviembre de 2026** sobre la app desplegada en
Render (https://agente-barberflow-1.onrender.com), usando Google Chrome.
Las capturas están en la carpeta [`evidencias/`](evidencias/).

Cómo se midió: cada respuesta del agente registra sus métricas con un
*callback* de LangChain (`core/metricas.py`). Se ven en la barra lateral
(sección **Métricas** e **Historial de la sesión**) y en los logs de Render
(líneas que empiezan por `METRICAS`).

---

## 1. Resumen

| Componente | ¿Funciona? | Prueba donde se comprobó |
|---|---|---|
| Interfaz (diseño, "pensando…", historial, errores) | Sí | P01 a P07, indicador de carga |
| LangChain (modelos, tools, chains, respaldo, callbacks) | Sí | P02, P03, H3 |
| LangGraph (enrutador, nodos, ciclo agente ⇄ herramientas) | Sí | P01, P02, P03 |
| Estado (`BarberState`: nombre, ruta, tools, nodos) | Sí | P02, R03 |
| Memoria (`MemorySaver` por `thread_id`) | Sí | P06, R04 |
| RAG (documento de la barbería; búsqueda con embeddings y respaldo por palabras) | Sí | P04, rag de pagos |
| Tools (7 herramientas) | Sí | P02, P03, P05, P06, R02 |
| Métricas y observabilidad | Sí | Todas |
| Despliegue en Render | Sí | Todas |

Se encontraron **8 hallazgos**; todos se corrigieron y se volvieron a probar
(ver sección 4).

---

## 2. Pruebas funcionales (primera ronda)

| # | Qué se probó | Mensaje enviado | Resultado esperado | Resultado obtenido | ¿Pasó? |
|---|---|---|---|---|---|
| P01 | LangGraph: ruta de saludo | "hola" | Ruta `conceptual` sin tools; el saludo no pasa por el modelo enrutador | Ruta `conceptual`, nodos `enrutador → nodo_conceptual`, 0 tools | Sí |
| P02 | Tool de servicios + estado del cliente | "Soy Simon. ¿Qué servicios tienen y cuánto cuestan?" | Lista real de servicios y precios; nombre "Simon" en el estado | Usó `consultar_servicios`, mostró los 5 servicios con precio; "Nombre: Simon" en la barra lateral | Sí |
| P03 | Tools de fecha y disponibilidad (ciclo agente ⇄ herramientas) | "¿Qué horarios tienen libres mañana para un corte clásico?" | Consultar fecha y disponibilidad real | Usó `obtener_fecha` y `consultar_disponibilidad` (2 vueltas del ciclo) y respondió el rango libre del martes 3 de noviembre | Sí |
| P04 | RAG | "Si después necesito cancelar, ¿con cuánta anticipación debo avisar?" | Respuesta sacada del documento de la barbería | Usó `consultar_informacion_barberia`: "avisar con al menos 2 horas de anticipación, por WhatsApp o llamada" (igual que `data/conocimiento/barberia.md`) | Sí |
| P05 | Tool de agendar | "Quiero el corte clásico mañana a las 10:00" | Mostrar resumen y pedir confirmación antes de agendar | **Agendó de inmediato sin pedir confirmación** | No → H5 |
| P06 | Memoria y tool de citas | "¿Cómo me llamo y qué cita tengo agendada?" | Recordar el nombre y la cita | Respondió "Te llamas Simon" y la cita del 3 de noviembre a las 10:00. Pero la barra lateral cambió el nombre a **"Y"** | Parcial → H6 |
| P06b | Tool de fecha | "¿Qué hora es en este momento?" | Hora de Colombia (00:49) | Respondió **05:49** (hora UTC del servidor) | No → H7 |
| P07 | Panel del barbero | Abrir "Panel Barbero" | Ver la cita nueva | Aparece la cita de Simon (2026-11-03 10:00). Pero Chrome **tradujo** la página ("solo lectura" → "lectura en solitario") | Parcial → H8 |

Evidencias: `p01_saludo.jpg` a `p07_panel_traducido.jpg`, `rag_formas_de_pago.jpg`.

---

## 3. Métricas registradas

### 3.1 Primera ronda (con el modelo principal en pausa, respondiendo `gemini-3.5-flash-lite`)

| Prueba | Tiempo (s) | Llamadas al modelo | Tokens (entrada / salida) | Tools usadas | Errores |
|---|---|---|---|---|---|
| P01 saludo | 20.93 | 2 | 108 (90 / 18) | ninguna | 1 (504 del modelo principal → respondió el respaldo) |
| P02 servicios | 5.21 | 3 | 2 796 (2 616 / 180) | consultar_servicios | 0 |
| P03 disponibilidad | 8.08 | 4 | 6 176 (5 990 / 186) | obtener_fecha, consultar_informacion_barberia, consultar_disponibilidad | 0 |
| P04 RAG cancelación | 5.61 | 3 | 5 559 (5 417 / 142) | consultar_informacion_barberia | 0 |
| P05 agendar | 5.15 | 3 | 6 431 (6 244 / 187) | agendar_cita | 0 |
| P06 memoria | 5.93 | 3 | 6 956 (6 829 / 127) | consultar_citas | 0 |
| P06b hora | 5.19 | 3 | 7 271 (7 194 / 77) | obtener_fecha | 0 |

**Promedio de P02 a P06b: 5,9 s por respuesta.**

### 3.2 Antes de los arreglos de velocidad

| Situación | Tiempo (s) | Llamadas | Errores | Evidencia |
|---|---|---|---|---|
| Modelo viejo `gemini-2.5-flash` | — (error inmediato) | 1 | 404 NOT_FOUND | `h1_antes_modelo_404.jpg` |
| Modelo saturado, sin límite de espera | más de 120 sin respuesta | — | — | `h2_antes_cargando_sin_respuesta.jpg` |
| Con límite de espera, sin respaldo | 4.64 (muestra el error) | 1 | 503 UNAVAILABLE | `h2_despues_error_en_segundos.jpg` |
| Con respaldo, espera de 40 s | 41.71 | 2 | 1 (504) | `h3_respaldo_saludo_41s.jpg` |
| Pregunta RAG con respaldo, sin pausa del principal | 80.94 | 5 | 2 (504 y 429) | `h4_antes_81s_modelo_sin_cupo.jpg` |

### 3.3 Segunda ronda (después de los arreglos)

| Prueba | Tiempo (s) | Llamadas | Tokens | Tools | Errores |
|---|---|---|---|---|---|
| R01 pedir cita completa | 8.76 | 5 | 4 568 | obtener_fecha, consultar_servicios, consultar_disponibilidad | 1 (429: el principal queda en pausa) |
| R02 "Sí, confirmo" | 5.26 | 3 | 4 225 | agendar_cita | 0 |
| R03 nombre y hora | 6.25 | 2 | 1 478 | ninguna | 0 |
| R04 después de reiniciar | 8.79 | 2 | — | ninguna | 0 |

**Mejora medida:** una pregunta que usa tools pasó de **80,9 s** (antes de la
pausa del modelo principal) a **5–8 s**.

---

## 4. Hallazgos y acciones correctivas

| # | Hallazgo (qué pasaba) | Causa | Acción correctiva | Resultado al repetir la prueba |
|---|---|---|---|---|
| H1 | El chat respondía "Error calling model 'gemini-2.5-flash' (NOT_FOUND)". | Google retiró ese modelo para usuarios nuevos. | Se cambió `GEMINI_MODEL` a `gemini-3.8-flash` en Render. | El error 404 desapareció. |
| H2 | La app se quedaba "cargando" más de 2 minutos sin responder ni mostrar error, y no había ninguna señal de que estuviera trabajando. | La librería no tenía límite de tiempo y hacía hasta 6 intentos por llamada. | Se agregó el aviso **"Pensando tu respuesta…"** y un límite de espera por llamada (`TIEMPO_ESPERA_MODELO`) con 1 solo intento (`REINTENTOS_MODELO`). | Ahora el usuario ve el aviso y, si el modelo falla, el error aparece en segundos (4,6 s). |
| H3 | `gemini-3.8-flash` devolvía 503 ("high demand") y 504; el agente no podía responder. | Modelo saturado en Google. | **Modelo de respaldo** con `with_fallbacks` de LangChain (`GEMINI_MODEL_RESPALDO = gemini-3.5-flash-lite`). Las métricas muestran qué modelo respondió. Se bajó la espera de 40 s a 20 s. | El agente responde con el respaldo (de 41,7 s se pasó a 20,9 s en el peor caso). |
| H4 | Una pregunta con tools tardaba 81 s. | La clave no tenía cupo para `gemini-3.8-flash` (429 RESOURCE_EXHAUSTED) y cada paso esperaba primero al modelo que fallaba. | Si el modelo principal falla, queda **en pausa 10 minutos** (`PAUSA_MODELO_PRINCIPAL`) y todo va directo al respaldo. | 5–8 s por respuesta (sección 3.3). |
| H5 | El agente agendó una cita sin pedir confirmación (P05). | La regla del prompt no era lo bastante clara para el modelo. | Se reescribió la regla en 3 pasos: consultar disponibilidad → mostrar resumen y preguntar "¿Confirmas la cita?" → agendar solo si el cliente confirma. | R01: mostró el resumen y preguntó "¿Confirmas la cita?". R02: con "Sí, confirmo" la agendó. |
| H6 | Al preguntar "¿Cómo me llamo y…?", el nombre del cliente cambió a **"Y"**. | La regla que detecta el nombre tomaba "me llamo y" como si el cliente se presentara. | Se ignoran las preguntas ("¿cómo me llamo?") y las palabras que no son nombres (y, el, la, de…). | R03: el nombre siguió siendo "Simon". |
| H7 | El agente decía que eran las 05:49 cuando en Colombia eran las 00:49. | El servidor de Render trabaja en hora UTC. | Toda la app usa la zona horaria de Colombia (`ZONA_HORARIA = America/Bogota`): tool de fecha, validación de citas, panel y métricas. | R03: respondió 01:06, la hora real de Colombia. |
| H8 | Chrome traducía la página: "solo lectura" → "lectura en solitario", "Simon" → "Simón", "app" → "aplicación". | Streamlit marca la página como inglés (`<html lang="en">`). | La página se marca en español desde el inicio (`lang="es"`, `translate="no"` y la etiqueta `notranslate` de Google). | Ver R05. |

---

## 5. Segunda ronda: repetición de las pruebas que fallaron

| # | Qué se probó | Mensaje | Esperado | Obtenido | ¿Pasó? |
|---|---|---|---|---|---|
| R01 | H5: pedir confirmación | "Soy Simon. Quiero un afeitado tradicional mañana a las 11:00" | Resumen + "¿Confirmas la cita?" sin agendar | Mostró servicio, fecha, hora y precio, y preguntó "¿Confirmas la cita?" | Sí |
| R02 | H5: agendar tras confirmar | "Sí, confirmo" | Agendar la cita | Usó `agendar_cita`: "Tu cita para el Afeitado tradicional ha quedado confirmada…" | Sí |
| R03 | H6 y H7: nombre y hora | "¿Cómo me llamo y qué hora es en este momento?" | Nombre sigue "Simon"; hora de Colombia | "Te llamas Simon… son las 01:06"; barra lateral: "Nombre: Simon" | Sí |
| R04 | Memoria al reiniciar | Botón "Reiniciar conversación" y luego "¿Recuerdas cómo me llamo?" | Conversación nueva: no recuerda el nombre | Thread ID nuevo, "Nombre: No registrado", el agente no recuerda el nombre | Sí |
| R05 | H8: página sin traducir | Abrir el Panel del barbero en Chrome | Textos originales en español | El servidor envía `<html lang="es" translate="no">`; Chrome ya no traduce: se lee "app" y "Consulta de solo lectura… hazlo manualmente" | Sí |

Evidencias: `r01_pide_confirmacion.jpg` a `r05_pagina_sin_traducir.jpg`.

---

## 6. Limitaciones conocidas

- En el plan gratis de Render la app se apaga si nadie la usa; la primera
  visita puede tardar cerca de un minuto.
- La memoria (`MemorySaver`) y las citas nuevas se guardan en el servidor, así
  que se borran cuando Render reinicia o vuelve a desplegar la app.
- El arreglo del idioma (H8) se aplica cuando la app arranca; justo después
  de un nuevo despliegue, la primera visita todavía puede salir traducida.
- La clave de Gemini usada no tiene cupo para `gemini-3.8-flash`; por eso, en
  estas pruebas, casi todas las respuestas las dio el modelo de respaldo
  `gemini-3.5-flash-lite`.
