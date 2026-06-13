:- use_module(library(http/json)).
:- use_module(library(lists)).
:- use_module(library(pairs)).

% Doctor Byte: motor experto y administracion de la base de conocimiento.
% Los sintomas, fallas, recomendaciones y reglas viven como hechos Prolog
% persistentes en doctor_byte_knowledge.pl. SQLite no participa en inferencia.

severidad_peso(critica, 4) :- !.
severidad_peso(alta, 3) :- !.
severidad_peso(media, 2) :- !.
severidad_peso(baja, 1) :- !.
severidad_peso(_, 1).

bool_value(@(true), true) :- !.
bool_value(@(false), false) :- !.
bool_value(true, true) :- !.
bool_value(false, false) :- !.
bool_value(_, false).

cargar_conocimiento(Path) :-
    consult(Path).

symptom_dict(_{id:Id, name:Name, category:Category, weight:Weight}) :-
    symptom(Id, Name, Category, Weight).

failure_dict(_{id:Id, name:Name, category:Category, severity:Severity, message:Message, solution_steps:Steps}) :-
    failure(Id, Name, Category, Severity, Message),
    findall(Order-_{order:Order, text:Text}, solution_step(Id, Order, Text), RawSteps),
    keysort(RawSteps, SortedSteps),
    pairs_values(SortedSteps, Steps).

recommendation_dict(_{id:Id, failure_id:FailureId, text:Text, order:Order}) :-
    recommendation(Id, FailureId, Text, Order).

rule_dict(_{id:Id, failure_id:FailureId, required_symptoms:Required, support_symptoms:Support, min_score:MinScore, enabled:Enabled}) :-
    diagnosis_rule(Id, FailureId, Required, Support, MinScore, Enabled).

knowledge_dict(_{symptoms:Symptoms, failures:Failures, recommendations:Recommendations, diagnosis_rules:Rules}) :-
    findall(S, symptom_dict(S), Symptoms),
    findall(F, failure_dict(F), Failures),
    findall(R, recommendation_dict(R), Recommendations),
    findall(Rule, rule_dict(Rule), Rules).

peso_sintoma(Id, Peso) :- symptom(Id, _, _, Peso), !.
peso_sintoma(_, 1).

puntuar_sintomas([], _, _, 0, 0, []).
puntuar_sintomas([S|Resto], Usuario, Multiplicador, Puntaje, Posible, Coincidentes) :-
    peso_sintoma(S, PesoBase),
    Peso is PesoBase * Multiplicador,
    puntuar_sintomas(Resto, Usuario, Multiplicador, PuntajeResto, PosibleResto, CoincidentesResto),
    Posible is PosibleResto + Peso,
    ( memberchk(S, Usuario)
      -> Puntaje is PuntajeResto + Peso,
         Coincidentes = [S|CoincidentesResto]
      ;  Puntaje = PuntajeResto,
         Coincidentes = CoincidentesResto
    ).

faltantes([], _, []).
faltantes([S|Resto], Usuario, Faltantes) :-
    faltantes(Resto, Usuario, FaltantesResto),
    ( memberchk(S, Usuario) -> Faltantes = FaltantesResto ; Faltantes = [S|FaltantesResto] ).

unir_unicos([], Lista, Lista).
unir_unicos([S|Resto], Lista, Resultado) :-
    ( memberchk(S, Lista)
      -> unir_unicos(Resto, Lista, Resultado)
      ;  unir_unicos(Resto, [S|Lista], Resultado)
    ).

clamp(Min, Max, Valor, Resultado) :-
    ( Valor < Min -> Resultado = Min
    ; Valor > Max -> Resultado = Max
    ; Resultado = Valor
    ).

crear_diagnostico(SintomasUsuario, RuleId, FailureId, Required, Support, MinScore, Dict) :-
    failure(FailureId, Name, Category, Severity, Message),
    severidad_peso(Severity, SeverityWeight),
    puntuar_sintomas(Required, SintomasUsuario, 2, RequiredScore, RequiredPossible, RequiredMatches),
    puntuar_sintomas(Support, SintomasUsuario, 1, SupportScore, SupportPossible, SupportMatches),
    Possible is RequiredPossible + SupportPossible,
    TotalScore is RequiredScore + SupportScore,
    ( Possible =:= 0 -> Score = 0 ; Score is round((TotalScore * 100) / Possible) ),
    unir_unicos(RequiredMatches, SupportMatches, MatchUnsorted),
    sort(MatchUnsorted, Matches),
    length(Matches, MatchCount),
    faltantes(Required, SintomasUsuario, Missing),
    length(Required, RequiredCount),
    ( RequiredCount =:= 0 -> ProblemPercentage = Score
    ; length(RequiredMatches, RequiredMatchCount),
      ProblemPercentage is round((RequiredMatchCount * 100) / RequiredCount)
    ),
    RawEffectiveness is 45 + round(Score * 0.5),
    clamp(0, 98, RawEffectiveness, Effectiveness),
    ( Score >= MinScore -> Passes = true ; Passes = false ),
    findall(Text, recommendation(_, FailureId, Text, _), Recommendations),
    findall(Order-Step, solution_step(FailureId, Order, Step), StepPairs),
    keysort(StepPairs, SortedStepPairs),
    pairs_values(SortedStepPairs, SolutionSteps),
    Dict = _{
        id:FailureId, rule_id:RuleId, name:Name, message:Message,
        category:Category, severity:Severity, severity_weight:SeverityWeight,
        score:Score, probability:Score, problem_percentage:ProblemPercentage,
        effectiveness_probability:Effectiveness, matched_symptoms:MatchCount,
        matched_symptom_ids:Matches, missing_required_symptoms:Missing,
        required_symptoms:Required, support_symptoms:Support,
        recommendations:Recommendations, solution_steps:SolutionSteps,
        min_score:MinScore, passes_threshold:Passes
    }.

comparar_diagnosticos(Order, A, B) :-
    ValueA is (A.score * 10) + A.severity_weight,
    ValueB is (B.score * 10) + B.severity_weight,
    ( ValueA > ValueB -> Order = '<'
    ; ValueA < ValueB -> Order = '>'
    ; compare(Order, A.id, B.id)
    ).

diagnosticar(Symptoms, Diagnostics) :-
    findall(D,
        ( diagnosis_rule(RuleId, FailureId, Required, Support, MinScore, true),
          crear_diagnostico(Symptoms, RuleId, FailureId, Required, Support, MinScore, D)
        ),
        RawDiagnostics),
    predsort(comparar_diagnosticos, RawDiagnostics, Diagnostics), !.

valid_symptom_refs([]).
valid_symptom_refs([Id|Rest]) :- symptom(Id, _, _, _), valid_symptom_refs(Rest).

assert_payload_symptom(Payload) :-
    assertz(symptom(Payload.id, Payload.name, Payload.category, Payload.weight)).

assert_payload_failure(Payload) :-
    assertz(failure(Payload.id, Payload.name, Payload.category, Payload.severity, Payload.message)),
    assert_steps(Payload.id, Payload.solution_steps, 1).

assert_steps(_, [], _).
assert_steps(FailureId, [Text|Rest], Order) :-
    assertz(solution_step(FailureId, Order, Text)),
    Next is Order + 1,
    assert_steps(FailureId, Rest, Next).

assert_payload_recommendation(Payload) :-
    assertz(recommendation(Payload.id, Payload.failure_id, Payload.text, Payload.order)).

assert_payload_rule(Payload) :-
    bool_value(Payload.enabled, Enabled),
    assertz(diagnosis_rule(Payload.id, Payload.failure_id, Payload.required_symptoms, Payload.support_symptoms, Payload.min_score, Enabled)).

replace_symptom_in_list([], _, _, []).
replace_symptom_in_list([Old|Rest], Old, New, [New|Updated]) :- !,
    replace_symptom_in_list(Rest, Old, New, Updated).
replace_symptom_in_list([Item|Rest], Old, New, [Item|Updated]) :-
    replace_symptom_in_list(Rest, Old, New, Updated).

replace_symptom_references(Old, New) :-
    findall(rule(Id, FailureId, Required, Support, MinScore, Enabled),
        diagnosis_rule(Id, FailureId, Required, Support, MinScore, Enabled), Rules),
    retractall(diagnosis_rule(_, _, _, _, _, _)),
    forall(member(rule(Id, FailureId, Required, Support, MinScore, Enabled), Rules),
        ( replace_symptom_in_list(Required, Old, New, UpdatedRequired),
          replace_symptom_in_list(Support, Old, New, UpdatedSupport),
          assertz(diagnosis_rule(Id, FailureId, UpdatedRequired, UpdatedSupport, MinScore, Enabled))
        )).

remove_symptom_references(SymptomId) :-
    findall(rule(Id, FailureId, Required, Support, MinScore, Enabled),
        diagnosis_rule(Id, FailureId, Required, Support, MinScore, Enabled), Rules),
    retractall(diagnosis_rule(_, _, _, _, _, _)),
    forall(member(rule(Id, FailureId, Required, Support, MinScore, Enabled), Rules),
        ( delete(Required, SymptomId, UpdatedRequired),
          delete(Support, SymptomId, UpdatedSupport),
          assertz(diagnosis_rule(Id, FailureId, UpdatedRequired, UpdatedSupport, MinScore, Enabled))
        )).

write_fact(Stream, Goal) :- forall(call(Goal), (copy_term(Goal, Fact), portray_clause(Stream, Fact))).

persist_knowledge(Path) :-
    atom_concat(Path, '.tmp', TempPath),
    setup_call_cleanup(
        open(TempPath, write, Stream, [encoding(utf8)]),
        ( format(Stream, ':- dynamic symptom/4, failure/5, recommendation/4, diagnosis_rule/6, solution_step/3.~n~n', []),
          write_fact(Stream, symptom(_, _, _, _)), nl(Stream),
          write_fact(Stream, failure(_, _, _, _, _)), nl(Stream),
          write_fact(Stream, recommendation(_, _, _, _)), nl(Stream),
          write_fact(Stream, solution_step(_, _, _)), nl(Stream),
          write_fact(Stream, diagnosis_rule(_, _, _, _, _, _))
        ),
        close(Stream)
    ),
    rename_file(TempPath, Path).

handle_mode(knowledge, _, Response) :- knowledge_dict(Response).
handle_mode(symptoms, _, _{symptoms:Symptoms}) :- findall(S, symptom_dict(S), Symptoms).
handle_mode(failures, _, _{failures:Failures}) :- findall(F, failure_dict(F), Failures).
handle_mode(recommendations, _, _{recommendations:Recommendations}) :- findall(R, recommendation_dict(R), Recommendations).
handle_mode(rules, _, _{diagnosis_rules:Rules}) :- findall(R, rule_dict(R), Rules).
handle_mode(diagnose, Payload, _{diagnostics:Diagnostics}) :- diagnosticar(Payload.symptoms, Diagnostics).

handle_mode(create_symptom, Payload, Payload.entity) :-
    \+ symptom(Payload.entity.id, _, _, _), assert_payload_symptom(Payload.entity).
handle_mode(update_symptom, Payload, Payload.entity) :-
    symptom(Payload.target_id, _, _, _),
    retractall(symptom(Payload.target_id, _, _, _)),
    assert_payload_symptom(Payload.entity),
    ( Payload.target_id == Payload.entity.id -> true ; replace_symptom_references(Payload.target_id, Payload.entity.id) ).
handle_mode(delete_symptom, Payload, _{deleted:true, id:Payload.target_id}) :-
    symptom(Payload.target_id, _, _, _), retractall(symptom(Payload.target_id, _, _, _)), remove_symptom_references(Payload.target_id).

handle_mode(create_failure, Payload, Payload.entity) :-
    \+ failure(Payload.entity.id, _, _, _, _), assert_payload_failure(Payload.entity).
handle_mode(update_failure, Payload, Payload.entity) :-
    failure(Payload.target_id, _, _, _, _),
    retractall(failure(Payload.target_id, _, _, _, _)), retractall(solution_step(Payload.target_id, _, _)),
    assert_payload_failure(Payload.entity),
    ( Payload.target_id == Payload.entity.id -> true
    ; forall(retract(recommendation(Id, Payload.target_id, Text, Order)), assertz(recommendation(Id, Payload.entity.id, Text, Order))),
      forall(retract(diagnosis_rule(Id, Payload.target_id, Req, Sup, Min, Enabled)), assertz(diagnosis_rule(Id, Payload.entity.id, Req, Sup, Min, Enabled)))
    ).
handle_mode(delete_failure, Payload, _{deleted:true, id:Payload.target_id}) :-
    failure(Payload.target_id, _, _, _, _),
    retractall(failure(Payload.target_id, _, _, _, _)), retractall(solution_step(Payload.target_id, _, _)),
    retractall(recommendation(_, Payload.target_id, _, _)), retractall(diagnosis_rule(_, Payload.target_id, _, _, _, _)).

handle_mode(create_recommendation, Payload, Payload.entity) :-
    \+ recommendation(Payload.entity.id, _, _, _), failure(Payload.entity.failure_id, _, _, _, _),
    assert_payload_recommendation(Payload.entity).
handle_mode(update_recommendation, Payload, Payload.entity) :-
    recommendation(Payload.target_id, _, _, _), failure(Payload.entity.failure_id, _, _, _, _),
    retractall(recommendation(Payload.target_id, _, _, _)), assert_payload_recommendation(Payload.entity).
handle_mode(delete_recommendation, Payload, _{deleted:true, id:Payload.target_id}) :-
    recommendation(Payload.target_id, _, _, _), retractall(recommendation(Payload.target_id, _, _, _)).

handle_mode(create_rule, Payload, Payload.entity) :-
    \+ diagnosis_rule(Payload.entity.id, _, _, _, _, _), failure(Payload.entity.failure_id, _, _, _, _),
    valid_symptom_refs(Payload.entity.required_symptoms), valid_symptom_refs(Payload.entity.support_symptoms),
    assert_payload_rule(Payload.entity).
handle_mode(update_rule, Payload, Payload.entity) :-
    diagnosis_rule(Payload.target_id, _, _, _, _, _), failure(Payload.entity.failure_id, _, _, _, _),
    valid_symptom_refs(Payload.entity.required_symptoms), valid_symptom_refs(Payload.entity.support_symptoms),
    retractall(diagnosis_rule(Payload.target_id, _, _, _, _, _)), assert_payload_rule(Payload.entity).
handle_mode(delete_rule, Payload, _{deleted:true, id:Payload.target_id}) :-
    diagnosis_rule(Payload.target_id, _, _, _, _, _), retractall(diagnosis_rule(Payload.target_id, _, _, _, _, _)).

mutation_mode(create_symptom). mutation_mode(update_symptom). mutation_mode(delete_symptom).
mutation_mode(create_failure). mutation_mode(update_failure). mutation_mode(delete_failure).
mutation_mode(create_recommendation). mutation_mode(update_recommendation). mutation_mode(delete_recommendation).
mutation_mode(create_rule). mutation_mode(update_rule). mutation_mode(delete_rule).

doctor_byte_cli :-
    read_string(user_input, _, Input),
    atom_json_dict(Input, Payload, [value_string_as(atom)]),
    cargar_conocimiento(Payload.knowledge_path),
    Mode = Payload.mode,
    ( catch(handle_mode(Mode, Payload, Response), Error, (term_string(Error, ErrorText), Response = _{error:ErrorText}))
      -> ( mutation_mode(Mode), \+ get_dict(error, Response, _) -> persist_knowledge(Payload.knowledge_path) ; true )
      ;  Response = _{error:'Operacion invalida o referencia inexistente'}
    ),
    json_write_dict(current_output, Response, [width(0)]),
    halt.
