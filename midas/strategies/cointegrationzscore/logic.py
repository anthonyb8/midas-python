from typing import Dict
from queue import Queue
from datetime import datetime
import pandas as pd
import numpy as np
import logging
from enum import Enum, auto
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar
from ibapi.contract import Contract

from midas.events import TradeInstruction, OrderType, Action
from midas.strategies import BaseStrategy
from midas.symbols import Symbol
from midas.order_book import OrderBook
from midas.portfolio import PortfolioServer

from research.backtesting import HTMLReportGenerator
from research.data_analysis import DataProcessing, TimeseriesTests

def adjust_to_business_time(df, frequency='daily'):
    """
    Adjusts the DataFrame to the specified business time frequency: 'daily', 'hourly', or 'minute'.
    
    Parameters:
    - df: DataFrame to be adjusted.
    - frequency: The target frequency ('daily', 'hourly', or 'minute').
    
    Returns:
    - Adjusted DataFrame.
    """
    # Define the business day calendar
    us_business_day = CustomBusinessDay(calendar=USFederalHolidayCalendar())
    
    # Determine the start and end dates from the DataFrame
    start_date = df.index.min()
    end_date = df.index.max()
    
    # Generate the appropriate date range based on the specified frequency
    if frequency == 'daily':
        # Daily frequency, only business days
        target_range = pd.date_range(start_date, end_date, freq=us_business_day)
    elif frequency == 'hourly':
        # Generate hourly timestamps within business days
        business_days = pd.date_range(start_date, end_date, freq=us_business_day)
        target_range = pd.date_range(start_date, end_date, freq='H')
        target_range = target_range[target_range.date.isin(business_days.date)]
    elif frequency == 'minute':
        # Generate minute timestamps within business days, assuming 9:00 AM to 5:00 PM as business hours
        business_days = pd.date_range(start_date, end_date, freq=us_business_day)
        target_range = pd.date_range(start_date, end_date, freq='T')  # 1-minute frequency
        # Filter for business hours; adjust 'hour >= 9 & hour < 17' as needed for specific business hours
        target_range = target_range[(target_range.date.isin(business_days.date)) & (target_range.hour >= 9) & (target_range.hour < 17)]
    else:
        raise ValueError("Unsupported frequency specified. Choose 'daily', 'hourly', or 'minute'.")
    
    # Reindex the DataFrame to match the target range, forward-filling missing values
    adjusted_df = df.reindex(target_range).ffill()
    
    return adjusted_df

class Signal(Enum):
    """ Long and short are treated as entry actions and short/cover are treated as exit actions. """
    Overvalued = auto()
    Undervalued = auto()
    Exit_Overvalued = auto()
    Exit_Undervalued = auto()

class Cointegrationzscore(BaseStrategy):
    def __init__(self, symbols_map:Dict[str, Symbol], train_data:pd.DataFrame,portfolio_server: PortfolioServer, logger:logging.Logger, order_book:OrderBook,event_queue:Queue):
        super().__init__(order_book, event_queue)
        self.logger = logger
        self.portfolio_server = portfolio_server
        self.symbols_map = symbols_map
        self.trade_id = 1
        
        self.last_signal = None  # 0: no position, 1: long, -1: short
        self.historical_data = None
        self.current_zscore = None
        self.historical_zscore = []
        self.historical_spread = []
        self.cointegration_vector_dict = {}
        self.hedge_ratio = {}

        self.prepare(train_data)

    def reset(self):
        """
        Resets the strategy's state for a new test phase while preserving the training data spread.
        """
        self.last_signal = None
        self.trade_id = 1
        self.current_zscore = None

        # Establish histroccal values
        self.historic_spread(self.historical_data, self.cointegration_vector)
        self.historic_zscore()

    def prepare(self, train_data: pd.DataFrame, report_generator: HTMLReportGenerator=None):
        # train_data = adjust_to_business_time(train_data, frequency='daily')
        self.historical_data = train_data
        cointegration_vector = self.cointegration(train_data, report_generator)

        # Establish histroccal values
        self.historic_spread(train_data, cointegration_vector)
        self.historic_zscore()
        
        # Create hedge ratio dictionary
        symbols = train_data.columns.tolist()
        self.asset_allocation(symbols, cointegration_vector)
        
        self.data_validation()

    def cointegration(self,train_data:pd.DataFrame, report_generator: HTMLReportGenerator=None):
        # Determine Lag Length
        lag = TimeseriesTests.select_lag_length(data=train_data)
        
        # Check Cointegration Relationship
        johansen_results, num_cointegrations = TimeseriesTests.johansen_test(data=train_data, k_ar_diff=lag-1)
        
        #Create Cointegration Vector
        cointegration_vector = johansen_results['Cointegrating Vector'][0]
        
        if report_generator:
            report_generator.add_summary({'Ideal Lag': lag})
            html_content = TimeseriesTests.display_johansen_results(johansen_results, num_cointegrations, False, True)
            report_generator.add_html(html_content)  
            report_generator.add_summary({"Cointegration Vector" : cointegration_vector})
        else:
            self.logger.info(f"Ideal Lag : {lag}")
            self.logger.info(TimeseriesTests.display_johansen_results(johansen_results, num_cointegrations, False))
            self.logger.info(f"Cointegration Vector :{cointegration_vector}")

        return cointegration_vector

    def historic_spread(self, train_data: pd.DataFrame, cointegration_vector:list):
        new_spread = train_data.dot(cointegration_vector)
        self.historical_spread = new_spread.tolist()

    def update_spread(self, new_data: pd.DataFrame):
        # Convert the cointegration vector dictionary to a pandas Series
        cointegration_series = pd.Series(self.cointegration_vector_dict)

        # Ensure the new_data DataFrame is aligned with the cointegration vector
        aligned_new_data = new_data[cointegration_series.index]

        # Calculate the new spread value
        new_spread_value = aligned_new_data.dot(cointegration_series)
        
        # Append the new spread value to the historical spread list
        self.historical_spread.append(new_spread_value.item())

    def historic_zscore(self, lookback_period=None):
        self.historical_zscore = []

        for end_index in range(1, len(self.historical_spread) + 1):
            if lookback_period:
                start_index = max(0, end_index - lookback_period)
                spread_lookback = self.historical_spread[start_index:end_index]
            else:
                spread_lookback = self.historical_spread[:end_index]

            z_score = self.calculate_single_zscore(spread_lookback)
            self.historical_zscore.append(z_score)

    def calculate_single_zscore(self, spread_lookback):
        if len(spread_lookback) < 2:
            return 0
        mean = np.mean(spread_lookback)
        std = np.std(spread_lookback)
        return (spread_lookback[-1] - mean) / std if std != 0 else 0
    
    def update_zscore(self,lookback_period=None):
        # Determine the lookback range for the z-score calculation
        spread_lookback = self.historical_spread[-lookback_period:] if lookback_period else self.historical_spread

        # Calculate and append the new z-score
        self.current_zscore = self.calculate_single_zscore(spread_lookback)
        self.historical_zscore.append(self.current_zscore)

    def data_validation(self, report_generator: HTMLReportGenerator=None):
        # Test Stationarity in Spread
        adf_spread_results = TimeseriesTests.adf_test(self.historical_spread)
        pp_spread_results = TimeseriesTests.phillips_perron_test(self.historical_spread)

        # Test historical nature of spread w/ Hurst Exponent
        hurst_exponent_result = TimeseriesTests.hurst_exponent(self.historical_spread)
        
        # Test historical half-life (expected time to mean revert)
        spread_series = pd.Series(self.historical_spread)
        spread_lagged = DataProcessing.lag_series(spread_series)
        spread_combined = pd.DataFrame({'Original': spread_series, 'Lagged': spread_lagged}).dropna()
        half_life, residuals = TimeseriesTests.half_life(Y = spread_combined['Original'], Y_lagged = spread_combined['Lagged'])

        if report_generator:
            html_content = TimeseriesTests.display_adf_results({'spread': adf_spread_results}, False, True)
            report_generator.add_html(html_content)  
            
            html_content = TimeseriesTests.display_pp_results({'spread': pp_spread_results}, False, True)
            report_generator.add_html(html_content)  

            report_generator.add_summary({'Hurst Exponent': {hurst_exponent_result}})
            report_generator.add_summary({'Half-Life': {half_life}})
            report_generator.add_image(TimeseriesTests.plot_price_and_spread, price_data=self.historical_data, spread=pd.Series(self.historical_zscore), show_plot=False)

        else:
            # Log the results if no HTML report generator is provided
            self.logger.info(TimeseriesTests.display_adf_results({'spread': adf_spread_results}, False))
            self.logger.info(TimeseriesTests.display_pp_results({'spread': pp_spread_results}, False))
            self.logger.info(f"\nHurst Exponent: {hurst_exponent_result}")
            self.logger.info(f"\nHalf-Life: {half_life}")
            # TimeseriesTests.plot_price_and_spread(price_data=self.historical_data, spread=pd.Series(self.historical_zscore))
    
    def asset_allocation(self, symbols: list, cointegration_vector: np.array):
        """
        Create a dictionary of hedge ratios for each ticker.

        Parameters:
            symbols (list): List of ticker symbols.
            cointegration_vector (np.array): Array representing the cointegration vector (hedge ratios).

        Returns:
            dict: Dictionary with tickers as keys and hedge ratios as values.
        """

        self.cointegration_vector_dict = {symbol: ratio for symbol, ratio in zip(symbols, cointegration_vector)}

        # Normalize the cointegration vector
        normalized_cointegration_vector = cointegration_vector / np.sum(np.abs(cointegration_vector))

        # Ensure the length of the normalized cointegration vector matches the number of symbols
        if len(normalized_cointegration_vector) != len(symbols):
            raise ValueError("Length of normalized cointegration vector must match the number of symbols.")

        # Create a dictionary of symbols and corresponding normalized hedge ratios
        self.hedge_ratio = {symbol: ratio for symbol, ratio in zip(symbols, normalized_cointegration_vector)}

    def entry_signal(self, z_score: float, entry_threshold: float):
        if not any(ticker in self.portfolio_server.positions for ticker in self.symbols_map.keys()):
            if z_score > entry_threshold: # overvalued
                self.last_signal = Signal.Overvalued
                self.logger.info(f"Entry signal z_score : {z_score} // entry_threshold : {entry_threshold} // action : {self.last_signal}")
                return True
            elif z_score < -entry_threshold:
                self.last_signal = Signal.Undervalued
                self.logger.info(f"Entry signal z_score : {z_score} // entry_threshold : {entry_threshold} // action : {self.last_signal}")
                return True
        else:
            return False

    def exit_signal(self, z_score: float, exit_threshold: float):
        if any(ticker in self.portfolio_server.positions for ticker in self.symbols_map.keys()):
            if self.last_signal == Signal.Undervalued and z_score >= exit_threshold:
                self.last_signal = Signal.Exit_Undervalued
                self.logger.info(f"Exit signal z_score : {z_score} // entry_threshold : {exit_threshold} // action : {self.last_signal}")
                return True
            elif self.last_signal == Signal.Overvalued and z_score <= -exit_threshold:
                self.last_signal = Signal.Exit_Overvalued
                self.logger.info(f"Exit signal z_score : {z_score} // entry_threshold : {exit_threshold} // action : {self.last_signal}")
                return True
        else: 
            return False
    
    def generate_trade_instructions(self, signal: Signal):
        trade_instructions = []
        leg_id = 1

        for ticker, hedge_ratio in self.hedge_ratio.items():
            if signal in [Signal.Overvalued, Signal.Exit_Undervalued]:
                if hedge_ratio < 0:
                    action = Action.LONG if signal == Signal.Overvalued else Action.COVER
                    hedge_ratio *= -1
                elif hedge_ratio > 0:
                    action = Action.SHORT if signal == Signal.Overvalued else Action.SELL
                    hedge_ratio *= -1
            elif signal in [Signal.Undervalued, Signal.Exit_Overvalued]:
                if hedge_ratio > 0:
                    action = Action.LONG if signal == Signal.Undervalued else Action.COVER
                elif hedge_ratio < 0:
                    action = Action.SHORT if signal == Signal.Undervalued else Action.SELL
            
            trade_instructions.append(TradeInstruction(ticker=ticker, 
                                                       order_type=OrderType.MARKET, 
                                                       action=action,
                                                       trade_id= self.trade_id, 
                                                       leg_id=leg_id, 
                                                       weight=hedge_ratio))
            leg_id += 1
            
        return trade_instructions 
    
    def handle_market_data(self,data= None,entry_threshold: float=0.5, exit_threshold: float=0.0):
        trade_instructions = None
        # Get current_prices from order_book
        close_values = self.order_book.current_prices()
        print(close_values)
        data = pd.DataFrame([close_values])

        # Update features
        self.update_spread(data)
        self.update_zscore()

        if self.exit_signal(self.current_zscore, exit_threshold):
            trade_instructions = self.generate_trade_instructions(self.last_signal) 
            self.trade_id += 1
            self.last_signal = None
        elif self.entry_signal(self.current_zscore, entry_threshold):
            trade_instructions = self.generate_trade_instructions(self.last_signal)
        
        if trade_instructions:
            self.set_signal(trade_instructions,self.order_book.last_updated)
    
