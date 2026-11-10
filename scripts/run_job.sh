#!/bin/bash
# Ejecuta el job MapReduce con Hadoop Streaming (modo local) DENTRO del contenedor hadoop.
# Uso:  docker exec hadoop bash /scripts/run_job.sh <archivo.csv>
#       (el CSV debe estar en la carpeta ./data del proyecto)
set -e

CSV="/data/${1:?Falta el nombre del CSV. Ej: bash /scripts/run_job.sh datos.csv}"
SALIDA="/results/salida"

[ -f "$CSV" ] || { echo "No existe $CSV"; exit 1; }

# Hadoop falla si la carpeta de salida ya existe
rm -rf "$SALIDA"

echo ">>> Job Hadoop Streaming sobre $CSV"
time hadoop jar "$HADOOP_HOME"/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -D mapreduce.job.reduces=1 \
    -input "file://$CSV" \
    -output "file://$SALIDA" \
    -mapper "python3 /mapreduce/mapper.py" \
    -reducer "python3 /mapreduce/reducer.py"

echo ">>> Resultado (primeras líneas):"
head "$SALIDA"/part-00000
