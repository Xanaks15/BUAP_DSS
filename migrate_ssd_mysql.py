import mysql.connector
import re

# Configuration
DB_CONFIG = {
    'host': 'shinkansen.proxy.rlwy.net',
    'port': 57709,
    'user': 'root',
    'password': 'cRUltTthzitfncdZCrMTwHAHjbrGMHQk',
    'database': 'railway'
}

SQL_FILE = 'create_ssd_db.sql'

def execute_sql_script(cursor, script_path):
    print(f"Executing SQL script: {script_path}")
    with open(script_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Adapt for MySQL
    # 1. Remove CREATE DATABASE / USE
    # 2. Replace AUTOINCREMENT with AUTO_INCREMENT
    # 3. Ensure INT PRIMARY KEY works (it does)
    
    sql = sql.replace('AUTOINCREMENT', 'AUTO_INCREMENT')
    
    statements = sql.split(';')
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt: continue
        if stmt.upper().startswith('CREATE DATABASE') or stmt.upper().startswith('USE'):
            continue
            
        try:
            cursor.execute(stmt)
        except mysql.connector.Error as err:
            print(f"Error executing statement: {stmt[:50]}... -> {err}")

def main():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("Connected to SSD MySQL.")
            cursor = conn.cursor()
            
            # Create Schema
            execute_sql_script(cursor, SQL_FILE)
            
            conn.close()
            print("SSD Migration Successful.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    main()
