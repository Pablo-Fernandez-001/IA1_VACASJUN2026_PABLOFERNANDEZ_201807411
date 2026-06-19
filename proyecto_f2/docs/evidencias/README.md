# Evidencias sugeridas

Capturas recomendadas para la entrega:

1. Frontend con mapa 10x10 renderizado.
2. Primer paso mostrando accion devuelta por Prolog.
3. Robot recogiendo un paquete.
4. Robot entregando un paquete en zona valida.
5. Dashboard con metricas e historial.
6. Swagger de la API en `/docs`.

Comando de evidencia Prolog:

```bash
'{"robot_id":"r1","robots":[{"id":"r1","x":1,"y":1,"carrying":"none"}],"packages":[{"id":"p1","x":1,"y":3,"zone":"zona_a","status":"pendiente"}]}' | swipl -q -s prolog/warehouse.pl -g warehouse_cli
```
