from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from app.config import (
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME,
    SECRET_KEY, CORS_ORIGINS
)

load_dotenv()

db = SQLAlchemy()

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{DB_USER}:"
        f"{DB_PASSWORD}@"
        f"{DB_HOST}:"
        f"{DB_PORT}/"
        f"{DB_NAME}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'connect_timeout': 10,
            'read_timeout': 10,
        },
        'pool_pre_ping': True,  # Verifica la conexión antes de usar
        'pool_recycle': 3600,    # Recicla conexiones cada hora
    }
    app.config['SECRET_KEY'] = SECRET_KEY
    
    # Inicializar extensiones
    db.init_app(app)
    
    # CORS
    cors_origins_list = CORS_ORIGINS.split(',')
    CORS(app, origins=cors_origins_list, supports_credentials=True)
    
    # Registrar blueprints
    from app.routes import auth_bp, proyecto_bp, tarea_bp, dia_bp, usuario_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(proyecto_bp, url_prefix='/api/proyectos')
    app.register_blueprint(tarea_bp, url_prefix='/api/tareas')
    app.register_blueprint(dia_bp, url_prefix='/api/dias')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    
    # Crear tablas de manera segura (lazy loading)
    @app.before_request
    def create_tables():
        """Crear tablas si no existen (ejecuta una sola vez)"""
        if not hasattr(create_tables, 'initialized'):
            try:
                with app.app_context():
                    db.create_all()
                create_tables.initialized = True
            except Exception as e:
                print(f"Advertencia: No se pudieron crear las tablas inicialmente: {e}")
                print("Las tablas se crearán cuando la BD esté lista...")
    
    return app
