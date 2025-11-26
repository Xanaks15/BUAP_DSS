import os
import warnings
from typing import Dict, Tuple, Any
import time
import pandas as pd
import numpy as np

# Try to import DB connectors
try:
    import sqlalchemy
    from sqlalchemy import create_engine
except ImportError:
    sqlalchemy = None
    create_engine = None

try:
    import mysql.connector
except ModuleNotFoundError:
    mysql = None

import sqlite3

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
# Read from Environment Variables
DB_TYPE = os.getenv('DB_TYPE', 'sqlite') # 'sqlite' or 'mysql'

# SQLite Defaults
PMO_DB_PATH = 'pmo_db.sqlite'
SSD_DB_PATH = 'ssd_db.sqlite'

def get_db_config(prefix):
    if DB_TYPE == 'sqlite':
        return {'database': PMO_DB_PATH if prefix == 'PMO' else SSD_DB_PATH}
    
    return {
        'host': os.getenv(f'{prefix}_HOST'),
        'port': int(os.getenv(f'{prefix}_PORT', 3306)),
        'user': os.getenv(f'{prefix}_USER'),
        'password': os.getenv(f'{prefix}_PASSWORD'),
        'database': os.getenv(f'{prefix}_DB')
    }

# ... (Functions remain same) ...

def main():
    """
    Función principal de orquestación del ETL.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    extraction_file = os.path.join(base_dir, 'sql_queries', 'extraction_queries.sql')
    load_file = os.path.join(base_dir, 'sql_queries', 'load_queries.sql')
    
    extraction_queries = load_sql_queries(extraction_file)
    load_queries = load_sql_queries(load_file)

    pmo_config = get_db_config('PMO')
    ssd_config = get_db_config('SSD')
    
    print(f"--- INICIO ETL ({DB_TYPE}) ---")
    total_start_time = time.time()

    # 1. EXTRACCIÓN
    start_ext = time.time()
    print("Extrayendo datos...")
    tables = extract_data(pmo_config, extraction_queries, db_type=DB_TYPE)
    ext_time = time.time() - start_ext
    print(f"Extracción completada en {ext_time:.2f}s")

    # 2. TRANSFORMACIÓN
    start_trans = time.time()
    print("Transformando datos...")
    (fact_df, dim_estado, dim_tipo, dim_tiempo, dim_dia, dim_mes, dim_anio, 
     dim_cliente, dim_tipo_defecto, dim_fase, fact_defecto) = transform_data(tables)
    trans_time = time.time() - start_trans
    print(f"Transformación completada en {trans_time:.2f}s")

    # 3. CARGA
    start_load = time.time()
    print("Cargando datos...")
    ssd_conn = get_db_connection(ssd_config, db_type=DB_TYPE)
    
    try:
        # Load Dimensions
        insert_dataframe(ssd_conn, dim_anio[['anio_id', 'anio']], load_queries['load_dim_anio'], DB_TYPE)
        insert_dataframe(ssd_conn, dim_mes[['mes_id', 'nombre_mes', 'numero_mes', 'trimestre', 'anio_id']], load_queries['load_dim_mes'], DB_TYPE)
        
        dim_dia_load = dim_dia.rename(columns={'dia': 'numero_dia'})
        insert_dataframe(ssd_conn, dim_dia_load[['dia_id', 'nombre_dia', 'numero_dia', 'mes_id']], load_queries['load_dim_dia'], DB_TYPE)
        
        insert_dataframe(ssd_conn, dim_tiempo[['tiempo_id', 'fecha', 'dia_id']], load_queries['load_dim_tiempo'], DB_TYPE)
        insert_dataframe(ssd_conn, dim_estado[['estado_id', 'nombre_estado']], load_queries['load_dim_estado'], DB_TYPE)
        
        dim_tipo_load = dim_tipo.rename(columns={'nombre_tipo': 'nombre'})
        insert_dataframe(ssd_conn, dim_tipo_load[['tipo_proyecto_id', 'nombre']], load_queries['load_dim_tipo_proyecto'], DB_TYPE)

        insert_dataframe(ssd_conn, dim_cliente[['cliente_id', 'nombre_cliente', 'sector', 'pais']], load_queries['load_dim_cliente'], DB_TYPE)
        insert_dataframe(ssd_conn, dim_tipo_defecto[['tipo_defecto_id', 'nombre_tipo_defecto']], load_queries['load_dim_tipo_defecto'], DB_TYPE)
        
        dim_fase_load = dim_fase.rename(columns={'fase_id': 'fase_sdlc_id'})
        insert_dataframe(ssd_conn, dim_fase_load[['fase_sdlc_id', 'nombre_fase']], load_queries['load_dim_fase_sdlc'], DB_TYPE)

        # Load Fact Proyecto
        if not fact_df.empty:
            insert_dataframe(ssd_conn, fact_df[[
                'fact_id', 'proyecto_id', 'nombre', 'descripcion', 'horas_planificadas', 'horas_trabajadas',
                'monto_planificado', 'monto_real', 'ganancia_proyecto', 'tareas_planificadas',
                'tareas_completadas', 'tareas_retrasadas', 'empleados_asignados', 'roi', 'tuct',
                'fecha_inicio_plan', 'fecha_fin_plan', 'fecha_inicio_real', 'fecha_fin_real',
                'estado_id', 'tipo_proyecto_id', 'cliente_id'
            ]], load_queries['load_fact_proyecto'], DB_TYPE)

        # Load Fact Defecto
        if not fact_defecto.empty:
            insert_dataframe(ssd_conn, fact_defecto[[
                'proyecto_id', 'tipo_defecto_id', 'fase_id', 'severidad', 'tiempo_id'
            ]], load_queries['load_fact_defecto'], DB_TYPE)
        
    finally:
        ssd_conn.close()
        
    load_time = time.time() - start_load
    print(f"Carga completada en {load_time:.2f}s")

    # --- 4. Update Source (Incremental Logic) ---
    print("Actualizando fuente (marcando registros extraídos)...")
    start_update = time.time()
    
    # Define which tables need updating and their ID columns
    update_map = {
        'projects': ('proyecto', 'proyecto_id'),
        'tasks': ('tarea', 'tarea_id'),
        'finances': ('finanzas_proyecto', 'id'),
        'defects': ('defecto', 'defecto_id')
        # 'project_employees': ('proyecto_empleado', ['proyecto_id', 'empleado_id']) # Composite key handling is complex, skipping for simplicity or need custom logic
    }
    
    # Re-open connection to PMO for updates (or reuse if possible, but safe to new)
    conn_pmo_update = get_db_connection(pmo_config, db_type=DB_TYPE)
    cursor_pmo = conn_pmo_update.cursor()
    
    try:
        for key, (table_name, id_col) in update_map.items():
            if key in tables and not tables[key].empty:
                ids = tables[key][id_col].tolist()
                if not ids: continue
                
                # Batch update for efficiency
                # SQLite limit is usually 999 variables, so chunk it
                chunk_size = 500
                for i in range(0, len(ids), chunk_size):
                    chunk = ids[i:i+chunk_size]
                    placeholders = ','.join(['%s'] * len(chunk)) # MySQL uses %s
                    if DB_TYPE == 'sqlite':
                        placeholders = ','.join(['?'] * len(chunk))
                        
                    sql_update = f"UPDATE {table_name} SET metadata_extraccion = 1 WHERE {id_col} IN ({placeholders})"
                    cursor_pmo.execute(sql_update, chunk)
        
        # Handle composite key for project_employees separately if needed, 
        # or just assume if project is extracted, assignments are too.
        # For this demo, we'll skip complex composite updates to avoid errors unless critical.
        
        conn_pmo_update.commit()
        print(f"Actualización fuente completada en {time.time() - start_update:.2f}s")
    except Exception as e:
        print(f"Error updating source metadata: {e}")
        conn_pmo_update.rollback()
    finally:
        conn_pmo_update.close()

    print(f"Tiempo Total: {time.time() - total_start_time:.2f}s")
    print("--- FIN ETL ---")

if __name__ == '__main__':
    main()