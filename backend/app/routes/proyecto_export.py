from flask import Blueprint, request, jsonify
from app.services.proyecto_service import ProyectoService
from app.services.tarea_service import TareaService
from app.services.dia_service import DiaService
from app.models.dia_colaborador import DiaColaborador
from app.models.proyecto_colaborador import ProyectoColaborador
from app.models.usuario import Usuario
from app.decorators import organization_required

proyecto_export_bp = Blueprint('proyecto_export', __name__)

@proyecto_export_bp.route('/proyectos/<int:proyecto_id>/export-colaboradores', methods=['GET'])
@organization_required
def export_colaboradores_data(context, proyecto_id):
    """Obtiene datos de todos los colaboradores para exportación (PDF/CSV)"""
    # Verificar que el proyecto existe
    proyecto = ProyectoService.obtener_proyecto_por_id(proyecto_id)
    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
    # Verificar que es un proyecto colaborativo
    if proyecto.tipo_proyecto != 'colaborativo':
        return jsonify({'error': 'Este endpoint solo funciona para proyectos colaborativos'}), 400
    
    # Obtener mes y año de los parámetros (opcional, si no se especifica toma el mes del proyecto)
    mes = request.args.get('mes', type=int, default=proyecto.mes)
    anio = request.args.get('anio', type=int, default=proyecto.anio)
    
    # Obtener todos los colaboradores activos del proyecto
    colaboradores = ProyectoColaborador.query.filter_by(
        proyecto_id=proyecto_id,
        estado='aceptado'
    ).all()
    
    # Estructura de respuesta
    resultado = {
        'proyecto': {
            'id': proyecto.id,
            'nombre': proyecto.nombre,
            'mes': mes,
            'anio': anio
        },
        'colaboradores': []
    }
    
    # Para cada colaborador, obtener sus tareas y días
    for collab in colaboradores:
        usuario = Usuario.query.get(collab.usuario_id)
        if not usuario:
            continue
        
        # Verificar si es el propietario
        es_propietario = (proyecto.usuario_id == collab.usuario_id)
        
        # Obtener tareas del colaborador
        tareas = TareaService.obtener_tareas_proyecto(
            proyecto_id=proyecto_id,
            mes=mes,
            anio=anio,
            usuario_colaborador_id=collab.usuario_id,
            es_propietario=es_propietario
        )
        
        # Obtener días compartidos del proyecto (en colaborativos los días son compartidos)
        dias = DiaService.obtener_dias_mes(
            proyecto_id=proyecto_id,
            anio=anio,
            mes=mes
        )

        # Obtener las horas específicas de este colaborador para cada día
        horas_colaborador = {
            dc.dia_id: dc
            for dc in DiaColaborador.query.filter_by(
                usuario_colaborador_id=collab.usuario_id
            ).filter(
                DiaColaborador.dia_id.in_([d.id for d in dias])
            ).all()
        }

        dias_data = []
        for d in dias:
            dia_dict = d.to_dict()
            dc = horas_colaborador.get(d.id)
            dia_dict['horas_trabajadas'] = dc.horas_trabajadas if dc else 0
            dia_dict['horas_reales'] = dc.horas_reales if dc else 0
            dias_data.append(dia_dict)

        colaborador_data = {
            'usuario_id': usuario.id,
            'nombre': usuario.nombre_completo or usuario.username,
            'rol': collab.rol,
            'tareas': [t.to_dict(incluir_desglose_empleados=False) for t in tareas],
            'dias': dias_data,
            'estadisticas': collab.to_dict(incluir_estadisticas=True).get('estadisticas', {})
        }
        
        resultado['colaboradores'].append(colaborador_data)
    
    return jsonify(resultado), 200
