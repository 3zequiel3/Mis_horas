# helpers.py
from sqlalchemy.orm import Session
from db import SessionLocal

def get_db():
    """Generador para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()