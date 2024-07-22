import pandas as pd
from time import sleep
from pandas.tseries.offsets import MonthEnd
from sqlalchemy import inspect
from binance.client import Client
from binance.exceptions import BinanceAPIException

class DataFetcher:

    # def __init__(self, db_connection):
    #     self.client = Client()
    #     self.engine = db_connection.get_engine()

    def __init__(self, db_connection):
        try:
            self.client = Client()
        except BinanceAPIException as e:
            self.client = None
            # raise Exception(f"Error initializing Binance Client, please connect from outside the United States. You will not be able to download data from Binance")
        self.engine = db_connection.get_engine()

    def get_data(self, symbol, start):
        end = str(pd.to_datetime(start) + MonthEnd(0))
        frame = pd.DataFrame(self.client.get_historical_klines(symbol, '5m', start, end))

        frame = frame.iloc[:, :6]
        frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        frame.set_index('Time', inplace=True)
        frame.index = pd.to_datetime(frame.index, unit='ms')
        frame = frame.astype(float)
        return frame

    def get_summary_statistics(self):
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        summary = []

        for table in tables:
            query = f"SELECT MIN(Time) as start_date, MAX(Time) as end_date, COUNT(*) as num_rows FROM {table}"
            result = pd.read_sql_query(query, self.engine)
            summary.append({
                "Table": table,
                "Start Date": result["start_date"].iloc[0],
                "End Date": result["end_date"].iloc[0],
                "Number of Rows": result["num_rows"].iloc[0]
            })
        
        return pd.DataFrame(summary)

    def fetch_and_store_data(self, coins, date_range):
        for coin in coins:
            for date in date_range:
                print(f'Processing {date.month_name()} for {coin}...')
                df = self.get_data(coin, str(date))
                df.to_sql(coin, self.engine, if_exists='append', index=True)
                sleep(60)  # Respect rate limits and avoid API overload
            print(f'Finished {coin}')
