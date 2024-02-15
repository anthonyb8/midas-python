from midas.events import BarData,TickData, MarketDataType, MarketEvent, MarketData
from typing import Dict, Union
from datetime import datetime

class OrderBook:
    def __init__(self, data_type:MarketDataType):
        # Each ticker will now have an additional 'last_updated' key to store the timestamp
        self.book : Dict[str,Union[BarData, TickData]] = {} # Example: {ticker : {'data': {Ask:{}, Bid:{}}, 'last_updated': timestamp}, ...}
        self.last_updated = None
        self.data_type = data_type

    def on_market_data(self, event: MarketEvent):
        """
        Handle new market data events.

        Parameters:
            event (MarketDataEvent): The market data event to handle.
        """
        timestamp = event.timestamp
        data = event.data
        self.handle_market_data(data, timestamp)

    def handle_market_data(self, data: Union[BarData, TickData], timestamp: str):
        """
        Process market data and generate trading signals.

        Parameters:
            data (Dict): The market data.
            timestamp (str): The timestamp of the data.
        """
        for ticker in data:
            self.insert(ticker, data[ticker], timestamp)

        self.last_updated = timestamp
        
    def insert(self, ticker, data: MarketData, timestamp: str):
        """
        Insert or update the data for a ticker along with the timestamp.

        Parameters:
            ticker (str): The ticker symbol.
            data (dict): The data to be stored for the ticker.
            timestamp (str): The timestamp when the data was received.
        """
        # Update or add the ticker data along with the last updated timestamp
        self.book[ticker] = data

    def current_price(self, ticker: str):
        if ticker in self.book:
            data = self.book[ticker]
            if self.data_type.value == MarketDataType.BAR.value:
                # Assuming 'Close' price is relevant for BAR data
                return data.CLOSE
            elif self.data_type.value == MarketDataType.TICK.value:
                # Assuming 'Last' price is relevant for TICK data, or choose another relevant key
                return data.Last
        else:
            return None  # Ticker not found

    def current_prices(self) -> dict:
        prices = {}
        for key, data in self.book.items():
            if self.data_type.value == MarketDataType.BAR.value:
                prices[key] = data.CLOSE
            elif self.data_type.value == MarketDataType.TICK.value:
                prices[key] = data.Last
        return prices
        
    def modify(self):
        # Changing an old bar or order in the book
        pass
    def cancellation(self):
        pass
        # remove a cancelled order from the book
    def retrieval(self):
        pass
        # makes for a fast access of a the current best price for a given symbol