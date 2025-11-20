#!/usr/bin/env python3
"""
Script para exportar el schema completo de la base de datos
Genera los CREATE TABLE con todas las relaciones, índices y constraints
Útil para replicar la estructura en producción
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import inspect, MetaData
from sqlalchemy.schema import CreateTable, CreateIndex
from datetime import datetime


def export_database_schema(app, output_file='database_schema.sql'):
    """
    Exporta el schema completo de la base de datos a un archivo SQL
    """
    print("=" * 80)
    print("EXPORTANDO SCHEMA DE BASE DE DATOS")
    print("=" * 80)
    
    # Crear metadata y reflejar la base de datos actual
    metadata = MetaData()
    metadata.reflect(bind=db.engine)
    
    # Abrir archivo de salida en directorio temporal
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f'/tmp/schema_export_{timestamp}.sql'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Escribir encabezado
        f.write("-- " + "=" * 76 + "\n")
        f.write("-- SCHEMA DE BASE DE DATOS - MisHoras\n")
        f.write(f"-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- " + "=" * 76 + "\n\n")
        
        # Desactivar checks de foreign keys temporalmente
        f.write("-- Desactivar verificación de foreign keys durante la creación\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
        
        # Obtener todas las tablas en orden de dependencias
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        
        print(f"\n📋 Tablas encontradas: {len(table_names)}")
        for table_name in sorted(table_names):
            print(f"  - {table_name}")
        
        print(f"\n📝 Generando CREATE TABLE statements...\n")
        
        # Generar CREATE TABLE para cada tabla
        for table_name in sorted(table_names):
            table = metadata.tables[table_name]
            
            print(f"  ✓ Procesando tabla: {table_name}")
            
            # Escribir comentario de sección
            f.write("-- " + "-" * 76 + "\n")
            f.write(f"-- Tabla: {table_name}\n")
            f.write("-- " + "-" * 76 + "\n\n")
            
            # Eliminar tabla si existe
            f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n\n")
            
            # Generar CREATE TABLE
            create_table_stmt = str(CreateTable(table).compile(db.engine))
            f.write(create_table_stmt + ";\n\n")
            
            # Generar índices adicionales si existen
            for index in table.indexes:
                if not index.unique:  # Los unique ya están en CREATE TABLE
                    create_index_stmt = str(CreateIndex(index).compile(db.engine))
                    f.write(create_index_stmt + ";\n")
            
            f.write("\n")
        
        # Reactivar checks de foreign keys
        f.write("-- Reactivar verificación de foreign keys\n")
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")
        
        # Escribir información adicional
        f.write("-- " + "=" * 76 + "\n")
        f.write("-- INFORMACIÓN DE FOREIGN KEYS\n")
        f.write("-- " + "=" * 76 + "\n\n")
        
        for table_name in sorted(table_names):
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                f.write(f"-- Foreign Keys de tabla '{table_name}':\n")
                for fk in fks:
                    f.write(f"--   {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n")
                    if fk.get('ondelete'):
                        f.write(f"--     ON DELETE: {fk['ondelete']}\n")
                    if fk.get('onupdate'):
                        f.write(f"--     ON UPDATE: {fk['onupdate']}\n")
                f.write("\n")
        
        # Escribir resumen
        f.write("\n-- " + "=" * 76 + "\n")
        f.write(f"-- RESUMEN: {len(table_names)} tablas exportadas\n")
        f.write(f"-- Archivo: {output_path}\n")
        f.write("-- " + "=" * 76 + "\n")
    
    print(f"\n✅ Schema exportado exitosamente!")
    print(f"📁 Archivo generado: {output_path}")
    print(f"📊 Total de tablas: {len(table_names)}\n")
    
    # Mostrar estructura de relaciones
    print("🔗 RELACIONES ENTRE TABLAS:")
    print("-" * 80)
    
    for table_name in sorted(table_names):
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print(f"\n📌 {table_name}:")
            for fk in fks:
                cols = ', '.join(fk['constrained_columns'])
                ref_cols = ', '.join(fk['referred_columns'])
                print(f"   └─ {cols} → {fk['referred_table']}.{ref_cols}")
                if fk.get('ondelete'):
                    print(f"      (ON DELETE {fk['ondelete']})")
    
    print("\n" + "=" * 80)
    print("Para copiar el archivo a tu máquina local, ejecuta:")
    print(f"docker cp timeflow_backend:{output_path} ./schema_export.sql")
    print("=" * 80 + "\n")
    
    return output_path


if __name__ == '__main__':
    try:
        # Crear la aplicación Flask y contexto
        app = create_app()
        with app.app_context():
            export_database_schema(app)
    except Exception as e:
        print(f"\n❌ Error al exportar schema: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
