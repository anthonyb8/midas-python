import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from research.backtesting import BacktestLogger, FuturesBacktest, HTMLReportGenerator
from research.data_analysis import DataProcessing, TimeseriesTests
from research.strategies.cointegrationzscore.logic import Cointegrationzscore
from midas.symbols import Symbol, Equity, Future, Currency, Exchange
import logging


# Step 1 : Set data parameters
start_date = "2020-05-18"
end_date = "2024-02-07"

symbols = [
            Future(ticker="HE.n.0",currency=Currency.USD,exchange=Exchange.SMART, fees=0.85, lastTradeDateOrContractMonth="continuous",contractSize=50,tickSize=0.25, initialMargin=4564.17),
            Future(ticker="ZC.n.0",currency=Currency.USD,exchange=Exchange.CME,fees=0.85,lastTradeDateOrContractMonth="continuous",contractSize=50,tickSize=0.25, initialMargin=2056.75),
             Future(ticker="ZM.n.0",currency=Currency.USD,exchange=Exchange.CME,fees=0.85,lastTradeDateOrContractMonth="continuous",contractSize=50,tickSize=0.25, initialMargin=2056.75),
        ]

symbols_map = {symbol.ticker: symbol for symbol in symbols}


# Step 2 : Retrieve Data
data_processing = DataProcessing()
data = data_processing.get_data(list(symbols_map.keys()), start_date,end_date)


## Step 3 : Data preparation
# data = data.ffill()
data.dropna(inplace=True)
data_processing.check_missing(data)


## Step 4 : Walkforward Analysis
strategy_name = "cointegrationzscore"

# Instantiate the BacktestLogger
logger = BacktestLogger(strategy_name).logger

# Report Generator
report_generator = HTMLReportGenerator(strategy_name)

# Strategy
strategy = Cointegrationzscore(symbols_map,logger, report_generator)

# Backtest
backtest = FuturesBacktest(strategy, symbols_map, full_data=data, trade_allocation=0.20, logger=logger, report_generator=report_generator)

# Parameters to be sensitized 
entry_thresholds = np.arange(0.5, 1.5, 0.5)  # Example range for entry
exit_thresholds = np.arange(0.5, 2.5, 0.5)  # Example range for exit

# Walk forward-analysis
backtest.walk_forward_analysis(total_segments=1, entry_thresholds=entry_thresholds, exit_thresholds=[0.0])
report_generator.complete_report()
