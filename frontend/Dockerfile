FROM node:20-alpine AS build

WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json ./

# Instalar todas las dependencias (incluyendo dev)
RUN npm ci --no-audit --no-fund

# Copiar código
COPY . .

# Build para producción
RUN npm run build

# Runtime stage
FROM node:20-alpine

WORKDIR /app

# Crear usuario no-root por seguridad
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

# Copiar solo los archivos necesarios del build
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/package-lock.json ./package-lock.json

# Instalar solo dependencias de producción
RUN npm ci --omit=dev --no-audit --no-fund && npm cache clean --force

# Cambiar propietario de archivos
RUN chown -R nodejs:nodejs /app

# Ejecutar como usuario no-root
USER nodejs

# Exponer puerto
EXPOSE 3000

# Comando para ejecutar
CMD ["node", "./dist/server/entry.mjs"]
