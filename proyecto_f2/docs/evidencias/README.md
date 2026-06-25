# Evidencias de funcionamiento

Archivos incluidos:

- `simulacion_redisenada.png`: mapa 10x10, primer movimiento, objetivo, ruta BFS y fuente Prolog.
- `dashboard_redisenado.png`: metricas e historial persistente asociado a escenarios.
- `editor_estanterias.png`: una estanteria trasladada desde el editor.
- `editor_inventario.png`: sexto paquete añadido y disponible para eliminar o configurar.
- `analitica_proceso.png`: detalle individual con acciones y decisiones paso a paso.
- `editor_estanterias_zonas.png`: estanteria adicional y zona A reubicada.
- `escenario_autoguardado.png`: diseño temporal persistido automáticamente al iniciar.
- `historial_autoguardado.png`: proceso conservado tras eliminar el escenario, con checkpoints de inicio y reinicio.

La prueba automatizada integral tambien constituye evidencia reproducible:

```powershell
docker compose build backend
docker run --rm -v "${PWD}/backend/tests:/app/tests:ro" `
  -e PROLOG_PATH=/app/prolog/warehouse.pl `
  ia-vacas-proyecto-f2-backend:latest python -m unittest discover -s tests -v
```

Resultado verificado: cinco pruebas correctas, incluida una simulacion completa con cinco entregas y decisiones originadas en Prolog.

Evidencias adicionales recomendadas para la presentacion:

1. Editor con un paquete arrastrado a una nueva casilla.
2. Biblioteca con un escenario personalizado guardado.
3. Robot recogiendo y entregando una caja.
4. Swagger en `/docs` mostrando los endpoints de escenarios.
