import sqlite3
import pandas as pd

DB_PATH = 'pmo_db.sqlite'

def verify_pmo_flags():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['proyecto', 'tarea', 'finanzas_proyecto']
    
    print("--- PMO Flag Verification ---")
    for table in tables:
        try:
            cursor.execute(f"SELECT metadata_extraccion, COUNT(*) FROM {table} GROUP BY metadata_extraccion")
            rows = cursor.fetchall()
            print(f"Table: {table}")
            for status, count in rows:
                print(f"  metadata_extraccion={status}: {count} rows")
        except Exception as e:
            print(f"Error checking {table}: {e}")
            
    conn.close()

if __name__ == '__main__':
    verify_pmo_flags()
