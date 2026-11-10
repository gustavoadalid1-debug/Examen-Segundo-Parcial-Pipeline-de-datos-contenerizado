#!/usr/bin/env python3
"""Versión SECUENCIAL (sin Hadoop) de la misma agregación, para la comparativa.

Uso:  python3 secuencial.py <archivo.csv>
Imprime  clave<TAB>suma  ordenado por clave (stdout) y el tiempo (stderr).

Los índices COL_CLAVE y COL_VALOR deben ser IGUALES a los de mapper.py.
"""
import csv
import sys
import time
from collections import defaultdict

COL_CLAVE = 0
COL_VALOR = 1


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 secuencial.py <archivo.csv>")

    inicio = time.time()
    acumulado = defaultdict(float)

    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        for fila in csv.reader(f):
            try:
                clave = fila[COL_CLAVE].strip()
                valor = float(fila[COL_VALOR])
                if not clave:
                    raise ValueError("clave vacía")
            except (IndexError, ValueError):
                continue  # encabezado o fila mala
            acumulado[clave] += valor

    for clave in sorted(acumulado):
        print(f"{clave}\t{acumulado[clave]:.2f}")

    print(f"Tiempo secuencial: {time.time() - inicio:.3f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
