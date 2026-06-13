# Explicación del Código

- `app/main.py`: crea FastAPI y registra routers.
- `app/core/security.py`: JWT, bcrypt y dependencia de administrador.
- `app/db/models.py`: entidades SQLAlchemy.
- `app/db/init_db.py`: crea tablas, ejecuta `seed.sql` y crea el administrador.
- `features/questions`: CRUD de preguntas.
- `features/answers`: CRUD independiente de respuestas.
- `features/categories`: CRUD de categorías.
- `features/search`: normalización, coincidencia, respuesta y registro.
- `features/stats`: agregaciones sobre `query_logs`.
- `features/settings`: configuración y prueba Telegram.
- `telegram_bot/app/bot.py`: polling y consumo de `/api/search`.
- `frontend/app.js`: login, panel y consumo REST.

La fuente de verdad de preguntas y respuestas es SQLite. `seed.sql` solo inicializa la base cuando está vacía.
