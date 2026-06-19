:- use_module(library(http/json)).
:- [facts].
:- [rules].

valor_none(@(null), none) :- !.
valor_none(null, none) :- !.
valor_none("", none) :- !.
valor_none(Value, Value).

cargar_robot(Dict) :-
    valor_none(Dict.carrying, Carrying),
    assertz(robot_estado(Dict.id, Dict.x, Dict.y, Carrying)).

cargar_paquete(Dict) :-
    assertz(paquete_estado(Dict.id, Dict.x, Dict.y, Dict.zone, Dict.status)).

cargar_estado(Payload) :-
    limpiar_estado,
    forall(member(Robot, Payload.robots), cargar_robot(Robot)),
    forall(member(Package, Payload.packages), cargar_paquete(Package)).

warehouse_cli :-
    read_string(user_input, _, Input),
    atom_json_dict(Input, Payload, [value_string_as(atom)]),
    cargar_estado(Payload),
    Robot = Payload.robot_id,
    accion(Robot, Accion),
    explicacion(Robot, Accion, Reason),
    Response = _{
        robot_id: Robot,
        action: Accion,
        reason: Reason,
        source: prolog
    },
    json_write_dict(current_output, Response, [width(0)]),
    halt.
