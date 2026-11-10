#!/usr/bin/env python3
"""MAPPER (Hadoop Streaming).

Lee el CSV por la entrada estándar y emite pares  clave<TAB>valor.

>>> CAMBIA AQUÍ según tu pregunta asignada <<<
  COL_CLAVE : índice (desde 0) de la columna por la que se agrupa
  COL_VALOR : índice (desde 0) de la columna numérica que se agrega
  (secuencial.py debe usar los MISMOS índices)

Manejo de errores:
  - El encabezado se descarta: su valor no es numérico, así que float() falla.
  - Filas cortas, vacías o con valor no numérico se ignoran (y se cuentan).
"""
import csv
import sys

COL_CLAVE = 0
COL_VALOR = 1


def main():
    descartadas = 0
    for fila in csv.reader(sys.stdin):
        try:
            clave = fila[COL_CLAVE].strip()
            valor = float(fila[COL_VALOR])
            if not clave:
                raise ValueError("clave vacía")
        except (IndexError, ValueError):
            descartadas += 1  # encabezado, fila rota o valor no numérico
            continue
        print(f"{clave}\t{valor}")

    # Contador visible en la salida de Hadoop (cuenta encabezado + filas malas)
    print(f"reporter:counter:Calidad,FilasDescartadas,{descartadas}", file=sys.stderr)


if __name__ == "__main__":
    main()
