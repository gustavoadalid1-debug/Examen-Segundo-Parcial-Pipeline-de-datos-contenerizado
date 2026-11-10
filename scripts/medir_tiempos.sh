#!/bin/bash
# Compara Hadoop Streaming vs versión secuencial: mide tiempos y verifica que el resultado coincida.
# Uso:  docker exec hadoop bash /scripts/medir_tiempos.sh <archivo.csv>
set -e

CSV="/data/${1:?Falta el nombre del CSV}"
[ -f "$CSV" ] || { echo "No existe $CSV"; exit 1; }

echo "===== Hadoop Streaming ====="
INICIO=$(date +%s.%N)
bash /scripts/run_job.sh "$1" > /results/log_hadoop.txt 2>&1
FIN=$(date +%s.%N)
echo "Tiempo Hadoop: $(python3 -c "print(round($FIN - $INICIO, 2))") s (log en results/log_hadoop.txt)"

echo "===== Secuencial ====="
INICIO=$(date +%s.%N)
python3 /mapreduce/secuencial.py "$CSV" > /results/secuencial.tsv
FIN=$(date +%s.%N)
echo "Tiempo secuencial: $(python3 -c "print(round($FIN - $INICIO, 2))") s"

echo "===== ¿Coinciden los resultados? ====="
sort /results/salida/part-00000 > /results/_hadoop_ordenado.tsv
sort /results/secuencial.tsv   > /results/_seq_ordenado.tsv
if diff -q /results/_hadoop_ordenado.tsv /results/_seq_ordenado.tsv > /dev/null; then
    echo "SI: ambos resultados son idénticos"
else
    echo "NO: hay diferencias"; diff /results/_hadoop_ordenado.tsv /results/_seq_ordenado.tsv | head
fi
rm -f /results/_hadoop_ordenado.tsv /results/_seq_ordenado.tsv
