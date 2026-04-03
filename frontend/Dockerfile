# Stage 1: Dependencies - solo dependencias de producción
FROM node:20-alpine as deps

WORKDIR /app

RUN npm install -g pnpm@latest

COPY frontend/package.json frontend/pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile --prod

# Stage 2: Builder - Compilar la aplicación
FROM node:20-alpine as builder

WORKDIR /app

RUN npm install -g pnpm@latest

COPY frontend/package.json frontend/pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

# Copiar código fuente y archivos de configuración para el build
COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/astro.config.mjs ./
COPY frontend/tsconfig.json ./
COPY frontend/tailwind.config.mjs ./

# Compilar la aplicación
RUN pnpm run build

# Stage 3: Runtime - Imagen final optimizada
FROM node:20-alpine

WORKDIR /app

# Crear usuario no-root por seguridad
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

# Copiar dependencias de producción (stage 1)
COPY --from=deps --chown=nodejs:nodejs /app/node_modules ./node_modules

# Copiar build compilado (stage 2)
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist

# Copiar package.json
COPY --chown=nodejs:nodejs frontend/package.json ./

# Ejecutar como usuario no-root
USER nodejs

EXPOSE 3000

# Ejecutar servidor SSR compilado
CMD ["node", "./dist/server/entry.mjs"]

