from queue import Queue
import pandas as pd
from typing import Dict

from midas.events import MarketEvent, BarData
from midas.symbols import Symbol
from midas.tools import DatabaseClient

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

    def get_data(self, symbols_map:Dict[str, Symbol], start_date: str, end_date: str, missing_values_strategy: str = 'fill_forward'):
        """
        Retrieves data from the database and initates the data processing. Stores initial data response in self.price_log.

        Args:
            symbols (List[str]) : A list of tickers ex. ['AAPL', 'MSFT']
            start_date (str) : Beginning date for the backtest ex. "2023-01-01"
            end_date (str) : End date for the backtest ex. "2024-01-01"
            missing_values_strategy (str): Strategy to handle missing values ('drop' or 'fill_forward'). Default is 'fill_forward'.
        """
        tickers = list(symbols_map.keys())
        response = self.data_client.get_bar_data(tickers=tickers, start_date=start_date, end_date=end_date)
        self.price_log = response

        # Process the data
        data = pd.DataFrame(response)

        # Handle missing values based on the specified strategy
        # if missing_values_strategy == 'drop':
        #     data.dropna(inplace=True)
        # elif missing_values_strategy == 'fill_forward':
        #     data.fillna(method='ffill', inplace=True)
        
        # # Extract contract details for mapping
        # contracts_map = {symbol: symbols_map[symbol].contract for symbol in symbols_map}
        # self.data['contract'] = self.data['symbol'].map(contracts_map)

        self.process_data(data, missing_values_strategy)

    def process_data(self, data:pd.DataFrame, missing_values_strategy: str = 'fill_forward'):
        """ Transform the data provide by the database into the needed format for the backtest. """
        # Convert the 'timestamp' column to datetime objects
        data['timestamp'] = pd.to_datetime(data['timestamp'])

        # Convert OHLCV columns to floats
        ohlcv_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in ohlcv_columns:
            data[col] = data[col].astype(float)


  
        data = data.pivot(index='timestamp', columns='symbol')
        
        # Handle missing values based on the specified strategy
        if missing_values_strategy == 'drop':
            data.dropna(inplace=True)
        elif missing_values_strategy == 'fill_forward':
            data.fillna(method='ffill', inplace=True)

        data = data.stack(level='symbol').reset_index()

        # Step 2: Rename columns to match the original format's naming conventions
        data.rename(columns={'level_1': 'symbol'}, inplace=True)

        # Optional: Sort by timestamp and symbol for better readability
        data.sort_values(by=['timestamp', 'symbol'], inplace=True)

        # Sorting the DataFrame by the 'timestamp' column in ascending order
        self.data = data.sort_values(by='timestamp', ascending=True).reset_index(drop=True)

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
            ticker = row['symbol']
            result_dict[ticker] = BarData.from_series(row) 

        self.event_queue.put(MarketEvent(result_dict))

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

        




