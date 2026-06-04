# Manual de Usuario

## Sistema de ruta más corta entre ciudades

Este manual explica cómo utilizar la aplicación desarrollada para encontrar la ruta más corta entre ciudades conectadas por carreteras.

El sistema utiliza una interfaz web donde el usuario puede seleccionar una ciudad de origen y una ciudad de destino. Luego, la aplicación consulta al backend y muestra la ruta recomendada, la distancia total y las rutas alternativas disponibles.

---

## Requisitos previos

Antes de usar el sistema, se debe contar con:

- Python instalado.
- SWI-Prolog instalado.
- Backend ejecutándose correctamente.
- Navegador web actualizado.
- Archivos del proyecto descargados o clonados desde GitHub.

---

## Iniciar el backend

1. Abrir una terminal.
2. Entrar a la carpeta `backend`.

~~~bash
cd backend
~~~

3. Activar el entorno virtual.

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

4. Ejecutar el servidor:

~~~bash
uvicorn app.main:app --reload
~~~

5. Verificar que el backend esté funcionando entrando a:

~~~text
http://127.0.0.1:8000
~~~

Si todo está correcto, se mostrará un mensaje indicando que la API está funcionando.

---

## Abrir el frontend

Existen dos formas recomendadas.

### Opción 1: Usando Python

1. Abrir otra terminal.
2. Entrar a la carpeta `frontend`.

~~~bash
cd frontend
~~~

3. Ejecutar:

~~~bash
python -m http.server 5500
~~~

4. Abrir en el navegador:

~~~text
http://localhost:5500
~~~

---

### Opción 2: Usando Live Server

1. Abrir el proyecto en Visual Studio Code.
2. Instalar la extensión Live Server.
3. Dar clic derecho sobre `frontend/index.html`.
4. Seleccionar `Open with Live Server`.

---

## Buscar la ruta más corta

Para buscar una ruta:

1. Ir a la sección `Buscar ruta`.
2. Seleccionar una ciudad en el campo `Ciudad origen`.
3. Seleccionar una ciudad en el campo `Ciudad destino`.
4. Presionar el botón `Buscar ruta más corta`.

El sistema mostrará:

- Ruta recomendada.
- Ciudades por las que se debe pasar.
- Distancia total en kilómetros.

Ejemplo:

~~~text
guatemala → antigua → chimaltenango → quetzaltenango
Distancia total: 230 km
~~~

---

## Ver todas las rutas posibles

Para consultar todas las rutas:

1. Seleccionar ciudad de origen.
2. Seleccionar ciudad de destino.
3. Presionar el botón `Ver todas las rutas`.

El sistema mostrará una lista de rutas ordenadas de menor a mayor distancia.

Cada ruta mostrará:

- Número de ruta.
- Secuencia de ciudades.
- Distancia total.

---

## Agregar una nueva conexión

El sistema permite agregar nuevas conexiones de forma dinámica.

Pasos:

1. Ir a la sección `Agregar nueva conexión`.
2. Escribir la ciudad origen.
3. Escribir la ciudad destino.
4. Escribir la distancia en kilómetros.
5. Presionar `Agregar conexión`.

Ejemplo:

| Campo | Valor |
|---|---|
| Origen | Guatemala |
| Destino | Peten |
| Distancia | 480 |

Después de agregarla, la nueva ciudad o conexión aparecerá en los selectores del sistema.

---

## Eliminar una conexión

Para eliminar una conexión:

1. Ir a la sección `Eliminar conexión`.
2. Escribir la ciudad origen.
3. Escribir la ciudad destino.
4. Presionar `Eliminar conexión`.

El sistema eliminará la conexión tanto de Prolog en ejecución como del archivo donde se almacenan las conexiones.

---

## Limpiar resultados

El botón `Limpiar` permite borrar los resultados actuales de la pantalla y realizar una nueva búsqueda.

---

## Mensajes comunes del sistema

### No se encontró una ruta

Este mensaje aparece cuando no existe una conexión posible entre la ciudad origen y la ciudad destino.

### El origen y destino no pueden ser iguales

Este mensaje aparece cuando se selecciona la misma ciudad como origen y destino.

### No se pudo agregar la conexión

Puede ocurrir por las siguientes razones:

- La conexión ya existe.
- La distancia ingresada no es válida.
- Algún campo está vacío.

### Error al consultar la ruta

Puede ocurrir si el backend no está encendido o si existe un problema de comunicación entre el frontend y la API.

---

## Recomendaciones de uso

- Mantener el backend encendido mientras se usa el frontend.
- Verificar que SWI-Prolog esté instalado correctamente.
- Usar nombres de ciudades claros.
- Evitar agregar conexiones duplicadas.
- Ingresar distancias mayores que cero.

---

## Ejemplo completo de uso

1. Encender backend.
2. Abrir frontend.
3. Seleccionar:

~~~text
Origen: guatemala
Destino: quetzaltenango
~~~

4. Presionar `Buscar ruta más corta`.
5. Revisar el resultado.
6. Presionar `Ver todas las rutas` para comparar alternativas.
7. Agregar una nueva conexión si se desea ampliar la red de ciudades.

