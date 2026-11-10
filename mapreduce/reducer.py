#!/usr/bin/env python3
"""REDUCER (Hadoop Streaming).

Recibe líneas  clave<TAB>valor  YA ORDENADAS por clave (Hadoop hace el sort
entre map y reduce) y suma los valores de cada clave.

Para pasar de SUMA a PROMEDIO (defensa oral):
  1) lleva también un contador:   total, n = 0.0, 0
  2) en cada línea:               total += valor; n += 1
  3) al imprimir:                 print(f"{actual}\t{total / n:.2f}")
"""
import sys


def main():
    actual = None
    total = 0.0

    for linea in sys.stdin:
        try:
            clave, valor = linea.rstrip("\n").split("\t")
            valor = float(valor)
        except ValueError:
            continue  # línea mal formada: se ignora

        if clave != actual:
            if actual is not None:
                print(f"{actual}\t{total:.2f}")
            actual, total = clave, 0.0
        total += valor

    if actual is not None:
        print(f"{actual}\t{total:.2f}")


if __name__ == "__main__":
    main()
