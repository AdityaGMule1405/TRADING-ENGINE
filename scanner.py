import yfinance as yf
import pandas as pd
import ta
import sqlite3
from datetime import datetime

DB_NAME = 'market_data.db'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def insert_signal(timestamp, ticker, rsi, volume, ai_thesis):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO signals (timestamp, ticker, rsi, volume, ai_thesis)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, ticker, rsi, volume, ai_thesis))
            conn.commit()
            print(f"Inserted signal for {ticker}: RSI={rsi}, Volume={volume}")
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()

def run_scanner():
    tickers = ['RELIANCE.NS', 'TATAPOWER.NS', 'ICICIBANK.NS']
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        try:
            data = yf.download(ticker, period="1mo", interval="1d")
            
            if data.empty:
                print(f"No data downloaded for {ticker}. Skipping.")
                continue

            # Ensure 'Close' column is a Series before passing to ta
            close_series = pd.Series(data['Close'])
            
            # Calculate RSI
            data['RSI'] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
            
            # Drop rows with NaN RSI values which appear at the beginning
            data.dropna(subset=['RSI'], inplace=True)

            if data.empty:
                print(f"Not enough data to calculate RSI for {ticker}. Skipping.")
                continue

            # Get latest RSI and Volume
            latest_rsi = data['RSI'].iloc[-1]
            latest_volume = data['Volume'].iloc[-1]
            
            # Get current timestamp
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insert into signals table
            insert_signal(current_timestamp, ticker, latest_rsi, latest_volume, 'PENDING')

        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            
    print("SCANNER FULLY COMPLETE")

if __name__ == '__main__':
    run_scanner()
