# Manual de Usuario - SmartBot

## 1. Descripción

SmartBot es una aplicación de preguntas frecuentes que permite administrar categorías, preguntas y respuestas desde un panel web. Los usuarios pueden consultar el mismo contenido mediante Telegram o desde una herramienta de prueba incluida en el panel.

Toda la información se almacena en una base de datos SQLite. Las preguntas y respuestas no están escritas dentro del código JavaScript o Python.

El sistema permite:

- Iniciar sesión como administrador.
- Consultar estadísticas e historial.
- Crear, editar y eliminar categorías.
- Crear, editar, activar y desactivar preguntas.
- Crear, editar, priorizar, activar y desactivar respuestas.
- Probar preguntas sin utilizar Telegram.
- Configurar el chat de Telegram y el mensaje para consultas desconocidas.
- Enviar mensajes de prueba a Telegram.
- Recibir preguntas libres desde un bot.
- Conservar los datos al reiniciar Docker.

## 2. Requisitos

Para la ejecución recomendada se necesita:

- Windows 10 u 11.
- Docker Desktop iniciado.
- PowerShell.
- Un navegador actualizado.
- Conexión a Internet si se utilizará Telegram.

Para utilizar el bot también se necesita:

- Una cuenta de Telegram.
- Un bot creado con `@BotFather`.
- El token privado del bot.

## 3. Preparación inicial

Abrir PowerShell dentro de la carpeta `practica2` y crear el archivo local de configuración:

```powershell
Copy-Item .env.example .env
```

El archivo `.env` contiene puertos, credenciales, secreto JWT y configuración de Telegram.

Los valores iniciales para evaluación son:

```env
ADMIN_USERNAME=IA1-User
ADMIN_PASSWORD=IA1-password@_new
```

El archivo `.env` no debe publicarse cuando contiene un token real de Telegram o un secreto JWT de producción.

## 4. Iniciar SmartBot

### Opción recomendada

```powershell
docker compose up -d --build
```

Comprobar el estado:

```powershell
docker compose ps
```

### Mediante el script de Windows

```powershell
.\scripts\start_docker_windows.ps1
```

Este script ejecuta `docker compose up --build` en primer plano. La terminal mostrará los logs y deberá permanecer abierta. Para trabajar en segundo plano se recomienda el comando con `-d` de la opción anterior.

## 5. Direcciones del sistema

| Componente | Dirección predeterminada |
|---|---|
| Panel administrativo | `http://localhost:8090` |
| API REST | `http://localhost:8100` |
| Swagger | `http://localhost:8100/docs` |
| Estado de la API | `http://localhost:8100/api/health` |

Los puertos se pueden cambiar mediante `FRONTEND_PORT` y `API_PORT` dentro de `.env`.

## 6. Datos iniciales

La primera vez que inicia una base vacía, SmartBot registra automáticamente:

- 4 categorías.
- 20 preguntas frecuentes.
- 20 respuestas.
- 3 opciones de configuración.
- 1 usuario administrador.

La semilla no vuelve a insertar las FAQ cuando ya existen preguntas. Esto evita duplicados al reiniciar contenedores.

## 7. Iniciar sesión

1. Abrir `http://localhost:8090`.
2. Escribir el usuario:

```text
IA1-User
```

3. Escribir la contraseña:

```text
IA1-password@_new
```

4. Presionar **Entrar**.

Si las credenciales son correctas, el backend devuelve un token JWT. El navegador lo almacena en `localStorage` con la clave `smartbot_token`.

El token tiene una duración predeterminada de 480 minutos. Si caduca o deja de ser válido, el panel vuelve automáticamente al formulario de acceso.

## 8. Cerrar sesión

Presionar **Cerrar sesión** en la parte superior.

Esta acción elimina el JWT del navegador y oculta el panel. No elimina categorías, preguntas, respuestas ni historial.

## 9. Navegación del panel

Después del acceso aparecen las pestañas:

1. **Dashboard**.
2. **Preguntas**.
3. **Respuestas**.
4. **Categorías**.
5. **Probar consulta**.
6. **Configuración**.

Solo una pestaña se muestra a la vez. Los datos se cargan desde la API REST y no desde una copia incrustada en el frontend.

## 10. Dashboard

El Dashboard resume el uso del sistema.

### Indicadores

| Indicador | Significado |
|---|---|
| Consultas | Número total de búsquedas registradas. |
| Usuarios | Cantidad de valores distintos en `telegram_user`. |
| FAQ | Consultas que encontraron pregunta y respuesta. |
| Unknown | Consultas sin coincidencia o sin respuesta activa. |

### Consultas más frecuentes

Muestra hasta diez textos de consulta, ordenados por cantidad de apariciones.

Dos consultas que significan lo mismo pero están escritas de forma diferente se cuentan por separado porque la estadística agrupa el texto original.

### Categorías más consultadas

Muestra hasta diez categorías según los registros del historial. Las consultas desconocidas aparecen como **sin categoría**.

### Últimas consultas

La tabla muestra hasta 100 registros, del más reciente al más antiguo:

- Fecha.
- Usuario.
- Consulta original.
- Respuesta enviada.
- Tipo de coincidencia.

Presionar **Actualizar** para recargar los indicadores y el historial.

## 11. Administrar categorías

Una categoría agrupa preguntas por tema.

Campos:

| Campo | Descripción |
|---|---|
| Nombre | Identificador visible y único. |
| Descripción | Explicación opcional del tema. |

### Crear una categoría

1. Abrir **Categorías**.
2. Escribir el nombre.
3. Escribir una descripción opcional.
4. Presionar **Guardar categoría**.

### Editar una categoría

1. Localizarla en la tabla.
2. Presionar **Editar**.
3. Modificar los campos cargados en el formulario.
4. Presionar **Guardar categoría**.

### Eliminar una categoría

1. Presionar **Eliminar**.
2. Confirmar la operación.

No se puede eliminar una categoría que tenga preguntas asociadas. Para hacerlo, primero se deben mover o eliminar esas preguntas.

No se permiten dos categorías con el mismo nombre.

El botón **Limpiar** vacía el formulario y cambia nuevamente al modo de creación.

## 12. Administrar preguntas

Cada pregunta representa una intención que SmartBot puede reconocer.

Campos:

| Campo | Descripción |
|---|---|
| Pregunta | Texto principal de la FAQ. Debe tener entre 3 y 500 caracteres. |
| Palabras clave | Términos alternativos usados por la búsqueda. |
| Categoría | Categoría existente a la que pertenece. |
| Activa | Determina si puede participar en búsquedas. |

### Crear una pregunta

1. Crear primero la categoría si todavía no existe.
2. Abrir **Preguntas**.
3. Escribir la pregunta completa.
4. Agregar palabras relacionadas separadas por espacios.
5. Seleccionar una categoría.
6. Dejar marcada **Activa** si debe responder desde ese momento.
7. Presionar **Guardar pregunta**.

Ejemplo:

```text
Pregunta: ¿Cómo reinicio los contenedores?
Palabras clave: docker compose reiniciar restart contenedores
Categoría: Soporte técnico
```

### Editar una pregunta

1. Presionar **Editar** en la fila.
2. Modificar texto, palabras clave, categoría o estado.
3. Guardar.

### Desactivar una pregunta

Editarla, desmarcar **Activa** y guardar. La pregunta permanece en SQLite, pero la búsqueda la ignora.

### Eliminar una pregunta

Al confirmar la eliminación también se eliminan todas sus respuestas debido a la relación en cascada.

No se permiten dos preguntas con el mismo texto.

## 13. Administrar respuestas

Una pregunta puede tener varias respuestas. SmartBot selecciona la respuesta activa con el número de prioridad más bajo.

Por ejemplo:

| Respuesta | Prioridad | Resultado |
|---|---:|---|
| Respuesta principal | 1 | Se selecciona primero. |
| Respuesta alternativa | 2 | Se utiliza solo si la anterior está inactiva o fue eliminada. |

Campos:

| Campo | Descripción |
|---|---|
| Pregunta asociada | Pregunta a la que pertenece la respuesta. |
| Respuesta | Texto enviado al usuario. Entre 2 y 2000 caracteres. |
| Prioridad | Número entre 1 y 100; un número menor tiene preferencia. |
| Activa | Indica si puede ser seleccionada. |

### Crear una respuesta

1. Crear primero la pregunta.
2. Abrir **Respuestas**.
3. Elegir la pregunta asociada.
4. Escribir el texto.
5. Asignar prioridad.
6. Marcar **Activa**.
7. Presionar **Guardar respuesta**.

### Editar o desactivar

Presionar **Editar**, cambiar los campos y guardar. Una respuesta inactiva permanece almacenada, pero no es enviada.

### Eliminar

Presionar **Eliminar** y confirmar. Esto no elimina la pregunta.

Si una pregunta coincide pero no tiene respuestas activas, la búsqueda termina utilizando el mensaje configurado para consultas desconocidas.

## 14. Probar una consulta sin Telegram

La pestaña **Probar consulta** utiliza exactamente el mismo endpoint y la misma base de datos que el bot.

1. Abrir la pestaña.
2. Escribir una pregunta, por ejemplo:

```text
¿Cómo levanto el proyecto?
```

3. Presionar **Consultar**.

El resultado muestra:

- Pregunta reconocida o texto **Sin coincidencia**.
- Respuesta seleccionada.
- Categoría, si existe.

La consulta se registra con el usuario `panel` y actualiza las estadísticas.

## 15. Cómo funciona la coincidencia

La búsqueda:

1. Convierte el texto a minúsculas.
2. Elimina tildes.
3. Conserva letras y números.
4. Ignora tokens de dos caracteres o menos.
5. Compara los tokens con la pregunta y sus palabras clave.
6. Da una bonificación grande a una coincidencia exacta.
7. Da una bonificación menor cuando la consulta completa está contenida en el texto.
8. Selecciona la pregunta con mayor puntaje.

Por eso es importante escribir palabras clave representativas y no repetir términos irrelevantes.

## 16. Configuración

La pestaña **Configuración** carga las claves almacenadas en SQLite.

### `telegram_chat_id`

Chat privado o grupo utilizado por el botón **Enviar prueba**. Puede obtenerse con el script de chat ID.

### `unknown_message`

Texto enviado cuando no existe coincidencia o no hay una respuesta activa.

### `welcome_message`

Texto almacenado como configuración de bienvenida. En la versión actual, el comando `/start` del bot utiliza un saludo fijo escrito en `bot.py`; modificar esta clave no cambia todavía ese saludo.

### Guardar una opción

Modificar el valor y presionar el botón **Guardar** correspondiente. La descripción existente se conserva cuando el frontend envía una descripción vacía.

### Enviar una prueba de Telegram

1. Configurar token y chat ID.
2. Escribir el mensaje de prueba.
3. Presionar **Enviar prueba**.
4. Revisar el resultado debajo del botón.

El chat se elige en este orden:

1. Chat enviado explícitamente al endpoint.
2. Valor `telegram_chat_id` de SQLite.
3. Variable `TELEGRAM_DEFAULT_CHAT_ID` de `.env`.

## 17. Configurar Telegram

### Crear el bot

1. Buscar `@BotFather` en Telegram.
2. Ejecutar `/newbot`.
3. Elegir nombre y usuario.
4. Copiar el token.
5. Abrir `.env` y establecer:

```env
TELEGRAM_BOT_TOKEN=token_real
```

6. Reconstruir o reiniciar el contenedor:

```powershell
docker compose up -d --build telegram-bot api-gateway
```

### Abrir el bot

```powershell
.\scripts\open_telegram_bot_windows.ps1
```

Enviar `/start` para generar una actualización y habilitar el chat.

### Obtener el chat ID

```powershell
.\scripts\telegram_chat_id_windows.ps1 -SaveFirst
```

El script:

- Comprueba el token con `getMe`.
- Consulta `getUpdates`.
- Lista chats encontrados.
- Guarda el primero en `TELEGRAM_DEFAULT_CHAT_ID`.
- Indica que también debe registrarse en la configuración `telegram_chat_id` del panel.

### Probar directamente la Bot API

```powershell
.\scripts\telegram_test_windows.ps1
```

O con un chat específico:

```powershell
.\scripts\telegram_test_windows.ps1 -ChatId "123456789"
```

## 18. Usar el bot

### Ayuda

```text
/start
/ayuda
```

Ambos comandos muestran instrucciones de uso.

### Listar categorías

```text
/categorias
```

El bot consulta `GET /api/categories` y muestra los nombres actuales.

### Consultar una pregunta

Enviar texto libre:

```text
¿Cómo levanto el proyecto?
```

El bot llama `GET /api/search`, envía el username o ID de Telegram y devuelve la respuesta. Cuando existe coincidencia también agrega la categoría.

## 19. Consultar la API manualmente

### Estado

```powershell
Invoke-RestMethod http://localhost:8100/api/health
```

### Búsqueda pública

```powershell
Invoke-RestMethod 'http://localhost:8100/api/search?q=como%20levanto%20el%20proyecto&telegram_user=manual'
```

### Login

```powershell
$body = @{
  username = 'IA1-User'
  password = 'IA1-password@_new'
} | ConvertTo-Json

$login = Invoke-RestMethod `
  -Method Post `
  -Uri 'http://localhost:8100/api/auth/login' `
  -ContentType 'application/json' `
  -Body $body
```

### Endpoint protegido

```powershell
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod 'http://localhost:8100/api/stats' -Headers $headers
```

## 20. Colección Postman

La colección está en:

```text
postman/SmartBot.postman_collection.json
```

Incluye solicitudes para:

- Health.
- Login.
- Listar categorías.
- Listar preguntas.
- Listar respuestas.
- Buscar una respuesta.

Después del login, copiar el token a un encabezado:

```text
Authorization: Bearer <token>
```

para probar endpoints protegidos adicionales.

## 21. Prueba rápida automatizada

Con los contenedores activos:

```powershell
.\scripts\test_api.ps1
```

El script comprueba:

- Estado de la API.
- Login.
- Conteo de categorías.
- Conteo de preguntas.
- Conteo de respuestas.
- Búsqueda conocida.
- Cantidad de consultas registradas.

## 22. Respaldar la base de datos

Crear una copia dentro del volumen:

```powershell
docker compose exec api-gateway sh -c "cp /data/smartbot.db /data/smartbot-backup.db"
```

Para copiarla al equipo:

```powershell
docker cp smartbot-api-gateway:/data/smartbot.db .\smartbot.db
```

## 23. Detener SmartBot

```powershell
docker compose down
```

O:

```powershell
.\scripts\stop_docker_windows.ps1
```

No utilizar `docker compose down -v` si se desea conservar la base. La opción `-v` elimina el volumen `smartbot_data`.

## 24. Problemas frecuentes

### No se puede iniciar sesión

Comprobar:

- Usuario y contraseña de `.env`.
- Que la base se haya creado correctamente.
- Que la API responda en `/api/health`.

Las credenciales de `.env` se utilizan para crear el administrador cuando no existe. Cambiarlas después no actualiza automáticamente el hash de un usuario ya creado.

### Sesión expirada

Volver a iniciar sesión. El panel elimina automáticamente el token inválido.

### No se puede eliminar una categoría

La categoría todavía tiene preguntas. Moverlas a otra categoría o eliminarlas primero.

### La pregunta no obtiene respuesta

Revisar:

- Que la pregunta esté activa.
- Que tenga palabras clave relacionadas.
- Que exista al menos una respuesta activa.
- Que la respuesta con prioridad deseada tenga el número más bajo.

### Telegram no responde

Ejecutar:

```powershell
docker compose logs telegram-bot
docker compose logs api-gateway
```

Comprobar token, conexión a Internet y estado de la API.

### El mensaje de bienvenida no cambia

La clave `welcome_message` se almacena en SQLite, pero el bot actual utiliza un texto fijo para `/start`. `unknown_message` sí se usa dinámicamente en búsquedas sin coincidencia.

### Los datos iniciales no reaparecen

La semilla solo se ejecuta cuando la tabla `questions` está vacía. Reiniciar contenedores no restaura registros eliminados mientras el volumen siga existiendo.

### Puerto ocupado

Cambiar `API_PORT` o `FRONTEND_PORT` en `.env`, o detener el proceso que ocupa 8100/8090.

## 25. Persistencia

| Información | Ubicación |
|---|---|
| Categorías | SQLite, tabla `categories`. |
| Preguntas | SQLite, tabla `questions`. |
| Respuestas | SQLite, tabla `answers`. |
| Administradores | SQLite, tabla `admin_users`. |
| Configuración | SQLite, tabla `settings`. |
| Historial | SQLite, tabla `query_logs`. |
| Archivo SQLite en Docker | Volumen `smartbot_data`, ruta `/data/smartbot.db`. |
| Token y secretos | `.env`. |

## 26. Documentación relacionada

- [Manual técnico](MANUAL_TECNICO.md)
- [Arquitectura](ARQUITECTURA.md)
- [Diagrama entidad-relación](ER.md)
- [Requerimientos](REQUERIMIENTOS.md)
- [Casos de prueba](CASOS_PRUEBA.md)
- [Hoja de cumplimiento](HOJA_CUMPLIMIENTO.md)
