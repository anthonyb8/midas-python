from queue import Queue
from utilities.database import DatabaseClient
from typing import List
from queue import Queue
import pandas as pd
from core.base.data import BarData
from core.base.events import MarketDataEvent

class DataClient(DatabaseClient):
    def __init__(self, event_queue: Queue, data_client: DatabaseClient):
        """
        Class constructor.

        Args:
            event_queue (Queue) : The main event queue, new MarketDataEvents are added to this queue.
            data_client (DatabaseClient) : Responsible for interacting with the database to pull the data via a client class based on a Django Rest-Framework API.
        
        """
        self.event_queue = event_queue
        self.data_client = data_client
        self.price_log = None
        
        # Data 
        self.data = None
        self.unique_dates = None
        self.next_date = None
        self.current_date_index = -1

    def get_data(self, symbols_map: List[str], start_date: str, end_date: str):
        """
        Retrieves data from the database and initates the data processing. Stores initial data response in self.price_log.

        Args:
            symbols (List[str]) : A list of tickers ex. ['AAPL', 'MSFT']
            start_date (str) : Beginning date for the backtest ex. "2023-01-01"
            end_date (str) : End date for the backtest ex. "2024-01-01"
        """
        symbols = list(symbols_map.keys())
        response = self.data_client.get_price_data(symbols, start_date, end_date)
        self.price_log = response

        # Process the data
        self.data = pd.DataFrame(response)
        self.data['contract'] = self.data['symbol'].map(symbols_map)

        self.process_data()

    def process_data(self):
        """ Transform the data provide by the database into the needed format for the backtest. """
        # Convert the 'timestamp' column to datetime objects
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])

        # Convert OHLCV columns to floats
        ohlcv_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in ohlcv_columns:
            self.data[col] = self.data[col].astype(float)

        # Sorting the DataFrame by the 'timestamp' column in ascending order
        self.data = self.data.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
        
        # Storing unique dates if needed
        self.unique_dates = self.data['timestamp'].unique().tolist()


    def get_latest_data(self):
        """ Return the next most recent bar data for all symbols. """
        return self.data[self.data['timestamp'] == self.next_date]

    def set_market_data(self):
        """
        Sets the MarketDataEvent into the main event queue.
        """
        latest_data_batch = self.get_latest_data()
        result_dict = {}
        for idx, row in latest_data_batch.iterrows():
            contract = row['contract']
            result_dict[contract] = BarData.from_series(row) 

        self.event_queue.put(MarketDataEvent(result_dict))

    def data_stream(self):
        """
        Simulates a market data listener, iterates through the unique dates, callign the setMarketData for each date until finished.
        """
        self.current_date_index += 1

        if self.current_date_index >= len(self.unique_dates):
            return False  # No more unique dates
            
        # Update the next_date here
        self.next_date = self.unique_dates[self.current_date_index]
        self.set_market_data()
        return True

    def get_last_bar(self):
        last_bar = self.data[self.data['timestamp'] == self.next_date]

        result_dict = {}
        for idx, row in last_bar.iterrows():
            symbol = row['symbol']
            result_dict[symbol] = BarData.from_series(row) 

        return MarketDataEvent(result_dict)
        




