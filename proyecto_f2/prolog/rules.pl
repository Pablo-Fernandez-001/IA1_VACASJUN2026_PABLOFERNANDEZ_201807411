:- use_module(library(lists)).
:- use_module(library(pairs)).

limpiar_estado :-
    retractall(robot_estado(_, _, _, _)),
    retractall(paquete_estado(_, _, _, _, _)).

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
            distancia_manhattan(RX, RY, PX, PY, Distancia)
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

paso_hacia(X, _, TX, _, mover_derecha) :- TX > X.
paso_hacia(X, _, TX, _, mover_izquierda) :- TX < X.
paso_hacia(_, Y, _, TY, mover_abajo) :- TY > Y.
paso_hacia(_, Y, _, TY, mover_arriba) :- TY < Y.

candidatos_movimiento(X, Y, TX, TY, Candidatos) :-
    findall(Accion, paso_hacia(X, Y, TX, TY, Accion), Preferidos),
    append(Preferidos, [mover_derecha, mover_abajo, mover_izquierda, mover_arriba], Candidatos).

movimiento_valido(X, Y, Accion) :-
    movimiento(Accion, DX, DY),
    NX is X + DX,
    NY is Y + DY,
    celda_libre(NX, NY).

decision_movimiento(Robot, Accion) :-
    robot_estado(Robot, X, Y, _),
    objetivo(Robot, posicion(TX, TY)),
    candidatos_movimiento(X, Y, TX, TY, Candidatos),
    member(Accion, Candidatos),
    movimiento_valido(X, Y, Accion), !.

accion(Robot, recoger_paquete) :- puede_recoger(Robot, _), !.
accion(Robot, entregar_paquete) :- puede_entregar(Robot, _), !.
accion(Robot, Accion) :- decision_movimiento(Robot, Accion), !.
accion(_, esperar).

explicacion(Robot, recoger_paquete, Texto) :-
    puede_recoger(Robot, Paquete), format(atom(Texto), 'El robot esta sobre ~w y puede recogerlo.', [Paquete]), !.
explicacion(Robot, entregar_paquete, Texto) :-
    puede_entregar(Robot, Paquete), format(atom(Texto), 'El robot llego a la zona de entrega de ~w.', [Paquete]), !.
explicacion(Robot, Accion, Texto) :-
    objetivo(Robot, posicion(TX, TY)),
    format(atom(Texto), 'Prolog eligio ~w para acercarse al objetivo (~w,~w).', [Accion, TX, TY]), !.
explicacion(_, esperar, 'No hay accion disponible o todos los paquetes fueron atendidos.').
