#!/usr/bin/env python3
"""MAPPER (Hadoop Streaming) — Ticket promedio por tienda.

Dataset ventas_125052712.csv (8 columnas):
  0 id | 1 fecha_hora | 2 tienda | 3 categoria | 4 producto |
  5 cantidad | 6 precio_unitario | 7 metodo_pago

Por cada registro emite:   tienda <TAB> cantidad * precio_unitario
(el "ingreso" del registro). El reducer promedia esos ingresos por tienda.

Manejo de errores:
  - El encabezado se descarta: "cantidad" no es numérico y float() falla.
  - Filas cortas, vacías, sin tienda o con números inválidos se ignoran y se cuentan.
"""
import csv
import sys

COL_TIENDA = 2
COL_CANTIDAD = 5
COL_PRECIO = 6


def main():
    descartadas = 0
    for fila in csv.reader(sys.stdin):
        try:
            tienda = fila[COL_TIENDA].strip()
            ingreso = float(fila[COL_CANTIDAD]) * float(fila[COL_PRECIO])
            if not tienda:
                raise ValueError("tienda vacía")
        except (IndexError, ValueError):
            descartadas += 1  # encabezado, fila rota o valor no numérico
            continue
        print(f"{tienda}\t{ingreso}")

    # Contador visible en la salida de Hadoop (incluye el encabezado)
    print(f"reporter:counter:Calidad,FilasDescartadas,{descartadas}", file=sys.stderr)


if __name__ == "__main__":
    main()
