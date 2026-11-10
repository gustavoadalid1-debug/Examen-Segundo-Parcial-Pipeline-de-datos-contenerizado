#!/usr/bin/env python3
"""Carga el resultado del job MapReduce (clave<TAB>valor) en PostgreSQL.

Se ejecuta dentro del contenedor api (ahí está psycopg2 y las variables del .env):
    docker compose exec api python /scripts/cargar_resultados.py
Opcional: pasar otra ruta   python /scripts/cargar_resultados.py /results/salida/part-00000
"""
import os
import sys

import psycopg2

RUTA = sys.argv[1] if len(sys.argv) > 1 else "/results/salida/part-00000"


def main():
    if not os.path.isfile(RUTA):
        sys.exit(f"No existe {RUTA}. Corre primero el job de Hadoop (scripts/run_job.sh).")

    con = psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    cargadas = 0
    with con, con.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS resultados ("
            "clave TEXT PRIMARY KEY, valor DOUBLE PRECISION NOT NULL)"
        )
        with open(RUTA, encoding="utf-8") as f:
            for linea in f:
                try:
                    clave, valor = linea.rstrip("\n").split("\t")
                    valor = float(valor)
                except ValueError:
                    continue  # línea vacía o mal formada
                cur.execute(
                    "INSERT INTO resultados (clave, valor) VALUES (%s, %s) "
                    "ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor",
                    (clave, valor),
                )
                cargadas += 1
    con.close()
    print(f"Filas cargadas: {cargadas}")


if __name__ == "__main__":
    main()
