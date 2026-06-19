# Prompt de resolución — proyecto_f2 / Smart Warehouse

Actúa como desarrollador full-stack y asistente de arquitectura para resolver el **Proyecto 2 de Inteligencia Artificial 1: Smart Warehouse**. Este proyecto debe trabajarse después de terminar `practica3` y es independiente de `practica3` y `facturas_generadas.zip`.

## Contexto del repositorio y lineamientos globales

Trabaja dentro del mismo repositorio del curso de IA1. En la raíz deben coexistir, sin sobrescribirse entre sí, las carpetas:

```text
practica1/
proyecto_f1/
practica2/
proyecto_f2/
practica3/
```

Antes de programar, revisa `practica1`, `proyecto_f1` y `practica2` para mantener una estructura similar, reutilizar estilo de documentación, dockerización, forma de endpoints y forma de integración frontend/backend/Prolog cuando aplique. No copies código roto ni dependencias innecesarias: úsalo solo como guía de formato y coherencia del repositorio.

Cuando un requisito no exista en los proyectos anteriores, impleméntalo de la forma más limpia, directa y mantenible posible, priorizando funcionalidad comprobable. Evita soluciones solo simuladas salvo cuando el enunciado lo permita explícitamente. Usa base de datos para persistencia real de datos; no dejes persistencia principal en JSON.

Cada carpeta debe quedar autocontenida, con su propio `README.md`, `MANUAL_TECNICO.md`, `MANUAL_USUARIO.md`, archivos de configuración, instrucciones de instalación, ejecución, pruebas y evidencias. Mantén commits descriptivos y no mezcles cambios de `practica3` con `proyecto_f2` en el mismo paso si se puede evitar.

## Ubicación obligatoria

Crea y trabaja únicamente dentro de:

```text
proyecto_f2/
```

No mezcles archivos con `practica3`. El ZIP de facturas no pertenece a este proyecto.

## Archivos fuente disponibles

Usa estos recursos como fuente principal:

```text
Proyecto 2 VACASJUN 2026.docx.pdf
proyecto_f2/transcripcion_proyecto_f2.md
```

## Objetivo del sistema

Implementar **Smart Warehouse**, una simulación de bodega inteligente donde uno o más robots transportan paquetes hacia zonas de entrega. La toma de decisiones principal debe originarse en reglas de inferencia implementadas en **Prolog**, integradas con un backend en Python y una interfaz web visual.

## Requisitos obligatorios que debes cumplir

Implementa como mínimo:

1. Base de conocimiento en SWI-Prolog para decisiones de robots.
2. Mapa de simulación de al menos **10x10 casillas**.
3. Interfaz para iniciar, pausar, reiniciar y ejecutar simulación.
4. Modo automático y modo paso a paso.
5. Al menos **6 reglas de inferencia** sobre navegación, transporte y entrega.
6. En Prolog deben existir hechos, reglas, variables, listas y al menos un corte `!`.
7. Al menos **1 robot funcional**.
8. Al menos **5 paquetes**.
9. Al menos **2 zonas de entrega**.
10. Al menos **8 obstáculos** distribuidos en el mapa.
11. Cada paquete debe tener zona de entrega válida.
12. Backend en Python con FastAPI o Flask para comunicarse con Prolog.
13. Integración frontend/backend/Prolog real.
14. Visualización del estado actual de robots, paquetes, obstáculos y zonas.
15. Acciones mínimas originadas en Prolog:
    - `mover_arriba`
    - `mover_abajo`
    - `mover_izquierda`
    - `mover_derecha`
    - `recoger_paquete`
    - `entregar_paquete`
    - `esperar`
16. Estadísticas de ejecución: entregas realizadas, movimientos, eficiencia, tiempo y paquetes pendientes.
17. Historial de simulaciones en base de datos real. No uses JSON como persistencia principal.
18. Dashboard de estadísticas.
19. Documento técnico.
20. Manual de usuario.
21. Evidencias de funcionamiento.

## Restricción crítica

La lógica principal de navegación, selección de ruta, recolección y entrega debe estar en Prolog. Python y JavaScript solo coordinan, visualizan y ejecutan la acción devuelta por Prolog. No resuelvas la decisión final del robot exclusivamente en Python o JavaScript.

## Estructura mínima recomendada

```text
proyecto_f2/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   │   ├── prolog_service.py
│   │   │   ├── simulation_service.py
│   │   │   ├── metrics_service.py
│   │   │   └── history_service.py
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── prolog/
│   ├── warehouse.pl
│   ├── facts.pl
│   ├── rules.pl
│   └── queries.pl
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── css/
│   └── js/
├── docs/
│   └── evidencias/
├── docker-compose.yml
├── .env.example
├── README.md
├── MANUAL_TECNICO.md
├── MANUAL_USUARIO.md
└── transcripcion_proyecto_f2.md
```

## API mínima sugerida

```text
GET    /api/health
GET    /api/simulation/state
POST   /api/simulation/start
POST   /api/simulation/pause
POST   /api/simulation/reset
POST   /api/simulation/step
POST   /api/simulation/auto
GET    /api/robots
GET    /api/packages
GET    /api/obstacles
GET    /api/zones
GET    /api/metrics
GET    /api/history
GET    /api/history/{id}
```

## Prolog mínimo esperado

Diseña hechos y reglas claras. Ejemplo conceptual, puedes mejorarlo:

```prolog
robot(r1, posicion(1,1), libre).
paquete(p1, posicion(4,3), zona_a, pendiente).
zona_entrega(zona_a, posicion(8,8)).
obstaculo(posicion(2,2)).
mapa(10,10).

accion(Robot, recoger_paquete) :- puede_recoger(Robot), !.
accion(Robot, entregar_paquete) :- puede_entregar(Robot), !.
accion(Robot, mover_derecha) :- decision_movimiento(Robot, mover_derecha), !.
accion(_, esperar).
```

Debe existir una consulta desde backend que solicite la siguiente acción y Prolog debe responder la acción. Documenta las consultas usadas.

## Base de datos mínima

Aunque el PDF no exige base de datos de forma tan explícita como la práctica, usa persistencia real para cumplir con historial y estadísticas de forma seria y coherente con los proyectos anteriores:

- `simulations`
- `simulation_steps`
- `robots`
- `packages`
- `metrics`

## Frontend mínimo

La interfaz debe tener:

- Mapa visual 10x10.
- Leyenda: robot, paquete, obstáculo, zona de entrega y casilla vacía.
- Botones: iniciar, pausar, reiniciar, paso a paso, automático.
- Panel de estado del robot.
- Panel de paquetes pendientes/entregados.
- Dashboard de estadísticas.
- Historial de simulaciones.

## Criterios de aceptación

Al terminar, verifica y documenta:

- El mapa 10x10 se renderiza correctamente.
- Hay mínimo 1 robot, 5 paquetes, 2 zonas y 8 obstáculos.
- El usuario puede iniciar, pausar, reiniciar y ejecutar paso a paso.
- En cada paso el backend consulta Prolog.
- Prolog devuelve la acción y esa acción se refleja en el frontend.
- El robot recoge al menos un paquete y lo entrega exitosamente.
- Las decisiones principales no están hardcodeadas en JavaScript/Python.
- Se generan estadísticas.
- Se guarda historial en base de datos.
- Existe `MANUAL_TECNICO.md` y `MANUAL_USUARIO.md` dentro de `proyecto_f2/`.

## Manual técnico obligatorio

Crea `proyecto_f2/MANUAL_TECNICO.md` con:

- Resumen del sistema.
- Arquitectura y diagrama Mermaid.
- Tecnologías utilizadas.
- Estructura de carpetas.
- Integración frontend/backend/Prolog.
- Explicación de hechos, reglas, listas, variables y corte `!`.
- Reglas de inferencia implementadas.
- Consultas Prolog usadas por el backend.
- API REST.
- Modelo de base de datos.
- Flujo de simulación.
- Estadísticas e historial.
- Docker/Docker Compose, aunque Docker sea opcional en el PDF.
- Instrucciones de instalación, ejecución y pruebas.
- Distribución del trabajo entre integrantes, aunque sea en formato plantilla si no se conocen los nombres.
- Posibles mejoras futuras.

## Manual de usuario obligatorio

Crea `proyecto_f2/MANUAL_USUARIO.md` con:

- Cómo iniciar el sistema.
- Cómo abrir la interfaz web.
- Cómo interpretar el mapa y la leyenda.
- Cómo iniciar, pausar, reiniciar y ejecutar paso a paso.
- Cómo leer el estado de robots y paquetes.
- Cómo revisar estadísticas.
- Cómo consultar historial.
- Qué hacer si la simulación se detiene o hay error.

## Orden de trabajo

1. Lee la transcripción completa del enunciado.
2. Revisa los proyectos anteriores solo como guía de estructura.
3. Crea `proyecto_f2/` y su estructura.
4. Implementa Prolog primero.
5. Prueba Prolog por consola con consultas básicas.
6. Implementa backend Python y servicio de comunicación con Prolog.
7. Implementa frontend visual.
8. Implementa estadísticas, historial y persistencia.
9. Agrega Docker Compose.
10. Crea manual técnico y manual de usuario.
11. Prueba que el robot pueda completar al menos una entrega real.

## Transcripción base del enunciado

Usa como referencia completa el archivo `proyecto_f2/transcripcion_proyecto_f2.md`. No contradigas el PDF original. Si hay conflicto entre este prompt y el PDF, prioriza el PDF y documenta la decisión.
