# Casos de prueba

| Caso | Entrada | Resultado esperado |
|---|---|---|
| CP-01 Login correcto | IA1-User / IA1-password@_new | Token JWT válido. |
| CP-02 Login incorrecto | contraseña mala | Error 401. |
| CP-03 Buscar FAQ existente | `docker compose` | Respuesta de ejecución del proyecto. |
| CP-04 Buscar FAQ no existente | texto sin relación | Mensaje configurable de no encontrado. |
| CP-05 Crear categoría | Nombre nuevo | Categoría guardada. |
| CP-06 Editar FAQ | Cambiar respuesta | El bot devuelve la nueva respuesta. |
| CP-07 Diagnóstico Telegram | `no_responde,token_vacio,chat_id_malo` | Diagnóstico Telegram no configurado con porcentaje alto. |
| CP-08 Diagnóstico múltiple | `no_responde,api_caida` | Más de un diagnóstico posible si hay varias reglas coincidentes. |
| CP-09 Regla nueva | Crear regla con síntomas | Prolog la evalúa en la siguiente consulta. |
| CP-10 Estadísticas | Realizar consultas | Aumenta total de logs. |
