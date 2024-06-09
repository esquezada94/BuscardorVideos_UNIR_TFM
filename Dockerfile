# Imagen base con CUDA 11.8 y Ubuntu 20.04
FROM nvidia/cuda:11.8.0-base-ubuntu20.04

# Actualizar el sistema y instalar dependencias
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git ffmpeg

# RUN apt-get install -y cuda-toolkit-12-5

# Copiar el código de tu proyecto
COPY . /app

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar las dependencias de tu proyecto (si las tienes)
RUN pip3 install -r requirements.txt

# Comando para ejecutar tu código
CMD ["python3", "app.py"] 
