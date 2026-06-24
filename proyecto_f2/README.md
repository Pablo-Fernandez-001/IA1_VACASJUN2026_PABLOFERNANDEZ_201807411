# Smart Warehouse - Proyecto 2 IA1

Smart Warehouse simula una bodega configurable de 10x10. Un robot recoge cinco paquetes y los entrega en su zona; la seleccion del objetivo, la ruta BFS y cada accion se originan en SWI-Prolog. FastAPI coordina el estado y SQLAlchemy conserva escenarios, pasos, metricas e historial.

## Funciones principales

- Editor visual para añadir o mover estanterias, reubicar zonas A/B y administrar paquetes mediante clic o arrastre.
- Biblioteca persistente de escenarios personalizados.
- Autoguardado de diseños temporales al iniciar y checkpoints antes de reiniciar.
- Eliminacion de escenarios desde la interfaz, excepto `Bodega clasica`.
- Validacion de limites, colisiones y zonas de entrega.
- Busqueda de ruta minima BFS implementada completamente en Prolog.
- Sincronizacion de mapa, robots, paquetes, zonas y obstaculos con Prolog en cada paso.
- Ruta calculada y explicacion de la decision visibles en el mapa.
- Controles de inicio, pausa, reinicio, paso a paso y modo automatico.
- Dashboard con analisis individual de cada proceso: duracion, acciones, esperas, configuracion inicial y decisiones paso a paso.
- Interfaz adaptable para escritorio y movil.

La vision por computadora no forma parte de esta version.

## Ejecutar con Docker Compose

```powershell
cd proyecto_f2
docker compose up --build -d
```

Abrir:

- Interfaz: http://localhost:8401
- API: http://localhost:8400/api/health
- Swagger: http://localhost:8400/docs

Si esos puertos estan ocupados:

```powershell
$env:BACKEND_PORT="8420"
$env:FRONTEND_PORT="8421"
docker compose up --build -d
```

## Flujo recomendado

1. Abrir `Simulacion`.
2. Pulsar `Editar mapa`.
3. Administrar paquetes o seleccionar la pestaña `Estanterias` para reorganizar el mapa.
4. Pulsar `Aplicar diseño`, o guardar la configuracion con `Guardar como`.
5. Pulsar `Iniciar` y luego `Ejecutar paso` o `Automatico`.
6. Observar la ruta BFS, el objetivo y la explicacion generada por Prolog.
7. Abrir `Analitica` y pulsar `Analizar` en cualquier proceso para consultar sus decisiones.

## Pruebas

Pruebas locales; la prueba integral se omite si `swipl` no esta instalado:

```powershell
$env:PYTHONPATH="backend"
python -m unittest discover -s backend/tests -v
```

Prueba integral dentro de la imagen Docker:

```powershell
docker compose build backend
docker run --rm -v "${PWD}/backend/tests:/app/tests:ro" `
  -e PROLOG_PATH=/app/prolog/warehouse.pl `
  proyecto_f2-backend:latest python -m unittest discover -s tests -v
```

La prueba integral exige que Prolog complete los cinco paquetes en menos de 250 decisiones sin devolver `esperar`.

## Documentacion y evidencias

- `docs/MANUAL_TECNICO.md`
- `docs/MANUAL_USUARIO.md`
- `docs/evidencias/simulacion_redisenada.png`
- `docs/evidencias/dashboard_redisenado.png`

## Estructura

```text
backend/app/schemas/       validacion de escenarios
backend/app/services/      simulacion, escenarios e integracion Prolog
backend/tests/             pruebas unitarias e integrales
prolog/                    hechos, BFS, reglas y entrada JSON
frontend/                  simulacion, editor y dashboard
docs/                      manuales y evidencias
```
