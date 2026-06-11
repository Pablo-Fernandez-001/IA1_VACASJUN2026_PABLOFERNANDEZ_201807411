# Explicación parte por parte del código

## 1. `docker-compose.yml`

Define cuatro servicios:

- `api-gateway`: API principal.
- `prolog-service`: servicio lógico con SWI-Prolog.
- `telegram-bot`: bot de Telegram.
- `frontend`: panel administrativo con Nginx.

También crea el volumen `smartbot_data` para conservar la base de datos aunque se reinicien contenedores.

## 2. API Gateway

### `app/main.py`

Crea la aplicación FastAPI, habilita CORS, inicializa la base de datos al arrancar e incluye todos los routers.

### `core/config.py`

Centraliza variables de entorno: URL de base de datos, secreto JWT y URL del servicio Prolog.

### `core/security.py`

Maneja:

- Hash de contraseñas.
- Verificación de contraseña.
- Creación de token JWT.
- Validación del administrador actual.

### `db/models.py`

Define las tablas del sistema con SQLAlchemy:

- `AdminUser`: usuario del panel.
- `Category`: categorías de FAQ.
- `Faq`: preguntas y respuestas.
- `Symptom`: síntomas editables.
- `Diagnosis`: diagnósticos editables.
- `DiagnosticRule`: reglas editables.
- `RuleSymptom`: relación muchos a muchos entre reglas y síntomas.
- `Setting`: configuración, como chat ID.
- `QueryLog`: historial de consultas.

### `db/init_db.py`

Crea las tablas, crea el usuario `IA1-User`, configura mensajes iniciales y carga datos desde `seeds/seed_data.json`.

No coloca FAQs ni reglas directamente en endpoints; las carga como datos iniciales.

## 3. Routers

### `features/auth/router.py`

Tiene `/api/auth/login` y `/api/auth/me`.

### `features/categories/router.py`

CRUD completo de categorías.

### `features/faqs/router.py`

CRUD de preguntas frecuentes y búsqueda con `/api/faqs/search`.

La búsqueda compara tokens del texto ingresado contra pregunta y keywords.

### `features/settings/router.py`

Permite editar `telegram_chat_id` y `unknown_message`.

### `features/stats/router.py`

Calcula consultas totales, usuarios únicos, consultas por tipo, consultas frecuentes y logs recientes.

### `features/diagnostics/router.py`

Aquí está lo más importante:

- CRUD de síntomas.
- CRUD de diagnósticos.
- CRUD de reglas.
- Endpoint `/api/diagnostics/diagnose`.

Cuando diagnostica, lee la base de datos, arma un JSON con reglas dinámicas y lo manda al `prolog-service`.

## 4. Prolog Service

### `app/main.py`

Recibe el JSON del API Gateway. Luego:

1. Convierte códigos a átomos Prolog seguros.
2. Genera hechos `selected/1`, `diagnosis/6`, `rule/5` y `required_symptom/2`.
3. Crea un archivo temporal `.pl`.
4. Ejecuta `swipl`.
5. Lee el JSON devuelto por Prolog.
6. Ordena diagnósticos por probabilidad.

### `prolog/expert_engine.pl`

Es el corazón lógico.

- `selected(S)`: síntoma seleccionado.
- `count_matched`: cuenta síntomas que sí coinciden.
- `missing_symptoms`: calcula síntomas que faltan.
- `problem_level`: convierte porcentaje en bajo, medio o alto.
- `diagnostic_result`: construye el diagnóstico final.
- `main`: imprime JSON para que Python lo lea.

## 5. Telegram Bot

### `app/bot.py`

Hace polling con Telegram.

- `/start`: saluda.
- `/diagnostico sintoma1,sintoma2`: llama a `/api/diagnostics/diagnose`.
- Cualquier otro texto: llama a `/api/faqs/search`.

## 6. Frontend

### `index.html`

Define las secciones visuales:

- Login.
- Dashboard.
- Preguntas.
- Categorías.
- Síntomas.
- Diagnósticos.
- Reglas.
- Prueba de diagnóstico.
- Configuración.

### `app.js`

Consume la API con `fetch`, guarda el token en `localStorage`, llena tablas y permite crear, editar o eliminar datos.

### `style.css`

Da presentación visual responsiva con tarjetas, tablas y pestañas.
