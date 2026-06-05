import sqlite3
import os

DB_NAME = 'market_data.db'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_signals_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    ticker TEXT,
                    rsi REAL,
                    volume INTEGER,
                    ai_thesis TEXT
                )
            """)
            conn.commit()
            print("Signals table checked/created successfully.")
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()

if __name__ == '__main__':
    create_signals_table()
