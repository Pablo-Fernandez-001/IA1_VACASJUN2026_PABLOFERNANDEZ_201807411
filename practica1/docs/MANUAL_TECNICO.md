# Manual Técnico

## Nombre del proyecto

Ruta más corta entre ciudades usando Prolog, Python y frontend web.

---

## Objetivo técnico

Desarrollar un sistema híbrido capaz de encontrar rutas entre ciudades, calcular distancias y determinar la ruta más corta utilizando Prolog como motor lógico principal.

Python funciona únicamente como capa de integración entre el frontend y Prolog.  
La lógica de búsqueda y optimización no se implementa en Python.

---

## Arquitectura implementada

El backend utiliza una arquitectura orientada por funcionalidades con separación por capas internas.

Esta arquitectura permite dividir el sistema por responsabilidades, evitando concentrar toda la lógica en un único archivo.

La organización general es:

~~~text
Frontend
   ↓
API FastAPI
   ↓
Features del backend
   ↓
Prolog Engine
   ↓
SWI-Prolog
   ↓
rutas.pl
~~~

---

## Módulos del backend

### `core`

Contiene configuraciones generales del proyecto.

Archivo principal:

~~~text
backend/app/core/config.py
~~~

Responsabilidades:

- Definir rutas principales del proyecto.
- Definir ubicación del archivo Prolog.
- Centralizar configuraciones reutilizables.

---

### `prolog_engine`

Contiene la integración directa entre Python y SWI-Prolog.

Archivos principales:

~~~text
backend/app/prolog_engine/engine.py
backend/app/prolog_engine/serializer.py
~~~

Responsabilidades:

- Cargar el archivo `rutas.pl`.
- Ejecutar consultas Prolog.
- Convertir nombres de ciudades a átomos válidos.
- Agregar conexiones dinámicas.
- Eliminar conexiones dinámicas.
- Persistir cambios en el archivo Prolog.
- Normalizar respuestas de Prolog para enviarlas como JSON.

---

### `cities_feature`

Módulo encargado de consultar las ciudades disponibles.

Archivos principales:

~~~text
backend/app/cities_feature/router.py
backend/app/cities_feature/service.py
~~~

Responsabilidades:

- Exponer endpoint para listar ciudades.
- Consultar a Prolog mediante `ciudades(Ciudades)`.
- Devolver la lista de ciudades al frontend.

Endpoint:

~~~text
GET /ciudades/
~~~

---

### `routes_feature`

Módulo encargado de consultar rutas.

Archivos principales:

~~~text
backend/app/routes_feature/router.py
backend/app/routes_feature/service.py
backend/app/routes_feature/schemas.py
~~~

Responsabilidades:

- Consultar ruta más corta.
- Consultar todas las rutas posibles.
- Convertir resultados de Prolog en JSON.
- Manejar errores cuando no existen rutas.

Endpoints:

~~~text
GET /rutas/mas-corta
GET /rutas/todas
~~~

---

### `connections_feature`

Módulo encargado de administrar conexiones.

Archivos principales:

~~~text
backend/app/connections_feature/router.py
backend/app/connections_feature/service.py
backend/app/connections_feature/schemas.py
~~~

Responsabilidades:

- Agregar conexiones nuevas.
- Eliminar conexiones existentes.
- Validar datos de entrada.
- Enviar cambios hacia Prolog.
- Permitir cambios dinámicos sin usar base de datos.

Endpoints:

~~~text
POST /conexiones/
DELETE /conexiones/
~~~

---

## Archivo Prolog

El archivo principal de lógica se encuentra en:

~~~text
prolog/rutas.pl
~~~

Este archivo contiene:

- Base de conocimiento.
- Hechos de conexión.
- Reglas para caminos bidireccionales.
- Reglas para detectar ciudades.
- Búsqueda recursiva de rutas.
- Prevención de ciclos.
- Cálculo de distancias.
- Consulta de todas las rutas posibles.
- Selección de la ruta más corta.
- Agregado dinámico de conexiones.
- Eliminación dinámica de conexiones.

---

## Base de conocimiento

Las conexiones se representan mediante hechos de la forma:

~~~prolog
conexion(Origen, Destino, Distancia).
~~~

Ejemplo:

~~~prolog
conexion(guatemala, antigua, 45).
~~~

Esto significa que existe una conexión entre Guatemala y Antigua con una distancia de 45 kilómetros.

---

## Caminos bidireccionales

Para evitar escribir dos veces cada carretera, se utiliza la regla `camino/3`:

~~~prolog
camino(A, B, D) :-
    conexion(A, B, D).

camino(A, B, D) :-
    conexion(B, A, D).
~~~

Con esta regla, una conexión registrada en una dirección puede usarse también en sentido contrario.

---

## Detección de ciudades

Una ciudad puede aparecer como origen o destino dentro de una conexión.

~~~prolog
ciudad(C) :-
    conexion(C, _, _).

ciudad(C) :-
    conexion(_, C, _).
~~~

Luego, para obtener todas las ciudades sin repetidos, se usa:

~~~prolog
ciudades(ListaCiudades) :-
    findall(C, ciudad(C), Ciudades),
    sort(Ciudades, ListaCiudades).
~~~

`findall/3` obtiene todas las ciudades posibles y `sort/2` ordena la lista y elimina duplicados.

---

## Búsqueda de rutas

La búsqueda inicia con el predicado:

~~~prolog
ruta(Origen, Destino, Ruta, Distancia)
~~~

Este predicado recibe:

| Parámetro | Descripción |
|---|---|
| `Origen` | Ciudad inicial |
| `Destino` | Ciudad final |
| `Ruta` | Lista de ciudades recorridas |
| `Distancia` | Distancia total de la ruta |

La búsqueda real se realiza mediante recursividad con `viajar/5`.

---

## Prevención de ciclos

Para evitar que una ciudad se repita en una misma ruta, se mantiene una lista de ciudades visitadas.

La validación principal es:

~~~prolog
\+ member(Intermedio, Visitados)
~~~

Esto significa que la ciudad intermedia no debe estar en la lista de ciudades ya visitadas.

Gracias a esta validación se evitan rutas infinitas como:

~~~text
guatemala → antigua → guatemala → antigua
~~~

---

## Cálculo de distancias

La distancia total se calcula acumulando las distancias parciales:

~~~prolog
DistanciaTotal is Distancia1 + Distancia2.
~~~

Prolog suma la distancia desde el origen hacia una ciudad intermedia y luego la distancia desde esa ciudad intermedia hasta el destino.

---

## Todas las rutas posibles

Para obtener todas las rutas se utiliza:

~~~prolog
rutas_posibles(Origen, Destino, RutasOrdenadas)
~~~

Internamente se usa `findall/3`:

~~~prolog
findall(
    [Distancia, Ruta],
    ruta(Origen, Destino, Ruta, Distancia),
    Rutas
)
~~~

Cada solución se guarda con la distancia primero para que luego pueda ordenarse fácilmente.

---

## Ruta más corta

La ruta más corta se obtiene con:

~~~prolog
ruta_mas_corta(Origen, Destino, MejorRuta, MenorDistancia)
~~~

Esta regla toma la primera ruta de la lista ordenada por distancia:

~~~prolog
ruta_mas_corta(Origen, Destino, MejorRuta, MenorDistancia) :-
    rutas_posibles(Origen, Destino, [[MenorDistancia, MejorRuta]|_]).
~~~

Como las rutas están ordenadas de menor a mayor distancia, la primera corresponde a la ruta óptima.

---

## Agregado dinámico de conexiones

Para permitir cambios dinámicos, el archivo Prolog declara:

~~~prolog
:- dynamic conexion/3.
~~~

Esto permite modificar hechos `conexion/3` durante la ejecución.

El predicado para agregar conexiones es:

~~~prolog
agregar_conexion(Origen, Destino, Distancia) :-
    Distancia > 0,
    \+ conexion_existente(Origen, Destino),
    assertz(conexion(Origen, Destino, Distancia)).
~~~

`assertz/1` agrega una nueva conexión a la base de conocimiento en memoria.

Además, Python persiste la conexión escribiéndola en el archivo `rutas.pl`, para que el cambio no se pierda al reiniciar el servidor.

---

## Eliminación dinámica de conexiones

El predicado utilizado es:

~~~prolog
eliminar_conexion(Origen, Destino) :-
    retractall(conexion(Origen, Destino, _)),
    retractall(conexion(Destino, Origen, _)).
~~~

`retractall/1` elimina todos los hechos que coincidan con la conexión indicada.

---

## Integración Python-Prolog

La integración se realiza mediante PySwip.

El flujo es:

~~~text
Frontend envía solicitud HTTP
        ↓
FastAPI recibe la solicitud
        ↓
Service correspondiente procesa la petición
        ↓
PrologEngine ejecuta una consulta Prolog
        ↓
SWI-Prolog responde
        ↓
Python transforma la respuesta a JSON
        ↓
Frontend muestra el resultado
~~~

Ejemplo de consulta desde Python:

~~~python
query = f"ruta_mas_corta({origen_atom}, {destino_atom}, Ruta, Distancia)"
result = self.engine.query(query)
~~~

La consulta se ejecuta en Prolog, no en Python.

---

## Frontend

El frontend se compone de:

~~~text
frontend/index.html
frontend/style.css
frontend/app.js
~~~

Responsabilidades:

- Mostrar formulario de búsqueda.
- Cargar ciudades dinámicamente.
- Consultar la ruta más corta.
- Consultar todas las rutas posibles.
- Agregar nuevas conexiones.
- Eliminar conexiones.
- Mostrar mensajes de error.
- Limpiar resultados.

---

## Persistencia sin base de datos

La práctica indica que no se puede usar base de datos.

Por ello, el sistema maneja la persistencia de conexiones agregadas escribiendo directamente en el archivo Prolog `rutas.pl`.

Esto permite:

- Mantener Prolog como fuente de conocimiento.
- Evitar el uso de bases de datos.
- Conservar conexiones nuevas después de reiniciar la aplicación.

---

## Validaciones implementadas

| Validación | Lugar |
|---|---|
| Distancia mayor que cero | Prolog y Pydantic |
| Ciudad origen requerida | Pydantic |
| Ciudad destino requerida | Pydantic |
| Evitar conexiones duplicadas | Prolog |
| Evitar ciclos en rutas | Prolog |
| Origen diferente de destino | Prolog y frontend |
| Mensajes cuando no hay ruta | Backend y frontend |

---

## Restricciones cumplidas

- La búsqueda de rutas está implementada en Prolog.
- El cálculo de distancia está implementado en Prolog.
- La ruta más corta se determina en Prolog.
- Python no implementa el algoritmo de rutas.
- Python solo funciona como backend de integración.
- No se utiliza base de datos.
- El frontend permite consultar y administrar conexiones.
- El sistema tiene arquitectura orientada por funcionalidades.
- Se permite el cambio dinámico de rutas.

---

## Posibles mejoras futuras

- Mostrar un grafo visual de ciudades y conexiones.
- Agregar edición de distancias.
- Agregar importación/exportación de conexiones.
- Agregar pruebas unitarias al backend.
- Mejorar el diseño visual del frontend.
- Validar nombres repetidos con tildes o variantes.
- Agregar logs de consultas realizadas.
- Mostrar estadísticas de rutas, como ruta más larga, promedio de distancia y número total de rutas.

---

## Evidencias recomendadas

Para demostrar el funcionamiento del sistema se recomienda incluir capturas de:

1. Instalación o versión de SWI-Prolog.
2. Consulta directa en Prolog.
3. Backend ejecutándose con Uvicorn.
4. Documentación automática en `/docs`.
5. Frontend cargando ciudades.
6. Búsqueda de ruta más corta.
7. Visualización de todas las rutas.
8. Agregado dinámico de conexión.
9. Eliminación dinámica de conexión.
10. Archivo `rutas.pl` actualizado.
11. Repositorio en GitHub.

