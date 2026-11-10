# Examen Segundo Parcial — Pipeline de datos contenerizado

| | |
|---|---|
| **Alumno** | Gustavo Adalid Catalán Carmen |
| **Matrícula** | 125052712 |
| **Pregunta asignada** | _(PENDIENTE: pegar aquí el enunciado de tu pregunta de MapReduce)_ |
| **Docente** | Javier Moya |

## Arquitectura

```
 ./data/*.csv ──► [hadoop]  Hadoop Streaming (mapper.py + reducer.py)
                     │            └── escribe results/salida/part-00000
                     ▼
              scripts/cargar_resultados.py ──► [db] PostgreSQL (volumen pgdata)
                                                   ▲
                                         [api] Flask  (GET / POST / DELETE)
```

Servicios de `docker-compose.yml`: `hadoop`, `db`, `api` (red `pipeline`, volumen nombrado `pgdata`, variables en `.env`, `depends_on` con healthcheck). El servicio `hadoop2` solo existe bajo el perfil `ssh` para demostrar SSH entre contenedores.

## Cómo reproducirlo (Windows 11 + Docker Desktop)

```powershell
git clone https://github.com/gustavoadalid1-debug/Examen-Segundo-Parcial-Pipeline-de-datos-contenerizado.git
cd Examen-Segundo-Parcial-Pipeline-de-datos-contenerizado

copy .env.example .env          # edita .env y cambia la contraseña
# copia tu CSV a la carpeta data\   (los .csv NO se suben al repo)

docker compose up --build -d
docker compose ps
```

### A1 · Hadoop

```powershell
docker exec hadoop hadoop version
```

### B · SSH sin contraseña

```powershell
docker exec hadoop ssh localhost hostname                # a sí mismo
docker compose --profile ssh up -d hadoop2               # segundo contenedor
docker exec hadoop ssh hadoop2 hostname                  # entre contenedores
docker exec hadoop2 ssh hadoop hostname                  # y en sentido contrario
```

No pide contraseña: la llave RSA se genera sin passphrase en el `Dockerfile` y `sshd` tiene `PasswordAuthentication no`.

### C1 · Job MapReduce

```powershell
docker exec hadoop bash /scripts/run_job.sh <archivo>.csv
```

La salida queda en `results/salida/part-00000` (formato `clave<TAB>valor`).

### C2 · Comparativa Hadoop vs secuencial

```powershell
docker exec hadoop bash /scripts/medir_tiempos.sh <archivo>.csv
```

| Método | Tiempo medido |
|---|---|
| Hadoop Streaming (local) | _(completar)_ s |
| Secuencial (`secuencial.py`) | _(completar)_ s |
| ¿Resultados idénticos? | _(sí / no)_ |

**Explicación** _(completar con tus tiempos)_: con un dataset pequeño o mediano, Hadoop suele ser más lento porque arrancar la JVM, planificar el job y escribir archivos intermedios cuesta varios segundos; esa sobrecarga solo se compensa con volúmenes grandes y un clúster real que paralelice map y reduce en varios nodos. El modo local usado aquí ejecuta todo en una sola máquina, así que no hay ganancia por paralelismo.

### D · Integración con la API y persistencia

```powershell
docker compose exec api python /scripts/cargar_resultados.py

curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/resultados
curl.exe http://localhost:8000/resultados/<clave>
curl.exe -X POST http://localhost:8000/resultados -H "Content-Type: application/json" -d "{\"clave\":\"prueba\",\"valor\":1}"
curl.exe -X DELETE http://localhost:8000/resultados/prueba
```

**Persistencia:**

```powershell
docker compose down            # sin -v: conserva el volumen
docker compose up -d
curl.exe http://localhost:8000/resultados    # los datos siguen ahí
```

## Evidencias

Guardar en `evidencias/`:

- [ ] `hadoop version`
- [ ] `ssh localhost` y SSH entre contenedores sin contraseña
- [ ] Salida del job (`run_job.sh`)
- [ ] Comparativa de tiempos (`medir_tiempos.sh`)
- [ ] Respuesta de la API (`GET /resultados`)
- [ ] Persistencia tras `docker compose down` y `up`

## E · Teoría

**1. Diferencia entre `CMD` y `ENTRYPOINT`, y entre `COPY` y `ADD`.**

- `CMD` define el comando por defecto del contenedor y se reemplaza fácilmente: `docker run imagen otro-comando` lo sustituye. `ENTRYPOINT` define el ejecutable fijo; lo que se escribe después del nombre de la imagen se agrega como argumentos. Combinados, `ENTRYPOINT` es el programa y `CMD` sus argumentos por defecto.
- `COPY` solo copia archivos o carpetas del contexto de construcción a la imagen. `ADD` hace lo mismo, pero además descomprime `.tar` locales y puede descargar desde una URL. Se prefiere `COPY` por ser explícito y predecible.

_(PENDIENTE: agregar las demás preguntas de teoría del examen y sus respuestas.)_

## F · Guía para la defensa oral

| Cambio pedido | Cómo hacerlo |
|---|---|
| Cambiar el puerto de la API | Editar `API_PORT` en `.env` → `docker compose up -d` → `curl.exe http://localhost:<nuevo>/resultados` |
| Otra agregación (promedio / filtro por mes) | Editar `mapper.py` (filtro con un `if`) y `reducer.py` (ver el docstring para promedio) → `run_job.sh` → `cargar_resultados.py` |
| Borrar el volumen y recargar | `docker compose down -v` → `docker compose up -d` → `docker exec hadoop bash /scripts/run_job.sh <csv>` → `docker compose exec api python /scripts/cargar_resultados.py` |
| Explicar el Dockerfile / compose | Cada instrucción está comentada en los propios archivos |

Diagnóstico ante errores: `docker compose ps`, `docker compose logs <servicio>`, `docker exec -it hadoop bash`.

## Notas

- `.gitignore` excluye `*.csv` y `.env` (sin CSV ni credenciales en el repo).
- `.gitattributes` fuerza saltos de línea LF para que los scripts funcionen dentro de los contenedores aunque Git en Windows use CRLF.
- Solo se versiona `.env.example`, con valores de ejemplo.
