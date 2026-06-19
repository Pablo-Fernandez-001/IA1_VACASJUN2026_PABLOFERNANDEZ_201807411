# Documento Técnico - Doctor Byte

> La explicación completa de arquitectura, tecnologías, flujos y cada archivo del proyecto está en el [Manual Técnico](manual_tecnico.md).

## Objetivo

Diagnosticar fallas de computadoras mediante reglas declarativas reales en SWI-Prolog e integrar el resultado con Python, web y Telegram.

## Servicios

| Servicio | Tecnología | Responsabilidad |
|---|---|---|
| frontend | React, Vite, Nginx | Consulta, historial y administración. |
| api-gateway | FastAPI, SQLAlchemy | Orquestación, validación, historial y configuración. |
| prolog-service | FastAPI, SWI-Prolog | CRUD del conocimiento e inferencia. |
| telegram-service | FastAPI, Telegram API | Recepción, procesamiento y envío de mensajes. |
| SQLite | SQL | Solo historial y configuración auxiliar. |

## Base de conocimiento

`doctor_byte_knowledge.pl` contiene los hechos editables:

```prolog
symptom(Id, Nombre, Categoria, Peso).
failure(Id, Nombre, Categoria, Severidad, Mensaje).
recommendation(Id, FailureId, Texto, Orden).
solution_step(FailureId, Orden, Texto).
diagnosis_rule(Id, FailureId, Requeridos, Apoyo, MinScore, Activa).
```

`doctor_byte.pl` contiene las reglas generales de inferencia, puntuación, listas, recursión, ordenamiento, validación de referencias y persistencia. Los cortes aparecen en `severidad_peso/2`, `bool_value/2`, `peso_sintoma/2`, reemplazo de listas y `diagnosticar/2`.

## Inferencia

1. Python envía IDs de síntomas al proceso SWI-Prolog.
2. Prolog consulta hechos y reglas del archivo `.pl`.
3. Los síntomas requeridos pesan el doble que los de apoyo.
4. Se calcula coincidencia, faltantes, probabilidad y efectividad.
5. `predsort/3` devuelve todas las fallas ordenadas.
6. Python guarda una copia del resultado en el historial SQLite.

No existe diagnóstico simulado en Python y SQLite no contiene síntomas, fallas, recomendaciones ni reglas.

## CRUD Prolog

Los endpoints `/symptoms`, `/failures`, `/recommendations` y `/diagnosis-rules` invocan modos del programa Prolog. Este usa `assertz/1`, `retractall/1`, valida asociaciones y reescribe atómicamente `doctor_byte_knowledge.pl` mediante un archivo temporal.

## SQLite auxiliar

| Tabla | Justificación |
|---|---|
| `diagnosis_history` | Historial solicitado por la interfaz. |
| `system_config` | Chat ID, estado y mensajes configurables. |

## Variables de entorno

`DATABASE_URL`, `PROLOG_SERVICE_URL`, `TELEGRAM_SERVICE_URL`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_DEFAULT_CHAT_ID`, `API_GATEWAY_URL` y `CORS_ORIGINS`.

## Docker

`docker-compose.yml` levanta cuatro servicios, healthchecks, red privada, volumen SQLite y montaje persistente del conocimiento Prolog.
