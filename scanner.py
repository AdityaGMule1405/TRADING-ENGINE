import yfinance as yf
import pandas as pd
import ta
import sqlite3
import datetime

def run_scanner():
    tickers = ['RELIANCE.NS', 'TATAPOWER.NS', 'ICICIBANK.NS']
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()

    for ticker_symbol in tickers:
        try:
            data = yf.download(ticker_symbol, period='1mo')
            if data.empty:
                print(f"No data downloaded for {ticker_symbol}")
                continue

            close_prices = data['Close'].squeeze()
            volume = data['Volume'].squeeze()

            if not isinstance(close_prices, pd.Series):
                print(f"Close prices for {ticker_symbol} is not a Series. Type: {type(close_prices)}")
                continue

            rsi_series = ta.momentum.RSIIndicator(close=close_prices, window=14).rsi()

            latest_timestamp = data.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            latest_rsi = rsi_series.iloc[-1]
            latest_volume = volume.iloc[-1]

            cursor.execute("INSERT INTO signals (timestamp, ticker, rsi, volume, ai_thesis) VALUES (?, ?, ?, ?, ?)",
                           (latest_timestamp, ticker_symbol, latest_rsi, latest_volume, 'PENDING'))
            conn.commit()
            print(f"Inserted data for {ticker_symbol}")

        except Exception as e:
            print(f"Error processing {ticker_symbol}: {e}")

    conn.close()
    print("SCANNER FULLY COMPLETE")

if __name__ == '__main__':
    run_scanner()
