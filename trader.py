import sqlite3
import time
import random
import pandas as pd

class MockBrokerAPI:
    def place_order(self, ticker, side, qty):
        order_id = f"ORDER_{random.randint(10000, 99999)}"
        print(f"Simulating API: Routing {side} order for {qty} shares of {ticker}...")
        time.sleep(1) # Simulate network latency
        print(f"Simulating API: Order {order_id} placed successfully for {ticker} ({side} {qty})")
        return order_id

def execute_trades():
    conn = None
    try:
        conn = sqlite3.connect('market_data.db')
        cursor = conn.cursor()

        # Query the latest 3 rows from the signals table
        cursor.execute("SELECT timestamp, ticker, ai_thesis FROM signals ORDER BY timestamp DESC LIMIT 3")
        signals = cursor.fetchall()

        if not signals:
            print("No new signals to process.")
            return

        print(f"Processing {len(signals)} latest signals:")
        mock_broker = MockBrokerAPI()

        for timestamp, ticker, ai_thesis in signals:
            print(f"\nSignal: {ticker} at {timestamp} with thesis '{ai_thesis}'")
            if ai_thesis == 'BUY' or ai_thesis == 'SELL':
                print(f"Action: Placing a {ai_thesis} order for {ticker} (10 shares).")
                mock_broker.place_order(ticker, ai_thesis, 10)
            elif ai_thesis == 'HOLD' or ai_thesis == 'PENDING':
                print("Action: No trade action taken for HOLD/PENDING signal.")
            else:
                print(f"Action: Unknown signal '{ai_thesis}'. No trade action taken.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == '__main__':
    execute_trades()
