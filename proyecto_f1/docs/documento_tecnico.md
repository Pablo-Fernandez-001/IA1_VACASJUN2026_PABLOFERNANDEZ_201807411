# Documento técnico - Doctor Byte

## 1. Descripción general

Doctor Byte es un sistema experto para diagnóstico preliminar de fallas en computadoras. El usuario selecciona síntomas desde una interfaz web y el sistema consulta una base de conocimiento en Prolog para generar diagnósticos con recomendaciones.

## 2. Arquitectura no monolítica

Se implementó una arquitectura orientada a servicios:

| Servicio | Tecnología | Responsabilidad |
|---|---|---|
| frontend-web | React + Vite | Interfaz dinámica para usuario |
| api-gateway | FastAPI | Orquestación, historial, validaciones |
| prolog-service | FastAPI + SWI-Prolog | Motor de inferencia experto |
| telegram-service | FastAPI + Telegram Bot API | Notificaciones externas |
| SQLite | SQLAlchemy | Persistencia de historial |

## 3. Motor experto

La base de conocimiento está en `backend/prolog_service/knowledge_base/doctor_byte.pl`.

Contiene:

- 25 síntomas.
- 14 fallas diagnosticables.
- Recomendaciones por falla.
- Hechos `sintoma/4`, `falla/6`, `recomendacion/2`.
- Reglas de inferencia para coincidencias, severidad y ordenamiento.
- Uso de variables, listas y corte `!`.

## 4. Flujo de diagnóstico

1. El frontend solicita catálogo de síntomas.
2. El usuario selecciona síntomas.
3. El frontend envía la solicitud al API Gateway.
4. El API Gateway llama al Prolog Service.
5. Prolog calcula diagnósticos con puntaje de confianza.
6. El API Gateway guarda historial en SQLite.
7. Opcionalmente se notifica por Telegram.
8. La interfaz muestra resultado principal, recomendaciones e historial.

## 5. Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/health` | Estado general |
| GET | `/api/symptoms` | Catálogo dinámico de síntomas |
| POST | `/api/diagnose` | Ejecuta diagnóstico |
| GET | `/api/history` | Lista historial |
| DELETE | `/api/history/{id}` | Elimina diagnóstico |

## 6. Seguridad y robustez

- Validación de payloads con Pydantic.
- Timeouts al ejecutar Prolog.
- Separación de responsabilidades por servicio.
- CORS configurable.
- Variables de entorno para Telegram.
- Historial persistente.
- Tests unitarios base.
