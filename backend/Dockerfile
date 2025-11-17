FROM python:3.12-slim

WORKDIR /app

# Crear usuario no-root por seguridad
RUN useradd -m -u 1001 appuser

# Instalar solo dependencias de runtime (no build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt PRIMERO (layer de caché)
COPY backend/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar .env
COPY .env .env

# Copiar código del backend
COPY --chown=appuser:appuser backend/ .

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Comando por defecto
CMD ["python", "main.py"]
