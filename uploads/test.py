import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_btc_1min_data(start_date, end_date):
    print(f"Fetching data from {start_date} to {end_date}")
    try:
        df = yf.download(
            tickers='BTC-USD',
            interval='1m',
            start=start_date,
            end=end_date,
            progress=False
        )
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        print(f"Failed to fetch data from {start_date} to {end_date}: {e}")
        return pd.DataFrame()

def main():
    now = datetime.utcnow()
    one_month_ago = now - timedelta(days=30)

    current = one_month_ago
    delta = timedelta(days=7)  # Yahoo allows max 7 days per 1m interval fetch
    all_data = []

    while current < now:
        chunk_end = min(current + delta, now)
        df_chunk = fetch_btc_1min_data(current.strftime('%Y-%m-%d'), chunk_end.strftime('%Y-%m-%d'))

        if not df_chunk.empty:
            all_data.append(df_chunk)

        current = chunk_end

    if all_data:
        full_df = pd.concat(all_data)

        # Flatten MultiIndex columns
        full_df.columns = [col[0] if isinstance(col, tuple) else col for col in full_df.columns]

        # Ensure Datetime column is in proper datetime format
        full_df['Datetime'] = pd.to_datetime(full_df['Datetime'])

        # Drop duplicates based on 'Datetime' if it exists
        if 'Datetime' in full_df.columns:
            full_df.drop_duplicates(subset=['Datetime'], inplace=True)
        else:
            print("Datetime column still missing! Skipping duplicates removal.")

        full_df.sort_values(by='Datetime', inplace=True)

        # Save data to CSV
        full_df.to_csv('btc_1min_last_month.csv', index=False)
        print("Data saved to btc_1min_last_month.csv")
        print(f"Total rows: {len(full_df)}")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()
