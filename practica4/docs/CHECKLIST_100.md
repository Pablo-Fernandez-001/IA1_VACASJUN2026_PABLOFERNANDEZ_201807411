# Checklist de cobertura — RoboMaze

Este control traduce el enunciado a evidencia verificable; `scripts/verificar_practica4.py`
automatiza los elementos locales. La calificación oficial corresponde al docente.

| Área | Evidencia | Estado |
|---|---|---:|
| Backend Python | `backend/app/` | ✅ |
| API REST | 6 endpoints y Swagger | ✅ |
| BFS manual | `bfs_service.py`, `deque`, padres | ✅ |
| DFS manual | `dfs_service.py`, pila, padres | ✅ |
| Inicio/meta/obstáculos | Editor visual | ✅ |
| Ruta y visitados | Animación + respuesta JSON | ✅ |
| Métricas | Tarjetas y tabla | ✅ |
| Ejecución independiente | Botones BFS/DFS | ✅ |
| Comparación | Servicio, tabla y conclusión | ✅ |
| Sin solución | `maze_05.json` | ✅ |
| Cinco laberintos | `examples/maze_01..05.json` | ✅ |
| Arquitectura | Capas + Mermaid | ✅ |
| Sin base de datos | No hay dependencia/persistencia | ✅ |
| Validaciones | Suite parametrizada | ✅ |
| JSON inválido | Handler + test API | ✅ |
| Backend caído | Estado y toast | ✅ |
| Manual técnico | Raíz, RF/RNF/mejoras | ✅ |
| Manual de usuario | Raíz, flujo y capturas | ✅ |
| Instalación | README y Docker | ✅ |
| Evidencias | Seis rutas documentadas | ✅ |
| Pruebas | 22 casos verdes | ✅ |
| Postman | Colección versionada | ✅ |
| Repositorio | URL consignada | ✅ |
| Cinco commits | Revisar en GitHub | ⚠️ Acción del estudiante |
| UEDI | Enlace antes del 24/06/2026 | ⚠️ Acción del estudiante |

## Extras implementados

- Diseño adaptable y accesible.
- Dibujo por arrastre.
- Inicio igual a destino.
- Docker health check.
- Scripts Windows.
- Verificador estático de entrega.
- Guía de defensa.
