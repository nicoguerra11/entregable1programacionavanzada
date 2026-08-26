# Juego de tablero (Entregable 1 - Programacion Funcional)

Juego de tablero para 2 a 4 jugadores, implementado en Python usando
herramientas de programacion funcional (funciones puras, composicion,
comprensiones, generadores, map/filter/reduce, recursion y un
decorador de logging). Se juega y se muestra en la terminal con la
libreria `rich`.

## Instalacion

Necesitas Python 3.9 o superior. Para instalar la unica dependencia
(`rich`):

```
pip install -r requirements.txt
```

## Como ejecutar

```
python main.py
```

(en Windows tambien se puede usar `py main.py`)

Al arrancar, el juego pregunta:

1. **Modo de juego**: `S` para simulacion (se juega todo solo, con una
   pausa entre turno y turno) o `I` para interactivo (cada jugador
   presiona ENTER para tirar el dado en su turno, y se le pide el
   nombre a cada uno al principio).
2. **Cantidad de jugadores**: entre 2 y 4.

El juego termina apenas un jugador llega a la casilla FIN.

## Estructura del codigo

- `tablero.py` - forma del tablero: dimensiones, casillas especiales,
  y como se traduce una casilla a una coordenada (fila, columna) para
  dibujar el zigzag. Todo puro.
- `estado.py` - el nucleo funcional: como se representa el estado del
  juego (jugadores, posiciones) y las funciones puras que calculan un
  nuevo estado a partir de uno existente.
- `juego.py` - la logica de turnos y reglas (tirar el dado, resolver
  competencias, aplicar premios/castigos). Ademas del nucleo puro de
  estado.py, aca estan las partes impuras del motor del juego: el dado
  (random) y el logging.
- `visual.py` - dibuja el tablero y el estado en la terminal con
  `rich`. Impuro (solo imprime en pantalla).
- `main.py` - punto de entrada: pide el modo de juego, arma los
  jugadores y corre el bucle principal hasta que hay un ganador.
