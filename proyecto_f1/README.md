# Doctor Byte - Fase 1 IA1

Sistema experto distribuido para diagnóstico de fallas comunes en computadoras.

**Autor:** Pablo Daniel Fernández Chacón  
**Carnet:** 201807411  
**Curso:** Inteligencia Artificial 1 - Vacaciones Junio 2026

## Arquitectura

Este proyecto no es monolítico. Está dividido en servicios independientes:

1. **frontend-web:** interfaz React/Vite para selección dinámica de síntomas, diagnóstico e historial.
2. **api-gateway:** API principal FastAPI, guarda historial y orquesta servicios.
3. **prolog-service:** microservicio FastAPI que ejecuta SWI-Prolog como motor experto.
4. **telegram-service:** microservicio FastAPI para notificaciones por Telegram.
5. **SQLite:** persistencia local del historial de diagnósticos.

## Requisitos cubiertos

- Base de conocimiento en Prolog.
- 25 síntomas implementados.
- 14 fallas diagnosticables.
- 14 recomendaciones.
- Hechos, reglas, variables, listas y corte `!` en Prolog.
- Interfaz web funcional.
- Backend en Python con FastAPI.
- Comunicación backend-Prolog.
- Diagnósticos generados con reglas de inferencia.
- Integración con Telegram.
- Historial de diagnósticos.
- Documentación técnica, manual, casos de prueba y diagrama.
- Docker y PyTest como valor agregado.

## Ejecución rápida en Windows

Abrir PowerShell desde la raíz del proyecto:

```powershell
cd C:\Users\pabda\Desktop\IA1_VACASJUN2026_PABLOFERNANDEZ_201807411\proyecto_f1
```

Configurar dependencias una vez:

```powershell
.\scripts\setup_windows.ps1
```

Iniciar todos los servicios:

```powershell
.\scripts\start_dev_windows.ps1
```

Abrir:

```text
http://localhost:5173
```

API:

```text
http://localhost:8000/docs
```

Detener servicios:

```powershell
.\scripts\stop_services_windows.ps1
```

Si un puerto quedó ocupado, iniciar liberando puertos del proyecto:

```powershell
.\scripts\start_dev_windows.ps1 -StopExisting
```

## Pruebas

Desde la raíz del proyecto:

```powershell
cd backend\prolog_service
.\.venv\Scripts\python -m pytest
```

```powershell
cd ..\api_gateway
.\.venv\Scripts\python -m pytest
```

```powershell
cd ..\..\frontend
npm run build
```

El servicio Prolog incluye pruebas automatizadas para los 12 casos documentados en `docs/casos_prueba.md`.

## Docker

```powershell
cd C:\Users\pabda\Desktop\IA1_VACASJUN2026_PABLOFERNANDEZ_201807411\proyecto_f1
.\scripts\start_docker_windows.ps1
```

Al finalizar verás:

```text
todo está subido en:
Frontend:          http://localhost:8080
API Gateway docs:  http://localhost:8000/docs
API health:        http://localhost:8000/api/health
Prolog health:     http://localhost:8001/health
Telegram health:   http://localhost:8002/health
```

Detener Docker:

```powershell
.\scripts\stop_docker_windows.ps1
```

## Telegram

1. En Telegram abrir `@BotFather`.
2. Crear bot con `/newbot`.
3. Copiar token en `.env` como `TELEGRAM_BOT_TOKEN`.
4. Obtener tu chat id escribiéndole al bot y consultando `https://api.telegram.org/botTU_TOKEN/getUpdates`.
5. Colocar el chat id en la interfaz o en `.env` como `TELEGRAM_DEFAULT_CHAT_ID`.

Sin token, el sistema funciona normalmente y marca Telegram como no configurado.

Para obtener el `chat_id` sin copiar JSON:

```powershell
.\scripts\telegram_chat_id_windows.ps1
```

Si todavía no aparece, abre el bot, envía `/start` y luego ejecuta:

```powershell
.\scripts\telegram_chat_id_windows.ps1 -SaveFirst
```

Para probar un mensaje directo:

```powershell
.\scripts\telegram_test_windows.ps1
```

## Problemas comunes

- `Unable to copy ... venvlauncher.exe`: ya existe un `.venv` en uso. Detén servicios con `.\scripts\stop_services_windows.ps1` y no recrees el venv si ya existe.
- `[WinError 10013]`: el puerto está ocupado. Usa `.\scripts\start_dev_windows.ps1 -StopExisting`.
- `uvicorn no se reconoce`: no estás dentro del venv o estás en la carpeta incorrecta. Usa `.\scripts\start_dev_windows.ps1`.
- `Cannot find path ... frontend\backend\...`: estás ejecutando rutas relativas desde `frontend`. Vuelve a la raíz con `cd ..` o usa los scripts.

## Estructura

```text
proyecto_f1/
  backend/
    api_gateway/
    prolog_service/
    telegram_service/
  frontend/
  docs/
  scripts/
  docker-compose.yml
  README.md
```
