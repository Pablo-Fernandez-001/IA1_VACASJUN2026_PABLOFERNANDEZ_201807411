# Manual de Usuario - Smart Warehouse

## Iniciar el sistema

```bash
cd proyecto_f2
cp .env.example .env
docker compose up --build
```

Abra http://localhost:8401.

## Interpretar el mapa

La grilla representa una bodega 10x10.

- Robot: casilla verde con `R`.
- Paquete: borde azul con identificador `P1`, `P2`, etc.
- Obstaculo: casilla oscura.
- Zona A: casilla verde agua con `A`.
- Zona B: casilla amarilla con `B`.

## Controles

- `Iniciar`: crea una simulacion nueva.
- `Pausar`: detiene la ejecucion.
- `Reiniciar`: vuelve al estado inicial.
- `Paso`: consulta Prolog y ejecuta una accion.
- `Automatico`: ejecuta pasos cada pocos milisegundos hasta detenerlo o completar entregas.

## Estado del robot

El panel muestra pasos, movimientos, entregas y paquetes pendientes. El mensaje inferior muestra la ultima accion y la explicacion devuelta por Prolog.

## Paquetes

Cada paquete muestra zona asignada, estado y posicion. Estados esperados:

- `pendiente`: aun no recogido.
- `en_robot`: cargado por el robot.
- `entregado`: entregado en su zona.

## Dashboard

Abra `Dashboard` para ver:

- Entregas realizadas.
- Movimientos.
- Paquetes pendientes.
- Eficiencia.
- Tiempo transcurrido.
- Historial de simulaciones.

## Si la simulacion se detiene

Verifique que SWI-Prolog este instalado si ejecuta localmente. Con Docker Compose ya viene instalado. Si Prolog no esta disponible, la API respondera un error indicando que `swipl` no esta en PATH.
