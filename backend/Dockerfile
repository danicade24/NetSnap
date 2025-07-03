FROM python:3.13-slim

# Evitar prompts de instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias de sistema
RUN apt-get update && apt-get install -y \
    nmap \
    gcc \
    build-essential \
    openssh-client \
    sshpass \
    && rm -rf /var/lib/apt/lists/*

# Instalar Ansible
RUN pip install --no-cache-dir ansible

# Crear carpeta de trabajo
WORKDIR /code

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Exponer el puerto
EXPOSE 5000

# Comando por defecto
CMD ["flask", "run", "--host=0.0.0.0"]
