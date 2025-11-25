from app import create_app
from app.config import API_HOST, API_PORT, FLASK_DEBUG
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.marcado_automatico_service import MarcadoAutomaticoService
import atexit
import logging
import os

load_dotenv()

app = create_app()

# Scheduler global para evitar duplicación en modo debug
scheduler = None

def init_scheduler():
    """Inicializa el scheduler de tareas automáticas"""
    global scheduler
    
    # Solo inicializar si no existe o si no estamos en el proceso de reloader de Flask
    if scheduler is not None or os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return
    
    scheduler = BackgroundScheduler()
    
    # Función wrapper para ejecutar con contexto de aplicación
    def run_with_app_context(func):
        def wrapper():
            with app.app_context():
                func()
        return wrapper
    
    # Ejecutar marcado automático cada hora
    scheduler.add_job(
        func=run_with_app_context(MarcadoAutomaticoService.procesar_marcados_automaticos),
        trigger="cron",
        hour='*',
        minute=0,
        id='marcado_automatico',
        name='Marcado automático de salida'
    )
    
    # Procesar horas extras cada 2 horas
    scheduler.add_job(
        func=run_with_app_context(MarcadoAutomaticoService.procesar_horas_extras_con_confirmacion),
        trigger="cron",
        hour='*/2',
        minute=0,
        id='horas_extras',
        name='Procesamiento de horas extras'
    )
    
    scheduler.start()
    print("✅ Scheduler de tareas automáticas iniciado")
    print("📅 Próximas ejecuciones:")
    print("   - Marcado automático: cada hora en punto (próxima: siguiente hora :00)")
    print("   - Horas extras: cada 2 horas")
    
    # Shutdown del scheduler cuando la app se cierra
    atexit.register(lambda: scheduler.shutdown() if scheduler else None)

if __name__ == '__main__':
    host = API_HOST
    port = int(API_PORT)
    debug = FLASK_DEBUG == 'True'
    
    # Inicializar scheduler (solo se ejecuta una vez gracias al check de WERKZEUG_RUN_MAIN)
    init_scheduler()
    
    app.run(host=host, port=port, debug=debug)
