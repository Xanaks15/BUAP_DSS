import mysql.connector
import pandas as pd
import os
import sys

# Configuration
DB_CONFIG = {
    'host': 'yamabiko.proxy.rlwy.net',
    'port': 27081,
    'user': 'root',
    'password': 'uwlMQNkutAeSqNGduCudtUJQoyhPlhcU',
    'database': 'railway'
}

SQL_FILE = 'create_pmo_db.sql'
DATA_DIR = 'synthetic_output'

def execute_sql_script(cursor, script_path):
    print(f"Executing SQL script: {script_path}")
    with open(script_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    statements = sql.split(';')
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt: continue
        if stmt.upper().startswith('CREATE DATABASE') or stmt.upper().startswith('USE'):
            continue
            
        try:
            cursor.execute(stmt)
        except mysql.connector.Error as err:
            print(f"Warning executing statement: {stmt[:50]}... -> {err}")

def load_data(conn):
    print("Loading data from CSVs...")
    files_tables = [
        ('departamento.csv', 'departamento'),
        ('rol.csv', 'rol'),
        ('empleado.csv', 'empleado'),
        ('cliente.csv', 'cliente'),
        ('tipo_proyecto.csv', 'tipo_proyecto'),
        ('estado.csv', 'estado'),
        ('catalogo_tareas.csv', 'catalogo_tareas'),
        ('proyecto.csv', 'proyecto'),
        ('tarea.csv', 'tarea'),
        ('proyecto_empleado.csv', 'proyecto_empleado'),
        ('finanzas_proyecto.csv', 'finanzas_proyecto'),
        ('tipo_defecto.csv', 'tipo_defecto'),
        ('fase_sdlc.csv', 'fase_sdlc'),
        ('defecto.csv', 'defecto')
    ]
    
    cursor = conn.cursor()
    
    for csv_file, table_name in files_tables:
        path = os.path.join(DATA_DIR, csv_file)
        if not os.path.exists(path):
            print(f"Warning: {path} not found.")
            continue
            
        print(f"Loading {table_name} from {csv_file}...")
        df = pd.read_csv(path)
        
        # Replace NaN with None for MySQL
        df = df.where(pd.notnull(df), None)
        
        if table_name == 'proyecto':
            print(f"Original columns: {df.columns.tolist()}")
            if 'horas_totales' in df.columns:
                df.rename(columns={'horas_totales': 'horas_planificadas'}, inplace=True)
            print(f"Renamed columns: {df.columns.tolist()}")
        
        # Build INSERT statement
        cols = ",".join([f"`{c}`" for c in df.columns])
        placeholders = ",".join(["%s"] * len(df.columns))
        sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"
        
        # Convert numpy types to python types
        def to_python(x):
            if hasattr(x, 'item'): return x.item()
            if pd.isna(x): return None
            return x
            
        data = [tuple(to_python(x) for x in row) for row in df.to_numpy()]
        
        try:
            cursor.executemany(sql, data)
        except mysql.connector.Error as err:
            print(f"❌ Error loading {table_name}: {err}")
            raise err # Re-raise to trigger rollback
            
    print("Data loading complete.")

def main():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.autocommit = False # Disable autocommit for atomicity
        
        if conn.is_connected():
            print("Connected to PMO MySQL.")
            cursor = conn.cursor()
            
            # 1. Create Schema (DDL causes implicit commit, so we do it first)
            # We might want to DROP tables first to ensure clean state?
            # For now, let's rely on IF NOT EXISTS in SQL, but if tables exist with wrong schema, it might fail.
            # Let's try to run it.
            execute_sql_script(cursor, SQL_FILE)
            
            # 2. Load Data (Transactional)
            load_data(conn)
            
            conn.commit()
            print("✅ PMO Migration Successful (Committed).")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            print("Rolling back changes...")
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    main()
