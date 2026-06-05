import sqlite3
import pandas as pd

try:
    conn = sqlite3.connect('market_data.db')
    
    query = "SELECT ai_thesis FROM signals ORDER BY timestamp DESC LIMIT 1"
    
    df = pd.read_sql_query(query, conn)
    
    if not df.empty:
        thesis = df.iloc[0]['ai_thesis']
        print(f"EXECUTING BROKERAGE ORDER: {thesis}")
    else:
        print("No signals found in the database.")
        
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
