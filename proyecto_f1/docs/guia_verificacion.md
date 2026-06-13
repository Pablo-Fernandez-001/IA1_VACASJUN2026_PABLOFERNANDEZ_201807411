# Guía de Verificación

## Conteos Prolog

```powershell
rg -c '^symptom\(' backend\prolog_service\knowledge_base\doctor_byte_knowledge.pl
rg -c '^failure\(' backend\prolog_service\knowledge_base\doctor_byte_knowledge.pl
rg -c '^recommendation\(' backend\prolog_service\knowledge_base\doctor_byte_knowledge.pl
rg -c '^diagnosis_rule\(' backend\prolog_service\knowledge_base\doctor_byte_knowledge.pl
```

Resultados esperados: `25`, `13`, `26`, `13`.

## Consulta directa a Prolog

```powershell
$kb = (Resolve-Path 'backend\prolog_service\knowledge_base\doctor_byte_knowledge.pl').Path.Replace('\','/')
'{"mode":"diagnose","symptoms":["pantalla_negra","ventiladores_giran"],"knowledge_path":"' + $kb + '"}' |
  swipl -q -s backend\prolog_service\knowledge_base\doctor_byte.pl -g doctor_byte_cli
```

El primer diagnóstico debe ser `falla_video_gpu`.

## API

```powershell
Invoke-RestMethod http://localhost:8000/api/health
Invoke-RestMethod http://localhost:8000/api/knowledge
Invoke-RestMethod http://localhost:8000/api/config
```

```powershell
$body = @{ symptoms=@('no_enciende','sin_led'); user_name='Prueba'; notify_telegram=$false } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/diagnose -ContentType application/json -Body $body
```

## CRUD

Usar Swagger en `http://localhost:8000/docs` o las pestañas administrativas. Verificar crear, editar y eliminar en:

- `/api/symptoms`
- `/api/failures`
- `/api/recommendations`
- `/api/diagnosis-rules`
- `/api/config`

## Pruebas y Docker

```powershell
backend\prolog_service\.venv\Scripts\python -m pytest -q backend\prolog_service\tests
backend\api_gateway\.venv\Scripts\python -m pytest -q backend\api_gateway\tests
docker compose config -q
docker compose up -d --build
docker compose ps
```
