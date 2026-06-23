:- dynamic robot_estado/4.
:- dynamic paquete_estado/5.
:- dynamic mapa/2.
:- dynamic zona_entrega/2.
:- dynamic obstaculo/1.

mapa(10, 10).

robot_base(r1, posicion(1, 1), libre).

zona_entrega(zona_a, posicion(10, 10)).
zona_entrega(zona_b, posicion(1, 10)).

paquete_base(p1, posicion(1, 3), zona_a, pendiente).
paquete_base(p2, posicion(4, 2), zona_b, pendiente).
paquete_base(p3, posicion(6, 8), zona_a, pendiente).
paquete_base(p4, posicion(9, 1), zona_b, pendiente).
paquete_base(p5, posicion(3, 9), zona_a, pendiente).

obstaculo(posicion(3, 1)).
obstaculo(posicion(3, 2)).
obstaculo(posicion(3, 3)).
obstaculo(posicion(5, 5)).
obstaculo(posicion(6, 5)).
obstaculo(posicion(7, 5)).
obstaculo(posicion(2, 7)).
obstaculo(posicion(8, 3)).

acciones([mover_arriba, mover_abajo, mover_izquierda, mover_derecha, recoger_paquete, entregar_paquete, esperar]).
