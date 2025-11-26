import sqlite3
import os

DB_PATH = 'ssd_db.sqlite'

def create_ssd_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    with open('create_ssd_db.sql', 'r') as f:
        sql_script = f.read()
        
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("SSD Database created successfully.")

if __name__ == '__main__':
    create_ssd_db()
