# Manual de Usuario - SmartBot

## Iniciar

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

Abrir `http://localhost:8090` e ingresar con:

```text
IA1-User
IA1-password@_new
```

## Administrar contenido

1. **Categorías:** crear, editar o eliminar categorías sin preguntas asociadas.
2. **Preguntas:** escribir la consulta, palabras clave, categoría y estado.
3. **Respuestas:** asociar una respuesta a una pregunta, indicar prioridad y estado.
4. **Configuración:** editar `telegram_chat_id`, mensaje desconocido y bienvenida.
5. **Dashboard:** revisar usuarios, consultas frecuentes, categorías e historial.

## Probar sin Telegram

Abrir **Probar consulta**, escribir una pregunta y presionar **Consultar**. La operación queda registrada igual que una consulta del bot.

## Usar Telegram

1. Configurar `TELEGRAM_BOT_TOKEN` en `.env`.
2. Reiniciar el servicio con `docker compose up -d telegram-bot`.
3. Enviar `/start` para ayuda.
4. Enviar `/categorias` para listar temas.
5. Escribir una pregunta libre.

Cuando no existe coincidencia se muestra el mensaje configurado y la consulta también queda registrada.

## Detener

```powershell
docker compose down
```

No agregar `-v` si se desea conservar la base de datos.
