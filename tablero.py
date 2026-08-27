FILAS = 7
COLUMNAS = 7
TOTAL_CASILLAS = FILAS * COLUMNAS
INICIO = 0
FIN = TOTAL_CASILLAS - 1  #casilla 48

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
    fila = posicion // COLUMNAS
    posicion_en_fila = posicion % COLUMNAS

    if fila % 2 == 0:
        columna = posicion_en_fila
    else:
        columna = COLUMNAS - 1 - posicion_en_fila

    return fila, columna

MAPA_COORDENADAS = {
    posicion: calcular_coordenadas(posicion) for posicion in range(TOTAL_CASILLAS)
}

MAPA_COORDENADAS_INVERSO = {
    coordenada: posicion for posicion, coordenada in MAPA_COORDENADAS.items()
}

def nombre_casilla(posicion):
    if posicion == INICIO:
        return "INICIO"
    if posicion == FIN:
        return "FIN"
    return CASILLAS_ESPECIALES.get(posicion, "")
