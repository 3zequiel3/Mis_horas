# Stage 1: Builder - Instalar dependencias
FROM node:20-alpine as builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci --no-audit --no-fund && npm cache clean --force

# Stage 2: Runtime - Aplicación final
FROM node:20-alpine

WORKDIR /app

# Crear usuario no-root por seguridad
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

# Copiar node_modules del builder
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules

# Copiar archivos de configuración
COPY --chown=nodejs:nodejs frontend/package.json frontend/package-lock.json ./
COPY --chown=nodejs:nodejs frontend/astro.config.mjs frontend/tsconfig.json ./

# Copiar .env
COPY --chown=nodejs:nodejs .env .env

# Copiar código fuente
COPY --chown=nodejs:nodejs frontend/src ./src

# Crear directorios necesarios
RUN mkdir -p ./public ./.astro && chown -R nodejs:nodejs ./public ./.astro

# Ejecutar como usuario no-root
USER nodejs

EXPOSE 3000

CMD ["npm", "run", "build"]
