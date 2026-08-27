import sys

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

import tablero
from estado import NOMBRES_COLORES, jugador_mas_avanzado
consola = Console(file=sys.stdout)

ANCHO_CASILLA = 8

def construir_celda(estado, posicion):
    etiqueta = tablero.nombre_casilla(posicion)

    if etiqueta in ("INICIO", "FIN"):
        primera_linea = f"[bold white]{etiqueta}[/bold white]"
    elif etiqueta:
        primera_linea = f"[bold yellow]{etiqueta}[/bold yellow]"
    else:
        primera_linea = f"[dim]{posicion}[/dim]"

    jugadores_aqui = [jugador for jugador in estado.jugadores if jugador.posicion == posicion]

    if not jugadores_aqui:
        return primera_linea

    iniciales = " ".join(
        f"[bold {jugador.color}]{jugador.nombre[0].upper()}[/bold {jugador.color}]"
        for jugador in jugadores_aqui
    )
    return f"{primera_linea}\n{iniciales}"

def construir_tabla_tablero(estado):
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
    tabla = Table(title="Jugadores", show_header=True, header_style="bold")
    tabla.add_column("Nombre")
    tabla.add_column("Color")
    tabla.add_column("Casilla", justify="center")
    tabla.add_column("Estado")

    lider = jugador_mas_avanzado(estado)    #para marcar en la tabla quien va primero en la partida

    for jugador in estado.jugadores:
        nombre_del_color = NOMBRES_COLORES[jugador.color]
        estado_turno = (
            f"pierde turno ({jugador.turnos_perdidos})" if jugador.turnos_perdidos > 0 else "juega"
        )
        
        if jugador == lider and lider.posicion > tablero.INICIO: #si nadie se movio todavia no marcamos un lider
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
    elementos = [construir_tabla_tablero(estado), construir_tabla_jugadores(estado)]

    if texto_log.strip():
        elementos.append(Panel(texto_log.strip(), title="Ultima jugada", border_style="grey50"))

    consola.print(Group(*elementos))
