# Arquitectura de SmartBot

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

La solución usa arquitectura por capas y módulos por funcionalidad:

| Capa | Responsabilidad |
|---|---|
| Presentación | Panel administrativo y Telegram. |
| API | Endpoints, validación Pydantic y manejo HTTP. |
| Dominio | Autenticación, búsqueda, CRUD y estadísticas. |
| Persistencia | Modelos SQLAlchemy y SQLite. |

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
