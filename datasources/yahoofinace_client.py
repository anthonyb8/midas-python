import yfinance as yf
import pandas as pd


class YahooClient:
    def __init__(self, symbols:list,period:str, interval:str):
        self.symbols = symbols
        self.period = period
        self.interval = interval
        self.data = None
        self.grouped_data = None

    def get_data(self):
        self.data = yf.download(tickers=self.symbols, period=self.period, interval=self.interval)

