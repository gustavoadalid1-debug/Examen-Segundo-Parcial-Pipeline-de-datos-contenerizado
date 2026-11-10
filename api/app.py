"""API Flask sobre PostgreSQL.

GET    /health                -> estado de la API
GET    /resultados            -> todos los resultados
GET    /resultados/<clave>    -> un resultado (404 si no existe)
POST   /resultados            -> inserta o actualiza {"clave": "...", "valor": 123.4}
DELETE /resultados/<clave>    -> borra un resultado

Las credenciales llegan por variables de entorno (archivo .env), nunca en el código.
"""
import os
import time

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def conectar():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def iniciar_tabla():
    """Crea la tabla si no existe. Reintenta por si la BD aún está arrancando."""
    for intento in range(10):
        try:
            with conectar() as con, con.cursor() as cur:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS resultados ("
                    "clave TEXT PRIMARY KEY, valor DOUBLE PRECISION NOT NULL)"
                )
            return
        except psycopg2.OperationalError:
            print(f"BD no disponible, reintento {intento + 1}/10", flush=True)
            time.sleep(2)
    raise RuntimeError("No se pudo conectar a la base de datos")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/resultados")
def listar():
    with conectar() as con, con.cursor() as cur:
        cur.execute("SELECT clave, valor FROM resultados ORDER BY clave")
        filas = cur.fetchall()
    return jsonify([{"clave": c, "valor": v} for c, v in filas])


@app.get("/resultados/<clave>")
def obtener(clave):
    with conectar() as con, con.cursor() as cur:
        cur.execute("SELECT clave, valor FROM resultados WHERE clave = %s", (clave,))
        fila = cur.fetchone()
    if fila is None:
        return jsonify(error="no existe"), 404
    return jsonify(clave=fila[0], valor=fila[1])


@app.post("/resultados")
def guardar():
    datos = request.get_json(silent=True) or {}
    try:
        clave = str(datos["clave"]).strip()
        valor = float(datos["valor"])
        if not clave:
            raise ValueError
    except (KeyError, ValueError, TypeError):
        return jsonify(error='se requiere JSON {"clave": texto, "valor": número}'), 400
    with conectar() as con, con.cursor() as cur:
        cur.execute(
            "INSERT INTO resultados (clave, valor) VALUES (%s, %s) "
            "ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor",
            (clave, valor),
        )
    return jsonify(clave=clave, valor=valor), 201


@app.delete("/resultados/<clave>")
def borrar(clave):
    with conectar() as con, con.cursor() as cur:
        cur.execute("DELETE FROM resultados WHERE clave = %s", (clave,))
        borradas = cur.rowcount
    if borradas == 0:
        return jsonify(error="no existe"), 404
    return jsonify(borrado=clave)


iniciar_tabla()

if __name__ == "__main__":
    # 0.0.0.0 para que sea accesible desde fuera del contenedor
    app.run(host="0.0.0.0", port=5000)
