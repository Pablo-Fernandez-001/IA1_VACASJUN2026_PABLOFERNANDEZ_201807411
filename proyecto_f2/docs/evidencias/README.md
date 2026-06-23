# Evidencias de funcionamiento

Archivos incluidos:

- `simulacion_redisenada.png`: mapa 10x10, primer movimiento, objetivo, ruta BFS y fuente Prolog.
- `dashboard_redisenado.png`: metricas e historial persistente asociado a escenarios.

La prueba automatizada integral tambien constituye evidencia reproducible:

```powershell
docker compose build backend
docker run --rm -v "${PWD}/backend/tests:/app/tests:ro" `
  -e PROLOG_PATH=/app/prolog/warehouse.pl `
  proyecto_f2-backend:latest python -m unittest discover -s tests -v
```

Resultado verificado: cinco pruebas correctas, incluida una simulacion completa con cinco entregas y decisiones originadas en Prolog.

Evidencias adicionales recomendadas para la presentacion:

1. Editor con un paquete arrastrado a una nueva casilla.
2. Biblioteca con un escenario personalizado guardado.
3. Robot recogiendo y entregando una caja.
4. Swagger en `/docs` mostrando los endpoints de escenarios.
