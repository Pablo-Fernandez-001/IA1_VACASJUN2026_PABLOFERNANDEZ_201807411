# Manual Técnico - SmartBot

## Objetivo técnico

Implementar un sistema SmartBot con bot de Telegram, API REST, base de datos, panel administrativo y motor lógico Prolog para respuestas frecuentes y diagnósticos dinámicos.

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.11 | Backend y servicios. |
| FastAPI | API Gateway y Prolog Service. |
| SQLAlchemy | ORM y persistencia. |
| SQLite | Base de datos local persistente. |
| SWI-Prolog | Motor lógico experto. |
| Docker Compose | Orquestación de servicios. |
| HTML/CSS/JS | Panel administrativo. |
| Telegram Bot API | Bot conversacional. |

## Estructura técnica

```text
backend/api_gateway/app
  core/          configuración y seguridad JWT
  db/            sesión, modelos e inicialización
  features/      módulos por funcionalidad
  services/      cliente HTTP hacia Prolog

backend/prolog_service
  app/main.py    genera hechos dinámicos y ejecuta SWI-Prolog
  prolog/expert_engine.pl  reglas de inferencia

backend/telegram_bot
  app/bot.py     polling de Telegram y consumo de API REST
```

## API Gateway

El API Gateway concentra la entrada principal del sistema.

### Módulos

| Módulo | Endpoint base | Responsabilidad |
|---|---|---|
| Auth | `/api/auth` | Login y usuario actual. |
| Categories | `/api/categories` | CRUD de categorías. |
| FAQs | `/api/faqs` | CRUD y búsqueda de preguntas. |
| Diagnostics | `/api/diagnostics` | CRUD de síntomas, diagnósticos, reglas y diagnóstico. |
| Settings | `/api/settings` | Configuración del sistema. |
| Stats | `/api/stats` | Estadísticas y logs. |

## Prolog Service

El servicio Prolog recibe desde API Gateway:

- Síntomas seleccionados.
- Diagnósticos activos.
- Reglas activas.
- Síntomas requeridos por cada regla.

Luego construye un programa temporal Prolog y consulta `expert_engine.pl`.

### Fórmula usada

```text
probabilidad = (síntomas_coincidentes / síntomas_requeridos) * peso_regla * probabilidad_base
```

El resultado se redondea y se clasifica:

| Rango | Nivel |
|---|---|
| 0 - 34 | bajo |
| 35 - 69 | medio |
| 70 - 100 | alto |

## Archivo Prolog

`backend/prolog_service/prolog/expert_engine.pl` contiene reglas generales, no conocimiento estático de un caso específico.

Predicados principales:

| Predicado | Uso |
|---|---|
| `selected/1` | Síntoma seleccionado por el usuario. |
| `diagnosis/6` | Diagnóstico recibido dinámicamente. |
| `rule/5` | Regla diagnóstica recibida dinámicamente. |
| `required_symptom/2` | Relación regla-síntoma. |
| `count_matched/3` | Cuenta coincidencias. |
| `missing_symptoms/2` | Calcula síntomas faltantes. |
| `problem_level/2` | Clasifica el porcentaje. |
| `diagnostic_result/1` | Construye el JSON final. |

## Base de datos

La base guarda conocimiento editable:

- `categories`
- `faqs`
- `symptoms`
- `diagnoses`
- `diagnostic_rules`
- `rule_symptoms`
- `settings`
- `query_logs`
- `admin_users`

## Seguridad

- Login por JWT.
- Contraseña con hash bcrypt.
- Endpoints de escritura protegidos.
- CORS habilitado para facilitar evaluación local.

## Docker Compose

Servicios definidos:

```text
api-gateway
prolog-service
telegram-bot
frontend
smartbot_data volume
```

## Mejores futuras

- Migrar SQLite a PostgreSQL.
- Añadir roles de administrador.
- Integrar WebSocket para estadísticas en tiempo real.
- Importar y exportar reglas Prolog desde archivos `.pl`.
- Agregar pruebas E2E con Playwright.
