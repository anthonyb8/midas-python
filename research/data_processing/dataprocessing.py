import os
os.chdir('/Users/anthony/git-projects/midas')

from engine.utilities.database import DatabaseClient
from decouple import config
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay
from scipy.optimize import curve_fit


pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', 100)
pd.set_option('display.width', 1000) # Adjust the width of the display in characters
pd.set_option('display.max_rows', None)

DATABASE_KEY = config('MIDAS_API_KEY')
DATABASE_URL = config('MIDAS_URL')

database = DatabaseClient(DATABASE_KEY, DATABASE_URL)

class DataProcessing:
    def __init__(self) -> None:
        self.raw_data = None
        self.processed_data = None
        self.unique_dates = None

    # -- Data Retrieval -- 
    def get_data(self, symbols:list, start_date:str, end_date:str):
        """
        start_date = "2018-05-18"
        end_date = "2023-01-19"
        """
        response = database.get_price_data(symbols, start_date, end_date)
        self.raw_data = pd.DataFrame(response)

        self.process_data()
        
        return self.processed_data
        
    # -- Processing -- 
    def process_data(self):
        # Convert OHLCV columns to floats
        ohlcv_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in ohlcv_columns:
            self.raw_data[col] = self.raw_data[col].astype(float)

        # Sorting the DataFrame by the 'timestamp' column in ascending order
        self.raw_data = self.raw_data.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
        self.raw_data['timestamp'] = pd.to_datetime(self.raw_data['timestamp'])
        self.processed_data = self.raw_data.pivot(index='timestamp', columns='symbol', values='close')
        self.check_missing(self.processed_data)

        # Reindex the DataFrame using the custom business day frequency ** Sets to daily data **
        us_business_day = CustomBusinessDay(calendar=USFederalHolidayCalendar())
        self.processed_data = self.processed_data.reindex(pd.date_range(start=self.processed_data.index.min(), end=self.processed_data.index.max(), freq=us_business_day))

    @staticmethod   
    def lag_series(series:pd.Series,lag:int=1):
        """ Lags a pandas series by a given lag. Default lag = 1."""
        # Create a lagged version of the series
        series_lagged = series.shift(lag)

        # Remove NaN values (first 'lag' elements will be NaN due to lagging)
        # The indices of the original and lagged series will still align
        return series_lagged[lag:]

    # -- Checks -- 
    def check_duplicates(self,series:pd.Series):
        duplicate_dates = series.duplicated()
        if any(duplicate_dates):
            print("There are duplicate dates in the DataFrame.")
        else:
            print("No duplicate dates in the DataFrame.")

    def check_missing(self,data:pd.DataFrame):
        # Check for missing values
        missing_values = data[data.isna().any(axis=1)]
        if not missing_values.empty:
            print("There are missing values in the DataFrame:")
            print(missing_values)
        else:
            print("No missing values in the DataFrame.")

    # -- Plots -- 
    # Linear model
    def _linear_model(self, t, a, b):
        return a + b * t

    # Exponential model
    def _exponential_model(self, t, a, b):
        return a * np.exp(b * t)

    # Log-transformed exponential model
    def _log_exponential_model(self, t, log_a, b):
        return log_a + b * t

    # Function to fit models and compare
    def fit_and_compare(self, time, values):
        # Fit linear model
        params_linear, _ = curve_fit(self._linear_model, time, values)

        # Fit log-transformed exponential model
        log_values = np.log(values)
        params_log_exp, _ = curve_fit(self._log_exponential_model, time, log_values)

        # Compute residuals
        residuals_linear = values - self._linear_model(time, *params_linear)
        residuals_log_exp = log_values - self._log_exponential_model(time, *params_log_exp)

        # Plotting
        plt.figure(figsize=(12, 6))

        # Linear Fit
        plt.subplot(1, 2, 1)
        plt.plot(time, values, 'o', label="Data")
        plt.plot(time, self._linear_model(time, *params_linear), label="Linear Fit")
        plt.title("Linear Fit")
        plt.legend()

        # Log-Transformed Exponential Fit
        plt.subplot(1, 2, 2)
        plt.plot(time, values, 'o', label="Data")
        plt.plot(time, np.exp(self._log_exponential_model(time, *params_log_exp)), label="Exponential Fit")
        plt.title("Exponential Fit")
        plt.legend()

        plt.show()

        return residuals_linear, np.exp(residuals_log_exp) - values
