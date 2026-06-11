# Hoja de cumplimiento - Práctica 2 SmartBot

| Requisito | Estado | Implementación |
|---|---:|---|
| Bot funcional en Telegram | ✅ | Servicio `backend/telegram_bot` con polling y comandos `/start` y `/diagnostico`. |
| Backend en Python | ✅ | `backend/api_gateway` y `backend/prolog_service` desarrollados con FastAPI. |
| API REST | ✅ | Endpoints bajo `/api/*` para auth, FAQ, categorías, configuración, estadísticas y diagnósticos. |
| Base de datos | ✅ | SQLite persistente en volumen Docker. Modelos SQLAlchemy. |
| 20 preguntas frecuentes | ✅ | Archivo `backend/api_gateway/seeds/seed_data.json` carga 20 FAQs iniciales. |
| CRUD preguntas/respuestas | ✅ | Panel y API `/api/faqs`. |
| CRUD categorías | ✅ | Panel y API `/api/categories`. |
| Panel administrativo | ✅ | `frontend/index.html`, `app.js`, `style.css`. |
| Autenticación | ✅ | JWT con usuario `IA1-User` y contraseña `IA1-password@_new`. |
| Mensaje si no hay respuesta | ✅ | Configuración `unknown_message`. |
| Docker Compose | ✅ | `docker-compose.yml` levanta API, Prolog, bot y frontend. |
| Configurar chat ID Telegram | ✅ | CRUD settings, clave `telegram_chat_id`. |
| Registro de consultas | ✅ | Tabla `query_logs`. |
| Estadísticas | ✅ | `/api/stats` y dashboard. |
| Al menos 3 categorías | ✅ | Seed inicial incluye 4 categorías. |
| Sin respuestas estáticas en código | ✅ | FAQs y reglas iniciales se cargan desde JSON de datos, no desde funciones hardcodeadas. |
| Lógica principal editable | ✅ | CRUD de síntomas, diagnósticos y reglas. Prolog recibe reglas dinámicas desde la DB. |
| Más de un diagnóstico | ✅ | Prolog devuelve todas las reglas con coincidencias, ordenadas por probabilidad. |
| Ruta de solución | ✅ | Cada diagnóstico incluye `solution_route`. |
| Porcentaje de problema | ✅ | Prolog calcula probabilidad y nivel bajo/medio/alto. |
| Manual técnico y usuario | ✅ | `docs/MANUAL_TECNICO.md` y `docs/MANUAL_USUARIO.md`. |
| Diagrama ER | ✅ | `docs/ER.md`. |
| Patrón de arquitectura | ✅ | `docs/ARQUITECTURA.md`. |
