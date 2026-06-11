# Casos de prueba - Doctor Byte

| ID | Síntomas seleccionados | Resultado esperado | Estado |
|---|---|---|---|
| CP01 | no_enciende, sin_led | Fuente de poder dañada o sin energía | Verificado con `pytest` |
| CP02 | beeps_arranque, pantalla_azul, reinicios_inesperados | Memoria RAM defectuosa o mal instalada | Verificado con `pytest` |
| CP03 | pantalla_negra, ventiladores_giran | Problema de tarjeta gráfica o salida de video | Verificado con `pytest` |
| CP04 | sobrecalentamiento, ruido_ventilador, apagones_repentinos | Sobrecalentamiento de CPU o ventilación deficiente | Verificado con `pytest` |
| CP05 | no_detecta_disco, disco_100, lentitud_general | Disco duro o SSD dañado | Verificado con `pytest` |
| CP06 | error_sistema_operativo, actualizacion_fallida | Sistema operativo corrupto o arranque dañado | Verificado con `pytest` |
| CP07 | virus_popups, lentitud_general, programas_se_cierran | Infección por malware o software no deseado | Verificado con `pytest` |
| CP08 | no_conecta_wifi, internet_lento | Controlador o configuración de red defectuosa | Verificado con `pytest` |
| CP09 | usb_no_funciona, teclado_no_responde, mouse_no_responde | Puertos USB o controlador USB con falla | Verificado con `pytest` |
| CP10 | bateria_no_carga, apagones_repentinos | Batería o cargador con falla | Verificado con `pytest` |
| CP11 | fecha_hora_se_reinicia | Pila CMOS agotada | Verificado con `pytest` |
| CP12 | lentitud_general, disco_100 | Bajo rendimiento por saturación de recursos | Verificado con `pytest` |

## Ejecución automatizada

Los casos CP01 a CP12 están automatizados en `backend/prolog_service/tests/test_prolog_service.py`.

```powershell
cd backend\prolog_service
.\.venv\Scripts\python -m pytest
```

Resultado esperado: 16 pruebas pasan.

## Evidencia recomendada

Para cada caso tomar captura de:

1. Selección de síntomas.
2. Resultado generado.
3. Registro creado en historial.
4. Notificación de Telegram si aplica.
