import sqlite3
import pandas as pd

DB_PATH = 'ssd_db.sqlite'

def verify_ssd():
    conn = sqlite3.connect(DB_PATH)
    
    tables = [
        'dim_cliente', 
        'dim_tipo_defecto', 
        'dim_fase_sdlc', 
        'fact_defecto',
        'fact_proyecto'
    ]
    
    print("--- SSD Verification ---")
    for table in tables:
        try:
            df = pd.read_sql(f"SELECT * FROM {table} LIMIT 5", conn)
            count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {table}", conn).iloc[0]['cnt']
            print(f"Table: {table} ({count} rows)")
            print(df.head())
            print("-" * 20)
            
            if table == 'fact_proyecto':
                # Check new columns
                cols = df.columns.tolist()
                print(f"Columns in fact_proyecto: {cols}")
                if 'cliente_id' in cols and 'proyecto_id' in cols:
                    print("✅ New columns present.")
                else:
                    print("❌ New columns MISSING.")
                    
        except Exception as e:
            print(f"Error checking {table}: {e}")
            
    conn.close()

if __name__ == '__main__':
    verify_ssd()
