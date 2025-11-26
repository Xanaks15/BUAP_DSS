import sqlite3
import pandas as pd
import os

# Configuration
DB_PATH = 'pmo_db.sqlite'
CSV_DIR = './synthetic_output'

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return conn

def create_tables(conn):
    # Read the SQL file and execute it (adapted for SQLite)
    # Note: The SQL generated was MySQL compatible. SQLite is mostly compatible but might need tweaks.
    # For simplicity, we will use pandas to write tables or simple CREATE statements if needed.
    # But let's try to run the SQL script with minor adjustments if possible, or just rely on pandas 'to_sql' 
    # to create the schema structure automatically from the CSVs, enforcing PKs if possible.
    
    # Actually, better to use the SQL script to ensure relationships are defined, 
    # but for this "show schema" step, loading into SQLite via pandas is fastest and sufficient for a demo.
    # However, to be strict with the schema, let's try to execute the SQL.
    
    with open('create_pmo_db.sql', 'r') as f:
        sql_script = f.read()
    
    # Remove MySQL specific syntax
    sql_script = sql_script.replace('CREATE DATABASE IF NOT EXISTS pmo_db;', '')
    sql_script = sql_script.replace('USE pmo_db;', '')
    sql_script = sql_script.replace('INT PRIMARY KEY', 'INTEGER PRIMARY KEY') # SQLite prefers INTEGER for autoinc/PK
    
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()

def load_data(conn):
    files = {
        "departamento.csv": "departamento",
        "rol.csv": "rol",
        "empleado.csv": "empleado",
        "cliente.csv": "cliente",
        "tipo_proyecto.csv": "tipo_proyecto",
        "estado.csv": "estado",
        "catalogo_tareas.csv": "catalogo_tareas", # Load before proyecto
        "proyecto.csv": "proyecto",
        "tarea.csv": "tarea",
        "proyecto_empleado.csv": "proyecto_empleado",
        "finanzas_proyecto.csv": "finanzas_proyecto",
        "tipo_defecto.csv": "tipo_defecto",
        "fase_sdlc.csv": "fase_sdlc",
        "defecto.csv": "defecto"
    }

    for csv_file, table_name in files.items():
        file_path = os.path.join(CSV_DIR, csv_file)
        if os.path.exists(file_path):
            print(f"Loading {table_name}...")
            df = pd.read_csv(file_path)
            # Rename columns if necessary to match schema (e.g. horas_totales -> horas_planificadas)
            if table_name == 'proyecto':
                df.rename(columns={'horas_totales': 'horas_planificadas'}, inplace=True)
            
            try:
                df.to_sql(table_name, conn, if_exists='append', index=False)
                print(f"Loaded {len(df)} rows into {table_name}")
            except Exception as e:
                print(f"Error loading {table_name}: {e}")
        else:
            print(f"File {csv_file} not found.")

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = create_connection(DB_PATH)
    if conn:
        print("Creating tables...")
        create_tables(conn)
        print("Loading data...")
        load_data(conn)
        conn.close()
        print("Done.")
