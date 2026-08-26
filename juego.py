"""
Modulo juego.py
----------------
Aca vive la logica de turnos y reglas del juego. A diferencia de
estado.py, este archivo SI tiene partes impuras: tirar el dado usa
random, y el logging escribe en la consola. Estas partes impuras estan
separadas y comentadas para que quede claro cuales son.

La idea general de un turno es:
1. Si el jugador tiene turnos perdidos pendientes, se lo saltea.
2. Si no, tira el dado y se mueve.
3. Si cae en una casilla ocupada por otro jugador, se resuelve una
   competencia (regla 4).
4. Si gano la competencia (o no hubo competencia), se aplica el efecto
   de la casilla especial en la que quedo (regla 3).
5. Si esa casilla era P2, se repite el turno (tira de nuevo).
"""

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
    """
    Tira un dado de 6 caras.

    TECNICA: NO es una funcion pura. Llamada dos veces con los mismos
    argumentos (ninguno) puede devolver resultados distintos, porque
    depende de random. Es, junto con el input del usuario y los prints,
    una de las partes del juego donde la pureza no es posible ni tiene
    sentido: la gracia de un dado es justamente que sea impredecible.
    """
    return random.randint(1, 6)


def registrar_jugada(funcion):
    """
    Decorador que envuelve una funcion de tirada de dado y, despues de
    ejecutarla, imprime en consola quien jugo, que saco en el dado y en
    que casilla quedo.

    TECNICA: decorador para hacer logging (requisito obligatorio 7).
    """

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
    """
    Tira el dado para el jugador indicado y lo mueve. Esta es la unica
    funcion que combina "tirar el dado" (impuro) con "mover" (puro,
    definida en estado.py): por eso esta funcion en si no es pura,
    aunque delega el calculo de la nueva posicion a mover_jugador.
    """
    jugador = estado.jugadores[indice_jugador]
    valor_dado = tirar_dado_fn()
    jugador_movido = mover_jugador(jugador, valor_dado)
    nuevo_estado = reemplazar_jugador(estado, indice_jugador, jugador_movido)
    return nuevo_estado, valor_dado


MAXIMO_INTENTOS_COMPETENCIA = 10


def resolver_competencia(par_jugador_a, par_jugador_b, tirar_dado_fn, intentos=0):
    """
    Regla 4: dos jugadores en la misma casilla tiran el dado. Gana el
    que saca mas. Si empatan, vuelven a tirar.

    par_jugador_a y par_jugador_b son tuplas (indice, jugador).
    Devuelve (par_ganador, par_perdedor).

    TECNICA: recursion. El caso de empate se resuelve llamando de
    nuevo a esta misma funcion, hasta que salga un valor distinto.
    No es una funcion pura porque depende de tirar_dado_fn (random),
    pero la logica de "quien gana" en si es simple y clara.

    Con un dado real, la probabilidad de empate en cada intento es
    1/6, asi que la probabilidad de seguir empatando baja muy rapido
    y la recursion termina con probabilidad 1 (matematicamente, en
    algun momento sale un valor distinto). El parametro intentos y el
    limite MAXIMO_INTENTOS_COMPETENCIA son una red de seguridad para
    un caso que no deberia pasar nunca con un dado real: si se empata
    MAXIMO_INTENTOS_COMPETENCIA veces seguidas, en vez de seguir
    recursionando para siempre, se desempata al azar con
    random.choice, para que el juego nunca se quede trabado.
    """
    _, jugador_a = par_jugador_a
    _, jugador_b = par_jugador_b

    valor_a = tirar_dado_fn()
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


def resolver_colision_si_corresponde(estado, indice_jugador, tirar_dado_fn, al_detectar_colision=None):
    """
    Si el jugador que se acaba de mover cayo en la misma casilla que
    otro jugador, resuelve la competencia y hace retroceder al que
    pierde (2 casillas, y una mas si esa nueva casilla tambien esta
    ocupada). La casilla INICIO es neutral: ahi no hay competencia,
    porque todos los jugadores arrancan parados en ella.

    al_detectar_colision es un callback opcional (por ejemplo, para
    dibujar el tablero) que se llama justo cuando se detectan los dos
    jugadores compartiendo casilla, antes de resolver quien gana. Si no
    se pasa nada, se ignora: esta funcion no sabe ni le importa como se
    muestra el juego en pantalla.
    """
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
    # Si el que pierde vuelve a caer en una casilla ocupada, retrocede una mas.
    if jugadores_en_casilla(estado, jugador_perdedor.posicion, indice_excluido=indice_perdedor):
        jugador_perdedor = mover_jugador(jugador_perdedor, -1)

    print(
        f"[LOG] En la casilla {jugador.posicion} gana {jugador_ganador.nombre}, "
        f"retrocede {jugador_perdedor.nombre} hasta la casilla {jugador_perdedor.posicion}"
    )

    return reemplazar_jugador(estado, indice_perdedor, jugador_perdedor)


def aplicar_efecto_casilla(estado, indice_jugador, elegir_color_objetivo_fn):
    """
    Aplica el premio o castigo de la casilla en la que quedo el
    jugador, si corresponde. Devuelve (nuevo_estado, jugar_de_nuevo),
    donde jugar_de_nuevo es True solo para la casilla P2.
    """
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
        return reemplazar_jugador(estado, indice_jugador, aplicar_p3(jugador)), False

    if codigo_casilla == "C1":
        return reemplazar_jugador(estado, indice_jugador, aplicar_c1(jugador)), False

    if codigo_casilla == "C2":
        return reemplazar_jugador(estado, indice_jugador, aplicar_c2(jugador)), False

    return estado, False


def jugar_turno(estado, indice_jugador, tirar_dado_fn, elegir_color_objetivo_fn, al_detectar_colision=None):
    """
    Juega el turno completo de un jugador.

    TECNICA: recursion. Si el jugador cae en la casilla P2 ("tira el
    dado nuevamente y avanza"), esta funcion se vuelve a llamar a si
    misma para jugar el turno extra. Como cada tirada de dado avanza
    al menos 1 casilla y el tablero es finito, la recursion siempre
    termina como maximo al llegar a la casilla FIN.

    al_detectar_colision es opcional, se lo pasa tal cual a
    resolver_colision_si_corresponde (ver ahi la explicacion).
    """
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
        # El jugador perdio la competencia y fue retrocedido: no llego
        # a "caer" de verdad en la casilla especial, asi que no se le
        # aplica ningun premio/castigo este turno.
        return estado

    if posicion_tras_mover == posicion_antes:
        # Ya estaba en el FIN u otro caso limite, no hay nada mas que hacer.
        return estado

    estado, jugar_de_nuevo = aplicar_efecto_casilla(estado, indice_jugador, elegir_color_objetivo_fn)

    if jugar_de_nuevo:
        return jugar_turno(estado, indice_jugador, tirar_dado_fn, elegir_color_objetivo_fn, al_detectar_colision)

    return estado
