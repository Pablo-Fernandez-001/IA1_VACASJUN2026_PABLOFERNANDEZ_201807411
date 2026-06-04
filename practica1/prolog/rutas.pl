% ==========================================================
% Ruta mas corta entre ciudades usando Prolog
% ==========================================================

:- dynamic conexion/3.

% ----------------------------------------------------------
% Base de conocimiento inicial
% conexion(Origen, Destino, Distancia).
% Distancias aproximadas en kilometros.
% ----------------------------------------------------------

conexion(guatemala, antigua, 45).
conexion(guatemala, escuintla, 60).
conexion(guatemala, jalapa, 100).
conexion(guatemala, zacapa, 145).
conexion(guatemala, coban, 210).

conexion(antigua, chimaltenango, 35).
conexion(chimaltenango, quetzaltenango, 150).

conexion(escuintla, mazatenango, 120).
conexion(mazatenango, quetzaltenango, 90).
conexion(mazatenango, retalhuleu, 35).
conexion(retalhuleu, quetzaltenango, 55).

conexion(coban, flores, 300).
conexion(flores, puerto_barrios, 350).

conexion(puerto_barrios, zacapa, 100).
conexion(zacapa, chiquimula, 35).
conexion(chiquimula, jalapa, 95).

% ----------------------------------------------------------
% camino/3
% Permite que las conexiones sean bidireccionales.
% Si existe conexion(A, B, D), tambien se puede viajar B -> A.
% ----------------------------------------------------------

camino(A, B, D) :-
    conexion(A, B, D).

camino(A, B, D) :-
    conexion(B, A, D).

% ----------------------------------------------------------
% ciudad/1
% Obtiene ciudades conocidas desde origen o destino.
% ----------------------------------------------------------

ciudad(C) :-
    conexion(C, _, _).

ciudad(C) :-
    conexion(_, C, _).

% ----------------------------------------------------------
% ciudades/1
% Devuelve lista unica y ordenada de ciudades.
% ----------------------------------------------------------

ciudades(ListaCiudades) :-
    findall(C, ciudad(C), Ciudades),
    sort(Ciudades, ListaCiudades).

% ----------------------------------------------------------
% conexion_existente/2
% Verifica si ya existe una conexion entre dos ciudades.
% ----------------------------------------------------------

conexion_existente(A, B) :-
    camino(A, B, _).

% ----------------------------------------------------------
% ruta/4
% Busca una ruta sin repetir ciudades.
% ----------------------------------------------------------

ruta(Origen, Destino, Ruta, Distancia) :-
    Origen \= Destino,
    viajar(Origen, Destino, [Origen], RutaInvertida, Distancia),
    reverse(RutaInvertida, Ruta).

% Caso base:
% Existe camino directo hacia el destino.
viajar(Origen, Destino, Visitados, [Destino|Visitados], Distancia) :-
    camino(Origen, Destino, Distancia).

% Caso recursivo:
% Busca una ciudad intermedia que no haya sido visitada.
viajar(Origen, Destino, Visitados, Ruta, DistanciaTotal) :-
    camino(Origen, Intermedio, Distancia1),
    Intermedio \= Destino,
    \+ member(Intermedio, Visitados),
    viajar(Intermedio, Destino, [Intermedio|Visitados], Ruta, Distancia2),
    DistanciaTotal is Distancia1 + Distancia2.

% ----------------------------------------------------------
% rutas_posibles/3
% Obtiene todas las rutas posibles ordenadas por distancia.
% ----------------------------------------------------------

rutas_posibles(Origen, Destino, RutasOrdenadas) :-
    findall(
        [Distancia, Ruta],
        ruta(Origen, Destino, Ruta, Distancia),
        Rutas
    ),
    sort(Rutas, RutasOrdenadas).

% ----------------------------------------------------------
% ruta_mas_corta/4
% Obtiene la primera ruta luego de ordenar por distancia.
% ----------------------------------------------------------

ruta_mas_corta(Origen, Destino, MejorRuta, MenorDistancia) :-
    rutas_posibles(Origen, Destino, [[MenorDistancia, MejorRuta]|_]).

% ----------------------------------------------------------
% agregar_conexion/3
% Agrega dinamicamente una conexion nueva a Prolog.
% ----------------------------------------------------------

agregar_conexion(Origen, Destino, Distancia) :-
    Distancia > 0,
    \+ conexion_existente(Origen, Destino),
    assertz(conexion(Origen, Destino, Distancia)).

% ----------------------------------------------------------
% eliminar_conexion/2
% Elimina dinamicamente una conexion.
% ----------------------------------------------------------

eliminar_conexion(Origen, Destino) :-
    retractall(conexion(Origen, Destino, _)),
    retractall(conexion(Destino, Origen, _)).