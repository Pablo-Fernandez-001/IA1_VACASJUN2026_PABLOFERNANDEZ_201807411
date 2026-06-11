# Manual de usuario - Doctor Byte

## 1. Abrir el sistema

Ejecutar los servicios y entrar a:

```text
http://localhost:5173
```

Con Docker:

```text
http://localhost:8081
```

## 2. Realizar diagnostico

1. Escribir el nombre del usuario.
2. Buscar o filtrar sintomas por categoria.
3. Seleccionar los sintomas observados en la computadora.
4. Presionar **Solicitar diagnostico**.
5. Revisar diagnostico principal, probabilidades, porcentaje de problema, efectividad y rutas de solucion.

## 3. Revisar diagnosticos posibles

Despues de solicitar diagnostico, el sistema muestra varias alternativas. Cada tarjeta incluye probabilidad, porcentaje de problema y efectividad.

Para ver la ruta de solucion de una alternativa, presionar la tarjeta del diagnostico.

## 4. Administrar sintomas

En **Administracion de conocimiento** abrir la pestana **Sintomas**.

Desde alli se puede:

- Crear un sintoma nuevo.
- Editar nombre, categoria o peso.
- Eliminar un sintoma.

El campo `id` debe ser corto, sin espacios y descriptivo, por ejemplo `pantalla_parpadea`.

## 5. Administrar reglas diagnosticas

En **Administracion de conocimiento** abrir la pestana **Reglas diagnosticas**.

Desde alli se puede:

- Crear una regla nueva.
- Editar mensaje, categoria, severidad, sintomas requeridos, sintomas de apoyo, recomendaciones y ruta de solucion.
- Activar o desactivar una regla.
- Eliminar una regla.

Los sintomas requeridos y de apoyo deben escribirse usando los IDs del catalogo, separados por coma o por salto de linea.

## 6. Enviar por Telegram

1. Activar la casilla **Enviar resultado por Telegram**.
2. Ingresar el Chat ID si no esta configurado en `.env`.
3. Realizar diagnostico.

Si no se activa Telegram, el diagnostico se guarda y se muestra normalmente.

## 7. Ver historial

En la parte inferior se muestra el historial de diagnosticos realizados con fecha, usuario, sintomas, resultado y estado de Telegram.

## 8. Cargar historial

Presionar el boton de carpeta en una fila del historial para cargar nuevamente ese diagnostico.

Al cargarlo, el sistema restaura:

- Usuario.
- Sintomas seleccionados.
- Resultado guardado.
- Diagnosticos alternativos.
- Rutas de solucion.

## 9. Eliminar historial

Presionar el boton de basurero en la fila del diagnostico.

## 10. Preguntas frecuentes

### 1. Que es Doctor Byte?

Doctor Byte es un sistema experto que ayuda a diagnosticar fallas comunes en computadoras usando sintomas, reglas en Prolog y una interfaz web.

### 2. El diagnostico es definitivo?

No. Es un diagnostico preliminar basado en sintomas seleccionados. Sirve como guia para revisar posibles causas, no reemplaza una revision tecnica completa.

### 3. Por que aparecen varios diagnosticos?

Porque Prolog evalua todas las reglas diagnosticas y ordena las alternativas por probabilidad. Asi el usuario puede ver mas de una posible causa.

### 4. Que significa probabilidad?

Es el porcentaje de coincidencia entre los sintomas seleccionados y los sintomas definidos en una regla diagnostica.

### 5. Que significa porcentaje de problema?

Es una estimacion del impacto o riesgo del diagnostico. Se calcula combinando la probabilidad con la severidad de la regla.

### 6. Que significa efectividad?

Es una estimacion de que tan util puede ser la ruta de solucion sugerida para ese diagnostico.

### 7. Como veo la ruta de solucion?

En la seccion de resultados, hacer clic sobre una tarjeta de diagnostico posible. Se desplegaran los pasos de solucion de esa alternativa.

### 8. Como agrego un sintoma nuevo?

Ir a **Administracion de conocimiento**, abrir **Sintomas**, llenar ID, nombre, categoria y peso, y presionar **Guardar sintoma**.

### 9. Como debe escribirse el ID de un sintoma?

Debe ser corto, sin espacios y en minusculas. Ejemplo: `pantalla_parpadea`, `wifi_intermitente` o `ruido_disco`.

### 10. Que significa el peso de un sintoma?

El peso indica la importancia del sintoma en el calculo. Un peso alto influye mas en la probabilidad del diagnostico.

### 11. Como agrego una regla diagnostica?

Ir a **Administracion de conocimiento**, abrir **Reglas diagnosticas**, completar los campos de la regla y presionar **Guardar regla**.

### 12. Que son sintomas requeridos?

Son los sintomas principales de una regla. En el calculo de Prolog pesan el doble que los sintomas de apoyo.

### 13. Que son sintomas de apoyo?

Son sintomas secundarios que refuerzan un diagnostico, pero no tienen el mismo peso que los requeridos.

### 14. Puedo editar una regla sin tocar Prolog?

Si. El formulario modifica `doctor_byte_data.json`, y Prolog lee ese archivo cada vez que diagnostica.

### 15. Puedo desactivar una regla sin borrarla?

Si. En el formulario de reglas se puede desmarcar **Regla activa**. Una regla desactivada no participa en el diagnostico.

### 16. Que pasa si borro un sintoma?

El sistema elimina ese sintoma del catalogo y tambien remueve sus referencias en las reglas diagnosticas.

### 17. Donde se guarda el historial?

El historial se guarda en SQLite desde el API Gateway. En Docker queda persistido en el volumen `doctor-byte-data`.

### 18. Puedo volver a abrir un diagnostico anterior?

Si. En el historial, usar el boton de carpeta para cargar nuevamente el diagnostico guardado.

### 19. Por que Telegram no envia mensajes?

Puede faltar `TELEGRAM_BOT_TOKEN`, faltar `TELEGRAM_DEFAULT_CHAT_ID`, o el usuario aun no le escribio `/start` al bot.

### 20. Que hago si el frontend no abre en Docker?

Verificar que Docker este levantado y abrir `http://localhost:8081`. Si el puerto cambio, revisar `FRONTEND_PORT` en `.env`.
