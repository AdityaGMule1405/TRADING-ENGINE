import sqlite3
import pandas as pd
import ta
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier

def run_strategy():
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()

    # Read the signals table and get the latest row per ticker
    signals_df = pd.read_sql_query("SELECT id, ticker FROM signals ORDER BY timestamp DESC", conn)
    latest_signals = signals_df.groupby('ticker').first().reset_index()

    for index, row in latest_signals.iterrows():
        ticker = row['ticker']
        signal_id = row['id']

        print(f"Processing {ticker} for ML prediction...")

        try:
            # Download 2 years of daily data
            data = yf.download(ticker, period='2y', interval='1d')
            if data.empty:
                print(f"No data downloaded for {ticker}. Skipping.")
                continue

            # Calculate 14-day RSI - Apply .squeeze() here
            data['RSI'] = ta.momentum.RSIIndicator(close=data['Close'].squeeze(), window=14).rsi()
            # Use Volume directly
            data['Volume'] = data['Volume']

            # Create 'Target' column: 1 if tomorrow's Close > today's Close, else 0
            data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)

            # Drop rows with NaN values (from RSI calculation and last row of Target)
            data.dropna(inplace=True)

            if data.empty:
                print(f"Insufficient data after dropping NaNs for {ticker}. Skipping.")
                continue

            # Prepare features and target
            features = ['RSI', 'Volume']
            X = data[features]
            y = data['Target']

            # Train RandomForestClassifier
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            model.fit(X, y)

            # Get the latest RSI and Volume from the downloaded data for prediction
            # This corresponds to the last complete row in the dataset after dropping NaNs
            latest_features = X.iloc[[-1]] 

            # Predict the outcome for the latest data
            prediction = model.predict(latest_features)[0]

            thesis = 'BUY' if prediction == 1 else 'SELL'
            
            # Update the signals table
            cursor.execute("UPDATE signals SET ai_thesis = ? WHERE id = ?", (thesis, signal_id))
            print(f"Updated signal_id {signal_id} for {ticker} with AI Thesis: {thesis}")

        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            conn.rollback() # Rollback changes if an error occurs for this ticker
            continue # Continue to the next ticker even if one fails

    conn.commit()
    conn.close()
    print('ML STRATEGY EVALUATION COMPLETE')

if __name__ == '__main__':
    run_strategy()
