# Manual de Usuario - Doctor Byte

## Iniciar

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

Abrir `http://localhost:8081`.

## Realizar diagnóstico

1. Escribir el nombre del usuario.
2. Buscar o filtrar síntomas.
3. Seleccionar al menos uno.
4. Opcionalmente activar Telegram.
5. Presionar **Solicitar diagnóstico**.
6. Revisar probabilidad, severidad, recomendaciones y ruta de solución.
7. Usar **Limpiar selección** para reiniciar.

El historial permite cargar o eliminar resultados anteriores.

## Administrar conocimiento

- **Síntomas:** ID, nombre, categoría y peso.
- **Fallas:** descripción, severidad y pasos de solución.
- **Recomendaciones:** texto asociado a una falla.
- **Reglas:** falla, síntomas requeridos, síntomas de apoyo, umbral y estado.
- **Configuración:** chat ID, bot activo y mensajes.

Los cambios se guardan directamente como hechos Prolog. Al eliminar una falla también se eliminan sus recomendaciones y reglas. Al cambiar el ID de un síntoma, las reglas se actualizan.

## Telegram

Después de configurar el token:

```text
/start
/sintomas
/diagnosticar pantalla_negra,ventiladores_giran
```

El bot consulta la API y la API consulta Prolog; no usa respuestas diagnósticas codificadas.

## Detener

```powershell
docker compose down
```

No usar `-v` si se desea conservar el historial.
