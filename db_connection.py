import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'auto_dealer_pro',
    'charset': 'utf8mb4'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=False, commit=False):
    conn = get_db_connection()
    if not conn:
        return None if fetch else False
    cursor = conn.cursor(dictionary=True if fetch else None)
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        if commit:
            conn.commit()
            return cursor.lastrowid
    except Error as e:
        print(f"Query error: {e}\nQuery: {query}")
        if commit:
            conn.rollback()
        return None if fetch else False
    finally:
        cursor.close()
        conn.close()
    return True