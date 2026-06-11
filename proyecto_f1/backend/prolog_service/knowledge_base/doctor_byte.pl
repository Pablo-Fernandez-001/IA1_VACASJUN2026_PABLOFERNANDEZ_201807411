:- use_module(library(http/json)).

% =============================================================
% Doctor Byte - Base de conocimiento Prolog
% Autor: Pablo Daniel Fernández Chacón - 201807411
% =============================================================

% -----------------------------
% Síntomas disponibles
% sintoma(ID, Nombre, Categoria, Peso).
% -----------------------------
sintoma(no_enciende, 'La computadora no enciende', energia, 5).
sintoma(sin_led, 'No encienden luces LED', energia, 4).
sintoma(ventiladores_giran, 'Los ventiladores giran pero no hay imagen', hardware, 4).
sintoma(pantalla_negra, 'Pantalla negra al iniciar', video, 5).
sintoma(beeps_arranque, 'Pitidos durante el arranque', hardware, 5).
sintoma(reinicios_inesperados, 'Reinicios inesperados', estabilidad, 4).
sintoma(apagones_repentinos, 'Apagones repentinos', energia, 5).
sintoma(sobrecalentamiento, 'Equipo muy caliente', temperatura, 5).
sintoma(ruido_ventilador, 'Ventilador con ruido excesivo', temperatura, 3).
sintoma(lentitud_general, 'Sistema demasiado lento', rendimiento, 3).
sintoma(disco_100, 'Uso de disco al 100%', almacenamiento, 4).
sintoma(pantalla_azul, 'Pantalla azul o error crítico', sistema, 5).
sintoma(no_detecta_disco, 'No detecta disco duro o SSD', almacenamiento, 5).
sintoma(error_sistema_operativo, 'Error al cargar sistema operativo', sistema, 4).
sintoma(no_conecta_wifi, 'No conecta a WiFi', red, 3).
sintoma(internet_lento, 'Internet lento o inestable', red, 2).
sintoma(usb_no_funciona, 'Puertos USB no funcionan', perifericos, 3).
sintoma(teclado_no_responde, 'Teclado no responde', perifericos, 3).
sintoma(mouse_no_responde, 'Mouse no responde', perifericos, 3).
sintoma(sonido_no_funciona, 'No hay sonido', multimedia, 2).
sintoma(programas_se_cierran, 'Programas se cierran solos', software, 4).
sintoma(virus_popups, 'Ventanas emergentes o comportamiento extraño', seguridad, 4).
sintoma(actualizacion_fallida, 'Actualización fallida del sistema', sistema, 3).
sintoma(bateria_no_carga, 'Batería no carga', energia, 4).
sintoma(fecha_hora_se_reinicia, 'Fecha y hora se reinician', motherboard, 3).

% -----------------------------
% Fallas diagnosticables
% falla(ID, Nombre, Categoria, Severidad, SintomasRequeridos, SintomasApoyo).
% -----------------------------
falla(fuente_poder_danada, 'Fuente de poder dañada o sin energía', hardware, critica,
      [no_enciende, sin_led], [apagones_repentinos, bateria_no_carga]).
falla(falla_ram, 'Memoria RAM defectuosa o mal instalada', hardware, alta,
      [beeps_arranque], [pantalla_azul, reinicios_inesperados, pantalla_negra]).
falla(falla_video_gpu, 'Problema de tarjeta gráfica o salida de video', hardware, alta,
      [pantalla_negra, ventiladores_giran], [beeps_arranque]).
falla(sobrecalentamiento_cpu, 'Sobrecalentamiento de CPU o ventilación deficiente', hardware, alta,
      [sobrecalentamiento], [ruido_ventilador, apagones_repentinos, reinicios_inesperados]).
falla(disco_danado, 'Disco duro o SSD dañado', hardware, alta,
      [no_detecta_disco], [lentitud_general, disco_100, error_sistema_operativo]).
falla(sistema_operativo_corrupto, 'Sistema operativo corrupto o arranque dañado', software, media,
      [error_sistema_operativo], [pantalla_azul, actualizacion_fallida, programas_se_cierran]).
falla(malware, 'Infección por malware o software no deseado', seguridad, alta,
      [virus_popups], [lentitud_general, programas_se_cierran, internet_lento]).
falla(driver_red, 'Controlador o configuración de red defectuosa', software, media,
      [no_conecta_wifi], [internet_lento, actualizacion_fallida]).
falla(puertos_usb_danados, 'Puertos USB o controlador USB con falla', hardware, media,
      [usb_no_funciona], [teclado_no_responde, mouse_no_responde]).
falla(perifericos_defectuosos, 'Periféricos desconectados o defectuosos', perifericos, baja,
      [teclado_no_responde], [mouse_no_responde, usb_no_funciona]).
falla(audio_driver, 'Controlador de audio incorrecto o dispositivo deshabilitado', software, baja,
      [sonido_no_funciona], [actualizacion_fallida]).
falla(bateria_cargador, 'Batería o cargador con falla', hardware, media,
      [bateria_no_carga], [apagones_repentinos, no_enciende]).
falla(pila_cmos, 'Pila CMOS agotada', motherboard, baja,
      [fecha_hora_se_reinicia], [error_sistema_operativo]).
falla(bajo_rendimiento_general, 'Bajo rendimiento por saturación de recursos', rendimiento, media,
      [lentitud_general], [disco_100, programas_se_cierran, virus_popups]).

% -----------------------------
% Recomendaciones asociadas
% -----------------------------
recomendacion(fuente_poder_danada, [
  'Verificar cable de poder y tomacorriente.',
  'Probar con otro cable o cargador compatible.',
  'Revisar fuente de poder con multímetro o reemplazarla si no entrega voltaje.'
]).
recomendacion(falla_ram, [
  'Apagar el equipo, retirar y volver a colocar los módulos RAM.',
  'Probar cada módulo por separado.',
  'Ejecutar MemTest86 o diagnóstico de memoria.'
]).
recomendacion(falla_video_gpu, [
  'Probar otro cable HDMI/VGA/DisplayPort y otro monitor.',
  'Limpiar y reinstalar la tarjeta gráfica si es de escritorio.',
  'Actualizar o reinstalar drivers de video si logra iniciar en modo seguro.'
]).
recomendacion(sobrecalentamiento_cpu, [
  'Limpiar polvo de ventiladores y disipador.',
  'Verificar que el ventilador gire correctamente.',
  'Cambiar pasta térmica si el equipo tiene mucho tiempo sin mantenimiento.'
]).
recomendacion(disco_danado, [
  'Respaldar información inmediatamente si el disco aún responde.',
  'Revisar estado SMART con CrystalDiskInfo o herramienta equivalente.',
  'Cambiar disco si hay sectores reasignados o errores críticos.'
]).
recomendacion(sistema_operativo_corrupto, [
  'Intentar reparación de inicio del sistema operativo.',
  'Restaurar a un punto anterior si está disponible.',
  'Reinstalar sistema operativo si la corrupción persiste.'
]).
recomendacion(malware, [
  'Desconectar de internet temporalmente.',
  'Ejecutar análisis con antivirus actualizado.',
  'Eliminar programas sospechosos y revisar extensiones del navegador.'
]).
recomendacion(driver_red, [
  'Reiniciar router y equipo.',
  'Olvidar la red WiFi y volver a conectarse.',
  'Reinstalar controlador de red desde el fabricante.'
]).
recomendacion(puertos_usb_danados, [
  'Probar el dispositivo en otro puerto y en otra computadora.',
  'Reinstalar controladores USB desde Administrador de dispositivos.',
  'Revisar daño físico o suciedad en los puertos.'
]).
recomendacion(perifericos_defectuosos, [
  'Verificar conexión del teclado o mouse.',
  'Probar con otro periférico.',
  'Cambiar baterías si el dispositivo es inalámbrico.'
]).
recomendacion(audio_driver, [
  'Verificar dispositivo de salida seleccionado.',
  'Reinstalar controlador de audio.',
  'Revisar que el audio no esté silenciado en sistema o aplicación.'
]).
recomendacion(bateria_cargador, [
  'Probar otro cargador compatible.',
  'Revisar el puerto de carga.',
  'Generar reporte de batería y evaluar reemplazo.'
]).
recomendacion(pila_cmos, [
  'Cambiar pila CR2032 de la placa madre.',
  'Configurar fecha y hora en BIOS/UEFI.',
  'Guardar configuración del BIOS después del cambio.'
]).
recomendacion(bajo_rendimiento_general, [
  'Revisar procesos de inicio y consumo de recursos.',
  'Liberar espacio en disco y desinstalar software innecesario.',
  'Considerar aumentar RAM o cambiar a SSD si el equipo usa disco mecánico.'
]).

% -----------------------------
% Uso de variables, listas y corte (!)
% -----------------------------
severidad_peso(critica, 4) :- !.
severidad_peso(alta, 3) :- !.
severidad_peso(media, 2) :- !.
severidad_peso(baja, 1).

contiene_todos([], _).
contiene_todos([S|Resto], SintomasUsuario) :-
    member(S, SintomasUsuario),
    contiene_todos(Resto, SintomasUsuario).

coincidencias([], _, 0).
coincidencias([S|Resto], SintomasUsuario, Total) :-
    member(S, SintomasUsuario), !,
    coincidencias(Resto, SintomasUsuario, Parcial),
    Total is Parcial + 1.
coincidencias([_|Resto], SintomasUsuario, Total) :-
    coincidencias(Resto, SintomasUsuario, Total).

crear_diagnostico(SintomasUsuario, Dict) :-
    falla(ID, Nombre, Categoria, Severidad, Requeridos, Apoyo),
    contiene_todos(Requeridos, SintomasUsuario),
    append(Requeridos, Apoyo, SintomasBase),
    coincidencias(SintomasBase, SintomasUsuario, Match),
    length(SintomasBase, Cantidad),
    Cantidad > 0,
    Score is round((Match * 100) / Cantidad),
    Score >= 45,
    recomendacion(ID, Recomendaciones),
    severidad_peso(Severidad, Peso),
    Dict = _{
        id: ID,
        name: Nombre,
        category: Categoria,
        severity: Severidad,
        severity_weight: Peso,
        score: Score,
        matched_symptoms: Match,
        required_symptoms: Requeridos,
        support_symptoms: Apoyo,
        recommendations: Recomendaciones
    }.

comparar_diagnosticos(Orden, A, B) :-
    ScoreA = A.score,
    ScoreB = B.score,
    PesoA = A.severity_weight,
    PesoB = B.severity_weight,
    ValorA is ScoreA + PesoA,
    ValorB is ScoreB + PesoB,
    ( ValorA > ValorB -> Orden = '<'
    ; ValorA < ValorB -> Orden = '>'
    ; Orden = '='
    ).

fallback_diagnostico([_{
    id: sin_diagnostico_concluyente,
    name: 'Sin diagnóstico concluyente',
    category: general,
    severity: baja,
    severity_weight: 1,
    score: 0,
    matched_symptoms: 0,
    required_symptoms: [],
    support_symptoms: [],
    recommendations: ['Seleccione más síntomas o consulte con un técnico si la falla persiste.']
}]).

diagnosticar(SintomasUsuario, DiagnosticosOrdenados) :-
    findall(D, crear_diagnostico(SintomasUsuario, D), Diagnosticos),
    ( Diagnosticos == []
      -> fallback_diagnostico(DiagnosticosOrdenados)
      ; predsort(comparar_diagnosticos, Diagnosticos, DiagnosticosOrdenados)
    ), !.

catalogo_sintomas(Sintomas) :-
    findall(_{id:ID, name:Nombre, category:Categoria, weight:Peso}, sintoma(ID, Nombre, Categoria, Peso), Sintomas).

responder_sintomas :-
    catalogo_sintomas(Sintomas),
    json_write_dict(current_output, _{symptoms:Sintomas}, [width(0)]).

responder_diagnostico(SintomasUsuario) :-
    diagnosticar(SintomasUsuario, Diagnosticos),
    json_write_dict(current_output, _{diagnostics:Diagnosticos}, [width(0)]).

doctor_byte_cli :-
    read_string(user_input, _, Entrada),
    atom_json_dict(Entrada, Data, [value_string_as(atom)]),
    Mode = Data.mode,
    ( Mode == symptoms -> responder_sintomas
    ; Mode == diagnose -> responder_diagnostico(Data.symptoms)
    ; json_write_dict(current_output, _{error:'Modo no soportado'}, [width(0)])
    ),
    halt.
