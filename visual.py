"""
Modulo visual.py
------------------
Dibuja el tablero y el estado del juego en la terminal usando la
libreria rich. Todo lo de este archivo es impuro: solo imprime en
pantalla lo que ya calcularon estado.py y juego.py, no decide nada del
juego en si.
"""

import sys

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

import tablero
from estado import NOMBRES_COLORES, jugador_mas_avanzado

# Atamos la consola explicitamente a la salida real de la terminal
# (sys.stdout tal cual es en este momento). Esto es importante porque
# main.py usa contextlib.redirect_stdout para capturar los mensajes
# [LOG] que imprime juego.py, y no queremos que ese capturado se lleve
# puesto tambien lo que dibuja rich: rich tiene que seguir escribiendo
# siempre en la terminal real, aunque sys.stdout este redirigido.
consola = Console(file=sys.stdout)

ANCHO_CASILLA = 8


def construir_celda(estado, posicion):
    """
    Arma el texto (con markup de rich) que va dentro de una casilla:
    primera linea con el codigo de la casilla (INICIO, FIN, P1, P2,
    P3, C1, C2, o el numero si es una casilla comun) y, si hay
    jugadores ahi parados, una segunda linea con sus iniciales, una
    por cada jugador y en su color. Si hay mas de un jugador (por
    ejemplo, el instante antes de resolver una competencia), se ven
    las iniciales de todos, una al lado de la otra.
    """
    etiqueta = tablero.nombre_casilla(posicion)

    if etiqueta in ("INICIO", "FIN"):
        primera_linea = f"[bold white]{etiqueta}[/bold white]"
    elif etiqueta:
        primera_linea = f"[bold yellow]{etiqueta}[/bold yellow]"
    else:
        primera_linea = f"[dim]{posicion}[/dim]"

    # TECNICA: comprension de listas.
    jugadores_aqui = [jugador for jugador in estado.jugadores if jugador.posicion == posicion]

    if not jugadores_aqui:
        return primera_linea

    iniciales = " ".join(
        f"[bold {jugador.color}]{jugador.nombre[0].upper()}[/bold {jugador.color}]"
        for jugador in jugadores_aqui
    )
    return f"{primera_linea}\n{iniciales}"


def construir_tabla_tablero(estado):
    """
    Arma la grilla completa del tablero como una Table de rich. Se
    recorre de la fila mas alta a la mas baja para que la casilla
    INICIO (fila 0) quede dibujada abajo del todo, como en un tablero
    real.
    """
    tabla = Table(show_header=False, show_lines=True, padding=0)

    for _ in range(tablero.COLUMNAS):
        tabla.add_column(justify="center", width=ANCHO_CASILLA)

    for fila in reversed(range(tablero.FILAS)):
        celdas_de_la_fila = [
            construir_celda(estado, tablero.MAPA_COORDENADAS_INVERSO[(fila, columna)])
            for columna in range(tablero.COLUMNAS)
        ]
        tabla.add_row(*celdas_de_la_fila)

    return tabla


def construir_tabla_jugadores(estado):
    """Tabla chica con el nombre, color, posicion y estado de cada jugador."""
    tabla = Table(title="Jugadores", show_header=True, header_style="bold")
    tabla.add_column("Nombre")
    tabla.add_column("Color")
    tabla.add_column("Casilla", justify="center")
    tabla.add_column("Estado")

    # Se usa para marcar en la tabla quien va primero en la partida.
    lider = jugador_mas_avanzado(estado)

    for jugador in estado.jugadores:
        nombre_del_color = NOMBRES_COLORES[jugador.color]
        estado_turno = (
            f"pierde turno ({jugador.turnos_perdidos})" if jugador.turnos_perdidos > 0 else "juega"
        )
        # Si nadie se movio todavia (todos en INICIO) no marcamos lider.
        if jugador == lider and lider.posicion > tablero.INICIO:
            estado_turno += " (lider)"
        tabla.add_row(
            jugador.nombre,
            f"[bold {jugador.color}]{nombre_del_color}[/bold {jugador.color}]",
            str(jugador.posicion),
            estado_turno,
        )

    return tabla


def mostrar_referencia_casillas():
    """Muestra una sola vez, al principio del juego, que hace cada casilla especial."""
    tabla = Table(title="Casillas especiales", show_header=True, header_style="bold")
    tabla.add_column("Codigo")
    tabla.add_column("Efecto")

    for codigo, descripcion in tablero.DESCRIPCION_CASILLAS.items():
        tabla.add_row(codigo, descripcion)

    consola.print(tabla)


def mostrar_estado(estado, texto_log=""):
    """
    Dibuja el tablero, la tabla de jugadores y, si hay, el log de la
    ultima jugada debajo de todo.
    """
    elementos = [construir_tabla_tablero(estado), construir_tabla_jugadores(estado)]

    if texto_log.strip():
        elementos.append(Panel(texto_log.strip(), title="Ultima jugada", border_style="grey50"))

    consola.print(Group(*elementos))
