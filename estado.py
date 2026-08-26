"""
Modulo estado.py
-----------------
Define el "nucleo" funcional del juego: como se representa el estado
(jugadores, posiciones, turnos perdidos, ganador) y las funciones que
calculan un nuevo estado a partir de uno existente.

Todas las funciones de este archivo son puras: reciben datos, devuelven
datos nuevos, y nunca modifican lo que reciben ni dependen de nada
externo (no hay random, no hay input, no hay print). Por eso el estado
se representa con NamedTuple: son estructuras inmutables, no se pueden
modificar in place.
"""

from functools import reduce
from typing import NamedTuple, Tuple

import tablero


class Jugador(NamedTuple):
    nombre: str
    color: str
    posicion: int = 0
    turnos_perdidos: int = 0


class EstadoJuego(NamedTuple):
    jugadores: Tuple[Jugador, ...]


COLORES_DISPONIBLES = ["red", "blue", "green", "yellow"]
NOMBRES_COLORES = {"red": "Rojo", "blue": "Azul", "green": "Verde", "yellow": "Amarillo"}


def crear_jugadores(nombres):
    """
    Arma la lista inicial de jugadores, asignandole a cada nombre un
    color distinto en orden (rojo, azul, verde, amarillo).

    TECNICA: comprension de listas + zip para emparejar cada nombre
    con un color.
    """
    return [
        Jugador(nombre=nombre, color=color)
        for nombre, color in zip(nombres, COLORES_DISPONIBLES)
    ]


def crear_estado_inicial(nombres):
    return EstadoJuego(jugadores=tuple(crear_jugadores(nombres)))


def componer(*funciones):
    """
    Combina varias funciones de un solo argumento en una sola funcion,
    aplicandolas de derecha a izquierda (como la composicion matematica
    f(g(x))).

    TECNICA: composicion de funciones, implementada con reduce.
    """

    def funcion_combinada(valor_inicial):
        return reduce(
            lambda valor, funcion: funcion(valor),
            reversed(funciones),
            valor_inicial,
        )

    return funcion_combinada


def mover_jugador(jugador, pasos):
    """
    Devuelve un jugador NUEVO, resultado de avanzar (o retroceder, si
    pasos es negativo) esa cantidad de casillas, sin salirse nunca del
    tablero (regla 5: no hay rebote, si te pasas del FIN, quedas en FIN).

    TECNICA: funcion pura (no modifica el jugador recibido, devuelve
    uno nuevo con _replace) + composicion de funciones: se arma
    encadenando un paso "avanzar" y un paso "limitar al tablero".
    """
    avanzar = lambda j: j._replace(posicion=j.posicion + pasos)
    limitar_al_tablero = lambda j: j._replace(
        posicion=min(max(j.posicion, tablero.INICIO), tablero.FIN)
    )

    aplicar_movimiento = componer(limitar_al_tablero, avanzar)
    return aplicar_movimiento(jugador)


def reemplazar_jugador(estado, indice, jugador_nuevo):
    """
    Devuelve un EstadoJuego nuevo, con el jugador en esa posicion de la
    lista reemplazado por jugador_nuevo. El resto de los jugadores
    quedan igual.

    TECNICA: funcion pura + comprension de listas para reconstruir la
    tupla de jugadores.
    """
    jugadores_actualizados = tuple(
        jugador_nuevo if indice_actual == indice else jugador
        for indice_actual, jugador in enumerate(estado.jugadores)
    )
    return estado._replace(jugadores=jugadores_actualizados)


def jugadores_en_casilla(estado, posicion, indice_excluido=None):
    """
    Devuelve la lista de (indice, jugador) de todos los jugadores que
    estan parados en esa casilla, excluyendo opcionalmente a uno (por
    ejemplo, al jugador que se acaba de mover, para no compararlo
    consigo mismo).

    TECNICA: comprension de listas.
    """
    return [
        (indice, jugador)
        for indice, jugador in enumerate(estado.jugadores)
        if jugador.posicion == posicion and indice != indice_excluido
    ]


def verificar_ganador(estado):
    """
    Devuelve el nombre del primer jugador que llego a la casilla FIN,
    o None si todavia nadie gano.

    TECNICA: uso de filter.
    """
    jugadores_en_la_meta = list(
        filter(lambda jugador: jugador.posicion == tablero.FIN, estado.jugadores)
    )
    return jugadores_en_la_meta[0].nombre if jugadores_en_la_meta else None


def obtener_posiciones(estado):
    """
    Devuelve solo las posiciones de todos los jugadores, en el mismo
    orden que estado.jugadores.

    TECNICA: uso de map.
    """
    return list(map(lambda jugador: jugador.posicion, estado.jugadores))


def jugador_mas_avanzado(estado):
    """
    Devuelve el jugador que esta mas cerca del FIN.

    TECNICA: uso de reduce.
    """
    return reduce(
        lambda mejor, jugador: jugador if jugador.posicion > mejor.posicion else mejor,
        estado.jugadores,
    )


# --- Efectos de las casillas especiales ---
# Todas estas funciones son puras: reciben un jugador (o un estado) y
# devuelven una version nueva, ya con el premio o castigo aplicado.
# Quien decide CUANDO llamarlas (por ejemplo, tirar el dado de nuevo
# para P2, o elegir a que color le toca el castigo de P1) es la parte
# impura del juego, en juego.py.


def aplicar_p3(jugador):
    """P3: avanza 2 casillas."""
    return mover_jugador(jugador, 2)


def aplicar_c2(jugador):
    """C2: retrocede 3 casillas."""
    return mover_jugador(jugador, -3)


def aplicar_c1(jugador):
    """C1: el propio jugador pierde 1 turno."""
    return jugador._replace(turnos_perdidos=jugador.turnos_perdidos + 1)


def aplicar_p1(estado, indice_objetivo):
    """P1: el jugador elegido (por indice) pierde 1 turno."""
    jugador_objetivo = estado.jugadores[indice_objetivo]
    jugador_actualizado = jugador_objetivo._replace(
        turnos_perdidos=jugador_objetivo.turnos_perdidos + 1
    )
    return reemplazar_jugador(estado, indice_objetivo, jugador_actualizado)


def generador_turnos(cantidad_jugadores):
    """
    Generador infinito que va dando, en orden, el indice del jugador
    al que le toca jugar: 0, 1, 2, ..., cantidad_jugadores - 1, 0, 1, 2...

    TECNICA: generador de funciones con yield.
    """
    indice = 0
    while True:
        yield indice
        indice = (indice + 1) % cantidad_jugadores
