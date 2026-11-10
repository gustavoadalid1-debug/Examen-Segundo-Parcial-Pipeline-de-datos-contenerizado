#!/usr/bin/env python3
"""Versión SECUENCIAL (sin Hadoop) del ticket promedio por tienda, para la comparativa.

Uso:  python3 secuencial.py <archivo.csv>
Imprime  tienda<TAB>promedio  ordenado por tienda (stdout) y el tiempo (stderr).

Las columnas deben ser IGUALES a las de mapper.py.
"""
import csv
import sys
import time
from collections import defaultdict

COL_TIENDA = 2
COL_CANTIDAD = 5
COL_PRECIO = 6


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 secuencial.py <archivo.csv>")

    inicio = time.time()
    total = defaultdict(float)
    n = defaultdict(int)

    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        for fila in csv.reader(f):
            try:
                tienda = fila[COL_TIENDA].strip()
                ingreso = float(fila[COL_CANTIDAD]) * float(fila[COL_PRECIO])
                if not tienda:
                    raise ValueError("tienda vacía")
            except (IndexError, ValueError):
                continue  # encabezado o fila mala
            total[tienda] += ingreso
            n[tienda] += 1

    for tienda in sorted(total):
        print(f"{tienda}\t{total[tienda] / n[tienda]:.2f}")

    print(f"Tiempo secuencial: {time.time() - inicio:.3f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
