# Cumplimiento de Hoja de Calificación

Este documento resume cómo la práctica cubre cada punto de la hoja de calificación de la Práctica 1.

## Ponderación

| Descripción de ponderación | Valor | Estado | Evidencia dentro del proyecto |
|---|---:|---|---|
| Uso correcto de hechos y reglas | 5 | Cumplido | `prolog/rutas.pl` define hechos `conexion/3` y reglas como `camino/3`, `ruta/4`, `viajar/5`, `rutas_posibles/3` y `ruta_mas_corta/4`. |
| Base de conocimiento en Prolog mínimo 10 ciudades y conexiones correctamente definidas | 10 | Cumplido | `prolog/rutas.pl` contiene más de 10 ciudades y conexiones con distancias. Se puede comprobar con `npm run verificar:rubrica`. |
| Representación de distancias mediante hechos Prolog | 5 | Cumplido | Cada conexión usa `conexion(Origen, Destino, Distancia)`, por ejemplo `conexion(guatemala, antigua, 45)`. |
| Búsqueda de rutas entre ciudades | 10 | Cumplido | Predicado `ruta/4`, endpoint `GET /rutas/todas` y botón `Ver todas las rutas` en el frontend. |
| Prevención de ciclos o ciudades repetidas | 10 | Cumplido | `viajar/5` mantiene la lista `Visitados` y valida `\+ member(Intermedio, Visitados)`. |
| Cálculo correcto de distancia total de una ruta | 10 | Cumplido | Prolog calcula `DistanciaTotal is Distancia1 + Distancia2`. La ruta Guatemala a Quetzaltenango da `230 km`. |
| Determinación automática de la ruta más corta | 20 | Cumplido | `ruta_mas_corta/4` usa rutas ordenadas por distancia y selecciona la primera. |
| Frontend funcional para consultas y visualización de resultados | 10 | Cumplido | `frontend/index.html`, `frontend/style.css` y `frontend/app.js`; evidencias en `evidencias/cypress/screenshots/frontend.cy.js`. |
| Funcionalidad para agregar ciudades y conexiones | 5 | Cumplido | `POST /conexiones/`, formulario `Agregar conexión` y predicado `agregar_conexion/3`. Si una ciudad no existe, queda disponible al crear una conexión. |
| Mostrar todas las rutas posibles ordenadas o con sus distancias | 5 | Cumplido | `rutas_posibles/3` usa `sort/2`; el frontend muestra rutas con distancia total. |
| Manual de usuario `.md` | 5 | Cumplido | `docs/MANUAL_USUARIO.md`. |
| Manual técnico `.md` | 5 | Cumplido | `docs/MANUAL_TECNICO.md`. |
| Total | 100 | Cubierto localmente | Validar además los puntos externos de entrega antes de subir. |

## Penalizaciones

| Penalización | Riesgo | Acción necesaria |
|---|---|---|
| No entregar en UEDI | Externo al código | Subir el proyecto en UEDI antes de la fecha/hora indicada. |
| No usar Prolog | Sin riesgo local | El motor lógico está en `prolog/rutas.pl` y se consulta desde Python mediante PySwip. |
| No usar Python | Sin riesgo local | El backend está en `backend/app` con FastAPI. |
| Llegar tarde a la calificación | Externo al código | Presentarse a tiempo a la revisión. |
| No existe frontend | Sin riesgo local | El frontend está en `frontend/`. |
| No tener al auxiliar en el repo | Externo al código | Agregar al auxiliar como colaborador del repositorio remoto o confirmar el mecanismo solicitado por el curso. |
| No usar patrón de arquitectura | Sin riesgo local | Backend organizado por funcionalidades y capas: `router`, `service`, `schemas`, `prolog_engine` y `core`. |

## Comandos de verificación

Desde la carpeta `practica1`:

~~~bash
npm run verificar:rubrica
npm run evidencias
~~~

`verificar:rubrica` consulta SWI-Prolog directamente.  
`evidencias` levanta backend y frontend reales, ejecuta Cypress y genera capturas.

## Evidencias rápidas

- Backend ejecutándose: `evidencias/cypress/screenshots/backend.cy.js/backend-servidor-ejecutandose.png`
- Documentación FastAPI: `evidencias/cypress/screenshots/backend.cy.js/backend-swagger-docs.png`
- Frontend conectado: `evidencias/cypress/screenshots/frontend.cy.js/frontend-live-server-conectado.png`
- Ruta más corta: `evidencias/cypress/screenshots/frontend.cy.js/frontend-ruta-mas-corta-real.png`
