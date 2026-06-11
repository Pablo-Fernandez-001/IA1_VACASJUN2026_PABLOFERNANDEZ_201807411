# Requerimientos funcionales y no funcionales

## Requerimientos funcionales

| Código | Requerimiento |
|---|---|
| RF-01 | El sistema permite iniciar sesión con un usuario administrador preconfigurado. |
| RF-02 | El administrador puede crear, consultar, actualizar y eliminar categorías. |
| RF-03 | El administrador puede crear, consultar, actualizar y eliminar preguntas frecuentes. |
| RF-04 | El bot responde consultas usando información de la base de datos. |
| RF-05 | El sistema registra consultas realizadas por usuarios. |
| RF-06 | El administrador puede configurar el chat ID de Telegram. |
| RF-07 | El administrador puede crear, editar y eliminar síntomas. |
| RF-08 | El administrador puede crear, editar y eliminar diagnósticos. |
| RF-09 | El administrador puede crear, editar y eliminar reglas diagnósticas. |
| RF-10 | El sistema calcula diagnósticos posibles usando Prolog. |
| RF-11 | El sistema muestra más de un diagnóstico cuando hay varias coincidencias. |
| RF-12 | El sistema muestra porcentaje, nivel de problema y ruta de solución. |
| RF-13 | El sistema muestra estadísticas de uso del bot. |

## Requerimientos no funcionales

| Código | Requerimiento |
|---|---|
| RNF-01 | El backend debe estar desarrollado en Python. |
| RNF-02 | El proyecto debe ejecutarse con Docker Compose. |
| RNF-03 | La lógica diagnóstica debe estar separada del API Gateway. |
| RNF-04 | El panel administrativo debe estar protegido por autenticación. |
| RNF-05 | Las preguntas frecuentes no deben estar codificadas en endpoints. |
| RNF-06 | La comunicación entre servicios debe hacerse mediante API REST. |
| RNF-07 | El sistema debe ser mantenible por separación de carpetas y servicios. |
| RNF-08 | La interfaz debe ser usable desde navegador moderno. |
