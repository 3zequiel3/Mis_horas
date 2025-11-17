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

# Instalar uv para dependencias rápidas
RUN pip install --no-cache-dir uv

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias con uv en el sistema
RUN uv pip install --no-cache-dir --system -r requirements.txt

# Copiar código
COPY --chown=appuser:appuser . .

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Comando por defecto
CMD ["python", "main.py"]
