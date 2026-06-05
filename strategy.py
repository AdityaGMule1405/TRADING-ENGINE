import sqlite3, json, pandas as pd

DB_NAME = 'market_data.db'

def run_strategy():
    try:
        with open('thresholds.json', 'r') as f:
            thresh = json.load(f)
    except FileNotFoundError:
        print("Error: 'thresholds.json' not found. Please create it first.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    df = pd.read_sql_query("SELECT id, ticker, timestamp, rsi, ai_thesis FROM signals", conn)

    if df.empty:
        print('No signals found to evaluate.')
        conn.close()
        return

    # Sort by ticker and timestamp to ensure correct tail(1) for each group
    df_sorted = df.sort_values(by=['ticker', 'timestamp'])
    
    # Get the latest signal for each ticker
    latest_signals = df_sorted.groupby('ticker').tail(1)

    for index, row in latest_signals.iterrows():
        thesis = 'HOLD'
        if float(row['rsi']) < thresh['rsi_buy']:
            thesis = 'BUY'
        elif float(row['rsi']) > thresh['rsi_sell']:
            thesis = 'SELL'
        
        cursor.execute("UPDATE signals SET ai_thesis = ? WHERE id = ?", (thesis, int(row['id'])))
    
    conn.commit()
    conn.close()
    print('STRATEGY EVALUATION COMPLETE')

if __name__ == '__main__':
    run_strategy()
