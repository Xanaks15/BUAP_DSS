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
from dotenv import load_dotenv

# Load env vars from etl.env
base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(base_dir)) # Go up to root
load_dotenv(os.path.join(root_dir, 'etl.env'))

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

def load_sql_queries(file_path: str) -> Dict[str, str]:
    queries: Dict[str, str] = {}
    current_name: str | None = None
    buffer: list[str] = []
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"SQL file not found: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('--'):
                if current_name is not None:
                    queries[current_name] = '\n'.join(buffer).strip()
                    buffer.clear()
                current_name = stripped[2:].strip()
            else:
                buffer.append(line.rstrip('\n'))
        if current_name is not None:
            queries[current_name] = '\n'.join(buffer).strip()
    return queries

def get_db_connection(config: Dict[str, str], db_type: str = 'mysql') -> Any:
    if db_type == 'sqlite':
        db_path = config.get('database')
        return sqlite3.connect(db_path)
    
    if mysql is None and sqlalchemy is None:
        raise ImportError("MySQL drivers not installed.")
        
    if sqlalchemy:
        user = config.get('user')
        password = config.get('password')
        host = config.get('host')
        port = config.get('port')
        database = config.get('database')
        engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")
        return engine.raw_connection()
    else:
        return mysql.connector.connect(**config)

def extract_data(config: Dict[str, str], queries: Dict[str, str], db_type: str = 'mysql') -> Dict[str, pd.DataFrame]:
    conn = get_db_connection(config, db_type)
    
    mapping = {
        'extract_projects': 'projects',
        'extract_tasks': 'tasks',
        'extract_project_employees': 'project_employees',
        'extract_states': 'states',
        'extract_types': 'types',
        'extract_finances': 'finances',
        'extract_catalogues': 'catalogues',
        'extract_clients': 'clients',
        'extract_defect_types': 'defect_types',
        'extract_phases': 'phases',
        'extract_defects': 'defects'
    }

    tables: Dict[str, pd.DataFrame] = {}
    try:
        for query_name, dest_key in mapping.items():
            sql = queries.get(query_name)
            if sql is None:
                print(f"Warning: Query '{query_name}' not found.")
                continue
            tables[dest_key] = pd.read_sql(sql, conn)
    finally:
        if hasattr(conn, 'close'):
            conn.close()
        elif hasattr(conn, 'dispose'):
            conn.dispose()
            
    return tables

def _calculate_task_metrics(tasks: pd.DataFrame, project_row: pd.Series) -> Tuple[int, int, int]:
    project_tasks = tasks.loc[tasks['catalogo_tareas_id'] == project_row['catalogo_id']]
    total = len(project_tasks)
    completed = int(project_tasks['completada'].sum())
    delay_count = 0

    for _, t in project_tasks.iterrows():
        entrega = t.get('fecha_entrega')
        completado = t.get('fecha_completado')
        finished = bool(t.get('completada'))
        
        if pd.notnull(entrega): entrega = pd.to_datetime(entrega)
        if pd.notnull(completado): completado = pd.to_datetime(completado)
        
        if finished and pd.notnull(entrega) and pd.notnull(completado):
            if completado > entrega:
                delay_count += 1
        elif not finished and pd.notnull(entrega) and pd.notnull(project_row.get('fecha_fin_real')):
            fin_real = pd.to_datetime(project_row['fecha_fin_real'])
            if entrega <= fin_real:
                delay_count += 1
                
    return total, completed, delay_count

def transform_data(tables: Dict[str, pd.DataFrame]) -> Tuple:
    projects = tables['projects']
    tasks = tables['tasks']
    project_employees = tables['project_employees']
    states = tables['states']
    types = tables['types']
    finances = tables['finances']
    clients = tables['clients']
    defect_types = tables['defect_types']
    phases = tables['phases']
    defects = tables['defects']

    if projects.empty:
        print("No hay proyectos nuevos para procesar.")
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

    # --- FILTERING LOGIC (ONLY FACTS) ---
    print("Filtrando proyectos activos (dejando solo Completado/Cancelado)...")
    valid_statuses = ['Completado', 'Cancelado']
    valid_status_ids = states[states['nombre_estado'].isin(valid_statuses)]['estado_id'].tolist()
    
    original_proj_count = len(projects)
    projects = projects[projects['estado_id'].isin(valid_status_ids)]
    print(f"Proyectos filtrados: {original_proj_count} -> {len(projects)}")
    
    valid_project_ids = projects['proyecto_id'].tolist()
    
    # Filter related tables
    tasks = tasks[tasks['catalogo_tareas_id'].isin(valid_project_ids)]
    project_employees = project_employees[project_employees['proyecto_id'].isin(valid_project_ids)]
    finances = finances[finances['proyecto_id'].isin(valid_project_ids)]
    defects = defects[defects['proyecto_id'].isin(valid_project_ids)]
    # ------------------------------------

    dim_estado_df = states.copy()
    dim_tipo_proyecto_df = types.copy()
    dim_cliente_df = clients.rename(columns={'nombre': 'nombre_cliente'})
    dim_tipo_defecto_df = defect_types.copy()
    dim_tipo_defecto_df['nombre_tipo_defecto'] = dim_tipo_defecto_df['categoria'] + ' - ' + dim_tipo_defecto_df['subtipo']
    dim_fase_sdlc_df = phases.copy()

    merged_projects = projects.merge(finances, on='proyecto_id', how='left')
    
    metrics_list = []
    for idx, row in merged_projects.iterrows():
        t_plan, t_comp, t_delay = _calculate_task_metrics(tasks, row)
        metrics_list.append((t_plan, t_comp, t_delay))
    
    metrics_df = pd.DataFrame(metrics_list, columns=['tareas_planificadas', 'tareas_completadas', 'tareas_retrasadas'], index=merged_projects.index)
    merged_projects = pd.concat([merged_projects, metrics_df], axis=1)
    
    emp_metrics = project_employees.groupby('proyecto_id').size().reset_index(name='empleados_asignados')
    merged_projects = merged_projects.merge(emp_metrics, on='proyecto_id', how='left')
    
    cols_to_fill = ['tareas_planificadas', 'tareas_completadas', 'tareas_retrasadas', 'empleados_asignados']
    for col in cols_to_fill:
        if col in merged_projects.columns:
            merged_projects[col] = merged_projects[col].fillna(0)
            
    merged_projects.rename(columns={
        'monto_presupuestado': 'monto_planificado',
        'monto_real_acumulado': 'monto_real',
        'ingreso_proyecto': 'ingreso_proyecto'
    }, inplace=True)
    
    cols_to_fill_fin = ['horas_planificadas', 'horas_trabajadas', 'monto_planificado', 'monto_real', 'ingreso_proyecto']
    for col in cols_to_fill_fin:
        if col in merged_projects.columns:
            merged_projects[col] = merged_projects[col].fillna(0)

    merged_projects['ganancia_proyecto'] = merged_projects['ingreso_proyecto'] - merged_projects['monto_real']
    merged_projects['roi'] = np.where(
        merged_projects['monto_real'] > 0,
        (merged_projects['ganancia_proyecto'] / merged_projects['monto_real']) * 100,
        0.0
    )

    def compute_tuct(row):
        try:
            start = pd.to_datetime(row['fecha_inicio_plan'])
            end = pd.to_datetime(row['fecha_fin_real'])
            if pd.isnull(start) or pd.isnull(end): return 0.0
            days = (end - start).days
            return float(days) if days >= 0 else 0.0
        except: return 0.0
    
    merged_projects['tuct'] = merged_projects.apply(compute_tuct, axis=1)

    date_cols_proj = ['fecha_inicio_plan', 'fecha_fin_plan', 'fecha_inicio_real', 'fecha_fin_real']
    proj_dates = merged_projects[date_cols_proj].values.ravel('K')
    defect_dates = defects['fecha_registro'].values if not defects.empty else []
    all_dates = np.concatenate([proj_dates, defect_dates])
    all_dates = pd.to_datetime([d for d in all_dates if pd.notnull(d)])
    all_dates = pd.Index(all_dates).drop_duplicates().sort_values()

    dias_esp = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    meses_esp = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

    date_info = pd.DataFrame({
        'fecha': all_dates,
        'anio': all_dates.year,
        'mes': all_dates.month,
        'dia': all_dates.day,
        'nombre_dia': [dias_esp[d] for d in all_dates.weekday],
        'nombre_mes': [meses_esp[m - 1] for m in all_dates.month],
        'trimestre': all_dates.quarter,
    })

    dim_anio_df = date_info[['anio']].drop_duplicates().sort_values('anio').reset_index(drop=True)
    dim_anio_df['anio_id'] = range(1, len(dim_anio_df) + 1)
    
    dim_mes_df = date_info[['mes', 'nombre_mes', 'trimestre', 'anio']].drop_duplicates().sort_values(['anio', 'mes']).reset_index(drop=True)
    dim_mes_df = dim_mes_df.merge(dim_anio_df, on='anio')
    dim_mes_df['mes_id'] = range(1, len(dim_mes_df) + 1)
    dim_mes_df.rename(columns={'mes': 'numero_mes'}, inplace=True)
    
    dim_dia_df = date_info[['dia', 'nombre_dia', 'mes', 'anio']].drop_duplicates().sort_values(['anio', 'mes', 'dia']).reset_index(drop=True)
    dim_dia_df = dim_dia_df.merge(dim_anio_df, on='anio').merge(dim_mes_df, left_on=['mes', 'anio_id'], right_on=['numero_mes', 'anio_id'])
    dim_dia_df['dia_id'] = range(1, len(dim_dia_df) + 1)
    
    dim_tiempo_df = date_info.copy()
    dim_tiempo_df = dim_tiempo_df.merge(dim_anio_df, on='anio') \
                                 .merge(dim_mes_df, left_on=['mes', 'anio_id'], right_on=['numero_mes', 'anio_id']) \
                                 .merge(dim_dia_df, left_on=['dia', 'mes_id', 'anio_id'], right_on=['dia', 'mes_id', 'anio_id'])
    dim_tiempo_df['tiempo_id'] = dim_tiempo_df['fecha'].dt.strftime('%Y%m%d').astype(int)

    def get_time_id(dt):
        if pd.isnull(dt): return None
        return int(pd.to_datetime(dt).strftime('%Y%m%d'))

    for col in date_cols_proj:
        merged_projects[col] = merged_projects[col].apply(get_time_id)
        
    merged_projects['fact_id'] = merged_projects['proyecto_id']
    fact_proyecto_df = merged_projects

    fact_defecto_df = pd.DataFrame()
    if not defects.empty:
        fact_defecto_df = defects.copy()
        fact_defecto_df['tiempo_id'] = fact_defecto_df['fecha_registro'].apply(get_time_id)

    return (
        fact_proyecto_df,
        dim_estado_df[['estado_id', 'nombre_estado']],
        dim_tipo_proyecto_df[['tipo_proyecto_id', 'nombre']],
        dim_tiempo_df[['tiempo_id', 'fecha', 'dia_id']],
        dim_dia_df[['dia_id', 'nombre_dia', 'dia', 'mes_id']],
        dim_mes_df[['mes_id', 'nombre_mes', 'numero_mes', 'trimestre', 'anio_id']],
        dim_anio_df[['anio_id', 'anio']],
        dim_cliente_df[['cliente_id', 'nombre_cliente', 'sector', 'pais']],
        dim_tipo_defecto_df[['tipo_defecto_id', 'nombre_tipo_defecto']],
        dim_fase_sdlc_df[['fase_id', 'nombre_fase']],
        fact_defecto_df
    )

def insert_dataframe(conn: Any, df: pd.DataFrame, sql: str, db_type: str = 'mysql') -> None:
    if df.empty: return

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d')
        elif pd.api.types.is_object_dtype(df[col]):
             try:
                 df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d') if hasattr(x, 'strftime') else x)
             except:
                 pass

    df = df.astype(object).where(pd.notnull(df), None)
    
    def to_python(x):
        if hasattr(x, 'item'): return x.item()
        return x
        
    data = [tuple(to_python(x) for x in row) for row in df.to_numpy()]

    cursor = conn.cursor()
    
    if db_type == 'sqlite':
        sql = sql.replace('INSERT IGNORE', 'INSERT OR IGNORE')
        sql = sql.replace('%s', '?')
        
    try:
        cursor.executemany(sql, data)
        conn.commit()
    except Exception as e:
        print(f"Error inserting data: {e}")

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
    
    print(f"DEBUG CONFIG: PMO_PORT={pmo_config.get('port')}, SSD_PORT={ssd_config.get('port')}")
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
    
    # --- TRUNCATE TABLES ---
    print("Vaciando tablas destino (Clean Load)...")
    cursor = ssd_conn.cursor()
    try:
        if DB_TYPE == 'mysql':
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        tables_to_truncate = [
            'fact_defecto', 'fact_proyecto', 
            'dim_fase_sdlc', 'dim_tipo_defecto', 'dim_cliente', 
            'dim_tipo_proyecto', 'dim_estado', 'dim_tiempo', 
            'dim_dia', 'dim_mes', 'dim_anio'
        ]
        
        for table in tables_to_truncate:
            try:
                if DB_TYPE == 'mysql':
                    cursor.execute(f"TRUNCATE TABLE {table};")
                else:
                    cursor.execute(f"DELETE FROM {table};")
            except Exception as e:
                print(f"Error truncating {table}: {e}")
                
        if DB_TYPE == 'mysql':
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        ssd_conn.commit()
        print("Tablas vaciadas correctamente.")
    except Exception as e:
        print(f"Error durante vaciado: {e}")
    # -----------------------
    
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