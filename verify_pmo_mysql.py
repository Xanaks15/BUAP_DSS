import mysql.connector
import pandas as pd

DB_CONFIG = {
    'host': 'yamabiko.proxy.rlwy.net',
    'port': 27081,
    'user': 'root',
    'password': 'uwlMQNkutAeSqNGduCudtUJQoyhPlhcU',
    'database': 'railway'
}

def verify_pmo_data():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    tables = [
        'defecto', 'fase_sdlc', 'proyecto', 'proyecto_empleado', 'tarea', 'tipo_defecto'
    ]
    
    print("--- PMO MySQL Verification ---")
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            count = cursor.fetchone()[0]
            print(f"Table: {table} ({count} rows)")
            
            if count == 0:
                print(f"❌ WARNING: {table} is empty!")
            else:
                print(f"✅ {table} populated.")
                
        except Exception as e:
            print(f"Error checking {table}: {e}")
            
    conn.close()

if __name__ == "__main__":
    verify_pmo_data()
