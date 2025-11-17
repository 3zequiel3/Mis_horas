"""
Variables de entorno centralizadas
Desestructuración de os.getenv para acceso fácil y validación
"""

import os

# Desestructuración de variables de entorno
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_ROOT_PASSWORD = os.getenv('DB_ROOT_PASSWORD')

API_HOST = os.getenv('API_HOST')
API_PORT = os.getenv('API_PORT')
FLASK_DEBUG = os.getenv('FLASK_DEBUG')
FLASK_ENV = os.getenv('FLASK_ENV')

SECRET_KEY = os.getenv('SECRET_KEY')
JWT_EXPIRATION_HOURS = os.getenv('JWT_EXPIRATION_HOURS')
CORS_ORIGINS = os.getenv('CORS_ORIGINS')

# Validar que las variables requeridas estén disponibles
REQUIRED_VARS = {
    'DB_HOST': DB_HOST,
    'DB_PORT': DB_PORT,
    'DB_USER': DB_USER,
    'DB_PASSWORD': DB_PASSWORD,
    'DB_NAME': DB_NAME,
    'API_HOST': API_HOST,
    'API_PORT': API_PORT,
    'SECRET_KEY': SECRET_KEY,
    'JWT_EXPIRATION_HOURS': JWT_EXPIRATION_HOURS,
    'CORS_ORIGINS': CORS_ORIGINS,
}

missing_vars = [var for var, value in REQUIRED_VARS.items() if not value]
if missing_vars:
    raise RuntimeError(f"Variables de entorno requeridas no definidas: {', '.join(missing_vars)}")
