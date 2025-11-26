import sqlite3

DB_PATH = 'pmo_db.sqlite'

def reset_flags():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['proyecto', 'tarea', 'finanzas_proyecto', 'defecto', 'proyecto_empleado']
    
    print("--- Resetting PMO Flags ---")
    for table in tables:
        try:
            cursor.execute(f"UPDATE {table} SET metadata_extraccion = 0")
            print(f"Updated {table}")
        except Exception as e:
            print(f"Error updating {table}: {e}")
            
    conn.commit()
    conn.close()

if __name__ == '__main__':
    reset_flags()
