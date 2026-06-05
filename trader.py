import sqlite3
import os
import pandas as pd
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

def execute_trades():
    load_dotenv()
    APCA_API_KEY_ID = os.environ.get('APCA_API_KEY_ID')
    APCA_API_SECRET_KEY = os.environ.get('APCA_API_SECRET_KEY')

    if not APCA_API_KEY_ID or not APCA_API_SECRET_KEY:
        print("API keys missing in .env. Halting execution.")
        return

    api = tradeapi.REST(base_url='https://paper-api.alpaca.markets')

    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            t1.ticker,
            t1.ai_thesis
        FROM ai_thesis t1
        INNER JOIN (
            SELECT
                ticker,
                MAX(timestamp) as max_timestamp
            FROM ai_thesis
            GROUP BY ticker
        ) t2 ON t1.ticker = t2.ticker AND t1.timestamp = t2.max_timestamp;
    """)
    latest_theses = cursor.fetchall()
    conn.close()

    if not latest_theses:
        print("No AI theses found to process.")
        return

    for ticker, thesis in latest_theses:
        if thesis == 'BUY':
            try:
                alpaca_symbol = ticker.replace('.NS', '')
                order = api.submit_order(
                    symbol=alpaca_symbol,
                    qty=1,
                    side='buy',
                    type='market',
                    time_in_force='gtc'
                )
                print(f"Submitted BUY order for {ticker}: {order.id}")
            except tradeapi.rest.APIError as e:
                print(f"Alpaca API Error for {ticker} (BUY): {e}")
            except Exception as e:
                print(f"An unexpected error occurred for {ticker} (BUY): {e}")
        elif thesis == 'SELL':
            print(f"Simulating SELL order for {ticker}")
        else:
            print(f"No action for {ticker} with thesis: {thesis}")

    print("PAPER TRADING EXECUTION COMPLETE")

if __name__ == '__main__':
    execute_trades()
