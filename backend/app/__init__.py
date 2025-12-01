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
    app.url_map.strict_slashes = False  # Evitar redirects 308 por trailing slashes
    
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
    
    # CORS - Configuración completa (FASE 1 MULTI-TENANT: incluir X-Organization-ID)
    cors_origins_list = CORS_ORIGINS.split(',')
    CORS(app, 
         origins=cors_origins_list, 
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Organization-ID"],
         expose_headers=["X-Organization-ID"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Registrar blueprints
    from app.routes import auth_bp, proyecto_bp, tarea_bp, dia_bp, usuario_bp, empleado_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(proyecto_bp, url_prefix='/api/proyectos')
    app.register_blueprint(tarea_bp, url_prefix='/api/tareas')
    app.register_blueprint(dia_bp, url_prefix='/api/dias')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    app.register_blueprint(empleado_bp, url_prefix='/api')
    
    # Registrar blueprints del sistema de asistencia
    from app.routes.invitacion import invitacion_bp
    from app.routes.notificacion import notificacion_bp
    from app.routes.asistencia import asistencia_bp
    from app.routes.deuda import deuda_bp
    from app.routes.configuracion_asistencia import configuracion_bp
    
    app.register_blueprint(invitacion_bp)
    app.register_blueprint(notificacion_bp)
    app.register_blueprint(asistencia_bp)
    app.register_blueprint(deuda_bp)
    app.register_blueprint(configuracion_bp)
    
    # Registrar blueprint de organizaciones (MULTI-TENANT)
    from app.routes.organization import organization_bp
    app.register_blueprint(organization_bp, url_prefix='/api/organizations')
    
    # Registrar blueprints de Fase 2: RBAC, Auditoría y Aprobaciones
    from app.routes.auditoria import auditoria_bp
    from app.routes.aprobaciones import aprobaciones_bp
    app.register_blueprint(auditoria_bp)
    app.register_blueprint(aprobaciones_bp)
    
    # Registrar blueprints de Fase 3: Motor Financiero
    from app.routes.rates import rates_bp
    from app.routes.budgets import budgets_bp
    from app.routes.expenses import expenses_bp
    from app.routes.profitability import profitability_bp
    app.register_blueprint(rates_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(profitability_bp)
    
    # Registrar blueprints de Fase 4: UX Unificada
    from app.routes.budget_addons import budget_addons_bp
    app.register_blueprint(budget_addons_bp)
    
    # Crear tablas al inicializar la app (solo una vez)
    with app.app_context():
        try:
            db.create_all()
            print("✓ Tablas de base de datos verificadas/creadas")
        except Exception as e:
            print(f"⚠ Advertencia al crear tablas: {e}")
    
    return app
