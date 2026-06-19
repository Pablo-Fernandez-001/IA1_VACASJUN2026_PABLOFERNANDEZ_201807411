# Manual de Usuario - Doctor Byte

## 1. Descripción

Doctor Byte es un sistema experto para realizar diagnósticos preliminares de fallas comunes en computadoras. El usuario selecciona síntomas observados y el sistema consulta reglas almacenadas y evaluadas en SWI-Prolog.

La aplicación permite:

- Seleccionar síntomas y solicitar un diagnóstico.
- Consultar resultados alternativos ordenados por probabilidad.
- Revisar severidad, porcentaje del problema, efectividad estimada y ruta de solución.
- Guardar automáticamente cada consulta en un historial.
- Enviar el diagnóstico principal a Telegram.
- Administrar síntomas, fallas, recomendaciones y reglas sin editar manualmente los archivos Prolog.
- Configurar el bot y sus mensajes desde la interfaz.

> Doctor Byte es una herramienta académica y de orientación preliminar. No reemplaza el diagnóstico físico de un técnico especializado.

## 2. Videos demostrativos

### Presentación del proyecto

- [Ver presentación de Doctor Byte en Canva](https://canva.link/90cnkt7xuu9z3zx)

### Videos

Los videos se encuentran dentro de `docs/videos`. Se pueden abrir directamente desde los siguientes enlaces:

| Video | Duración | Enlace |
|---|---:|---|
| Demostración web 1 | 5:22 | [Abrir video 1](<videos/Doctor Byte - Google Chrome 2026-06-13 08-34-47.mp4>) |
| Demostración web 2 | 2:58 | [Abrir video 2](<videos/Doctor Byte - Google Chrome 2026-06-13 08-41-20.mp4>) |
| Demostración web 3 | 1:00 | [Abrir video 3](<videos/Doctor Byte - Google Chrome 2026-06-13 08-49-02.mp4>) |
| Demostración de Doctor Byte en Telegram | 1:31 | [Abrir video 4](<videos/‎dr_byte – (28056) 2026-06-13 08-51-28.mp4>) |

Si el visor Markdown del editor no reproduce archivos MP4, se debe hacer clic derecho sobre el enlace, abrir la ubicación del archivo y reproducirlo con el navegador o un reproductor multimedia.

## 3. Requisitos

### Ejecución recomendada con Docker

- Windows 10 u 11.
- Docker Desktop iniciado y usando contenedores Linux.
- PowerShell.
- Un navegador moderno.
- Conexión a Internet únicamente si se utilizará Telegram.

### Ejecución local para desarrollo

- Python 3.12 o compatible.
- SWI-Prolog disponible mediante el comando `swipl`.
- Node.js y npm.
- PowerShell.

## 4. Preparación inicial

Abrir PowerShell en la carpeta `proyecto_f1` y crear el archivo de variables de entorno:

```powershell
Copy-Item .env.example .env
```

Para utilizar Telegram, abrir `.env` y completar al menos:

```env
TELEGRAM_BOT_TOKEN=token_entregado_por_BotFather
TELEGRAM_DEFAULT_CHAT_ID=
```

No se debe publicar el archivo `.env`, porque puede contener el token privado del bot.

## 5. Iniciar con Docker

### Opción rápida

```powershell
.\scripts\start_docker_windows.ps1
```

El script verifica Docker, construye las imágenes, inicia los servicios y espera sus respuestas de salud.

### Opción manual

```powershell
docker compose up -d --build
docker compose ps
```

Cuando todos los servicios estén listos, abrir:

| Componente | Dirección |
|---|---|
| Aplicación web | `http://localhost:8081` |
| Swagger del API Gateway | `http://localhost:8000/docs` |
| Estado del API Gateway | `http://localhost:8000/api/health` |
| Swagger del servicio Prolog | `http://localhost:8001/docs` |
| Estado del servicio Telegram | `http://localhost:8002/health` |

## 6. Iniciar en modo desarrollo

Preparar dependencias una sola vez:

```powershell
.\scripts\setup_windows.ps1
```

Después iniciar todos los procesos locales:

```powershell
.\scripts\start_dev_windows.ps1
```

En este modo el frontend utiliza `http://localhost:5173`. Los archivos de salida se almacenan en `logs/`.

## 7. Pantalla principal

La cabecera muestra el nombre **Doctor Byte**, una descripción del sistema y contadores de:

- Síntomas registrados.
- Fallas registradas.
- Recomendaciones registradas.
- Reglas Prolog registradas.

La zona principal se divide en:

1. Panel de diagnóstico.
2. Catálogo de síntomas.
3. Resultado principal y alternativas, cuando ya se ejecutó una consulta.
4. Historial.
5. Administración de conocimiento.

## 8. Realizar un diagnóstico

1. Escribir el nombre de la persona en **Nombre del usuario**.
2. Buscar un síntoma por nombre, ID o categoría.
3. Usar el filtro de categoría si se desea reducir el catálogo.
4. Hacer clic sobre cada tarjeta de síntoma observado.
5. Confirmar los síntomas dentro de **Síntomas seleccionados**.
6. Opcionalmente activar **Enviar resultado por Telegram**.
7. Si se activó Telegram, escribir un chat ID o utilizar el configurado por defecto.
8. Presionar **Solicitar diagnóstico**.

La selección puede modificarse de dos maneras:

- Haciendo clic nuevamente sobre una tarjeta activa.
- Haciendo clic sobre la etiqueta del síntoma dentro del cuadro de selección.

El botón **Limpiar selección** borra los síntomas y el resultado actual.

## 9. Interpretar los resultados

El diagnóstico principal muestra:

| Campo | Significado |
|---|---|
| Diagnóstico | Falla asociada a la regla con mayor puntuación. |
| Probabilidad | Coincidencia ponderada entre síntomas seleccionados y síntomas de la regla. |
| Categoría | Área de la falla, por ejemplo hardware, software, red o seguridad. |
| Severidad | Nivel cualitativo: baja, media, alta o crítica. |
| Problema | Porcentaje de síntomas requeridos que fueron encontrados. |
| Efectividad | Estimación derivada de la coincidencia, limitada a un máximo de 98 %. |
| Ruta de solución | Pasos ordenados para revisar o resolver la falla. |

Debajo aparece **Diagnósticos posibles**. Cada tarjeta se puede expandir para revisar su propia ruta de solución. El sistema muestra alternativas porque una misma combinación de síntomas puede relacionarse con varias fallas.

## 10. Historial

Cada diagnóstico solicitado desde la web o desde Telegram se guarda en SQLite.

El historial permite:

- Ver el nombre del usuario.
- Ver el diagnóstico principal.
- Consultar la fecha de creación.
- Cargar nuevamente el resultado completo.
- Eliminar un registro.

Al cargar un registro, la interfaz recupera los síntomas seleccionados y el resultado almacenado. Esto no vuelve a ejecutar Prolog; muestra la fotografía del diagnóstico guardado en ese momento.

## 11. Administración del conocimiento

La sección **Administración de conocimiento** contiene cinco pestañas. Los cambios de síntomas, fallas, recomendaciones y reglas se guardan en `doctor_byte_knowledge.pl`.

### 11.1 Síntomas

Campos:

| Campo | Uso |
|---|---|
| ID | Identificador Prolog en minúsculas y con guiones bajos. |
| Nombre | Texto visible para el usuario. |
| Categoría | Agrupación usada en el filtro del catálogo. |
| Peso | Importancia entre 1 y 5 dentro de la puntuación. |

Para crear un síntoma:

1. Abrir la pestaña **Síntomas**.
2. Escribir un ID, por ejemplo `pantalla_parpadea`.
3. Escribir nombre y categoría.
4. Asignar un peso entre 1 y 5.
5. Presionar **Guardar síntoma**.

Al editar el ID de un síntoma, las referencias existentes en reglas se actualizan. Al eliminarlo, se retira de las listas de síntomas requeridos y de apoyo.

### 11.2 Fallas

Campos:

- ID de la falla.
- Nombre visible.
- Categoría.
- Severidad.
- Mensaje explicativo.
- Pasos de solución, uno por línea.

Los pasos se numeran automáticamente en el orden escrito.

Al cambiar el ID de una falla, sus recomendaciones y reglas se reasocian. Al eliminar una falla también se eliminan sus pasos, recomendaciones y reglas relacionadas.

### 11.3 Recomendaciones

Cada recomendación contiene:

- ID único.
- Falla asociada.
- Texto.
- Orden.

La falla debe existir antes de registrar una recomendación. El orden permite controlar la posición lógica de la recomendación.

### 11.4 Reglas diagnósticas

Una regla relaciona una falla con síntomas requeridos y síntomas de apoyo.

1. Abrir **Reglas diagnósticas**.
2. Escribir el ID. Se puede escribir texto normal; el sistema lo transforma a minúsculas y guiones bajos.
3. Seleccionar la falla diagnosticada.
4. Definir el puntaje mínimo entre 0 y 100.
5. Marcar cada síntoma como **Requerido**, **Apoyo** o dejarlo sin seleccionar.
6. Activar o desactivar la regla.
7. Presionar **Guardar regla**.

Los síntomas requeridos tienen multiplicador 2 y los síntomas de apoyo multiplicador 1. La aplicación impide guardar una regla sin síntomas y Prolog verifica que todas las referencias existan.

### 11.5 Configuración

Esta pestaña administra datos auxiliares guardados en SQLite:

- Chat ID predeterminado.
- Estado activo o inactivo del bot.
- Mensaje de bienvenida.
- Mensaje previo al diagnóstico.
- Mensaje utilizado cuando no hay diagnóstico.

Después de cambiar los campos se debe presionar **Guardar configuración**.

## 12. Configurar Telegram

### 12.1 Crear el bot

1. Abrir Telegram y buscar `@BotFather`.
2. Ejecutar `/newbot`.
3. Seguir las instrucciones de nombre y usuario.
4. Copiar el token recibido a `TELEGRAM_BOT_TOKEN` dentro de `.env`.
5. Reiniciar los servicios.

### 12.2 Abrir el bot y obtener el chat ID

```powershell
.\scripts\open_telegram_bot_windows.ps1
```

Presionar **Start** o enviar `/start`. Después ejecutar:

```powershell
.\scripts\telegram_chat_id_windows.ps1 -SaveFirst
```

El script guarda el primer chat privado encontrado como `TELEGRAM_DEFAULT_CHAT_ID`. Se deben reiniciar los servicios para cargar el nuevo valor.

### 12.3 Probar el envío

```powershell
.\scripts\telegram_test_windows.ps1
```

También se puede indicar un chat específico:

```powershell
.\scripts\telegram_test_windows.ps1 -ChatId "123456789"
```

### 12.4 Comandos del bot

```text
/start
/ayuda
/sintomas
/diagnosticar pantalla_negra,ventiladores_giran
```

El bot no contiene diagnósticos codificados. Consulta el API Gateway y este solicita la inferencia al servicio Prolog.

## 13. Detener el sistema

Para Docker:

```powershell
.\scripts\stop_docker_windows.ps1
```

O manualmente:

```powershell
docker compose down
```

Para el modo de desarrollo:

```powershell
.\scripts\stop_services_windows.ps1
```

No usar `docker compose down -v` si se desea conservar el historial y la configuración de SQLite, porque `-v` elimina el volumen `doctor-byte-data`.

## 14. Problemas frecuentes

### Docker Desktop no está iniciado

Abrir Docker Desktop, esperar a que el motor indique que está listo y volver a ejecutar `start_docker_windows.ps1`.

### El puerto ya está ocupado

Detener el modo local o Docker, según corresponda:

```powershell
.\scripts\stop_services_windows.ps1
.\scripts\stop_docker_windows.ps1
```

### La regla no se guarda

Comprobar que:

- Se seleccionó una falla existente.
- Se marcó al menos un síntoma requerido o de apoyo.
- Los síntomas existen en el catálogo.
- El ID no está repetido.

La interfaz normaliza IDs con espacios, mayúsculas y guiones. Por ejemplo, `Regla Pantalla Nueva` se guarda como `regla_pantalla_nueva`.

### Telegram no envía mensajes

Comprobar:

- `TELEGRAM_BOT_TOKEN` configurado.
- El usuario inició el bot con `/start`.
- Existe un chat ID válido.
- El bot está activo en la pestaña **Configuración**.
- El servicio responde en `http://localhost:8002/health`.

### El frontend no carga datos

Revisar:

```powershell
docker compose ps
docker compose logs api-gateway prolog-service
```

El API Gateway y el servicio Prolog deben aparecer saludables.

## 15. Conservación de datos

| Dato | Ubicación | Persistencia |
|---|---|---|
| Síntomas, fallas, recomendaciones, pasos y reglas | `doctor_byte_knowledge.pl` | Montaje de carpeta del host. |
| Historial y configuración | Volumen Docker `doctor-byte-data` | Volumen administrado por Docker. |
| Token y valores locales | `.env` | Archivo local no destinado al repositorio público. |

## 16. Documentación relacionada

- [Manual técnico](manual_tecnico.md)
- [Documento técnico resumido](documento_tecnico.md)
- [Arquitectura](arquitectura.mmd)
- [Casos de prueba](casos_prueba.md)
- [Guía de verificación](guia_verificacion.md)
- [Prompt para presentación en Canva AI](prompt_canva_ai.md)
