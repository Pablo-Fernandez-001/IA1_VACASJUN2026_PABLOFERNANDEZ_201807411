# Smart Warehouse - Proyecto Fase 2 IA1

Smart Warehouse simula una bodega inteligente 10x10 donde un robot transporta paquetes hacia zonas de entrega. La decision de cada accion se origina en SWI-Prolog; Python coordina, aplica la accion y guarda historial.

## Documentacion

Los documentos Markdown de soporte estan en `docs/`:

- `docs/MANUAL_TECNICO.md`
- `docs/MANUAL_USUARIO.md`
- `docs/prompt_proyecto_f2.md`
- `docs/transcripcion_proyecto_f2.md`
- `docs/evidencias/README.md`

## Ejecutar rapido en local

Desde la raiz del repositorio:

```powershell
cd proyecto_f2
$env:PYTHONPATH="backend"
$env:DATABASE_URL="sqlite:///./warehouse_dev.db"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8400
```

En otra terminal:

```powershell
cd proyecto_f2/frontend
python -m http.server 8411 --bind 127.0.0.1
```

Abrir:

- Frontend: http://127.0.0.1:8411/index.html
- API: http://127.0.0.1:8400/api/health
- Swagger: http://127.0.0.1:8400/docs

Requisito local: tener `swipl` en PATH. Con Docker Compose ya va instalado.

## Ejecutar con Docker Compose

```powershell
cd proyecto_f2
docker compose up --build
```

Abrir:

- Frontend: http://localhost:8401
- API: http://localhost:8400/api/health
- Swagger: http://localhost:8400/docs

## Como ver que funciona

1. Entrar al frontend.
2. Pulsar `Iniciar`.
3. Pulsar `Paso` varias veces.
4. Observar que el robot se mueve en el mapa y el panel muestra la accion devuelta por Prolog.
5. Continuar hasta que el robot recoja un paquete y lo entregue en su zona.
6. Pulsar `Automatico` para ejecutar pasos continuos.
7. Abrir `Dashboard` para revisar entregas, movimientos, eficiencia, pendientes e historial.

## Prueba Prolog directa

Desde `proyecto_f2`:

```powershell
'{"robot_id":"r1","robots":[{"id":"r1","x":1,"y":1,"carrying":"none"}],"packages":[{"id":"p1","x":1,"y":3,"zone":"zona_a","status":"pendiente"}]}' | swipl -q -s prolog/warehouse.pl -g warehouse_cli
```

Respuesta esperada inicial: `mover_abajo`.

## Requisitos cubiertos

- Mapa 10x10.
- 1 robot funcional.
- 5 paquetes.
- 2 zonas de entrega.
- 8 obstaculos.
- Acciones: `mover_arriba`, `mover_abajo`, `mover_izquierda`, `mover_derecha`, `recoger_paquete`, `entregar_paquete`, `esperar`.
- Hechos, reglas, variables, listas y corte `!` en Prolog.
- Backend Python con FastAPI.
- Frontend visual con modo paso a paso y automatico.
- Historial y metricas en base de datos real SQLite.

## Estructura

```text
backend/   API FastAPI, simulacion, persistencia e integracion Prolog
prolog/    hechos, reglas y consulta CLI
frontend/  simulacion visual y dashboard
docs/      manuales, prompt, transcripcion y evidencias
```
