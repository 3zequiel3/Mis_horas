# Gestor de Horas

Sistema para gestionar horas trabajadas por proyecto y generar reportes.

## Características

- 📊 Seguimiento de horas por día y proyecto
- 📝 Gestión de tareas con días asignados
- 📄 Exportación a PDF
- 🗄️ Base de datos MySQL
- 🐳 Dockerizado

## Instalación

1. Clonar el repositorio:
```bash
git clone <tu-repo>
cd mis_horas
```

2. Ejecutar con Docker:
```bash
docker compose up -d
```

3. Acceder a la aplicación:
```
http://localhost:8501
```

## Estructura

```
mis_horas/
├── app.py              # Aplicación principal
├── models.py           # Modelos de base de datos
├── db.py              # Configuración de base de datos
├── requirements.txt    # Dependencias Python
├── Dockerfile         # Imagen de la aplicación
└── docker-compose.yml # Orquestación de servicios
```

## Variables de Entorno

Las siguientes variables se configuran automáticamente en Docker:

- `DB_HOST=db`
- `DB_PORT=3306`
- `DB_USER=mis_horas`
- `DB_PASSWORD=mis_horas`
- `DB_NAME=mis_horas`

## Uso

1. Crear un proyecto desde el sidebar
2. Agregar días y registrar horas
3. Crear tareas y asignar días trabajados
4. Exportar reportes en PDF

## Tecnologías

- **Frontend:** Streamlit
- **Backend:** Python + SQLAlchemy
- **Base de datos:** MySQL 8.0
- **Containerización:** Docker
- **PDF:** ReportLab