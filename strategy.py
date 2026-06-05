import sqlite3
import json
import pandas as pd

DB_NAME = 'market_data.db'

def run_strategy():
    with open('thresholds.json', 'r') as f:
        thresh = json.load(f)

    conn = sqlite3.connect(DB_NAME)
    
    try:
        signals_df = pd.read_sql_query("SELECT id, ticker, timestamp, rsi, volume FROM signals", conn)
    except pd.io.sql.DatabaseError:
        print('No signals.')
        conn.close()
        return

    if signals_df.empty:
        print('No signals.')
        conn.close()
        return

    signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])
    
    # Get only the latest signal for each ticker
    latest_signals = signals_df.sort_values(by=['ticker', 'timestamp']).groupby('ticker').tail(1)

    cursor = conn.cursor()

    for index, row in latest_signals.iterrows():
        thesis = 'HOLD'
        # Handle volume which might be stored as bytes
        # Try to convert to int, if it fails, it might be bytes
        try:
            volume_value = int(row['volume'])
        except ValueError:
            volume_value = int.from_bytes(row['volume'], 'little') # Assuming 'little' endian for SQLite BLOBs

        if float(row['rsi']) < thresh['rsi_buy'] and volume_value > thresh['volume_min']:
            thesis = 'BUY'
        elif float(row['rsi']) > thresh['rsi_sell']:
            thesis = 'SELL'
        
        cursor.execute("UPDATE signals SET ai_thesis = ? WHERE id = ?", (thesis, int(row['id'])))
    
    conn.commit()
    conn.close()
    print('ADVANCED STRATEGY EVALUATION COMPLETE')

if __name__ == '__main__':
    run_strategy()
