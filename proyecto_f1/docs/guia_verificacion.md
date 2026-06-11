# Guia de verificacion - Doctor Byte

Esta guia verifica que el proyecto cumple el enunciado de Fase 1: Prolog, backend Python, frontend, Telegram, historial, Docker y base de conocimiento editable.

## 1. Entrar al proyecto

```powershell
cd C:\Users\pabda\Desktop\IA1_VACASJUN2026_PABLOFERNANDEZ_201807411\proyecto_f1
```

Ejecuta los comandos desde esta raiz salvo que un paso indique otra carpeta.

## 2. Verificar herramientas

```powershell
python --version
swipl --version
node --version
npm --version
docker --version
```

Resultado usado en esta verificacion: Python 3.14.3, SWI-Prolog 10.0.2, Node 22.18.0, npm 11.6.3 y Docker 29.2.0.

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

Para encontrar y guardar el `chat_id`, abre el bot en Telegram, envia `/start` y ejecuta:

```powershell
.\scripts\telegram_chat_id_windows.ps1 -SaveFirst
```

Para probar un mensaje directo:

```powershell
.\scripts\telegram_test_windows.ps1
```

## 4. Verificar motor Prolog directo

El motor Prolog carga los datos editables desde `backend/prolog_service/knowledge_base/doctor_byte_data.json`.

```powershell
'{"mode":"symptoms","knowledge_path":"backend/prolog_service/knowledge_base/doctor_byte_data.json"}' | swipl -q -s '.\backend\prolog_service\knowledge_base\doctor_byte.pl' -g doctor_byte_cli
```

Debe devolver un JSON con 25 sintomas.

```powershell
'{"mode":"diagnose","knowledge_path":"backend/prolog_service/knowledge_base/doctor_byte_data.json","symptoms":["pantalla_negra","ventiladores_giran"]}' | swipl -q -s '.\backend\prolog_service\knowledge_base\doctor_byte.pl' -g doctor_byte_cli
```

Debe devolver una lista `diagnostics` con mas de un diagnostico. El primero debe ser `falla_video_gpu` y debe incluir `probability`, `problem_percentage`, `effectiveness_probability`, `recommendations` y `solution_steps`.

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

Volver a la raiz:

```powershell
cd ..
```

## 6. Levantar servicios sin Docker

Desde la raiz:

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

## 7. Verificar endpoints base

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

Debe listar 25 sintomas.

```powershell
curl.exe --% -X POST http://127.0.0.1:8000/api/diagnose -H "Content-Type: application/json; charset=utf-8" -d "{\"symptoms\":[\"pantalla_negra\",\"ventiladores_giran\"],\"user_name\":\"Prueba\",\"notify_telegram\":false}"
```

Debe devolver `falla_video_gpu` como primer diagnostico, con lista completa de alternativas y `telegram_sent: "no"`.

```powershell
curl.exe http://127.0.0.1:8000/api/history
```

Debe mostrar el diagnostico creado en historial.

## 8. Verificar CRUD editable

Estos pasos crean datos temporales, prueban que Prolog los use y luego los eliminan.

Crear sintoma:

```powershell
$body = @{
  id = "prueba_codex"
  name = "Sintoma temporal Codex"
  category = "prueba"
  weight = 4
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/symptoms" -ContentType "application/json; charset=utf-8" -Body $body
```

Editar sintoma:

```powershell
$body = @{
  id = "prueba_codex"
  name = "Sintoma temporal Codex editado"
  category = "prueba_editada"
  weight = 5
} | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:8000/api/symptoms/prueba_codex" -ContentType "application/json; charset=utf-8" -Body $body
```

Crear regla diagnostica:

```powershell
$body = @{
  id = "regla_codex"
  name = "Regla temporal Codex"
  message = "Prueba editable"
  category = "prueba"
  severity = "media"
  enabled = $true
  min_score = 0
  required_symptoms = @("prueba_codex")
  support_symptoms = @()
  recommendations = @("Recomendacion temporal")
  solution_steps = @("Paso temporal")
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/diagnosis-rules" -ContentType "application/json; charset=utf-8" -Body $body
```

Editar regla diagnostica:

```powershell
$body = @{
  id = "regla_codex"
  name = "Regla temporal Codex editada"
  message = "Prueba editable actualizada"
  category = "prueba_editada"
  severity = "alta"
  enabled = $true
  min_score = 0
  required_symptoms = @("prueba_codex")
  support_symptoms = @()
  recommendations = @("Recomendacion temporal editada")
  solution_steps = @("Paso temporal editado")
} | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:8000/api/diagnosis-rules/regla_codex" -ContentType "application/json; charset=utf-8" -Body $body
```

Diagnosticar usando el nuevo sintoma:

```powershell
$body = @{
  symptoms = @("prueba_codex")
  user_name = "Verificacion CRUD"
  notify_telegram = $false
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/diagnose" -ContentType "application/json; charset=utf-8" -Body $body
```

Resultado esperado: `regla_codex` aparece como primer diagnostico y se muestran porcentajes/ruta de solucion.

Limpiar datos temporales:

```powershell
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:8000/api/diagnosis-rules/regla_codex"
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:8000/api/symptoms/prueba_codex"
```

## 9. Verificar con Docker

```powershell
.\scripts\start_docker_windows.ps1
```

El script construye, levanta y espera los servicios. Al finalizar debe mostrar:

```text
todo esta subido en:
Frontend:          http://localhost:8081
API Gateway docs:  http://localhost:8000/docs
API health:        http://localhost:8000/api/health
Prolog health:     http://localhost:8001/health
Telegram health:   http://localhost:8002/health
```

Para detener:

```powershell
.\scripts\stop_docker_windows.ps1
```

El puerto del frontend Docker se controla con `FRONTEND_PORT` en `.env`. Por defecto queda en `8081`.

## 10. Verificar frontend

Abrir:

```text
http://localhost:8081
```

Comprobar:

- El panel de diagnostico permite seleccionar sintomas.
- Los resultados muestran mas de un diagnostico posible.
- Al hacer clic en cada diagnostico posible, se despliega su ruta de solucion.
- La seccion editable permite crear, editar y eliminar sintomas.
- La seccion editable permite crear, editar y eliminar reglas diagnosticas.
- Al editar una regla, el cambio se refleja en el siguiente diagnostico.
- El historial registra cada diagnostico ejecutado.
- Cada registro del historial se puede cargar nuevamente desde el boton de carpeta.

## 11. Errores comunes y solucion

| Error | Causa | Solucion |
|---|---|---|
| `Unable to copy ... venvlauncher.exe` | El `.venv` ya existe o esta en uso por un servicio corriendo. | Ejecutar `.\scripts\stop_services_windows.ps1` y luego `.\scripts\setup_windows.ps1`. |
| `[WinError 10013]` | El puerto ya esta ocupado. | Ejecutar `.\scripts\start_dev_windows.ps1 -StopExisting`. |
| `uvicorn no se reconoce` | No esta activado el venv o estas en una carpeta incorrecta. | Usar `.\scripts\start_dev_windows.ps1` desde la raiz. |
| `Cannot find path ... frontend\backend\...` | Se intento hacer `cd backend\...` desde `frontend`. | Volver a la raiz con `cd ..` o usar los scripts. |
| `Telegram todavia no devolvio ningun chat_id` | El bot no recibio mensajes nuevos. | Abrir el bot, enviar `/start` o cualquier mensaje, y volver a ejecutar `.\scripts\telegram_chat_id_windows.ps1 -SaveFirst`. |

## 12. Evidencias para entregar

Capturar:

- Pantalla principal en `http://localhost:8081` o `http://localhost:5173`.
- Diagnostico GPU con `pantalla_negra` y `ventiladores_giran`.
- Lista de diagnosticos alternativos con porcentajes.
- CRUD creando y editando una regla temporal.
- Historial mostrando el registro creado.
- Swagger en `http://localhost:8000/docs`.
- Telegram recibido, si se configura token y chat ID.
- Ejecucion de `pytest` y `npm run build`.
