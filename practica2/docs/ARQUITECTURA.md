# Arquitectura de SmartBot

> La explicación completa de cada servicio, módulo, función y decisión está en el [Manual Técnico](MANUAL_TECNICO.md).

```mermaid
flowchart LR
    U[Usuario Telegram] --> T[telegram-bot Python]
    A[Administrador] --> F[Panel HTML CSS JS]
    T -->|HTTP REST| API[FastAPI API Gateway]
    F -->|HTTP REST + JWT| API
    API --> AUTH[Auth y seguridad]
    API --> FAQ[Preguntas, respuestas y búsqueda]
    API --> STATS[Logs y estadísticas]
    AUTH --> DB[(SQLite)]
    FAQ --> DB
    STATS --> DB
```

## Patrón

La solución usa una arquitectura por funcionalidades con capas internas. Cada capacidad del negocio tiene un router independiente en `app/features`:

- `auth`: autenticación y sesión.
- `categories`: clasificación de FAQ.
- `questions`: intenciones consultables.
- `answers`: respuestas priorizadas.
- `search`: normalización, puntuación y registro.
- `settings`: configuración y prueba Telegram.
- `stats`: agregaciones e historial.

Las capas internas son:

| Capa | Responsabilidad |
|---|---|
| Presentación | Panel administrativo y Telegram. |
| API | Endpoints, validación Pydantic y manejo HTTP. |
| Dominio | Autenticación, búsqueda, CRUD y estadísticas. |
| Persistencia | Modelos SQLAlchemy y SQLite. |

Se eligió este patrón para mantener separadas la presentación, la seguridad, cada funcionalidad y el almacenamiento. Web y Telegram comparten la misma API y la misma base de datos, evitando duplicar respuestas dentro del bot.

## Flujo de consulta

```mermaid
sequenceDiagram
    participant U as Usuario
    participant B as Bot Telegram
    participant A as API REST
    participant D as SQLite
    U->>B: Pregunta libre
    B->>A: GET /api/search?q=...
    A->>D: Busca preguntas y respuestas activas
    D-->>A: Coincidencia y respuesta
    A->>D: Registra usuario, consulta, respuesta y fecha
    A-->>B: Respuesta JSON
    B-->>U: Mensaje automático
```
