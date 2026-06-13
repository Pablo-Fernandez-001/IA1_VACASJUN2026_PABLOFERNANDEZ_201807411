# Práctica 2 IA1 - SmartBot

**Autor:** Pablo Daniel Fernández Chacón  
**Carnet:** 201807411

SmartBot responde preguntas frecuentes desde Telegram mediante una API REST desarrollada exclusivamente en Python. Categorías, preguntas, respuestas, administradores, configuración y consultas se almacenan en SQLite; no existen FAQ en JSON ni en el código fuente.

## Servicios

```text
frontend (Nginx) -> api-gateway (FastAPI) -> SQLite
telegram-bot -----------------------------> API REST
```

SQLite se eligió por ser una base SQL válida, liviana y suficiente para una práctica de un solo nodo. El archivo vive en el volumen Docker `smartbot_data`.

## Inicio

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

Abrir:

- Panel: `http://localhost:8090`
- Swagger: `http://localhost:8100/docs`
- Health: `http://localhost:8100/api/health`

Credenciales exigidas:

```text
Usuario: IA1-User
Password: IA1-password@_new
```

## Telegram

1. Crear un bot con `@BotFather`.
2. Colocar el token en `TELEGRAM_BOT_TOKEN` dentro de `.env`.
3. Reiniciar con `docker compose up -d`.
4. Enviar `/start` o una pregunta al bot.

El token no se incluye en el repositorio. Sin token, API y panel siguen funcionando.

## Datos iniciales

`backend/api_gateway/seeds/seed.sql` registra:

- 4 categorías.
- 20 preguntas.
- 20 respuestas asociadas.
- Configuración inicial del bot.

La semilla se ejecuta solo cuando la tabla `questions` está vacía.

## API principal

| Recurso | Endpoints |
|---|---|
| Autenticación | `POST /api/auth/login`, `GET /api/auth/me` |
| Categorías | `GET/POST /api/categories`, `PUT/DELETE /api/categories/{id}` |
| Preguntas | `GET/POST /api/questions`, `PUT/DELETE /api/questions/{id}` |
| Respuestas | `GET/POST /api/answers`, `PUT/DELETE /api/answers/{id}` |
| Consulta | `GET /api/search?q=...&telegram_user=...` |
| Configuración | `GET /api/settings`, `PUT /api/settings/{key}` |
| Estadísticas | `GET /api/stats`, `GET /api/stats/logs` |

Las operaciones de escritura, configuración y estadísticas requieren JWT.

## Pruebas

```powershell
.\scripts\test_api.ps1
docker compose config -q
node --check frontend\app.js
```

Prueba rápida:

```powershell
Invoke-RestMethod 'http://localhost:8100/api/search?q=como%20levanto%20el%20proyecto&telegram_user=manual'
```

Detener servicios:

```powershell
docker compose down
```

No usar `-v` si se desea conservar la base de datos.

## Documentación

- `docs/MANUAL_TECNICO.md`
- `docs/MANUAL_USUARIO.md`
- `docs/ARQUITECTURA.md`
- `docs/ER.md`
- `docs/HOJA_CUMPLIMIENTO.md`
- `docs/CASOS_PRUEBA.md`
