# Manual de Usuario - Smart Warehouse

## Iniciar

```powershell
cd proyecto_f2
docker compose up --build -d
```

Abra http://localhost:8401. Si el puerto esta ocupado, configure `BACKEND_PORT` y `FRONTEND_PORT` antes de ejecutar Docker Compose.

## Interpretar la interfaz

- Robot: ficha circular verde.
- Paquete: caja amarilla identificada como `P1`, `P2`, etc.
- Obstaculo: estanteria oscura.
- Zona A/B: casilla punteada de entrega.
- Puntos verdes numerados: ruta calculada por Prolog.

El panel derecho muestra la accion, la explicacion, el objetivo, la longitud de la ruta, las metricas y el inventario.

## Diseñar un escenario

Solo se puede editar cuando no hay una simulacion activa.

1. Pulse `Editar mapa`.
2. Seleccione una caja en el mapa, inventario o selector del editor.
3. Pulse una casilla libre o arrastre la caja hasta ella.
4. Cambie la zona asignada si lo necesita.
5. Use una de estas opciones:
   - `Aplicar diseño`: usa el diseño sin guardarlo permanentemente.
   - `Guardar como`: crea un escenario persistente.
   - `Actualizar`: modifica el escenario personalizado activo.
   - `Salir sin aplicar`: descarta el borrador.

No se puede colocar una caja sobre el robot, otra caja, una zona o un obstaculo. El escenario base es inmutable para que siempre exista una configuracion recuperable.

## Cargar escenarios

Seleccione un escenario en la barra superior y pulse el boton de carga. Debe reiniciar primero si existe una simulacion activa.

## Ejecutar

- `Iniciar`: crea una corrida con el escenario activo.
- `Ejecutar paso`: pide una decision a Prolog y ejecuta una accion.
- `Automatico`: ejecuta pasos cada 650 ms; vuelva a pulsarlo para detenerlo.
- `Pausar`: detiene el modo automatico y marca la corrida en pausa.
- `Reiniciar`: cierra la corrida y recupera la distribucion inicial del escenario.

Estados de paquete:

- `pendiente`: espera ser recogido.
- `en_robot`: viaja con el robot.
- `entregado`: llego a su zona.

## Analitica

La vista `Analitica` presenta entregas, movimientos, pendientes, eficiencia, tiempo y un historial persistente. Cada fila identifica el escenario utilizado, incluso si posteriormente se modifica.

## Solucion de problemas

- `Puerto ocupado`: cambie los puertos en `.env` o detenga el contenedor que los utiliza.
- `SWI-Prolog no esta instalado`: utilice Docker Compose; la imagen ya lo incluye.
- `No se puede editar`: pulse `Reiniciar` para cerrar la simulacion activa.
- `Casilla protegida`: seleccione una casilla sin robot, zona, obstaculo ni otro paquete.
- `Prolog devuelve esperar`: revise que exista un camino entre el robot y los paquetes o zonas.
