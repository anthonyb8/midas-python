# client.py
import threading
import logging
from queue import Queue
from database import DatabaseClient

class DataClient(DatabaseClient):
    def __init__(self, api_key, api_url):
        super().__init__(api_key, api_url)
        
    def create_asset(self, symbol: str, asset_type: str):
        raise NotImplementedError("DataClient cannot create assets.")

    def create_price_data(self, price_data: dict):
        raise NotImplementedError("DataClient cannot create price data.")

    def create_bulk_price_data(self, bulk_data: list):
        raise NotImplementedError("DataClient cannot create bulk price data.")

    def create_backtest(self, data):
        raise NotImplementedError("DataClient cannot create backtests.")

