# Guía breve de defensa — RoboMaze

## Demostración de 5 minutos

1. Abra la interfaz y señale el indicador de API conectada.
2. Dibuje un obstáculo, mueva inicio y meta.
3. Cargue **Trampa para DFS** y compare: BFS 7 pasos, DFS 31.
4. Alterne **Mostrar** para visualizar ambos recorridos.
5. Cargue **Sin solución** y evidencie que no hay caída.
6. Abra Swagger y ejecute un POST.
7. Muestre los servicios Python y las 22 pruebas verdes.

## Preguntas probables

**¿Por qué BFS garantiza el camino más corto?**  
Porque explora por niveles y todas las aristas cuestan un movimiento. La primera
vez que alcanza la meta lo hace con la menor profundidad posible.

**¿Por qué DFS no garantiza el mínimo?**  
Profundiza una rama según el orden de vecinos. Puede llegar por un desvío antes de
examinar una alternativa corta.

**¿Cómo se evitan ciclos?**  
Cada algoritmo mantiene `discovered` y marca al insertar en la frontera, evitando
duplicados y padres inconsistentes.

**¿Cómo se reconstruye la ruta?**  
`parents[child] = current`; desde la meta se siguen padres hasta `None` y se invierte.

**¿La búsqueda se hace en JavaScript?**  
No. JavaScript edita, llama a la API y pinta `visited_nodes`/`path`. Las búsquedas
están exclusivamente en `backend/app/services/`.

**¿Por qué no hay base de datos?**  
Es una restricción del enunciado. Los cinco casos son JSON de solo lectura y los
resultados viven únicamente durante la petición.

**¿Qué significa tiempo?**  
`perf_counter` alrededor del algoritmo, sin red ni animación. En mapas pequeños
fluctúa; los nodos y la longitud son mejores para la comparación didáctica.

**Complejidad:** `O(V + E)` en tiempo para ambos y hasta `O(V)` en memoria.

**¿Por qué arquitectura por capas?**  
Separa HTTP, contratos, reglas y algoritmos; mejora pruebas, mantenibilidad y evita
duplicar validaciones.
