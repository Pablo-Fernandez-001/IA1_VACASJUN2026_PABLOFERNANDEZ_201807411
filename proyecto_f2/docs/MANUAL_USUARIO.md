# Manual de Usuario - Smart Warehouse

## 1. Objetivo del sistema

Smart Warehouse permite simular una bodega inteligente en una cuadrícula configurable. El usuario puede diseñar escenarios, mover estanterías, administrar paquetes, reubicar zonas de entrega, ejecutar el robot paso a paso o en modo automático, revisar métricas y descargar reportes PDF por cada corrida.

El robot toma decisiones con apoyo de SWI-Prolog: selecciona el objetivo más conveniente, calcula una ruta mínima con BFS y devuelve la acción que debe ejecutarse.

## 2. Requisitos para ejecutar

Para usar el proyecto se recomienda Docker Desktop, porque la imagen del backend ya incluye SWI-Prolog.

También se puede ejecutar localmente, pero en ese caso debe instalarse SWI-Prolog y configurar Python con las dependencias del backend.

## 3. Iniciar con Docker Compose

Abra PowerShell en la carpeta raíz del repositorio y ejecute:

```powershell
cd C:\Users\pabda\OneDrive\Escritorio\IA-VACAS\proyecto_f2
docker compose up --build -d
```

Cuando los contenedores estén listos, abra:

- Interfaz web: http://localhost:8621
- API: http://localhost:8620/api/health
- Swagger: http://localhost:8620/docs

El proyecto usa nombres Docker aislados para no mezclarse con otras prácticas:

- Proyecto Compose: `ia-vacas-proyecto-f2`
- Backend: `ia-vacas-proyecto-f2-backend`
- Frontend: `ia-vacas-proyecto-f2-frontend`
- Red: `ia-vacas-proyecto-f2-net`
- Volumen: `ia-vacas-proyecto-f2-data`

Si los puertos están ocupados, use otros:

```powershell
$env:PROYECTO_F2_BACKEND_PORT="8720"
$env:PROYECTO_F2_FRONTEND_PORT="8721"
docker compose up --build -d
```

## 4. Pantalla principal de simulación

La pantalla principal muestra el mapa, los controles de ejecución, el selector de escenarios, el selector de velocidad, la decisión actual de Prolog, métricas rápidas y el inventario.

![Simulación con selector de velocidad](evidencias/simulacion_velocidad_actualizada.png)

Elementos visuales:

| Elemento | Significado |
|---|---|
| Robot verde | Unidad que recoge y entrega paquetes |
| Caja amarilla | Paquete pendiente, en tránsito o entregado |
| Estantería oscura | Obstáculo que el robot debe evitar |
| Zona A/B | Punto de entrega |
| Puntos verdes numerados | Ruta calculada por Prolog |
| Tarjetas de métricas | Entregas, movimientos, pasos, pendientes y velocidad |

## 5. Controles principales

| Control | Uso |
|---|---|
| `Iniciar` | Crea una nueva corrida con el escenario activo |
| `Pausar` | Detiene la ejecución automática y registra checkpoint |
| `Reiniciar` | Cierra la corrida actual y restaura el escenario inicial |
| `Ejecutar paso` | Pide a Prolog una sola acción y la ejecuta |
| `Automático` | Ejecuta pasos continuos según la velocidad elegida |
| `Velocidad` | Cambia el intervalo de avance automático |
| `Editar mapa` | Activa el modo de diseño cuando no hay corrida activa |

Velocidades disponibles:

| Velocidad | Intervalo | Multiplicador visual |
|---|---:|---:|
| Lenta | 1100 ms/paso | 0.5x |
| Normal | 650 ms/paso | 1x |
| Rápida | 350 ms/paso | 2x |
| Turbo | 180 ms/paso | 4x |

Puede cambiar la velocidad incluso durante el modo automático. El temporizador se ajusta sin reiniciar la corrida.

## 6. Diseñar un escenario

El editor solo se puede abrir cuando no hay una simulación activa. Si el botón `Editar mapa` está deshabilitado, pulse `Reiniciar` primero.

![Editor actualizado de mapa](evidencias/editor_mapa_actualizado.png)

El editor tiene tres pestañas:

### 6.1 Paquetes

Permite:

- Seleccionar un paquete desde el mapa, inventario o lista del editor.
- Arrastrar el paquete a una casilla libre.
- Añadir nuevos paquetes.
- Eliminar el paquete seleccionado.
- Cambiar la zona de entrega asignada.

Reglas importantes:

- Un paquete no puede colocarse sobre el robot.
- Un paquete no puede colocarse sobre una estantería.
- Un paquete no puede colocarse sobre otro paquete.
- Un paquete debe estar asignado a una zona existente.

### 6.2 Estanterías

Permite:

- Seleccionar una estantería.
- Moverla por arrastre o clic.
- Añadir estanterías nuevas.
- Eliminar estanterías personalizadas si se conserva el mínimo requerido.

El escenario debe conservar al menos ocho estanterías.

### 6.3 Zonas A/B

Permite mover libremente las zonas de entrega A y B, siempre que la nueva casilla no esté ocupada por robot, paquete u obstáculo.

## 7. Guardar, aplicar y actualizar diseños

En modo editor hay tres acciones principales:

| Acción | Resultado |
|---|---|
| `Aplicar diseño` | Usa el diseño como escenario temporal |
| `Guardar como` | Crea un escenario persistente con nombre propio |
| `Actualizar` | Sobrescribe el escenario personalizado activo |
| `Salir sin aplicar` | Descarta el borrador |

Si aplica un diseño temporal y luego pulsa `Iniciar`, el sistema lo guarda automáticamente con un nombre del tipo `Auto fecha-hora`.

El escenario base `Bodega clásica` no se puede modificar ni eliminar.

## 8. Cargar y eliminar escenarios

En la barra superior puede seleccionar un escenario guardado. Para activarlo, pulse el botón de carga.

También puede eliminar escenarios personalizados con el botón `×`. El historial de corridas se conserva aunque el escenario sea eliminado.

No se permite eliminar:

- `Bodega clásica`.
- Un escenario que esté ejecutándose en ese momento.

## 9. Ejecutar una corrida

Flujo recomendado:

1. Seleccione o diseñe un escenario.
2. Elija la velocidad.
3. Pulse `Iniciar`.
4. Use `Ejecutar paso` para revisar cada decisión o `Automático` para dejar avanzar al robot.
5. Observe la tarjeta `Decisión actual`.
6. Revise la ruta resaltada en el mapa.
7. Al finalizar, abra `Analítica`.

Estados de paquete:

| Estado | Significado |
|---|---|
| `pendiente` | Aún no ha sido recogido |
| `en_robot` | Está siendo transportado |
| `entregado` | Llegó a su zona asignada |

## 10. Analítica e historial

La vista `Analítica` muestra métricas globales, historial de procesos, estado de cada corrida, pasos, entregas, eficiencia y acciones disponibles.

![Historial con descarga PDF](evidencias/analitica_reportes_pdf.png)

Cada fila del historial incluye:

- ID del proceso.
- Escenario usado.
- Fecha y hora de inicio.
- Estado.
- Duración.
- Pasos.
- Entregas.
- Eficiencia.
- Botón `Analizar`.
- Botón `Descargar`.

El botón `Descargar` aparece habilitado cuando la corrida tiene al menos un paso recorrido.

## 11. Analizar un proceso individual

Al pulsar `Analizar`, se abre el detalle del proceso:

![Detalle analítico con botón PDF](evidencias/detalle_analitica_pdf.png)

El detalle incluye:

- Entregas realizadas.
- Movimientos.
- Velocidad usada.
- Promedio de pasos por entrega.
- Eficiencia.
- Esperas.
- Checkpoints automáticos.
- Distribución de acciones.
- Configuración inicial.
- Decisiones paso a paso.

La tabla de decisiones muestra qué acción devolvió Prolog, la explicación y la hora registrada.

## 12. Descargar reporte PDF

Desde el historial o desde el detalle individual, pulse `Descargar` o `Descargar reporte`.

El sistema genera un archivo PDF con:

- Encabezado visual tipo Analítica.
- Resumen de la corrida.
- Métricas principales.
- Velocidad usada.
- Distribución de acciones.
- Configuración inicial.
- Recorrido paso a paso.
- Explicaciones generadas por Prolog.

Cada corrida tiene su propio reporte aunque se haya ejecutado el mismo escenario varias veces.

Ejemplo incluido en evidencias:

[Reporte PDF de ejemplo](evidencias/reporte_proceso_demo.pdf)

## 13. Guardado automático y checkpoints

El sistema guarda información automáticamente en estos momentos:

| Evento | Qué se guarda |
|---|---|
| Inicio | Snapshot inicial de la corrida |
| Pausa | Estado actual antes de pausar |
| Reanudación | Estado al continuar |
| Finalización | Estado final completado |
| Reinicio | Estado previo a restaurar el escenario |
| Reemplazo | Estado previo a iniciar una nueva corrida |

Esto permite consultar procesos anteriores aunque se reinicie o elimine un escenario personalizado.

## 14. Solución de problemas

| Problema | Solución |
|---|---|
| Puerto ocupado | Cambie `PROYECTO_F2_BACKEND_PORT` y `PROYECTO_F2_FRONTEND_PORT` |
| No carga la interfaz | Verifique `docker compose ps` y abra `http://localhost:8621` |
| No responde la API | Abra `http://localhost:8620/api/health` |
| No puedo editar | Reinicie la simulación activa |
| No puedo colocar un elemento | Use una casilla libre sin robot, paquete, estantería o zona |
| Prolog devuelve `esperar` | Revise que exista camino libre hacia el objetivo |
| No descarga el PDF | Asegúrese de que la corrida tenga al menos un paso |
| SWI-Prolog no está instalado localmente | Use Docker Compose |

## 15. Cierre del sistema

Para detener los contenedores:

```powershell
docker compose down
```

Si desea borrar también la base persistente del proyecto:

```powershell
docker compose down -v
```
