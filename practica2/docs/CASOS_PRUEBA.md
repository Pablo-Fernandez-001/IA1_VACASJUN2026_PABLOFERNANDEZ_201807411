# Casos de Prueba - SmartBot

| ID | Acción | Resultado esperado |
|---|---|---|
| CP-01 | Login correcto | Devuelve JWT. |
| CP-02 | Login incorrecto | HTTP 401. |
| CP-03 | Listar semillas | 4 categorías, 20 preguntas y 20 respuestas. |
| CP-04 | Crear/editar/eliminar pregunta | Cambios persistentes en SQLite. |
| CP-05 | Crear/editar/eliminar respuesta | Cambios persistentes y asociación válida. |
| CP-06 | CRUD categoría | Funciona; bloquea borrado con preguntas. |
| CP-07 | Buscar “cómo levanto el proyecto” | Devuelve respuesta de Docker. |
| CP-08 | Consulta inexistente | Devuelve `unknown_message`. |
| CP-09 | Consultar desde Telegram | Bot llama API y responde. |
| CP-10 | Revisar historial | Guarda fecha, usuario, consulta y respuesta. |
| CP-11 | Revisar estadísticas | Muestra frecuencia, usuarios y categorías. |
| CP-12 | Reiniciar contenedores | Datos permanecen en `smartbot_data`. |

Ejecutar humo automatizado:

```powershell
.\scripts\test_api.ps1
```
