# Evidencias

Las capturas se generan sobre la aplicación real y se referencian desde el manual:

| Archivo | Evidencia esperada |
|---|---|
| `01_inicio.png` | Interfaz inicial y API conectada |
| `02_laberinto_predefinido.png` | Caso cargado |
| `03_bfs_resultado.png` | Camino y métricas BFS |
| `04_dfs_resultado.png` | Camino y métricas DFS |
| `05_comparacion.png` | Tabla BFS vs DFS |
| `06_sin_ruta.png` | Manejo visual de ausencia de solución |

Para regenerarlas, inicie backend y frontend y ejecute:

```powershell
pip install -r scripts\requirements-evidencias.txt
python scripts\generar_evidencias.py
```

Antes de entregar, abra cada PNG y confirme que no existan mensajes de error,
datos privados ni contenido recortado.
