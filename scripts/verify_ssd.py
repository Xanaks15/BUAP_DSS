import sqlite3
import pandas as pd

DB_PATH = 'ssd_db.sqlite'

def verify_ssd():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['dim_anio', 'dim_mes', 'dim_dia', 'dim_tiempo', 'dim_estado', 'dim_tipo_proyecto', 'fact_proyecto']
    
    print("--- SSD Verification ---")
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} rows")
            
            if count > 0:
                print(f"Sample from {table}:")
                df = pd.read_sql(f"SELECT * FROM {table} LIMIT 3", conn)
                print(df.to_string(index=False))
                print("-" * 20)
        except Exception as e:
            print(f"Error checking {table}: {e}")
            
    conn.close()

if __name__ == '__main__':
    verify_ssd()
