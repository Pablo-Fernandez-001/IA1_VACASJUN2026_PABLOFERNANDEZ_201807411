:- use_module(library(lists)).
:- use_module(library(pairs)).

limpiar_estado :-
    retractall(robot_estado(_, _, _, _)),
    retractall(paquete_estado(_, _, _, _, _)),
    retractall(mapa(_, _)),
    retractall(zona_entrega(_, _)),
    retractall(obstaculo(_)).

dentro_mapa(X, Y) :-
    mapa(Ancho, Alto),
    X >= 1, X =< Ancho,
    Y >= 1, Y =< Alto.

celda_bloqueada(X, Y) :- obstaculo(posicion(X, Y)).
celda_libre(X, Y) :- dentro_mapa(X, Y), \+ celda_bloqueada(X, Y).

movimiento(mover_arriba, 0, -1).
movimiento(mover_abajo, 0, 1).
movimiento(mover_izquierda, -1, 0).
movimiento(mover_derecha, 1, 0).

distancia_manhattan(X1, Y1, X2, Y2, Distancia) :-
    DX is abs(X1 - X2),
    DY is abs(Y1 - Y2),
    Distancia is DX + DY.

puede_recoger(Robot, Paquete) :-
    robot_estado(Robot, X, Y, none),
    paquete_estado(Paquete, X, Y, _, pendiente).

puede_entregar(Robot, Paquete) :-
    robot_estado(Robot, X, Y, Paquete),
    Paquete \= none,
    paquete_estado(Paquete, _, _, Zona, en_robot),
    zona_entrega(Zona, posicion(X, Y)).

paquete_pendiente_mas_cercano(Robot, Paquete) :-
    robot_estado(Robot, RX, RY, none),
    findall(
        Distancia-Id,
        (
            paquete_estado(Id, PX, PY, _, pendiente),
            ruta_mas_corta(
                posicion(RX, RY),
                posicion(PX, PY),
                Acciones,
                _
            ),
            length(Acciones, Distancia)
        ),
        Pares
    ),
    keysort(Pares, [_-Paquete|_]).

objetivo(Robot, posicion(TX, TY)) :-
    robot_estado(Robot, _, _, Paquete),
    Paquete \= none,
    paquete_estado(Paquete, _, _, Zona, en_robot),
    zona_entrega(Zona, posicion(TX, TY)), !.
objetivo(Robot, posicion(TX, TY)) :-
    paquete_pendiente_mas_cercano(Robot, Paquete),
    paquete_estado(Paquete, TX, TY, _, pendiente).

vecino(posicion(X, Y), posicion(NX, NY), Accion) :-
    movimiento(Accion, DX, DY),
    NX is X + DX,
    NY is Y + DY,
    celda_libre(NX, NY).

% Busqueda en anchura: garantiza una ruta minima en cantidad de movimientos.
ruta_mas_corta(Inicio, Destino, Acciones, Posiciones) :-
    bfs(
        [nodo(Inicio, [], [Inicio])],
        Destino,
        [Inicio],
        AccionesInvertidas,
        PosicionesInvertidas
    ),
    reverse(AccionesInvertidas, Acciones),
    reverse(PosicionesInvertidas, Posiciones).

bfs([nodo(Destino, Acciones, Posiciones)|_], Destino, _, Acciones, Posiciones) :- !.
bfs([nodo(Actual, Acciones, Posiciones)|Pendientes], Destino, Visitadas, Ruta, Camino) :-
    findall(
        nodo(Siguiente, [Accion|Acciones], [Siguiente|Posiciones]),
        (
            vecino(Actual, Siguiente, Accion),
            \+ memberchk(Siguiente, Visitadas)
        ),
        NuevosNodos
    ),
    nodos_posiciones(NuevosNodos, NuevasPosiciones),
    append(Visitadas, NuevasPosiciones, VisitadasActualizadas),
    append(Pendientes, NuevosNodos, ColaActualizada),
    bfs(ColaActualizada, Destino, VisitadasActualizadas, Ruta, Camino).

nodos_posiciones([], []).
nodos_posiciones([nodo(Posicion, _, _)|Resto], [Posicion|Posiciones]) :-
    nodos_posiciones(Resto, Posiciones).

plan_ruta(Robot, Acciones, Pasos, Objetivo) :-
    robot_estado(Robot, X, Y, _),
    objetivo(Robot, Objetivo),
    ruta_mas_corta(posicion(X, Y), Objetivo, Acciones, [_|Pasos]).

decision_movimiento(Robot, Accion) :-
    plan_ruta(Robot, [Accion|_], _, _), !.

accion(Robot, recoger_paquete) :- puede_recoger(Robot, _), !.
accion(Robot, entregar_paquete) :- puede_entregar(Robot, _), !.
accion(Robot, Accion) :- decision_movimiento(Robot, Accion), !.
accion(_, esperar).

explicacion(Robot, recoger_paquete, Texto) :-
    puede_recoger(Robot, Paquete), format(atom(Texto), 'El robot esta sobre ~w y puede recogerlo.', [Paquete]), !.
explicacion(Robot, entregar_paquete, Texto) :-
    puede_entregar(Robot, Paquete), format(atom(Texto), 'El robot llego a la zona de entrega de ~w.', [Paquete]), !.
explicacion(Robot, Accion, Texto) :-
    plan_ruta(Robot, Acciones, _, posicion(TX, TY)),
    length(Acciones, Pasos),
    format(
        atom(Texto),
        'Prolog calculo con BFS una ruta minima de ~w pasos hacia (~w,~w) y eligio ~w.',
        [Pasos, TX, TY, Accion]
    ), !.
explicacion(_, esperar, 'No hay accion disponible o todos los paquetes fueron atendidos.').

posicion_dict(posicion(X, Y), _{x:X, y:Y}).

ruta_visual(Robot, Ruta) :-
    plan_ruta(Robot, _, Pasos, _),
    maplist(posicion_dict, Pasos, Ruta), !.
ruta_visual(_, []).

objetivo_visual(Robot, _{x:X, y:Y}) :-
    objetivo(Robot, posicion(X, Y)), !.
objetivo_visual(_, @(null)).
