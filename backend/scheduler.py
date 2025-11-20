"""
Scheduler para ejecutar tareas automáticas
Usa APScheduler para ejecutar procesos en segundo plano
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from app.services.marcado_automatico_service import MarcadoAutomaticoService
from app import create_app
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Crear app para contexto
app = create_app()

def ejecutar_marcado_automatico():
    """Ejecuta el marcado automático de salida"""
    with app.app_context():
        logger.info("🕒 Iniciando ejecución programada de marcado automático")
        try:
            cantidad = MarcadoAutomaticoService.procesar_marcados_automaticos()
            logger.info(f"✅ Marcado automático completado: {cantidad} marcados procesados")
        except Exception as e:
            logger.error(f"❌ Error en marcado automático: {str(e)}")

def ejecutar_horas_extras():
    """Procesa las horas extras con confirmación"""
    with app.app_context():
        logger.info("🕒 Iniciando procesamiento de horas extras")
        try:
            MarcadoAutomaticoService.procesar_horas_extras_con_confirmacion()
            logger.info("✅ Procesamiento de horas extras completado")
        except Exception as e:
            logger.error(f"❌ Error en procesamiento de horas extras: {str(e)}")

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    
    # Ejecutar marcado automático cada hora en punto
    scheduler.add_job(
        ejecutar_marcado_automatico,
        'cron',
        hour='*',
        minute=0,
        id='marcado_automatico',
        name='Marcado automático de salida'
    )
    
    # Procesar horas extras cada 2 horas
    scheduler.add_job(
        ejecutar_horas_extras,
        'cron',
        hour='*/2',
        minute=0,
        id='horas_extras',
        name='Procesamiento de horas extras'
    )
    
    logger.info("🚀 Scheduler iniciado")
    logger.info("📅 Tareas programadas:")
    logger.info("  - Marcado automático: cada hora en punto")
    logger.info("  - Horas extras: cada 2 horas")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Scheduler detenido")
