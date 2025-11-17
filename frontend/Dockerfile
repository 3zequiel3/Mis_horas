FROM node:20-alpine

WORKDIR /app

# Crear usuario no-root por seguridad
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

# Copiar archivos de dependencias
COPY frontend/package.json frontend/package-lock.json ./

# Instalar todas las dependencias (incluyendo dev)
RUN npm ci --no-audit --no-fund

# Copiar archivos de configuración
COPY frontend/astro.config.mjs frontend/tsconfig.json ./
COPY .env .env

# Copiar código (será montado como volumen en desarrollo)
COPY frontend/ .

# Cambiar propietario de archivos
RUN chown -R nodejs:nodejs /app

# Ejecutar como usuario no-root
USER nodejs

# Exponer puerto
EXPOSE 3000

# Comando por defecto (será sobrescrito en docker-compose para desarrollo)
CMD ["npm", "run", "build"]
