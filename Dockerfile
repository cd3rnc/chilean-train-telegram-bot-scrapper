# Utilizar una imagen base oficial de Python 3.9
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY . /app

# Instalar las dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget gnupg unzip fonts-liberation libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libgbm1 libgtk-3-0 \
    libpango-1.0-0 libvulkan1 libxcomposite1 libxdamage1 libxkbcommon0 \
    xdg-utils libcurl4 chromium chromium-driver && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar las dependencias de Python especificadas en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el archivo .env al contenedor (debe estar en el mismo directorio que el Dockerfile)
COPY .env /app/.env

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]

