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
PAUSA_TURNO_PERDIDO_SEGUNDOS = 1.5


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
    return [f"Jugador {numero}" for numero in range(1, cantidad + 1)]


def elegir_color_objetivo_simulacion(estado, indice_jugador):
    colores_disponibles = [
        jugador.color for i, jugador in enumerate(estado.jugadores) if i != indice_jugador
    ]
    return random.choice(colores_disponibles)


_log_ya_mostrado = 0
_hubo_tirada = False


def reiniciar_seguimiento_del_turno():
    global _log_ya_mostrado, _hubo_tirada
    _log_ya_mostrado = 0
    _hubo_tirada = False


def mostrar_log_en_vivo():
    global _log_ya_mostrado
    if not isinstance(sys.stdout, io.StringIO):
        return

    texto = sys.stdout.getvalue()
    pendiente = texto[_log_ya_mostrado:].strip()
    _log_ya_mostrado = len(texto)

    if pendiente:
        print(pendiente, flush=True, file=sys.__stdout__)


def elegir_color_objetivo_interactivo(estado, indice_jugador):
    jugador_actual = estado.jugadores[indice_jugador]
    otros = [(i, jugador) for i, jugador in enumerate(estado.jugadores) if i != indice_jugador]
    mostrar_log_en_vivo()
    print(f"{jugador_actual.nombre}, elegi a que color le haces perder un turno:", file=sys.__stdout__)
    for numero, (_, jugador) in enumerate(otros, start=1):
        print(f"  {numero}) {estado_modulo.NOMBRES_COLORES[jugador.color]} ({jugador.nombre})", file=sys.__stdout__)

    while True:
        print("Opcion: ", end="", flush=True, file=sys.__stdout__)
        texto = input().strip()
        if texto.isdigit() and 1 <= int(texto) <= len(otros):
            _, jugador_elegido = otros[int(texto) - 1]
            return jugador_elegido.color
        print("Opcion invalida.", file=sys.__stdout__)


def tirar_dado_interactivo():
    global _hubo_tirada
    _hubo_tirada = True
    mostrar_log_en_vivo()
    print("Presiona ENTER para tirar el dado... ", end="", flush=True, file=sys.__stdout__)
    input()
    return juego.tirar_dado()


def mostrar_colision_momentanea(estado):
    visual.consola.clear()
    visual.mostrar_estado(estado, texto_log="Dos jugadores en la misma casilla: van a competir por ella...")
    time.sleep(PAUSA_COLISION_SEGUNDOS)


def jugar_turno_con_log(estado, indice_jugador, tirar_dado_fn, elegir_color_objetivo_fn):
    buffer = io.StringIO()
    reiniciar_seguimiento_del_turno()
    with redirect_stdout(buffer):
        nuevo_estado = juego.jugar_turno(
            estado,
            indice_jugador,
            tirar_dado_fn,
            elegir_color_objetivo_fn,
            mostrar_colision_momentanea,
        )
    return nuevo_estado, buffer.getvalue()


def jugar_partida(nombres, tirar_dado_fn, elegir_color_objetivo_fn, antes_de_tirar_fn, despues_de_mostrar_fn):
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
        estado, texto_log = jugar_turno_con_log(estado, indice_jugador, tirar_dado_fn, elegir_color_objetivo_fn)

        visual.consola.clear()
        visual.mostrar_estado(estado, texto_log)

        ganador = estado_modulo.verificar_ganador(estado)
        if ganador is None:
            despues_de_mostrar_fn()

    visual.consola.print(f"\n[bold green]Gano {ganador}![/bold green]\n")


def antes_de_tirar_simulacion(jugador_del_turno):
    pass


def antes_de_tirar_interactivo(jugador_del_turno):
    print(f"Turno de {jugador_del_turno.nombre}")


def despues_de_mostrar_simulacion():
    time.sleep(PAUSA_SIMULACION_SEGUNDOS)


def despues_de_mostrar_interactivo():
    if not _hubo_tirada:
        time.sleep(PAUSA_TURNO_PERDIDO_SEGUNDOS)


def main():
    print("=== Juego de tablero ===")
    modo = pedir_modo_juego()
    cantidad = pedir_cantidad_jugadores()

    if modo == "simulacion":
        nombres = nombres_automaticos(cantidad)
        jugar_partida(
            nombres, juego.tirar_dado, elegir_color_objetivo_simulacion,
            antes_de_tirar_simulacion, despues_de_mostrar_simulacion
        )
    else:
        nombres = pedir_nombres_jugadores(cantidad)
        jugar_partida(
            nombres, tirar_dado_interactivo, elegir_color_objetivo_interactivo,
            antes_de_tirar_interactivo, despues_de_mostrar_interactivo
        )


if __name__ == "__main__":
    main()
