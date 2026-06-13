:- dynamic symptom/4, failure/5, recommendation/4, diagnosis_rule/6, solution_step/3.

symptom(no_enciende, 'La computadora no enciende', energia, 5).
symptom(sin_led, 'No encienden luces LED', energia, 4).
symptom(ventiladores_giran, 'Los ventiladores giran pero no hay imagen', hardware, 4).
symptom(pantalla_negra, 'Pantalla negra al iniciar', video, 5).
symptom(beeps_arranque, 'Pitidos durante el arranque', hardware, 5).
symptom(reinicios_inesperados, 'Reinicios inesperados', estabilidad, 4).
symptom(apagones_repentinos, 'Apagones repentinos', energia, 5).
symptom(sobrecalentamiento, 'Equipo muy caliente', temperatura, 5).
symptom(ruido_ventilador, 'Ventilador con ruido excesivo', temperatura, 3).
symptom(lentitud_general, 'Sistema demasiado lento', rendimiento, 3).
symptom(disco_100, 'Uso de disco al 100%', almacenamiento, 4).
symptom(pantalla_azul, 'Pantalla azul o error critico', sistema, 5).
symptom(no_detecta_disco, 'No detecta disco duro o SSD', almacenamiento, 5).
symptom(error_sistema_operativo, 'Error al cargar sistema operativo', sistema, 4).
symptom(no_conecta_wifi, 'No conecta a WiFi', red, 3).
symptom(internet_lento, 'Internet lento o inestable', red, 2).
symptom(usb_no_funciona, 'Puertos USB no funcionan', perifericos, 3).
symptom(teclado_no_responde, 'Teclado no responde', perifericos, 3).
symptom(mouse_no_responde, 'Mouse no responde', perifericos, 3).
symptom(sonido_no_funciona, 'No hay sonido', multimedia, 2).
symptom(programas_se_cierran, 'Programas se cierran solos', software, 4).
symptom(virus_popups, 'Ventanas emergentes o comportamiento extrano', seguridad, 4).
symptom(actualizacion_fallida, 'Actualizacion fallida del sistema', sistema, 3).
symptom(bateria_no_carga, 'Bateria no carga', energia, 4).
symptom(fecha_hora_se_reinicia, 'Fecha y hora se reinician', motherboard, 3).

failure(fuente_poder_danada, 'Fuente de poder danada o sin energia', hardware, critica, 'El equipo no recibe energia estable desde la fuente.').
failure(falla_ram, 'Memoria RAM defectuosa o mal instalada', hardware, alta, 'Los errores de memoria impiden un arranque estable.').
failure(falla_video_gpu, 'Falla de video o tarjeta grafica', hardware, alta, 'El equipo enciende, pero no genera una imagen correcta.').
failure(sobrecalentamiento_cpu, 'Sobrecalentamiento de CPU', hardware, critica, 'La temperatura obliga al equipo a reducir rendimiento o apagarse.').
failure(disco_danado, 'Disco duro o SSD con falla', hardware, alta, 'La unidad presenta sintomas de degradacion o desconexion.').
failure(sistema_operativo_corrupto, 'Sistema operativo corrupto', software, alta, 'Archivos de arranque o del sistema estan danados.').
failure(malware, 'Infeccion de malware', seguridad, alta, 'Procesos no deseados afectan estabilidad y rendimiento.').
failure(driver_red, 'Controlador o configuracion de red incorrecta', red, media, 'La interfaz de red no logra comunicarse correctamente.').
failure(puertos_usb_danados, 'Controladores o puertos USB con falla', perifericos, media, 'Los perifericos USB no son reconocidos de forma normal.').
failure(audio_driver, 'Controlador de audio incorrecto', software, baja, 'El dispositivo de audio esta deshabilitado o mal configurado.').
failure(bateria_cargador, 'Bateria o cargador con falla', hardware, media, 'La bateria o el cargador no entregan carga estable.').
failure(pila_cmos, 'Pila CMOS agotada', motherboard, baja, 'La placa madre pierde fecha y configuracion al apagarse.').
failure(bajo_rendimiento_general, 'Bajo rendimiento por saturacion de recursos', rendimiento, media, 'Procesos, memoria o almacenamiento estan saturados.').

recommendation(rec_fuente_1, fuente_poder_danada, 'Verificar cable, toma electrica y regulador.', 1).
recommendation(rec_fuente_2, fuente_poder_danada, 'Probar una fuente compatible conocida.', 2).
recommendation(rec_ram_1, falla_ram, 'Retirar, limpiar y reinstalar los modulos RAM.', 1).
recommendation(rec_ram_2, falla_ram, 'Probar un modulo y una ranura a la vez.', 2).
recommendation(rec_gpu_1, falla_video_gpu, 'Probar otro cable, monitor y puerto de video.', 1).
recommendation(rec_gpu_2, falla_video_gpu, 'Reinstalar la GPU y actualizar su controlador.', 2).
recommendation(rec_temp_1, sobrecalentamiento_cpu, 'Limpiar ventiladores y disipador.', 1).
recommendation(rec_temp_2, sobrecalentamiento_cpu, 'Cambiar pasta termica y verificar flujo de aire.', 2).
recommendation(rec_disco_1, disco_danado, 'Respaldar los datos inmediatamente.', 1).
recommendation(rec_disco_2, disco_danado, 'Revisar SMART, cableado y reemplazar la unidad si falla.', 2).
recommendation(rec_so_1, sistema_operativo_corrupto, 'Ejecutar reparacion de inicio y verificar archivos del sistema.', 1).
recommendation(rec_so_2, sistema_operativo_corrupto, 'Restaurar o reinstalar el sistema si no inicia.', 2).
recommendation(rec_malware_1, malware, 'Desconectar el equipo de la red y ejecutar un analisis completo.', 1).
recommendation(rec_malware_2, malware, 'Eliminar software sospechoso y actualizar credenciales.', 2).
recommendation(rec_red_1, driver_red, 'Reiniciar router y adaptador de red.', 1).
recommendation(rec_red_2, driver_red, 'Reinstalar controlador y restablecer configuracion IP.', 2).
recommendation(rec_usb_1, puertos_usb_danados, 'Probar otro puerto y otro periferico.', 1).
recommendation(rec_usb_2, puertos_usb_danados, 'Reinstalar controladores USB del chipset.', 2).
recommendation(rec_audio_1, audio_driver, 'Verificar salida y volumen seleccionados.', 1).
recommendation(rec_audio_2, audio_driver, 'Reinstalar el controlador de audio.', 2).
recommendation(rec_bateria_1, bateria_cargador, 'Probar un cargador compatible.', 1).
recommendation(rec_bateria_2, bateria_cargador, 'Evaluar bateria y puerto de carga.', 2).
recommendation(rec_cmos_1, pila_cmos, 'Cambiar la pila CR2032.', 1).
recommendation(rec_cmos_2, pila_cmos, 'Configurar fecha y guardar cambios en BIOS.', 2).
recommendation(rec_perf_1, bajo_rendimiento_general, 'Revisar procesos de inicio y uso de recursos.', 1).
recommendation(rec_perf_2, bajo_rendimiento_general, 'Liberar espacio y evaluar ampliacion de RAM o SSD.', 2).

solution_step(fuente_poder_danada, 1, 'Desconectar el equipo y revisar conexiones de energia.').
solution_step(fuente_poder_danada, 2, 'Probar toma, cable y fuente compatible.').
solution_step(falla_ram, 1, 'Apagar y retirar los modulos RAM.').
solution_step(falla_ram, 2, 'Limpiar contactos y probar cada modulo por separado.').
solution_step(falla_video_gpu, 1, 'Probar monitor y cable alternos.').
solution_step(falla_video_gpu, 2, 'Reinstalar GPU o probar video integrado.').
solution_step(sobrecalentamiento_cpu, 1, 'Limpiar ventilacion y verificar giro de ventiladores.').
solution_step(sobrecalentamiento_cpu, 2, 'Cambiar pasta termica y medir temperatura.').
solution_step(disco_danado, 1, 'Respaldar informacion importante.').
solution_step(disco_danado, 2, 'Ejecutar diagnostico SMART y revisar conexiones.').
solution_step(sistema_operativo_corrupto, 1, 'Abrir las opciones de recuperacion.').
solution_step(sistema_operativo_corrupto, 2, 'Reparar inicio o restaurar el sistema.').
solution_step(malware, 1, 'Aislar el equipo de la red.').
solution_step(malware, 2, 'Ejecutar analisis sin conexion y eliminar amenazas.').
solution_step(driver_red, 1, 'Reiniciar equipo y router.').
solution_step(driver_red, 2, 'Reinstalar adaptador y renovar configuracion IP.').
solution_step(puertos_usb_danados, 1, 'Probar puertos y perifericos alternos.').
solution_step(puertos_usb_danados, 2, 'Reinstalar controladores del chipset.').
solution_step(audio_driver, 1, 'Seleccionar el dispositivo de salida correcto.').
solution_step(audio_driver, 2, 'Reinstalar controlador y reiniciar servicios de audio.').
solution_step(bateria_cargador, 1, 'Probar cargador compatible.').
solution_step(bateria_cargador, 2, 'Generar reporte de bateria y evaluar reemplazo.').
solution_step(pila_cmos, 1, 'Apagar y desconectar el equipo.').
solution_step(pila_cmos, 2, 'Cambiar CR2032 y configurar BIOS.').
solution_step(bajo_rendimiento_general, 1, 'Abrir el administrador de tareas.').
solution_step(bajo_rendimiento_general, 2, 'Reducir inicio, liberar espacio y evaluar mejoras.').

diagnosis_rule(regla_fuente, fuente_poder_danada, [no_enciende, sin_led], [apagones_repentinos], 30, true).
diagnosis_rule(regla_ram, falla_ram, [beeps_arranque, pantalla_azul], [reinicios_inesperados, programas_se_cierran], 25, true).
diagnosis_rule(regla_gpu, falla_video_gpu, [pantalla_negra, ventiladores_giran], [beeps_arranque], 30, true).
diagnosis_rule(regla_temperatura, sobrecalentamiento_cpu, [sobrecalentamiento, ruido_ventilador], [apagones_repentinos, reinicios_inesperados], 25, true).
diagnosis_rule(regla_disco, disco_danado, [no_detecta_disco, disco_100], [lentitud_general, error_sistema_operativo], 25, true).
diagnosis_rule(regla_so, sistema_operativo_corrupto, [error_sistema_operativo, actualizacion_fallida], [pantalla_azul], 25, true).
diagnosis_rule(regla_malware, malware, [virus_popups, programas_se_cierran], [lentitud_general], 25, true).
diagnosis_rule(regla_red, driver_red, [no_conecta_wifi], [internet_lento], 20, true).
diagnosis_rule(regla_usb, puertos_usb_danados, [usb_no_funciona], [teclado_no_responde, mouse_no_responde], 20, true).
diagnosis_rule(regla_audio, audio_driver, [sonido_no_funciona], [actualizacion_fallida], 20, true).
diagnosis_rule(regla_bateria, bateria_cargador, [bateria_no_carga], [apagones_repentinos, no_enciende], 20, true).
diagnosis_rule(regla_cmos, pila_cmos, [fecha_hora_se_reinicia], [error_sistema_operativo], 20, true).
diagnosis_rule(regla_rendimiento, bajo_rendimiento_general, [lentitud_general], [disco_100, programas_se_cierran, virus_popups], 20, true).
