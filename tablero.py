"""
Modulo tablero.py
------------------
Define la forma del tablero: cuantas casillas tiene, donde estan las
casillas especiales (premios y castigos) y como se traduce una posicion
(un numero de 0 a 48) a una coordenada (fila, columna) para poder dibujar
el tablero en zigzag, como en el Anexo I de la consigna.

Todo lo de este archivo son datos y funciones puras: no hacen falta
random, input ni print aca.
"""

# --- Dimensiones del tablero ---
FILAS = 7
COLUMNAS = 7
TOTAL_CASILLAS = FILAS * COLUMNAS  # 49 casillas en total

INICIO = 0
FIN = TOTAL_CASILLAS - 1  # casilla 48

# --- Casillas especiales ---
# Cada clave es el numero de casilla (0 a 48), y el valor es el codigo
# de la casilla especial que hay ahi. Estan ubicadas mas o menos en las
# mismas proporciones del tablero que en el Anexo I.
CASILLAS_ESPECIALES = {
    7: "P1",
    14: "P2",
    23: "P3",
    31: "C1",
    40: "C2",
}

DESCRIPCION_CASILLAS = {
    "P1": "Elige un color para que pierda un turno",
    "P2": "Tira el dado nuevamente y avanza",
    "P3": "Avanza 2 casillas",
    "C1": "Pierde 1 turno",
    "C2": "Retrocede 3 casillas",
}


def calcular_coordenadas(posicion):
    """
    Traduce un numero de casilla (0 a 48) a una coordenada (fila, columna)
    en la grilla de 7x7, siguiendo un camino en zigzag (como una
    serpiente): la fila 0 va de izquierda a derecha, la fila 1 va de
    derecha a izquierda, la fila 2 de nuevo izquierda a derecha, etc.

    TECNICA: funcion pura. Con el mismo numero de posicion, siempre
    devuelve el mismo resultado, y no modifica nada externo.
    """
    fila = posicion // COLUMNAS
    posicion_en_fila = posicion % COLUMNAS

    if fila % 2 == 0:
        columna = posicion_en_fila
    else:
        columna = COLUMNAS - 1 - posicion_en_fila

    return fila, columna


# TECNICA: comprension de diccionario. Precalculamos la coordenada de
# cada una de las casillas una sola vez, para no recalcularla cada vez
# que dibujamos el tablero.
MAPA_COORDENADAS = {
    posicion: calcular_coordenadas(posicion) for posicion in range(TOTAL_CASILLAS)
}

# El mapa "al reves": dada una coordenada (fila, columna), a que numero
# de casilla corresponde. Lo usa visual.py para dibujar la grilla fila
# por fila. TECNICA: comprension de diccionario.
MAPA_COORDENADAS_INVERSO = {
    coordenada: posicion for posicion, coordenada in MAPA_COORDENADAS.items()
}


def nombre_casilla(posicion):
    """
    Devuelve el texto que corresponde mostrar en una casilla: INICIO,
    FIN, el codigo de una casilla especial (P1, P2, P3, C1, C2), o
    vacio si es una casilla comun.

    TECNICA: funcion pura.
    """
    if posicion == INICIO:
        return "INICIO"
    if posicion == FIN:
        return "FIN"
    return CASILLAS_ESPECIALES.get(posicion, "")
