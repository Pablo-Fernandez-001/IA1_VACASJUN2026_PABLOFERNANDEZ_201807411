# Arquitectura de SmartBot

La práctica utiliza una **arquitectura orientada a servicios**, para evitar un sistema monolítico.

```mermaid
flowchart LR
    U[Usuario Telegram] --> B[telegram-bot]
    A[Administrador Web] --> F[frontend-web]
    F --> G[api-gateway]
    B --> G
    G --> DB[(SQLite)]
    G --> P[prolog-service]
    P --> PL[expert_engine.pl]
```

## Responsabilidades

| Servicio | Responsabilidad |
|---|---|
| `frontend-web` | Panel administrativo, CRUD y pruebas visuales. |
| `api-gateway` | Autenticación, CRUD, base de datos, logs, estadísticas y orquestación. |
| `prolog-service` | Cálculo lógico de diagnósticos, porcentajes y rutas de solución. |
| `telegram-bot` | Recibir mensajes reales desde Telegram y consumir la API REST. |
| `SQLite` | Persistencia de preguntas, respuestas, categorías, síntomas, reglas, diagnósticos, usuarios, configuración y logs. |

## Flujo de una pregunta FAQ

```mermaid
sequenceDiagram
    participant T as Telegram
    participant B as Bot
    participant G as API Gateway
    participant D as SQLite
    T->>B: Mensaje del usuario
    B->>G: GET /api/faqs/search?q=...
    G->>D: Buscar FAQ activa
    D-->>G: Respuesta o vacío
    G-->>B: JSON con respuesta
    B-->>T: Mensaje automático
```

## Flujo de diagnóstico Prolog

```mermaid
sequenceDiagram
    participant F as Frontend/Bot
    participant G as API Gateway
    participant D as SQLite
    participant P as Prolog Service
    participant E as SWI-Prolog
    F->>G: POST /api/diagnostics/diagnose
    G->>D: Lee síntomas, diagnósticos y reglas
    G->>P: Envía conocimiento dinámico
    P->>E: Ejecuta expert_engine.pl + hechos dinámicos
    E-->>P: Diagnósticos con porcentaje
    P-->>G: JSON ordenado
    G-->>F: Diagnósticos + ruta de solución
```
