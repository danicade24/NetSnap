#!/bin/bash

# Variables con valores por defecto
: ${SSH_USERNAME:=ubuntu}
: ${SSH_PASSWORD:?"Error: SSH_PASSWORD environment variable is not set."}
: ${SSHD_CONFIG_ADDITIONAL:=""}

# Crear usuario si no existe
if id "$SSH_USERNAME" &>/dev/null; then
    echo "User $SSH_USERNAME already exists"
else
    useradd -ms /bin/bash "$SSH_USERNAME"
    echo "$SSH_USERNAME:$SSH_PASSWORD" | chpasswd
    echo "User $SSH_USERNAME created with provided password"
fi

# Crear carpeta .ssh con permisos correctos
mkdir -p /home/$SSH_USERNAME/.ssh
chown -R $SSH_USERNAME:$SSH_USERNAME /home/$SSH_USERNAME/.ssh
chmod 700 /home/$SSH_USERNAME/.ssh

# Manejar clave pública desde variable o desde archivo montado
if [ -n "$AUTHORIZED_KEYS" ]; then
    echo "$AUTHORIZED_KEYS" > /home/$SSH_USERNAME/.ssh/authorized_keys
    echo "Authorized key set from environment variable"
elif [ -f "/authorized_keys" ]; then
    cp /authorized_keys /home/$SSH_USERNAME/.ssh/authorized_keys
    echo "Authorized key copied from mounted file"
fi

# Permisos sobre la clave autorizada si existe
if [ -f /home/$SSH_USERNAME/.ssh/authorized_keys ]; then
    chown $SSH_USERNAME:$SSH_USERNAME /home/$SSH_USERNAME/.ssh/authorized_keys
    chmod 600 /home/$SSH_USERNAME/.ssh/authorized_keys
    sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    echo "Password authentication disabled"
else
    echo "No authorized_keys found, SSH will require password"
fi

#Configuración SSHD adicional si existe
if [ -n "$SSHD_CONFIG_ADDITIONAL" ]; then
    echo "$SSHD_CONFIG_ADDITIONAL" >> /etc/ssh/sshd_config
    echo "✅ Additional SSHD config applied"
fi

if [ -n "$SSHD_CONFIG_FILE" ] && [ -f "$SSHD_CONFIG_FILE" ]; then
    cat "$SSHD_CONFIG_FILE" >> /etc/ssh/sshd_config
    echo "Additional SSHD config from file applied"
fi

echo "Starting SSH server..."
exec /usr/sbin/sshd -D
