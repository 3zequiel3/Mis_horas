FROM node:20-alpine

WORKDIR /app

# Crear usuario no-root por seguridad
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

# Copiar solo package*.json PRIMERO (mejor caché)
COPY frontend/package.json frontend/package-lock.json ./

# Instalar dependencias (npm ci es más determinístico que npm install)
RUN npm ci --no-audit --no-fund && npm cache clean --force

# Copiar archivos de configuración
COPY frontend/astro.config.mjs frontend/tsconfig.json ./

# Copiar .env
COPY .env .env

# Copiar código fuente
COPY frontend/src ./src
COPY frontend/public ./public

# Cambiar propietario de archivos
RUN chown -R nodejs:nodejs /app

# Ejecutar como usuario no-root
USER nodejs

# Exponer puerto
EXPOSE 3000

# Comando por defecto (será sobrescrito en docker-compose para desarrollo)
CMD ["npm", "run", "build"]
