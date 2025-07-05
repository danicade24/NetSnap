# Usa Nginx como base para servir archivos estáticos
FROM nginx:alpine

# Elimina archivos HTML por defecto
RUN rm -rf /usr/share/nginx/html/*

# Establece el directorio de trabajo al contenedor
WORKDIR /usr/share/nginx/html

# Copia los archivos del frontend
COPY templates/ ./templates/
COPY css/ ./css/
COPY js/ ./js/
COPY assets/ ./assets/

# (Opcional) copiar index a raíz para servir desde /
COPY templates/index.html ./index.html

# Exponer el puerto por defecto de Nginx
EXPOSE 80

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]
