import requests
from typing import List, Dict
from queue import Queue
import pandas as pd


class DatabaseClient:
    def __init__(self, api_key : str , api_url: str ='http://127.0.0.1:8000'):
        self.api_url = api_url
        self.api_key = api_key

    def create_asset(self, symbol: str, asset_type: str):
        url = f"{self.api_url}/api/assets/assets/"
        data = {'symbol': symbol, 'type': asset_type}
        headers = {'Authorization': f'Token {self.api_key}'}
        response = requests.post(url, json=data, headers=headers)

        if response.status_code != 201:
            raise ValueError(f"Asset creation failed: {response.text}")
        return response.json()
    
    def get_asset_by_symbol(self, symbol: str):
        url = f"{self.api_url}/api/assets/assets/"
        params = {'symbol': symbol}
        headers = {'Authorization': f'Token {self.api_key}'}
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise ValueError(f"Failed to retrieve asset by symbol: {response.text}")
    
    def get_assets(self):
        url = f"{self.api_url}/api/assets/assets/"
        headers = {'Authorization': f'Token {self.api_key}'}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve assets: {response.text}")
        return response.json()
    
    def create_price_data(self, price_data: Dict):
        url = f"{self.api_url}/api/bar_data/equitybardata/"
        headers = {'Authorization': f'Token {self.api_key}'}
        response = requests.post(url, json=price_data, headers=headers)

        if response.status_code != 201:
            raise ValueError(f"Price data creation failed: {response.text}")
        return response.json()

    def create_bulk_price_data(self, bulk_data: List[Dict]):
        url = f"{self.api_url}/api/bar_data/equitybardata/bulk_create/"
        headers = {'Authorization': f'Token {self.api_key}'}
        response = requests.post(url, json=bulk_data, headers=headers)

        if response.status_code != 201:
            raise ValueError(f"Bulk price data creation failed: {response.text}")
        return response.json()
    
    def get_price_data(self, symbols: List[str], start_date: str = None, end_date: str = None):
        url = f"{self.api_url}/api/bar_data/equitybardata/"
        params = {'symbols': ','.join(symbols)}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        headers = {'Authorization': f'Token {self.api_key}'}
        response = requests.get(url, params=params, headers=headers)

        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve price data: {response.text}")
        return response.json()
    
    def create_backtest(self, data):
        """
        Create a new backtest.
        :param data: Dictionary containing backtest data.
        :return: Response from the API.
        """
        url = f"{self.api_url}/backtest/"
        headers = {'Authorization': f'Token {self.api_key}'}
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 201:
            raise ValueError(f"Backtest creation failed: {response.text}")
        return response.json()

    def get_backtests(self):
        """
        Retrieve all backtests.
        :return: List of backtests.
        """
        url = f"{self.api_url}/backtest/"
        headers = {'Authorization': f'Token {self.api_key}'}
        response = requests.get(url, headers = {'Authorization': f'Token {self.api_key}'})

        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve backtests: {response.text}")
        return response.json()

    def get_specific_backtest(self, backtest_id):
        """
        Retrieve a specific backtest by ID.
        :param backtest_id: ID of the backtest to retrieve.
        :return: Backtest data.
        """
        url = f"{self.api_url}/backtest/{backtest_id}/"
        headers = {'Authorization': f'Token {self.api_key}'}
        response = requests.get(url, headers)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve backtest: {response.text}")
        return response.json()

   