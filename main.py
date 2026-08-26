"""
Modulo main.py
---------------
Punto de entrada del juego. Pide el modo de juego (simulacion o
interactivo), arma los jugadores, y corre el bucle principal de turnos
hasta que alguien gane.

Este archivo es la capa impura que conecta todo: el nucleo puro de
estado.py, la logica de turnos de juego.py, y el dibujado en pantalla
de visual.py. Usa random (para elegir colores al azar en el castigo de
P1 en modo simulacion), input (para leer lo que escribe el usuario) y
print/rich (para mostrar todo en pantalla).
"""

import io
import random
import sys
import time
from contextlib import redirect_stdout

import estado as estado_modulo
import juego
import visual

PAUSA_SIMULACION_SEGUNDOS = 1.5
PAUSA_COLISION_SEGUNDOS = 1.2


# --- Entrada de datos (todo esto es impuro: usa input) ---


def pedir_modo_juego():
    while True:
        texto = input("Elegi el modo de juego - (S)imulacion o (I)nteractivo: ").strip().lower()
        if texto in ("s", "simulacion"):
            return "simulacion"
        if texto in ("i", "interactivo"):
            return "interactivo"
        print("Respuesta invalida, escribi S o I.")


def pedir_cantidad_jugadores():
    while True:
        texto = input("Cuantos jugadores van a jugar (2 a 4)? ").strip()
        if texto.isdigit() and 2 <= int(texto) <= 4:
            return int(texto)
        print("Ingresa un numero entre 2 y 4.")


def pedir_nombres_jugadores(cantidad):
    nombres = []
    for numero in range(1, cantidad + 1):
        nombre = input(f"Nombre del jugador {numero}: ").strip()
        nombres.append(nombre if nombre else f"Jugador {numero}")
    return nombres


def nombres_automaticos(cantidad):
    # TECNICA: comprension de listas.
    return [f"Jugador {numero}" for numero in range(1, cantidad + 1)]


# --- Como se elige el color castigado en la casilla P1 ---


def elegir_color_objetivo_simulacion(estado, indice_jugador):
    """En modo simulacion, P1 elige al azar el color de otro jugador."""
    colores_disponibles = [
        jugador.color for i, jugador in enumerate(estado.jugadores) if i != indice_jugador
    ]
    return random.choice(colores_disponibles)


def elegir_color_objetivo_interactivo(estado, indice_jugador):
    """
    En modo interactivo, se le pregunta al jugador que color castigar.

    Esta funcion se llama desde adentro del bloque redirect_stdout de
    jugar_turno_con_log (ver mas abajo), asi que un print() comun
    quedaria atrapado en el buffer y no se veria en pantalla hasta que
    termine el turno. Por eso el menu y el prompt se escriben directo a
    sys.__stdout__ (la terminal real), igual que hace visual.py con su
    Console. input() se llama sin texto de prompt porque, si se le
    pasa un prompt, Python intenta escribirlo usando el sys.stdout
    actual (el buffer) en vez de la terminal.
    """
    jugador_actual = estado.jugadores[indice_jugador]
    otros = [(i, jugador) for i, jugador in enumerate(estado.jugadores) if i != indice_jugador]

    print(f"{jugador_actual.nombre} cayo en P1: elegi a que color le haces perder un turno.", file=sys.__stdout__)
    for numero, (_, jugador) in enumerate(otros, start=1):
        print(f"  {numero}) {estado_modulo.NOMBRES_COLORES[jugador.color]} ({jugador.nombre})", file=sys.__stdout__)

    while True:
        print("Opcion: ", end="", file=sys.__stdout__)
        texto = input().strip()
        if texto.isdigit() and 1 <= int(texto) <= len(otros):
            _, jugador_elegido = otros[int(texto) - 1]
            return jugador_elegido.color
        print("Opcion invalida.", file=sys.__stdout__)


# --- Bucle principal de juego ---


def mostrar_colision_momentanea(estado):
    """
    Se le pasa a juego.jugar_turno como callback: cuando dos jugadores
    quedan en la misma casilla, se muestra el tablero con los dos ahi
    antes de resolver quien se la queda.
    """
    visual.consola.clear()
    visual.mostrar_estado(estado, texto_log="Dos jugadores en la misma casilla: van a competir por ella...")
    time.sleep(PAUSA_COLISION_SEGUNDOS)


def jugar_turno_con_log(estado, indice_jugador, elegir_color_objetivo_fn):
    """
    Ejecuta un turno completo, capturando en un texto todo lo que
    juego.py va imprimiendo con print() (los mensajes [LOG]) para
    poder mostrarlo despues junto con el tablero actualizado.
    """
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        nuevo_estado = juego.jugar_turno(
            estado,
            indice_jugador,
            juego.tirar_dado,
            elegir_color_objetivo_fn,
            mostrar_colision_momentanea,
        )
    return nuevo_estado, buffer.getvalue()


def jugar_partida(nombres, elegir_color_objetivo_fn, antes_de_tirar_fn, despues_de_mostrar_fn):
    estado = estado_modulo.crear_estado_inicial(nombres)
    turnos = estado_modulo.generador_turnos(len(estado.jugadores))

    visual.consola.clear()
    visual.mostrar_referencia_casillas()
    visual.mostrar_estado(estado)

    ganador = None
    while ganador is None:
        indice_jugador = next(turnos)
        jugador_del_turno = estado.jugadores[indice_jugador]

        antes_de_tirar_fn(jugador_del_turno)
        estado, texto_log = jugar_turno_con_log(estado, indice_jugador, elegir_color_objetivo_fn)

        visual.consola.clear()
        visual.mostrar_estado(estado, texto_log)

        ganador = estado_modulo.verificar_ganador(estado)
        if ganador is None:
            despues_de_mostrar_fn()

    visual.consola.print(f"\n[bold green]Gano {ganador}![/bold green]\n")


def antes_de_tirar_simulacion(jugador_del_turno):
    pass  # en simulacion no hace falta ningun input, el juego solo avanza


def antes_de_tirar_interactivo(jugador_del_turno):
    input(f"Turno de {jugador_del_turno.nombre} - presiona ENTER para tirar el dado...")


def despues_de_mostrar_simulacion():
    time.sleep(PAUSA_SIMULACION_SEGUNDOS)


def despues_de_mostrar_interactivo():
    pass  # el siguiente antes_de_tirar_fn ya va a pedir el ENTER del proximo jugador


def main():
    print("=== Juego de tablero ===")
    modo = pedir_modo_juego()
    cantidad = pedir_cantidad_jugadores()

    if modo == "simulacion":
        nombres = nombres_automaticos(cantidad)
        jugar_partida(
            nombres, elegir_color_objetivo_simulacion, antes_de_tirar_simulacion, despues_de_mostrar_simulacion
        )
    else:
        nombres = pedir_nombres_jugadores(cantidad)
        jugar_partida(
            nombres, elegir_color_objetivo_interactivo, antes_de_tirar_interactivo, despues_de_mostrar_interactivo
        )


if __name__ == "__main__":
    main()
