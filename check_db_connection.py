import mysql.connector
from mysql.connector import Error

def check_connection(name, config):
    print(f"Checking connection to {name}...")
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            db_info = conn.get_server_info()
            print(f"✅ Connected to {name} MySQL Server version {db_info}")
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"You're connected to database: {record[0]}")
            conn.close()
            return True
    except Error as e:
        print(f"❌ Error connecting to {name}: {e}")
        return False

if __name__ == "__main__":
    pmo_config = {
        'host': 'yamabiko.proxy.rlwy.net',
        'port': 27081,
        'user': 'root',
        'password': 'uwlMQNkutAeSqNGduCudtUJQoyhPlhcU',
        'database': 'railway'
    }

    ssd_config = {
        'host': 'shinkansen.proxy.rlwy.net',
        'port': 57709,
        'user': 'root',
        'password': 'cRUltTthzitfncdZCrMTwHAHjbrGMHQk',
        'database': 'railway'
    }

    pmo_ok = check_connection("PMO (Source)", pmo_config)
    ssd_ok = check_connection("SSD (Target)", ssd_config)
    
    if not (pmo_ok and ssd_ok):
        exit(1)
