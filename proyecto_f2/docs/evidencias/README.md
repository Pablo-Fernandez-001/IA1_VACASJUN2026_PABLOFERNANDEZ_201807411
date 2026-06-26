# Evidencias de funcionamiento

Esta carpeta contiene capturas y archivos de salida usados en los manuales del proyecto.

## Evidencias actualizadas

| Archivo | Descripción |
|---|---|
| `simulacion_velocidad_actualizada.png` | Pantalla principal con selector de velocidad en modo turbo, métricas y mapa operativo |
| `editor_mapa_actualizado.png` | Editor de mapa con pestaña de estanterías, selección visual y modo diseño |
| `analitica_reportes_pdf.png` | Dashboard de Analítica con historial, botones `Analizar` y `Descargar` |
| `detalle_analitica_pdf.png` | Detalle individual con métricas, checkpoints, acciones, tabla de decisiones y botón de PDF |
| `reporte_proceso_demo.pdf` | Reporte PDF generado desde `/api/history/{id}/report` |

## Evidencias anteriores conservadas

| Archivo | Descripción |
|---|---|
| `simulacion_redisenada.png` | Simulación rediseñada inicial |
| `dashboard_redisenado.png` | Dashboard inicial con métricas e historial |
| `editor_estanterias.png` | Editor con estantería movida |
| `editor_inventario.png` | Inventario con paquete añadido |
| `analitica_proceso.png` | Primer detalle analítico por proceso |
| `editor_estanterias_zonas.png` | Estantería adicional y zona reubicada |
| `escenario_autoguardado.png` | Escenario temporal autoguardado |
| `historial_autoguardado.png` | Historial con checkpoints previos al reinicio |

## Cómo reproducir las evidencias

1. Levantar la aplicación:

   ```powershell
   cd C:\Users\pabda\OneDrive\Escritorio\IA-VACAS\proyecto_f2
   docker compose up --build -d
   ```

2. Abrir http://localhost:8621.
3. Ejecutar una corrida con al menos un paso.
4. Ir a `Analítica`.
5. Pulsar `Analizar` para ver el detalle.
6. Pulsar `Descargar` para generar el PDF.

## Evidencia automatizada

La suite de pruebas también funciona como evidencia reproducible:

```powershell
$env:PYTHONPATH="backend"
python -m unittest discover -s backend/tests -v
```

Con Docker:

```powershell
docker compose build backend
docker run --rm -v "${PWD}/backend/tests:/app/tests:ro" `
  -e PROLOG_PATH=/app/prolog/warehouse.pl `
  ia-vacas-proyecto-f2-backend:latest python -m unittest discover -s tests -v
```

La prueba integral se ejecuta cuando SWI-Prolog está disponible.
