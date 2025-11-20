"""
Response Utils - Centraliza respuestas estandarizadas
"""

from flask import jsonify
from typing import Any, Dict, Optional


class ApiResponse:
    """Clase para generar respuestas API estandarizadas"""

    @staticmethod
    def success(data: Any = None, message: str = 'Éxito', status_code: int = 200) -> tuple:
        """
        Respuesta exitosa
        
        Args:
            data: Datos a retornar
            message: Mensaje descriptivo
            status_code: Código HTTP (200, 201, etc)
        """
        response = {
            'success': True,
            'message': message,
            'data': data,
        }
        return jsonify(response), status_code

    @staticmethod
    def error(message: str, status_code: int = 400, details: Optional[Dict] = None) -> tuple:
        """
        Respuesta de error
        
        Args:
            message: Mensaje de error
            status_code: Código HTTP (400, 404, 500, etc)
            details: Detalles adicionales del error
        """
        response = {
            'success': False,
            'error': message,
        }
        if details:
            response['details'] = details
        return jsonify(response), status_code

    @staticmethod
    def not_found(resource: str = 'Recurso') -> tuple:
        """Respuesta de recurso no encontrado"""
        return ApiResponse.error(f'{resource} no encontrado', 404)

    @staticmethod
    def bad_request(message: str = 'Solicitud inválida', required_fields: Optional[list] = None) -> tuple:
        """Respuesta de solicitud inválida"""
        details = None
        if required_fields:
            details = {'required_fields': required_fields}
        return ApiResponse.error(message, 400, details)

    @staticmethod
    def unauthorized() -> tuple:
        """Respuesta no autorizado"""
        return ApiResponse.error('No autenticado', 401)

    @staticmethod
    def forbidden() -> tuple:
        """Respuesta acceso prohibido"""
        return ApiResponse.error('Acceso prohibido', 403)

    @staticmethod
    def validation_error(field: str, message: str) -> tuple:
        """Respuesta de error de validación"""
        return ApiResponse.error(
            'Error de validación',
            400,
            {'field': field, 'message': message}
        )

    @staticmethod
    def internal_error(message: str = 'Error interno del servidor') -> tuple:
        """Respuesta error interno"""
        return ApiResponse.error(message, 500)


# Funciones helper para compatibilidad con rutas
def success_response(data: Any = None, message: str = 'Éxito', status_code: int = 200) -> tuple:
    """Función helper para respuestas exitosas"""
    return ApiResponse.success(data, message, status_code)


def error_response(message: str, status_code: int = 400, details: Optional[Dict] = None) -> tuple:
    """Función helper para respuestas de error"""
    return ApiResponse.error(message, status_code, details)
