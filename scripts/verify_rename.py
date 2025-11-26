import sqlite3
import pandas as pd

DB_PATH = 'ssd_db.sqlite'

def verify_column_rename():
    conn = sqlite3.connect(DB_PATH)
    try:
        # Check columns of fact_prediccion_proyecto
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(fact_prediccion_proyecto)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Columns in fact_prediccion_proyecto: {columns}")
        
        if 'severidad' in columns:
            print("✅ Column 'severidad' found.")
        else:
            print("❌ Column 'severidad' NOT found.")
            
        if 'complejidad' not in columns:
            print("✅ Column 'complejidad' correctly removed.")
        else:
            print("❌ Column 'complejidad' still present.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    verify_column_rename()
