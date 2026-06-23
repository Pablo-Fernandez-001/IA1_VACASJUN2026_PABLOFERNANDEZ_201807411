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

cargar_zona(Dict) :-
    assertz(zona_entrega(Dict.id, posicion(Dict.x, Dict.y))).

cargar_obstaculo(Dict) :-
    assertz(obstaculo(posicion(Dict.x, Dict.y))).

cargar_estado(Payload) :-
    limpiar_estado,
    Mapa = Payload.map,
    assertz(mapa(Mapa.width, Mapa.height)),
    forall(member(Robot, Payload.robots), cargar_robot(Robot)),
    forall(member(Package, Payload.packages), cargar_paquete(Package)),
    forall(member(Zone, Payload.zones), cargar_zona(Zone)),
    forall(member(Obstacle, Payload.obstacles), cargar_obstaculo(Obstacle)).

warehouse_cli :-
    read_string(user_input, _, Input),
    atom_json_dict(Input, Payload, [value_string_as(atom)]),
    cargar_estado(Payload),
    Robot = Payload.robot_id,
    accion(Robot, Accion),
    explicacion(Robot, Accion, Reason),
    ruta_visual(Robot, Route),
    objetivo_visual(Robot, Target),
    Response = _{
        robot_id: Robot,
        action: Accion,
        reason: Reason,
        source: prolog,
        algorithm: bfs,
        route: Route,
        target: Target
    },
    json_write_dict(current_output, Response, [width(0)]),
    halt.
