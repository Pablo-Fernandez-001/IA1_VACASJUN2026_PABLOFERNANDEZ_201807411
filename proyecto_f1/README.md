# Doctor Byte - Fase 1 IA1

**Autor:** Pablo Daniel Fernández Chacón  
**Carnet:** 201807411

Sistema experto para diagnóstico preliminar de computadoras. SWI-Prolog es la fuente de conocimiento y el motor de inferencia; Python únicamente expone y orquesta el servicio.

## Cumplimiento principal

- 25 síntomas como hechos `symptom/4`.
- 13 fallas como hechos `failure/5`.
- 26 recomendaciones como hechos `recommendation/4`.
- 13 reglas editables `diagnosis_rule/6`.
- Uso de hechos, reglas, variables, listas, recursión y cortes.
- CRUD de síntomas, fallas, recomendaciones y reglas persistido en `.pl`.
- Historial y configuración auxiliar en SQLite, sin participar en el diagnóstico.
- Bot de Telegram con recepción por polling, comandos y comunicación REST.
- Frontend React para consulta, historial y administración.

## Arquitectura

```text
React/Nginx -> API Gateway FastAPI -> Prolog Service -> SWI-Prolog
Telegram <-> Telegram Service ------> API Gateway
API Gateway -> SQLite (solo historial/configuración)
```

La base de conocimiento está en:

```text
backend/prolog_service/knowledge_base/doctor_byte_knowledge.pl
```

## Docker

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

Abrir:

- Frontend: `http://localhost:8081`
- API: `http://localhost:8000/docs`
- Prolog Service: `http://localhost:8001/docs`
- Telegram Service: `http://localhost:8002/docs`

El archivo `.pl` se monta como volumen para conservar cambios del CRUD. SQLite se guarda en `doctor-byte-data`.

## Telegram

Configurar en `.env`:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_DEFAULT_CHAT_ID=
```

Comandos:

```text
/start
/ayuda
/sintomas
/diagnosticar pantalla_negra,ventiladores_giran
```

El ID predeterminado, estado activo y mensajes también se administran desde la pestaña **Configuración**.

## Pruebas

```powershell
cd backend\prolog_service
.\.venv\Scripts\python -m pytest -q
cd ..\api_gateway
.\.venv\Scripts\python -m pytest -q
cd ..\..\frontend
npm run build
cd ..
docker compose config -q
```

## Consulta REST

```powershell
$body = @{
  symptoms = @('pantalla_negra', 'ventiladores_giran')
  user_name = 'Evaluador'
  notify_telegram = $false
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/api/diagnose' -ContentType 'application/json' -Body $body
```

## Documentación

- `docs/documento_tecnico.md`
- `docs/manual_usuario.md`
- `docs/arquitectura.mmd`
- `docs/HOJA_CUMPLIMIENTO.md`
- `docs/guia_verificacion.md`
- `docs/casos_prueba.md`
