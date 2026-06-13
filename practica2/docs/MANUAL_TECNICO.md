# Manual Técnico - SmartBot

## Objetivo

Implementar un bot de Telegram conectado a una API REST Python y una base SQL. El contenido del bot puede administrarse sin modificar código.

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.11 | Backend y bot. |
| FastAPI | API REST y OpenAPI. |
| SQLAlchemy | Modelado y acceso a datos. |
| SQLite | Persistencia SQL en volumen Docker. |
| JWT + bcrypt | Sesión administrativa y contraseñas con hash. |
| Nginx | Panel web y proxy `/api`. |
| Docker Compose | Ejecución reproducible. |

## Estructura

```text
backend/api_gateway/app
  core/          configuración y seguridad
  db/            sesión, modelos e inicialización
  features/      auth, categories, questions, answers, search, settings, stats
backend/api_gateway/seeds/seed.sql
backend/telegram_bot/app/bot.py
frontend/
docs/
```

## Base de datos

La base se configura con `DATABASE_URL`. En Docker usa `sqlite:////data/smartbot.db` y el volumen `smartbot_data`. SQLite está justificado porque la práctica se ejecuta en un solo nodo y no requiere un servidor de base de datos adicional.

No se usan archivos JSON, listas ni diccionarios como almacenamiento de preguntas y respuestas. Los datos iniciales son sentencias `INSERT` en `seed.sql`.

## Búsqueda

`GET /api/search` normaliza mayúsculas y tildes, compara tokens contra el texto y las palabras clave de preguntas activas, selecciona la respuesta activa de mayor prioridad y registra la consulta. Si no hay coincidencia devuelve `unknown_message` desde `settings`.

## Seguridad

- El login entrega un JWT con expiración.
- Las contraseñas se almacenan con bcrypt.
- CRUD de escritura, configuración, logs y estadísticas requieren JWT.
- Token de Telegram, secreto JWT y URL de base de datos se leen de `.env`.
- `.env` está excluido mediante `.gitignore`.

## Docker

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

Servicios: `api-gateway`, `telegram-bot` y `frontend`. La API tiene healthcheck y los demás servicios esperan a que esté saludable.

## Respaldo

```powershell
docker compose exec api-gateway sh -c "cp /data/smartbot.db /data/smartbot-backup.db"
```

## Mejoras futuras

- Migraciones Alembic.
- PostgreSQL para múltiples réplicas.
- Refresh tokens y rotación de secretos.
- Índice de búsqueda de texto completo.
