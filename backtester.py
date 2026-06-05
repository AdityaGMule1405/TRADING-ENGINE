import sqlite3
import pandas as pd

try:
    conn = sqlite3.connect('market_data.db')
    
    df = pd.read_sql_query("SELECT * FROM signals", conn)
    
    buy_count = df[df['ai_thesis'] == 'BUY'].shape[0]
    sell_count = df[df['ai_thesis'] == 'SELL'].shape[0]
    
    print("--- BACKTEST PERFORMANCE REPORT ---")
    print(f"Total BUY signals: {buy_count}")
    print(f"Total SELL signals: {sell_count}")
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
