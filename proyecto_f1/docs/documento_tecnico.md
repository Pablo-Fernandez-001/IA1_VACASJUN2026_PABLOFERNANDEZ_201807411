# Documento tecnico - Doctor Byte

## 1. Descripcion general

Doctor Byte es un sistema experto para diagnostico preliminar de fallas en computadoras. El usuario selecciona sintomas desde una interfaz web y el sistema consulta una base de conocimiento en Prolog para generar varios diagnosticos posibles, cada uno con probabilidad, porcentaje del problema, efectividad estimada, recomendaciones y ruta de solucion.

## 2. Arquitectura no monolitica

Se implemento una arquitectura orientada a servicios:

| Servicio | Tecnologia | Responsabilidad |
|---|---|---|
| frontend-web | React + Vite | Interfaz dinamica para usuario, resultados e interfaz CRUD |
| api-gateway | FastAPI | Orquestacion, historial, proxy CRUD y Telegram |
| prolog-service | FastAPI + SWI-Prolog | Motor de inferencia experto y administracion de conocimiento |
| telegram-service | FastAPI + Telegram Bot API | Notificaciones externas |
| SQLite | SQLAlchemy | Persistencia de historial |

## 3. Motor experto editable

La logica declarativa esta en `backend/prolog_service/knowledge_base/doctor_byte.pl`.

Los datos editables estan en `backend/prolog_service/knowledge_base/doctor_byte_data.json`.

Contiene:

- 25 sintomas iniciales.
- 14 reglas diagnosticas iniciales.
- Mensaje, categoria, severidad y estado habilitado por regla.
- Sintomas requeridos y sintomas de apoyo por regla.
- Recomendaciones y pasos de solucion por regla.
- Reglas de inferencia en Prolog para coincidencias, faltantes, porcentajes, severidad y ordenamiento.
- Uso de variables, listas, predicados auxiliares, comparadores y corte `!`.

La practica queda editable porque el CRUD modifica los sintomas y las reglas diagnosticas que Prolog consume. Si se agrega un nuevo sintoma y una nueva regla, el siguiente diagnostico ya puede usar esa nueva logica.

## 4. Flujo de diagnostico

1. El frontend solicita catalogo de sintomas y reglas al API Gateway.
2. El usuario selecciona sintomas.
3. El frontend envia la solicitud al API Gateway.
4. El API Gateway llama al Prolog Service.
5. Prolog carga `doctor_byte_data.json`.
6. Prolog calcula todos los diagnosticos posibles y los ordena por probabilidad.
7. El API Gateway guarda historial en SQLite.
8. Opcionalmente se notifica por Telegram.
9. La interfaz muestra diagnostico principal, alternativas, porcentajes, recomendaciones, ruta de solucion e historial.

## 5. Calculo de diagnostico

Cada regla define:

- `required_symptoms`: sintomas principales.
- `support_symptoms`: sintomas secundarios.
- `min_score`: umbral configurable.
- `severity`: baja, media, alta o critica.
- `solution_steps`: ruta de solucion mostrada al usuario.

Prolog calcula:

- `probability`: probabilidad de que el diagnostico aplique.
- `problem_percentage`: nivel estimado del problema.
- `effectiveness_probability`: probabilidad de efectividad de la ruta sugerida.
- `matched_symptoms`: cantidad de sintomas que coinciden.
- `missing_required_symptoms`: sintomas requeridos que faltan.
- `passes_threshold`: indica si supera el umbral de la regla.

## 6. Endpoints principales

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/api/health` | Estado general |
| GET | `/api/knowledge` | Base editable completa |
| GET | `/api/symptoms` | Catalogo dinamico de sintomas |
| POST | `/api/symptoms` | Crea sintoma |
| PUT | `/api/symptoms/{id}` | Edita sintoma |
| DELETE | `/api/symptoms/{id}` | Elimina sintoma |
| GET | `/api/diagnosis-rules` | Lista reglas diagnosticas |
| POST | `/api/diagnosis-rules` | Crea regla diagnostica |
| PUT | `/api/diagnosis-rules/{id}` | Edita regla diagnostica |
| DELETE | `/api/diagnosis-rules/{id}` | Elimina regla diagnostica |
| POST | `/api/diagnose` | Ejecuta diagnostico |
| GET | `/api/history` | Lista historial |
| DELETE | `/api/history/{id}` | Elimina diagnostico |

## 7. Docker

`docker-compose.yml` levanta todos los servicios. La base editable `doctor_byte_data.json` queda montada como volumen de archivo para que los cambios CRUD persistan en el proyecto.

URLs por defecto:

- Frontend: `http://localhost:8081`
- Swagger API: `http://localhost:8000/docs`
- API health: `http://localhost:8000/api/health`
- Prolog health: `http://localhost:8001/health`
- Telegram health: `http://localhost:8002/health`

## 8. Seguridad y robustez

- Validacion de payloads con Pydantic.
- Timeouts al ejecutar Prolog.
- Separacion de responsabilidades por servicio.
- CORS configurable.
- Variables de entorno para Telegram.
- Historial persistente.
- Base de conocimiento editable y persistente.
- Tests unitarios base y build de frontend.
