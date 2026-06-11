:- use_module(library(http/json)).

% Doctor Byte - motor de inferencia editable.
% Los hechos se cargan desde doctor_byte_data.json y las reglas de
% diagnostico se evalúan en Prolog para mantener la logica declarativa.

leer_conocimiento(Path, Data) :-
    open(Path, read, Stream, [encoding(utf8)]),
    json_read_dict(Stream, Data, [value_string_as(atom)]),
    close(Stream).

severidad_peso(critica, 4) :- !.
severidad_peso(alta, 3) :- !.
severidad_peso(media, 2) :- !.
severidad_peso(baja, 1) :- !.
severidad_peso(_, 1).

regla_habilitada(Regla) :-
    ( get_dict(enabled, Regla, Estado) -> Estado \== false, Estado \== @(false) ; true ).

campo(Regla, Llave, Defecto, Valor) :-
    ( get_dict(Llave, Regla, Valor) -> true ; Valor = Defecto ).

peso_sintoma(Catalogo, ID, Peso) :-
    member(Sintoma, Catalogo),
    Sintoma.id == ID,
    Peso = Sintoma.weight, !.
peso_sintoma(_, _, 1).

puntuar_sintomas([], _, _, _, 0, 0, []).
puntuar_sintomas([S|Resto], Usuario, Catalogo, Multiplicador, Puntaje, Posible, Coincidentes) :-
    peso_sintoma(Catalogo, S, PesoBase),
    Peso is PesoBase * Multiplicador,
    puntuar_sintomas(Resto, Usuario, Catalogo, Multiplicador, PuntajeResto, PosibleResto, CoincidentesResto),
    Posible is PosibleResto + Peso,
    ( member(S, Usuario)
      -> Puntaje is PuntajeResto + Peso,
         Coincidentes = [S|CoincidentesResto]
      ;  Puntaje = PuntajeResto,
         Coincidentes = CoincidentesResto
    ).

faltantes([], _, []).
faltantes([S|Resto], Usuario, Faltantes) :-
    faltantes(Resto, Usuario, FaltantesResto),
    ( member(S, Usuario)
      -> Faltantes = FaltantesResto
      ;  Faltantes = [S|FaltantesResto]
    ).

unir_unicos([], Lista, Lista).
unir_unicos([S|Resto], Lista, Resultado) :-
    ( member(S, Lista)
      -> unir_unicos(Resto, Lista, Resultado)
      ;  unir_unicos(Resto, [S|Lista], Resultado)
    ).

clamp(Min, Max, Valor, Resultado) :-
    ( Valor < Min -> Resultado = Min
    ; Valor > Max -> Resultado = Max
    ; Resultado = Valor
    ).

crear_diagnostico(SintomasUsuario, Data, Regla, Dict) :-
    regla_habilitada(Regla),
    Catalogo = Data.symptoms,
    campo(Regla, required_symptoms, [], Requeridos),
    campo(Regla, support_symptoms, [], Apoyo),
    puntuar_sintomas(Requeridos, SintomasUsuario, Catalogo, 2, PuntajeReq, PosibleReq, MatchReq),
    puntuar_sintomas(Apoyo, SintomasUsuario, Catalogo, 1, PuntajeApoyo, PosibleApoyo, MatchApoyo),
    PosibleTotal is PosibleReq + PosibleApoyo,
    PuntajeTotal is PuntajeReq + PuntajeApoyo,
    ( PosibleTotal =:= 0 -> Score = 0 ; Score is round((PuntajeTotal * 100) / PosibleTotal) ),
    campo(Regla, severity, baja, Severidad),
    severidad_peso(Severidad, PesoSeveridad),
    RiesgoCrudo is round((Score * PesoSeveridad) / 4),
    clamp(0, 100, RiesgoCrudo, PorcentajeProblema),
    EfectividadCruda is round((Score * 0.80) + ((5 - PesoSeveridad) * 5)),
    clamp(5, 95, EfectividadCruda, ProbabilidadEfectividad),
    unir_unicos(MatchReq, MatchApoyo, Coincidentes),
    length(Coincidentes, CantCoincidentes),
    faltantes(Requeridos, SintomasUsuario, FaltantesReq),
    campo(Regla, min_score, 0, MinScore),
    campo(Regla, recommendations, [], Recomendaciones),
    campo(Regla, solution_steps, [], RutaSolucion),
    campo(Regla, message, '', Mensaje),
    ( Score >= MinScore -> SuperaUmbral = true ; SuperaUmbral = false ),
    Dict = _{
        id: Regla.id,
        name: Regla.name,
        message: Mensaje,
        category: Regla.category,
        severity: Severidad,
        severity_weight: PesoSeveridad,
        score: Score,
        probability: Score,
        problem_percentage: PorcentajeProblema,
        effectiveness_probability: ProbabilidadEfectividad,
        matched_symptoms: CantCoincidentes,
        matched_symptom_ids: Coincidentes,
        missing_required_symptoms: FaltantesReq,
        required_symptoms: Requeridos,
        support_symptoms: Apoyo,
        recommendations: Recomendaciones,
        solution_steps: RutaSolucion,
        min_score: MinScore,
        passes_threshold: SuperaUmbral
    }.

comparar_diagnosticos(Orden, A, B) :-
    ScoreA = A.score,
    ScoreB = B.score,
    PesoA = A.severity_weight,
    PesoB = B.severity_weight,
    ValorA is (ScoreA * 10) + PesoA,
    ValorB is (ScoreB * 10) + PesoB,
    ( ValorA > ValorB -> Orden = '<'
    ; ValorA < ValorB -> Orden = '>'
    ; compare(Orden, A.id, B.id)
    ).

diagnosticar(SintomasUsuario, Data, DiagnosticosOrdenados) :-
    Reglas = Data.diagnosis_rules,
    findall(D, (member(Regla, Reglas), crear_diagnostico(SintomasUsuario, Data, Regla, D)), Diagnosticos),
    predsort(comparar_diagnosticos, Diagnosticos, DiagnosticosOrdenados), !.

responder_sintomas(Data) :-
    json_write_dict(current_output, _{symptoms:Data.symptoms}, [width(0)]).

responder_reglas(Data) :-
    json_write_dict(current_output, _{diagnosis_rules:Data.diagnosis_rules}, [width(0)]).

responder_conocimiento(Data) :-
    json_write_dict(current_output, Data, [width(0)]).

responder_diagnostico(SintomasUsuario, Data) :-
    diagnosticar(SintomasUsuario, Data, Diagnosticos),
    json_write_dict(current_output, _{diagnostics:Diagnosticos}, [width(0)]).

doctor_byte_cli :-
    read_string(user_input, _, Entrada),
    atom_json_dict(Entrada, Payload, [value_string_as(atom)]),
    leer_conocimiento(Payload.knowledge_path, Data),
    Mode = Payload.mode,
    ( Mode == symptoms -> responder_sintomas(Data)
    ; Mode == rules -> responder_reglas(Data)
    ; Mode == knowledge -> responder_conocimiento(Data)
    ; Mode == diagnose -> responder_diagnostico(Payload.symptoms, Data)
    ; json_write_dict(current_output, _{error:'Modo no soportado'}, [width(0)])
    ),
    halt.
