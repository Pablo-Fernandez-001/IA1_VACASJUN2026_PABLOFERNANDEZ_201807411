# Hoja de Cumplimiento - SmartBot

| Criterio | Estado | Evidencia |
|---|---|---|
| API REST funcional | Cumple | FastAPI y Swagger en `/docs`. |
| Endpoints organizados | Cumple | Módulos `features/*`. |
| Patrón de arquitectura | Cumple | `docs/ARQUITECTURA.md`. |
| Manejo de errores | Cumple | 401, 404, 409 y 422 controlados. |
| Base de datos conectada | Cumple | SQLite persistente en volumen. |
| Modelo correcto | Cumple | ER con categorías, preguntas y respuestas separadas. |
| Persistencia real | Cumple | SQLAlchemy y `seed.sql`; sin FAQ JSON/código. |
| Login funcional | Cumple | JWT y usuario exigido. |
| CRUD preguntas | Cumple | `/api/questions` y panel. |
| CRUD respuestas | Cumple | `/api/answers` y panel. |
| CRUD categorías | Cumple | `/api/categories` y panel. |
| Configuración chat ID | Cumple | `settings.telegram_chat_id`. |
| Bot recibe mensajes | Cumple | Polling `getUpdates`. |
| Bot consulta API | Cumple | `GET /api/search`. |
| Respuesta desde BD | Cumple | JOIN lógico Question/Answer en SQLite. |
| Consulta desconocida | Cumple | `unknown_message` configurable. |
| Docker Compose | Cumple | API, bot, frontend y volumen. |
| Manuales y diagramas | Cumple | Carpeta `docs`. |
| 20 FAQ / 3 categorías | Cumple | 20 preguntas, 20 respuestas y 4 categorías. |
| Registro de consultas | Cumple | Tabla `query_logs`. |
| Estadísticas | Cumple | Usuarios, frecuencia y categorías. |

## Penalizaciones Evitadas

- Backend exclusivamente Python.
- Base SQL real y persistente.
- Ninguna pregunta o respuesta almacenada en JSON o código Python/JavaScript.
- API, panel, autenticación, bot y Docker Compose presentes.
- Token, JWT y rutas configurables por variables de entorno.

## Condiciones Externas

El estudiante todavía debe verificar acceso al repositorio para el auxiliar, entrega en UEDI, puntualidad y un historial real de al menos cinco commits progresivos.
