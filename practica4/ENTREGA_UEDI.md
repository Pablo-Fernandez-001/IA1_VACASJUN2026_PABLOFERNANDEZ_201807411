# Entrega UEDI — Práctica 4 RoboMaze

## Datos

| Campo | Valor |
|---|---|
| Curso | Inteligencia Artificial 1 |
| Práctica | Práctica 4 — RoboMaze |
| Carpeta | `practica4/` |
| Estudiante | Pablo Fernández |
| Carné | 201807411 |
| Fecha de entrega | **24/06/2026** |
| Repositorio | https://github.com/Pablo-Fernandez-001/IA1_VACASJUN2026_PABLOFERNANDEZ_201807411 |

## Checklist de archivos

- [x] Backend Python/FastAPI por capas.
- [x] BFS manual con cola y reconstrucción de padres.
- [x] DFS manual con pila y reconstrucción de padres.
- [x] API REST y Swagger.
- [x] Interfaz HTML/CSS/JS interactiva.
- [x] Cinco laberintos JSON.
- [x] Comparación y caso sin solución.
- [x] Validaciones y mensajes recuperables.
- [x] Pruebas automatizadas.
- [x] `README.md`.
- [x] `MANUAL_TECNICO.md` con diagrama y RF/RNF.
- [x] `MANUAL_USUARIO.md` con evidencias.
- [x] Colección Postman.
- [x] Docker Compose.
- [x] Transcripción fuente.
- [ ] Confirmar que las seis capturas finales muestran la versión entregada.
- [ ] Confirmar al menos cinco commits funcionales en GitHub.
- [ ] Subir/push de la última revisión.
- [ ] Entregar el enlace solicitado en UEDI antes del cierre.

## Verificación previa

```powershell
cd practica4\backend
python -m pytest tests -q

cd ..
python scripts\verificar_practica4.py
docker compose config
```

Luego demostrar:

1. `/api/health` y `/docs`.
2. Carga de los cinco ejemplos.
3. Ejemplo 4: diferencia BFS/DFS.
4. Ejemplo 5: ambos informan “sin ruta” sin bloquearse.
5. Código manual de `bfs_service.py` y `dfs_service.py`.
6. Diagrama de capas y suite de pruebas.

## Commits funcionales

La consigna pide mínimo cinco commits progresivos. Registrar cambios reales por
etapas; no crear un único commit masivo ni falsificar fechas. Mensajes sugeridos:

```text
estructura inicial de practica4 robomaze
implementacion backend fastapi y modelos de laberinto
implementacion bfs y dfs con validaciones
frontend interactivo para laberintos y ejecucion de algoritmos
documentacion manuales evidencias y entrega final
```

## Recordatorio final

La existencia local de la carpeta no equivale a entregar. Confirmar que GitHub
muestre los archivos y el historial, copiar el enlace correcto y **subirlo a UEDI
antes del 24/06/2026**.
