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
    return [
        Jugador(nombre=nombre, color=color)
        for nombre, color in zip(nombres, COLORES_DISPONIBLES)
    ]


def crear_estado_inicial(nombres):
    return EstadoJuego(jugadores=tuple(crear_jugadores(nombres)))


def componer(*funciones):
    def funcion_combinada(valor_inicial):
        return reduce(
            lambda valor, funcion: funcion(valor),
            reversed(funciones),
            valor_inicial,
        )

    return funcion_combinada


def mover_jugador(jugador, pasos):
    avanzar = lambda j: j._replace(posicion=j.posicion + pasos)
    limitar_al_tablero = lambda j: j._replace(
        posicion=min(max(j.posicion, tablero.INICIO), tablero.FIN)
    )

    aplicar_movimiento = componer(limitar_al_tablero, avanzar)
    return aplicar_movimiento(jugador)


def reemplazar_jugador(estado, indice, jugador_nuevo):
    jugadores_actualizados = tuple(
        jugador_nuevo if indice_actual == indice else jugador
        for indice_actual, jugador in enumerate(estado.jugadores)
    )
    return estado._replace(jugadores=jugadores_actualizados)


def jugadores_en_casilla(estado, posicion, indice_excluido=None):
    return [
        (indice, jugador)
        for indice, jugador in enumerate(estado.jugadores)
        if jugador.posicion == posicion and indice != indice_excluido
    ]


def verificar_ganador(estado):
    jugadores_en_la_meta = list(
        filter(lambda jugador: jugador.posicion == tablero.FIN, estado.jugadores)
    )
    return jugadores_en_la_meta[0].nombre if jugadores_en_la_meta else None


def obtener_posiciones(estado):
    return list(map(lambda jugador: jugador.posicion, estado.jugadores))


def jugador_mas_avanzado(estado):
    return reduce(
        lambda mejor, jugador: jugador if jugador.posicion > mejor.posicion else mejor,
        estado.jugadores,
    )



def aplicar_p3(jugador):
    return mover_jugador(jugador, 2)


def aplicar_c2(jugador):
    return mover_jugador(jugador, -3)


def aplicar_c1(jugador):
    return jugador._replace(turnos_perdidos=jugador.turnos_perdidos + 1)


def aplicar_p1(estado, indice_objetivo):
    jugador_objetivo = estado.jugadores[indice_objetivo]
    jugador_actualizado = jugador_objetivo._replace(
        turnos_perdidos=jugador_objetivo.turnos_perdidos + 1
    )
    return reemplazar_jugador(estado, indice_objetivo, jugador_actualizado)


def generador_turnos(cantidad_jugadores):
    indice = 0
    while True:
        yield indice
        indice = (indice + 1) % cantidad_jugadores
