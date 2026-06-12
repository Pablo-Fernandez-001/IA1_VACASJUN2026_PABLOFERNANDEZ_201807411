# Manual de Usuario - SmartBot

## 1. Iniciar el sistema

Desde la raíz del proyecto:

```bash
cp .env.example .env
docker compose up --build
```

Abrir el panel:

```text
http://localhost:8090
```

## 2. Iniciar sesión

Usar las credenciales requeridas por el enunciado:

```text
Usuario: IA1-User
Contraseña: IA1-password@_new
```

## 3. Administrar preguntas frecuentes

1. Entrar a la pestaña **Preguntas**.
2. Escribir pregunta, respuesta, palabras clave y categoría.
3. Presionar **Guardar pregunta**.
4. Para modificar, usar **Editar**.
5. Para eliminar, usar **Eliminar**.

## 4. Administrar categorías

1. Entrar a **Categorías**.
2. Crear una categoría con nombre y descripción.
3. Guardar.

## 5. Configurar Telegram

1. Crear un bot nuevo en `@BotFather` solo para Practica 2.
2. Copiar token en `.env` como `TELEGRAM_BOT_TOKEN`.
3. Enviar `/start` al bot.
4. Guardar el chat ID desde la pestaña **Configuración**.
5. En Windows, se puede abrir el bot y obtener el chat con `scripts/open_telegram_bot_windows.ps1` y `scripts/telegram_chat_id_windows.ps1`.

## 6. Usar el bot

Preguntar normalmente:

```text
¿Cómo levanto el proyecto?
```

Ejecutar diagnóstico:

```text
/diagnostico no_responde,token_vacio,chat_id_malo
```

## 7. Crear lógica diagnóstica nueva

1. Crear un síntoma en **Síntomas**.
2. Crear o editar un diagnóstico en **Diagnósticos**.
3. Crear una regla en **Reglas**.
4. Asociar varios síntomas a la regla.
5. Probar en **Probar diagnóstico**.

Cuando se cambia una regla, Prolog recibe el nuevo conocimiento dinámico en la siguiente consulta.

## 8. Interpretar diagnóstico

Cada diagnóstico muestra:

- Nombre del problema.
- Categoría.
- Porcentaje de probabilidad.
- Nivel bajo, medio o alto.
- Cantidad de síntomas coincidentes.
- Síntomas faltantes.
- Ruta de solución paso por paso.
