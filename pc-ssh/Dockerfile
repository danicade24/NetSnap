FROM ubuntu:24.04

# Variables de entorno (sobreescritas en docker-compose)
ENV DEBIAN_FRONTEND=noninteractive
ENV SSH_USERNAME=ubuntu
ENV SSHD_CONFIG_ADDITIONAL=""

#Instalación de paquetes esenciales
RUN apt-get update && \
    apt-get install -y \
    iproute2 \
    iputils-ping \
    openssh-server \
    telnet \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Preparación de directorios para SSH
RUN mkdir -p /run/sshd

# Crear usuario solo si no existe
RUN if ! id -u "$SSH_USERNAME" >/dev/null 2>&1; then \
        useradd -ms /bin/bash "$SSH_USERNAME"; \
    fi && \
    mkdir -p /home/"$SSH_USERNAME"/.ssh && \
    chown -R "$SSH_USERNAME":"$SSH_USERNAME" /home/"$SSH_USERNAME"/.ssh && \
    chmod 700 /home/"$SSH_USERNAME"/.ssh

#Copiar el script de configuración SSH
COPY configure-ssh-user.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/configure-ssh-user.sh

#Ajustes de SSH básicos (habilitar login sin root)
RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config

# 🌐 8. Exponer puerto SSH
EXPOSE 22

# 🚀 9. Comando final para arrancar el contenedor
CMD ["/usr/local/bin/configure-ssh-user.sh"]
