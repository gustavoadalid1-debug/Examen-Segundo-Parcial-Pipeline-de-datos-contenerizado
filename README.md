# Examen Segundo Parcial — Pipeline de datos contenerizado

| | |
|---|---|
| **Alumno** | Gustavo Adalid Catalán Carmen |
| **Matrícula** | 125052712 |
| **Pregunta asignada** | **Ticket promedio** (ingreso promedio por registro) **por tienda** |
| **Docente** | Javier Moya |

**Dataset:** `ventas_125052712.csv` — 5,000,000 filas × 8 columnas (≈ 336 MB): `id, fecha_hora, tienda, categoria, producto, cantidad, precio_unitario, metodo_pago`. No se sube al repositorio (`*.csv` está en `.gitignore`).

**Definición usada:** el ingreso de cada registro es `cantidad × precio_unitario`; el ticket promedio de una tienda es la media de esos ingresos entre todos sus registros.

- **Mapper:** emite `tienda <TAB> cantidad × precio_unitario` y descarta el encabezado y las filas inválidas.
- **Reducer:** recibe las líneas ordenadas por tienda y calcula `suma / conteo` por tienda.

## Arquitectura

```
 ./data/ventas_125052712.csv ──► [hadoop]  Hadoop Streaming (mapper.py + reducer.py)
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
# copia ventas_125052712.csv a la carpeta data\

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
docker exec hadoop bash /scripts/run_job.sh ventas_125052712.csv
```

La salida queda en `results/salida/part-00000` (formato `tienda<TAB>ticket_promedio`). Con 5 millones de filas puede tardar varios minutos.

### C2 · Comparativa Hadoop vs secuencial

```powershell
docker exec hadoop bash /scripts/medir_tiempos.sh ventas_125052712.csv
```

| Método | Tiempo medido |
|---|---|
| Hadoop Streaming (local) | _(completar)_ s |
| Secuencial (`secuencial.py`) | _(completar)_ s |
| ¿Resultados idénticos? | _(sí / no)_ |

**Explicación** _(ajustar a tus tiempos)_: Hadoop en modo local corre en una sola máquina, así que no hay paralelismo real entre nodos, y aun así paga la sobrecarga de arrancar la JVM, planificar el job, ordenar y escribir archivos intermedios. Un script secuencial lee un archivo de unos 300 MB directamente y suele ser comparable o más rápido. MapReduce compensa con volúmenes mucho mayores y un clúster que reparta map y reduce entre varios nodos.

### D · Integración con la API y persistencia

```powershell
docker compose exec api python /scripts/cargar_resultados.py

curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/resultados
curl.exe http://localhost:8000/resultados/T013
```

Escritura (POST) y borrado (DELETE). En PowerShell, `Invoke-RestMethod` evita los problemas de comillas de `curl.exe`:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/resultados -ContentType "application/json" -Body '{"clave":"T999","valor":1}'
curl.exe http://localhost:8000/resultados/T999
Invoke-RestMethod -Method Delete -Uri http://localhost:8000/resultados/T999
```

(Equivalente en Linux/Mac o Git Bash: `curl -X POST http://localhost:8000/resultados -H "Content-Type: application/json" -d '{"clave":"T999","valor":1}'`.)

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

**1. Modos de Hadoop y uso de HDFS.** En el modo *standalone* (local) todo corre en un solo proceso Java, sin demonios, y lee y escribe en el sistema de archivos local; sirve para pruebas y depuración. En el *pseudo-distribuido* los demonios (NameNode, DataNode, ResourceManager, NodeManager) corren en una misma máquina como procesos separados, simulando un clúster pequeño. En el *totalmente distribuido* esos demonios se reparten en varios nodos reales, y HDFS replica los bloques entre ellos para escalar y tolerar fallas. HDFS se usa en el pseudo-distribuido y en el totalmente distribuido, pero no en el standalone.

**2. ¿Por qué el dataset se monta como volumen y no con `COPY`?** (1) El CSV pesa unos 336 MB: copiarlo a la imagen la infla y hace lentos el build, el push y el pull de cada versión. (2) Datos y código deben estar separados: si cambia el CSV no hay que reconstruir la imagen, y la misma imagen sirve para cualquier dataset. (3) El CSV no debe viajar con la imagen ni con el repositorio (privacidad y la penalización por subirlo), mientras que un volumen lo deja solo en la máquina local. (4) El volumen se comparte entre contenedores sin duplicar el archivo.

**3. `docker compose down` vs `docker compose down -v`.** `down` elimina contenedores y red, pero conserva los volúmenes nombrados, así que los datos de la base de datos (`pgdata`) siguen ahí al volver a levantar. `down -v` elimina además los volúmenes nombrados: la base de datos se pierde por completo y hay que volver a cargar los resultados con `cargar_resultados.py`.

**4. ¿Por qué MapReduce no siempre es más rápido que un script secuencial con 400 MB?** Porque tiene costos fijos: arrancar la JVM, planificar el job, serializar, ordenar y mezclar (shuffle) y escribir resultados intermedios a disco. Con 400 MB y una sola máquina no hay paralelismo real, y un script secuencial lee ese archivo en pocos segundos. Conviene cuando los datos son de varios GB o TB y no caben en memoria o tardarían demasiado, cuando hay un clúster con varios nodos que paralelicen map y reduce, y cuando la tarea se puede dividir en partes independientes y se necesita tolerancia a fallos.

**5. Diferencias entre `CMD` y `ENTRYPOINT`, y entre `COPY` y `ADD`.** `CMD` define el comando por defecto y se reemplaza fácilmente con `docker run imagen otro-comando`. `ENTRYPOINT` define el ejecutable fijo; lo que se escribe después del nombre de la imagen se agrega como argumentos. Combinados, `ENTRYPOINT` es el programa y `CMD` sus argumentos por defecto. `COPY` solo copia archivos o carpetas del contexto de build a la imagen. `ADD` hace lo mismo, pero además descomprime `.tar` locales y puede descargar desde una URL; se prefiere `COPY` por ser más explícito y predecible.

## F · Guía para la defensa oral

| Cambio pedido | Cómo hacerlo |
|---|---|
| Cambiar el puerto de la API | Editar `API_PORT` en `.env` → `docker compose up -d` → `curl.exe http://localhost:<nuevo>/resultados` |
| De promedio a suma | En `reducer.py` imprimir `total` en lugar de `total / n` → `run_job.sh` → `cargar_resultados.py` |
| Filtro por mes | En `mapper.py`, dentro del `try`, agregar `if fila[1][5:7] != "03": continue` (mes de `fecha_hora`, ej. marzo) → `run_job.sh` → `cargar_resultados.py` |
| Borrar el volumen y recargar | `docker compose down -v` → `docker compose up -d` → `docker exec hadoop bash /scripts/run_job.sh ventas_125052712.csv` → `docker compose exec api python /scripts/cargar_resultados.py` |
| Explicar el Dockerfile / compose | Cada instrucción está comentada en los propios archivos |

Si se cambia el mapper o el reducer, el mismo cambio debe hacerse en `secuencial.py` para que la comparativa siga coincidiendo.

Diagnóstico ante errores: `docker compose ps`, `docker compose logs <servicio>`, `docker exec -it hadoop bash`.

## Notas

- `.gitignore` excluye `*.csv` y `.env` (sin CSV ni credenciales en el repo).
- `.gitattributes` fuerza saltos de línea LF para que los scripts funcionen dentro de los contenedores aunque Git en Windows use CRLF.
- Solo se versiona `.env.example`, con valores de ejemplo.
