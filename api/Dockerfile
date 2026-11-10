# Imagen ligera de Python
FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Primero las dependencias: así Docker reutiliza la capa si requirements.txt no cambia
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Después el código de la API
COPY app.py .

# La API escucha en el puerto 5000 del contenedor
EXPOSE 5000

CMD ["python", "app.py"]
