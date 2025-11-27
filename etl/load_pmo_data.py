import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env vars
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, 'etl.env'))

# Configuration
CSV_DIR = os.path.join(base_dir, 'synthetic_output')

def get_db_connection():
    user = os.getenv('PMO_USER')
    password = os.getenv('PMO_PASSWORD')
    host = os.getenv('PMO_HOST')
    port = os.getenv('PMO_PORT')
    database = os.getenv('PMO_DB')
    
    if not all([user, password, host, port, database]):
        raise ValueError("Missing PMO database configuration in etl.env")
        
    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url)

def load_data(engine):
    files = {
        "departamento.csv": "departamento",
        "rol.csv": "rol",
        "empleado.csv": "empleado",
        "cliente.csv": "cliente",
        "tipo_proyecto.csv": "tipo_proyecto",
        "estado.csv": "estado",
        "catalogo_tareas.csv": "catalogo_tareas",
        "proyecto.csv": "proyecto",
        "tarea.csv": "tarea",
        "proyecto_empleado.csv": "proyecto_empleado",
        "finanzas_proyecto.csv": "finanzas_proyecto",
        "tipo_defecto.csv": "tipo_defecto",
        "fase_sdlc.csv": "fase_sdlc",
        "defecto.csv": "defecto"
    }

    with engine.connect() as conn:
        # Disable FK checks for bulk load
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        for csv_file, table_name in files.items():
            file_path = os.path.join(CSV_DIR, csv_file)
            if os.path.exists(file_path):
                print(f"Loading {table_name}...")
                df = pd.read_csv(file_path)
                
                if table_name == 'proyecto':
                    df.rename(columns={'horas_totales': 'horas_planificadas'}, inplace=True)
                
                # Truncate table before loading
                try:
                    conn.execute(text(f"TRUNCATE TABLE {table_name};"))
                except Exception as e:
                    print(f"Error truncating {table_name}: {e}")

                try:
                    df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=1000)
                    print(f"Loaded {len(df)} rows into {table_name}")
                except Exception as e:
                    print(f"Error loading {table_name}: {e}")
            else:
                print(f"File {csv_file} not found.")
        
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()

if __name__ == '__main__':
    try:
        print("Connecting to PMO Database...")
        engine = get_db_connection()
        print("Loading new synthetic data to PMO...")
        load_data(engine)
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")
