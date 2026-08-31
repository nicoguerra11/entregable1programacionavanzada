import random
from functools import wraps

import tablero
from estado import (
    aplicar_c1,
    aplicar_c2,
    aplicar_p1,
    aplicar_p3,
    jugadores_en_casilla,
    mover_jugador,
    reemplazar_jugador,
)


def tirar_dado():
    return random.randint(1, 6)


def registrar_jugada(funcion):
    @wraps(funcion)
    def envoltura(estado, indice_jugador, *args, **kwargs):
        nombre_previo = estado.jugadores[indice_jugador].nombre
        nuevo_estado, valor_dado = funcion(estado, indice_jugador, *args, **kwargs)
        casilla_resultante = nuevo_estado.jugadores[indice_jugador].posicion
        print(f"[LOG] {nombre_previo} tiro un {valor_dado} y quedo en la casilla {casilla_resultante}")
        return nuevo_estado, valor_dado

    return envoltura


@registrar_jugada
def tirar_y_mover(estado, indice_jugador, tirar_dado_fn):
    jugador = estado.jugadores[indice_jugador]
    valor_dado = tirar_dado_fn()
    jugador_movido = mover_jugador(jugador, valor_dado)
    nuevo_estado = reemplazar_jugador(estado, indice_jugador, jugador_movido)
    return nuevo_estado, valor_dado

MAXIMO_INTENTOS_COMPETENCIA = 10


def resolver_competencia(par_jugador_a, par_jugador_b, tirar_dado_fn, intentos=0):
    _, jugador_a = par_jugador_a
    _, jugador_b = par_jugador_b

    print(f"[LOG] Compite {jugador_a.nombre}: le toca tirar")
    valor_a = tirar_dado_fn()
    print(f"[LOG] Compite {jugador_b.nombre}: le toca tirar")
    valor_b = tirar_dado_fn()
    print(f"[LOG] Competencia: {jugador_a.nombre} saca {valor_a}, {jugador_b.nombre} saca {valor_b}")

    if valor_a == valor_b:
        if intentos >= MAXIMO_INTENTOS_COMPETENCIA:
            print("[LOG] Demasiados empates seguidos, se desempata al azar")
            return random.choice([(par_jugador_a, par_jugador_b), (par_jugador_b, par_jugador_a)])
        print("[LOG] Empate, vuelven a tirar")
        return resolver_competencia(par_jugador_a, par_jugador_b, tirar_dado_fn, intentos + 1)

    if valor_a > valor_b:
        return par_jugador_a, par_jugador_b
    return par_jugador_b, par_jugador_a


def retroceder_hasta_casilla_libre(jugador, indice_jugador, estado):
    if jugador.posicion == tablero.INICIO:
        return jugador

    if not jugadores_en_casilla(estado, jugador.posicion, indice_excluido=indice_jugador):
        return jugador

    return retroceder_hasta_casilla_libre(mover_jugador(jugador, -1), indice_jugador, estado)


def resolver_colision_si_corresponde(estado, indice_jugador, tirar_dado_fn, al_detectar_colision=None):
    jugador = estado.jugadores[indice_jugador]
    if jugador.posicion == tablero.INICIO:
        return estado

    ocupantes = jugadores_en_casilla(estado, jugador.posicion, indice_excluido=indice_jugador)
    if not ocupantes:
        return estado

    if al_detectar_colision is not None:
        al_detectar_colision(estado)

    indice_rival, jugador_rival = ocupantes[0]
    par_propio = (indice_jugador, jugador)
    par_rival = (indice_rival, jugador_rival)

    (indice_ganador, jugador_ganador), (indice_perdedor, jugador_perdedor) = resolver_competencia(
        par_propio, par_rival, tirar_dado_fn
    )

    jugador_perdedor = mover_jugador(jugador_perdedor, -2)
    jugador_perdedor = retroceder_hasta_casilla_libre(jugador_perdedor, indice_perdedor, estado)

    destino = (
        "INICIO"
        if jugador_perdedor.posicion == tablero.INICIO
        else f"la casilla {jugador_perdedor.posicion}"
    )
    print(
        f"[LOG] En la casilla {jugador.posicion} gana {jugador_ganador.nombre}, "
        f"retrocede {jugador_perdedor.nombre} hasta {destino}"
    )

    return reemplazar_jugador(estado, indice_perdedor, jugador_perdedor)


def aplicar_efecto_casilla(estado, indice_jugador, elegir_color_objetivo_fn):
    jugador = estado.jugadores[indice_jugador]
    codigo_casilla = tablero.CASILLAS_ESPECIALES.get(jugador.posicion)

    if codigo_casilla is None:
        return estado, False

    print(f"[LOG] {jugador.nombre} cae en {codigo_casilla}: {tablero.DESCRIPCION_CASILLAS[codigo_casilla]}")

    if codigo_casilla == "P1":
        color_elegido = elegir_color_objetivo_fn(estado, indice_jugador)
        indice_objetivo = next(i for i, j in enumerate(estado.jugadores) if j.color == color_elegido)
        return aplicar_p1(estado, indice_objetivo), False

    if codigo_casilla == "P2":
        return estado, True

    if codigo_casilla == "P3":
        jugador_movido = aplicar_p3(jugador)
        print(f"[LOG] {jugador.nombre} avanza hasta la casilla {jugador_movido.posicion}")
        return reemplazar_jugador(estado, indice_jugador, jugador_movido), False

    if codigo_casilla == "C1":
        return reemplazar_jugador(estado, indice_jugador, aplicar_c1(jugador)), False

    if codigo_casilla == "C2":
        jugador_movido = aplicar_c2(jugador)
        print(f"[LOG] {jugador.nombre} retrocede hasta la casilla {jugador_movido.posicion}")
        return reemplazar_jugador(estado, indice_jugador, jugador_movido), False

    return estado, False


def jugar_turno(estado, indice_jugador, tirar_dado_fn, elegir_color_objetivo_fn, al_detectar_colision=None):
    jugador = estado.jugadores[indice_jugador]

    if jugador.turnos_perdidos > 0:
        jugador_actualizado = jugador._replace(turnos_perdidos=jugador.turnos_perdidos - 1)
        print(f"[LOG] {jugador.nombre} pierde el turno (le quedan {jugador_actualizado.turnos_perdidos})")
        return reemplazar_jugador(estado, indice_jugador, jugador_actualizado)

    posicion_antes = jugador.posicion
    estado, _ = tirar_y_mover(estado, indice_jugador, tirar_dado_fn)
    posicion_tras_mover = estado.jugadores[indice_jugador].posicion

    estado = resolver_colision_si_corresponde(estado, indice_jugador, tirar_dado_fn, al_detectar_colision)

    if estado.jugadores[indice_jugador].posicion != posicion_tras_mover:
        return estado

    if posicion_tras_mover == posicion_antes:
        return estado

    estado, jugar_de_nuevo = aplicar_efecto_casilla(estado, indice_jugador, elegir_color_objetivo_fn)

    if jugar_de_nuevo:
        return jugar_turno(estado, indice_jugador, tirar_dado_fn, elegir_color_objetivo_fn, al_detectar_colision)

    jugador_actual = estado.jugadores[indice_jugador]
    if jugador_actual.posicion != posicion_tras_mover:
        jugador_reacomodado = retroceder_hasta_casilla_libre(jugador_actual, indice_jugador, estado)
        if jugador_reacomodado.posicion != jugador_actual.posicion:
            print(
                f"[LOG] La casilla {jugador_actual.posicion} estaba ocupada, "
                f"{jugador_actual.nombre} retrocede hasta la casilla {jugador_reacomodado.posicion}"
            )
        estado = reemplazar_jugador(estado, indice_jugador, jugador_reacomodado)

    return estado
