# Guía de verificación - Doctor Byte

Esta guía verifica que el proyecto cumple el enunciado de Fase 1: Prolog, backend Python, frontend, Telegram, historial y documentación.

## 1. Entrar al proyecto

```powershell
cd C:\Users\pabda\Desktop\IA1_VACASJUN2026_PABLOFERNANDEZ_201807411\proyecto_f1
```

Ejecuta los comandos desde esta raíz salvo que un paso indique otra carpeta.

## 2. Verificar herramientas

```powershell
python --version
swipl --version
node --version
npm --version
docker --version
```

Resultado usado en esta verificación: Python 3.14.3, SWI-Prolog 10.0.2, Node 22.18.0, npm 11.6.3 y Docker 29.2.0.

## 3. Configurar dependencias

Usa el script de setup. Este script crea `.env` si falta, crea `.venv` solo si no existe e instala dependencias de los tres servicios Python y del frontend.

```powershell
.\scripts\setup_windows.ps1
```

Para Telegram real, completar en `.env`:

```text
TELEGRAM_BOT_TOKEN=
TELEGRAM_DEFAULT_CHAT_ID=
```

Sin token, el sistema sigue funcionando y marca Telegram como no configurado.

Para encontrar y guardar el `chat_id`, abre el bot en Telegram, envía `/start` y ejecuta:

```powershell
.\scripts\telegram_chat_id_windows.ps1 -SaveFirst
```

Para probar un mensaje directo:

```powershell
.\scripts\telegram_test_windows.ps1
```

## 4. Verificar motor Prolog directo

```powershell
'{"mode":"symptoms"}' | swipl -q -s '.\backend\prolog_service\knowledge_base\doctor_byte.pl' -g doctor_byte_cli
```

Debe devolver un JSON con 25 síntomas.

```powershell
'{"mode":"diagnose","symptoms":["pantalla_negra","ventiladores_giran"]}' | swipl -q -s '.\backend\prolog_service\knowledge_base\doctor_byte.pl' -g doctor_byte_cli
```

Debe devolver `falla_video_gpu`.

## 5. Ejecutar pruebas automatizadas

```powershell
cd backend\prolog_service
.\.venv\Scripts\python -m pytest
```

Resultado esperado: 16 pruebas pasan.

```powershell
cd ..\api_gateway
.\.venv\Scripts\python -m pytest
```

Resultado esperado: 1 prueba pasa.

```powershell
cd ..\..\frontend
npm run build
```

Resultado esperado: Vite genera `dist/` sin errores.

Volver a la raíz:

```powershell
cd ..
```

## 6. Levantar servicios sin Docker

Desde la raíz:

```powershell
.\scripts\start_dev_windows.ps1
```

Si aparece puerto ocupado:

```powershell
.\scripts\start_dev_windows.ps1 -StopExisting
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

## 7. Verificar endpoints

```powershell
curl.exe http://127.0.0.1:8001/health
curl.exe http://127.0.0.1:8002/health
curl.exe http://127.0.0.1:8000/api/health
```

Resultados esperados:

- `prolog-service` con `swipl_available: true`.
- `telegram-service` con `configured: false` si no hay token.
- `api-gateway` con `prolog_service: ok`.

```powershell
curl.exe http://127.0.0.1:8000/api/symptoms
```

Debe listar 25 síntomas.

```powershell
curl.exe --% -X POST http://127.0.0.1:8000/api/diagnose -H "Content-Type: application/json; charset=utf-8" -d "{\"symptoms\":[\"pantalla_negra\",\"ventiladores_giran\"],\"user_name\":\"Prueba\",\"notify_telegram\":false}"
```

Debe devolver `falla_video_gpu`, confianza 67 y `telegram_sent: "no"`.

```powershell
curl.exe http://127.0.0.1:8000/api/history
```

Debe mostrar el diagnóstico creado en historial.

## 8. Verificar con Docker

```powershell
.\scripts\start_docker_windows.ps1
```

El script construye, levanta y espera los servicios. Al finalizar debe mostrar:

```text
todo está subido en:
Frontend:          http://localhost:8080
API Gateway docs:  http://localhost:8000/docs
API health:        http://localhost:8000/api/health
Prolog health:     http://localhost:8001/health
Telegram health:   http://localhost:8002/health
```

Para detener:

```powershell
.\scripts\stop_docker_windows.ps1
```

## 9. Errores comunes y solución

| Error | Causa | Solución |
|---|---|---|
| `Unable to copy ... venvlauncher.exe` | El `.venv` ya existe o está en uso por un servicio corriendo. | Ejecutar `.\scripts\stop_services_windows.ps1` y luego `.\scripts\setup_windows.ps1`. |
| `[WinError 10013]` | El puerto ya está ocupado. | Ejecutar `.\scripts\start_dev_windows.ps1 -StopExisting`. |
| `uvicorn no se reconoce` | No está activado el venv o estás en una carpeta incorrecta. | Usar `.\scripts\start_dev_windows.ps1` desde la raíz. |
| `Cannot find path ... frontend\backend\...` | Se intentó hacer `cd backend\...` desde `frontend`. | Volver a la raíz con `cd ..` o usar los scripts. |

## 10. Evidencias para entregar

Capturar:

- Pantalla principal en `http://localhost:5173`.
- Diagnóstico GPU con `pantalla_negra` y `ventiladores_giran`.
- Historial mostrando el registro creado.
- Swagger en `http://localhost:8000/docs`.
- Telegram recibido, si se configura token y chat ID.
- Ejecución de `pytest` y `npm run build`.
