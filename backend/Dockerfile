FROM python:3.12-slim

WORKDIR /app

# Crear usuario no-root por seguridad
RUN useradd -m -u 1001 appuser

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY backend/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar .env desde la raíz
COPY .env .env

# Copiar código del backend
COPY --chown=appuser:appuser backend/ .

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Comando por defecto
CMD ["python", "main.py"]
