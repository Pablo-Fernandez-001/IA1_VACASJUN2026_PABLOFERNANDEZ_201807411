# Práctica 2 IA1 - SmartBot Diagnóstico Dinámico

**Autor:** Pablo Daniel Fernández Chacón  
**Carnet:** 201807411  
**Curso:** Inteligencia Artificial 1 - Vacaciones Junio 2026

SmartBot es un sistema de atención automatizada con bot de Telegram, API REST, base de datos, panel administrativo y motor lógico en Prolog.

La solución se hizo parecida a la Práctica 1 y al proyecto Doctor Byte Fase 1: no es monolítica, tiene servicios separados y la lógica de diagnóstico vive en Prolog. El administrador puede modificar preguntas frecuentes, categorías, síntomas, diagnósticos, reglas, mensajes, categorías, pesos y configuración del chat de Telegram sin tocar código fuente.

## Servicios

```text
frontend-web       -> Panel administrativo HTML/CSS/JS
api-gateway        -> FastAPI principal, auth, CRUD, DB, logs y estadísticas
prolog-service     -> FastAPI + SWI-Prolog para inferencia diagnóstica
telegram-bot       -> Bot de Telegram que consume la API REST
sqlite             -> Base persistente en volumen Docker
```

## Credenciales del panel

```text
Usuario: IA1-User
Contraseña: IA1-password@_new
```

## Ejecución con Docker Compose

```bash
cp .env.example .env
# opcional: coloca TELEGRAM_BOT_TOKEN en .env
docker compose up --build
```

Abrir:

```text
Panel:              http://localhost:8080
API Gateway docs:   http://localhost:8000/docs
Prolog Service:     http://localhost:8001/docs
Health:             http://localhost:8000/api/health
```

## Ejecución local sin Docker

### 1. API Gateway

```bash
cd backend/api_gateway
python -m venv .venv
source .venv/bin/activate   # Linux/WSL
# .\.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Prolog Service

Instalar SWI-Prolog antes de iniciar.

```bash
cd backend/prolog_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### 3. Frontend

```bash
cd frontend
python -m http.server 8080
```

## Bot de Telegram

1. Crear bot con `@BotFather`.
2. Copiar el token en `.env`:

```env
TELEGRAM_BOT_TOKEN=tu_token_real
```

3. Levantar con Docker Compose.
4. Enviar `/start` al bot.
5. Desde el panel se puede configurar el `telegram_chat_id`.

Sin token el sistema sigue funcionando: API, panel, CRUD, diagnósticos y estadísticas.

## Funcionalidades principales

- Login con JWT.
- CRUD de categorías.
- CRUD de preguntas frecuentes y respuestas.
- CRUD de síntomas.
- CRUD de diagnósticos.
- CRUD de reglas diagnósticas.
- Asociación dinámica de síntomas a reglas.
- Consulta de FAQ desde bot y panel.
- Diagnóstico por síntomas usando Prolog.
- Más de un diagnóstico posible con porcentaje.
- Ruta de solución por diagnóstico.
- Porcentaje de problema detectado.
- Registro de consultas.
- Estadísticas de uso.
- Configuración del chat o grupo de Telegram.
- Documentación técnica, usuario, ER y arquitectura.

## Estructura

```text
practica2_smartbot_201807411/
  backend/
    api_gateway/
    prolog_service/
    telegram_bot/
  frontend/
  docs/
  scripts/
  postman/
  docker-compose.yml
  README.md
```

## Documentación

- `docs/MANUAL_TECNICO.md`
- `docs/MANUAL_USUARIO.md`
- `docs/REQUERIMIENTOS.md`
- `docs/ARQUITECTURA.md`
- `docs/ER.md`
- `docs/CASOS_PRUEBA.md`
- `docs/EXPLICACION_CODIGO.md`
- `docs/HOJA_CUMPLIMIENTO.md`

## Commits sugeridos

```bash
git init
git add .
git commit -m "feat: estructura base no monolitica de SmartBot"
git commit --allow-empty -m "feat: api gateway con autenticacion y base de datos"
git commit --allow-empty -m "feat: motor prolog dinamico para diagnosticos"
git commit --allow-empty -m "feat: panel administrativo y crud completo"
git commit --allow-empty -m "docs: manuales tecnicos usuario y evidencias"
```
