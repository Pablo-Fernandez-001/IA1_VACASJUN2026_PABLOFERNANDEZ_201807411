# Ruta más corta entre ciudades en Prolog

## Descripción del proyecto

Este proyecto corresponde a la Práctica 1 del curso Inteligencia Artificial 1.  
El objetivo principal es desarrollar un sistema capaz de encontrar la ruta más corta entre ciudades conectadas por carreteras, utilizando Prolog como motor lógico principal y Python como backend de integración.

El sistema permite:

- Consultar ciudades disponibles.
- Buscar la ruta más corta entre dos ciudades.
- Mostrar todas las rutas posibles entre dos ciudades.
- Calcular la distancia total de cada ruta.
- Agregar nuevas conexiones dinámicamente.
- Eliminar conexiones existentes.
- Utilizar una interfaz gráfica web para facilitar el uso del sistema.

La lógica de búsqueda, cálculo de rutas, prevención de ciclos y selección de la ruta más corta se implementa exclusivamente en Prolog.  
Python no calcula rutas directamente, sino que únicamente consulta a Prolog mediante PySwip y devuelve los resultados al frontend.

---

## Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| SWI-Prolog | Motor lógico y base de conocimiento |
| Python 3.11+ | Backend de integración |
| FastAPI | API REST |
| PySwip | Comunicación entre Python y Prolog |
| HTML | Estructura del frontend |
| CSS | Diseño visual |
| JavaScript | Consumo dinámico de la API |
| Git/GitHub | Control de versiones y repositorio |

---

## Arquitectura del sistema

El backend utiliza una arquitectura orientada por funcionalidades con separación por capas internas.

La estructura general es:

~~~text
Frontend HTML/CSS/JS
        ↓
Backend FastAPI
        ↓
Features del backend
        ↓
Prolog Engine
        ↓
SWI-Prolog
        ↓
Archivo rutas.pl
~~~

Cada funcionalidad del backend se encuentra separada en su propio módulo:

| Módulo | Responsabilidad |
|---|---|
| `cities_feature` | Consulta de ciudades disponibles |
| `routes_feature` | Consulta de ruta más corta y rutas posibles |
| `connections_feature` | Administración dinámica de conexiones |
| `prolog_engine` | Comunicación entre Python y Prolog |
| `core` | Configuración general del backend |

---

## Estructura del proyecto

~~~text
practica1/
│
├── backend/
│   ├── venv/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── core/
│       │   └── config.py
│       ├── prolog_engine/
│       │   ├── engine.py
│       │   └── serializer.py
│       ├── cities_feature/
│       │   ├── router.py
│       │   └── service.py
│       ├── routes_feature/
│       │   ├── router.py
│       │   ├── service.py
│       │   └── schemas.py
│       └── connections_feature/
│           ├── router.py
│           ├── service.py
│           └── schemas.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── prolog/
│   └── rutas.pl
│
├── docs/
│   ├── MANUAL_USUARIO.md
│   └── MANUAL_TECNICO.md
│
├── evidencias/
│
└── README.md
~~~

---

## Manuales

- [Manual de Usuario](docs/MANUAL_USUARIO.md)
- [Manual Técnico](docs/MANUAL_TECNICO.md)

---

## Instalación

### 1. Instalar SWI-Prolog

Descargar e instalar SWI-Prolog desde:

~~~text
https://www.swi-prolog.org
~~~

Verificar instalación:

~~~bash
swipl --version
~~~

---

### 2. Crear y activar entorno virtual

Desde la carpeta `backend`:

~~~bash
python -m venv venv
~~~

En Windows CMD:

~~~cmd
venv\Scripts\activate
~~~

En PowerShell:

~~~powershell
.\venv\Scripts\Activate.ps1
~~~

En Linux o WSL:

~~~bash
source venv/bin/activate
~~~

---

### 3. Instalar dependencias

Desde `backend`:

~~~bash
pip install -r requirements.txt
~~~

Si no existe `requirements.txt`, instalar manualmente:

~~~bash
pip install fastapi uvicorn pyswip pydantic
pip freeze > requirements.txt
~~~

---

## Ejecución del backend

Desde la carpeta `backend`:

~~~bash
uvicorn app.main:app --reload
~~~

El backend se ejecutará en:

~~~text
http://127.0.0.1:8000
~~~

La documentación automática de la API estará disponible en:

~~~text
http://127.0.0.1:8000/docs
~~~

---

## Ejecución del frontend

Desde la carpeta `frontend`:

~~~bash
python -m http.server 5500
~~~

Luego abrir en el navegador:

~~~text
http://localhost:5500
~~~

También se puede abrir con la extensión Live Server de Visual Studio Code.

---

## Pruebas y capturas con Cypress

Desde la carpeta `practica1`:

~~~bash
npm install
npm run evidencias
~~~

El comando levanta el backend real en `http://127.0.0.1:8000`, sirve el frontend con Live Server en `http://127.0.0.1:5500` y ejecuta Cypress contra ambos servicios.

Las capturas generadas quedan en:

~~~text
evidencias/cypress/screenshots
~~~

La suite valida endpoints reales del backend, abre `/docs` de FastAPI y consulta la ruta mas corta desde el frontend sin usar mocks.

---

## Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/ciudades/` | Lista todas las ciudades |
| GET | `/rutas/mas-corta?origen=X&destino=Y` | Obtiene la ruta más corta |
| GET | `/rutas/todas?origen=X&destino=Y` | Obtiene todas las rutas posibles |
| POST | `/conexiones/` | Agrega una conexión dinámica |
| DELETE | `/conexiones/` | Elimina una conexión |

---

## Ejemplo de uso

Consultar la ruta más corta entre Guatemala y Quetzaltenango:

~~~text
http://127.0.0.1:8000/rutas/mas-corta?origen=guatemala&destino=quetzaltenango
~~~

Respuesta esperada:

~~~json
{
  "ruta": [
    "guatemala",
    "antigua",
    "chimaltenango",
    "quetzaltenango"
  ],
  "distancia": 230
}
~~~

---

## Restricciones cumplidas

- La lógica de búsqueda está implementada en Prolog.
- Python no implementa el algoritmo de rutas.
- Python actúa como capa de integración.
- No se utiliza base de datos.
- El sistema permite agregar conexiones dinámicamente.
- El frontend permite consultar rutas de forma visual.
- Se muestran rutas posibles y distancia total.
- Se evita repetir ciudades dentro de una misma ruta.

---

## Repositorio

El repositorio debe tener el formato solicitado:

~~~text
[IA1]_VACASJUN2026_PABLOFERNANDEZ_201807411
~~~
