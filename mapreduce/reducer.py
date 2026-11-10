#!/usr/bin/env python3
"""REDUCER (Hadoop Streaming) — Ticket promedio por tienda.

Recibe líneas  tienda<TAB>ingreso  YA ORDENADAS por tienda (Hadoop hace el sort
entre map y reduce). Para cada tienda lleva la suma y el conteo, y al cambiar de
tienda imprime  tienda<TAB>promedio.

Para pasar de PROMEDIO a SUMA (defensa oral): imprime `total` en vez de `total / n`.
"""
import sys


def main():
    actual = None
    total = 0.0
    n = 0

    for linea in sys.stdin:
        try:
            tienda, ingreso = linea.rstrip("\n").split("\t")
            ingreso = float(ingreso)
        except ValueError:
            continue  # línea mal formada: se ignora

        if tienda != actual:
            if actual is not None:
                print(f"{actual}\t{total / n:.2f}")
            actual, total, n = tienda, 0.0, 0
        total += ingreso
        n += 1

    if actual is not None:
        print(f"{actual}\t{total / n:.2f}")


if __name__ == "__main__":
    main()
