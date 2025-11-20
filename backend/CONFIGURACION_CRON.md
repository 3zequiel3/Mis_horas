# Configuración de Procesos Automáticos

## 📋 Marcado Automático de Salida

El sistema necesita un proceso automático que ejecute el marcado de salida para empleados que no marcaron manualmente.

### Opción 1: Cron Job (Linux/Mac)

1. **Editar el crontab:**
```bash
crontab -e
```

2. **Agregar la siguiente línea:**
```cron
# Ejecutar marcado automático cada hora
0 * * * * cd /home/ezequiel/Escritorio/Proyectos/MisHoras/backend && /usr/bin/python3 -c "from app.services.marcado_automatico_service import ejecutar_marcado_automatico; ejecutar_marcado_automatico()"
```

**O ejecutar al final del día (23:00):**
```cron
0 23 * * * cd /home/ezequiel/Escritorio/Proyectos/MisHoras/backend && /usr/bin/python3 -c "from app.services.marcado_automatico_service import ejecutar_marcado_automatico; ejecutar_marcado_automatico()"
```

3. **Verificar que el cron está activo:**
```bash
crontab -l
```

### Opción 2: APScheduler (Integrado en Flask)

Instalar APScheduler:
```bash
pip install apscheduler
```

Agregar en `backend/main.py`:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.marcado_automatico_service import MarcadoAutomaticoService

def init_scheduler(app):
    """Inicializa el scheduler de tareas automáticas"""
    scheduler = BackgroundScheduler()
    
    # Ejecutar marcado automático cada hora
    scheduler.add_job(
        func=lambda: MarcadoAutomaticoService.procesar_marcados_automaticos(),
        trigger="cron",
        hour='*',  # Cada hora
        minute=0,
        id='marcado_automatico',
        name='Marcado automático de salida',
        replace_existing=True
    )
    
    # Procesar horas extras con confirmación cada 2 horas
    scheduler.add_job(
        func=lambda: MarcadoAutomaticoService.procesar_horas_extras_con_confirmacion(),
        trigger="cron",
        hour='*/2',  # Cada 2 horas
        minute=0,
        id='confirmacion_horas_extras',
        name='Procesamiento de horas extras con confirmación',
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Scheduler de tareas automáticas iniciado")
    
    # Shutdown del scheduler cuando la app se cierra
    import atexit
    atexit.register(lambda: scheduler.shutdown())

# En la inicialización de la app (después de crear app)
if __name__ == '__main__':
    init_scheduler(app)
    app.run(host=API_HOST, port=int(API_PORT), debug=(FLASK_DEBUG == 'True'))
```

### Opción 3: Celery (Para proyectos grandes)

Si el proyecto crece y necesitas una solución más robusta:

```bash
pip install celery redis
```

Crear `backend/celery_worker.py`:

```python
from celery import Celery
from celery.schedules import crontab
from app import create_app

app = create_app()
celery = Celery(app.name, broker='redis://localhost:6379/0')

@celery.task
def tarea_marcado_automatico():
    with app.app_context():
        from app.services.marcado_automatico_service import MarcadoAutomaticoService
        MarcadoAutomaticoService.procesar_marcados_automaticos()

@celery.task
def tarea_horas_extras():
    with app.app_context():
        from app.services.marcado_automatico_service import MarcadoAutomaticoService
        MarcadoAutomaticoService.procesar_horas_extras_con_confirmacion()

# Configurar tareas periódicas
celery.conf.beat_schedule = {
    'marcado-automatico-cada-hora': {
        'task': 'celery_worker.tarea_marcado_automatico',
        'schedule': crontab(minute=0),  # Cada hora en punto
    },
    'procesar-horas-extras': {
        'task': 'celery_worker.tarea_horas_extras',
        'schedule': crontab(hour='*/2', minute=0),  # Cada 2 horas
    },
}
```

Ejecutar:
```bash
# Terminal 1: Worker de Celery
celery -A celery_worker worker --loglevel=info

# Terminal 2: Scheduler de Celery
celery -A celery_worker beat --loglevel=info
```

### Opción 4: Docker Compose (Recomendado para producción)

Agregar en `docker-compose.yml`:

```yaml
services:
  scheduler:
    build: ./backend
    command: python -c "from app.services.marcado_automatico_service import ejecutar_marcado_automatico; import time; import schedule; schedule.every().hour.do(ejecutar_marcado_automatico); while True: schedule.run_pending(); time.sleep(60)"
    environment:
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
    depends_on:
      - db
    restart: unless-stopped
```

O crear un contenedor específico con cron:

```dockerfile
# Dockerfile.cron
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Instalar cron
RUN apt-get update && apt-get install -y cron

# Agregar el cron job
RUN echo "0 * * * * cd /app && python -c 'from app.services.marcado_automatico_service import ejecutar_marcado_automatico; ejecutar_marcado_automatico()' >> /var/log/cron.log 2>&1" > /etc/cron.d/marcado-automatico

RUN chmod 0644 /etc/cron.d/marcado-automatico
RUN crontab /etc/cron.d/marcado-automatico

CMD cron && tail -f /var/log/cron.log
```

Agregarlo al docker-compose:

```yaml
  cron:
    build:
      context: ./backend
      dockerfile: Dockerfile.cron
    environment:
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
    depends_on:
      - db
    restart: unless-stopped
```

## ⚙️ Configuración recomendada

Para desarrollo local: **Opción 2 (APScheduler)**
Para producción con Docker: **Opción 4 (Docker Compose con cron)**
Para proyectos muy grandes: **Opción 3 (Celery)**

## 🧪 Probar manualmente

Ejecutar desde la terminal:

```bash
cd backend
python -c "from app.services.marcado_automatico_service import ejecutar_marcado_automatico; ejecutar_marcado_automatico()"
```

## 📝 Logs

Los logs se mostrarán en consola con formato:
- ✅ Operaciones exitosas
- ⚠️ Advertencias
- ❌ Errores

Ejemplo de salida:
```
🕒 Iniciando proceso de marcado automático de salida - 2025-11-20 18:00:00
✅ Salida automática marcada para empleado 5 en proyecto MiProyecto - Hora: 18:00:00
✅ Proceso completado. 3 marcados procesados automáticamente
```
