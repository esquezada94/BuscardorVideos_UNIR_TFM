# syntax=docker/dockerfile:1

FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos y la aplicación
COPY requirements_app.txt requirements.txt

# Instalar las dependencias de Python
RUN pip install -r requirements.txt

# Copiar el resto de los archivos de la aplicación
COPY . /app

# Establecer el comando por defecto para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
