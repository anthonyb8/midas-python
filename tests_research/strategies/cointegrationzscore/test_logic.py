import unittest
import numpy as np
import pandas as pd
from contextlib import ExitStack
from unittest.mock import patch, Mock

from research.strategies.cointegrationzscore.logic import Cointegrationzscore, Signal

# TODO: edge cases

class TestCointegrationzscore(unittest.TestCase):
    def setUp(self):
        # Create an instance of Cointegrationzscore
        self.strategy = Cointegrationzscore()
        # Sample historical data for testing
        self.historical_data = pd.DataFrame({
            'timestamp': range(1, 101),  # Simulate Unix timestamp
            'asset1': np.random.normal(0, 1, 100),
            'asset2': np.random.normal(0, 1, 100),
            
        }).set_index('timestamp')
    
    # Basic Validation
    @patch('research.analysis.timeseries.TimeseriesTests.select_lag_length')
    @patch('research.analysis.timeseries.TimeseriesTests.johansen_test')
    def test_cointegration(self, mock_johansen_test, mock_select_lag_length):
        # Create a mock DataFrame as train_data
        train_data = pd.DataFrame({'A': [1, 2, 3], 'B': [3, 2, 1]})

        # Mock responses
        mock_select_lag_length.return_value = 2
        mock_johansen_results = {'Cointegrating Vector': [np.array([1, -1])]}
        mock_johansen_test.return_value = (mock_johansen_results, 1)
        
        # Test
        results = self.strategy._cointegration(train_data=train_data)

        # Validation
        # Assertions to validate the returned results
        self.assertEqual(results['lag'], 2)
        self.assertEqual(results['num_cointegrations'], 1)
        self.assertEqual(results['johansen_results'], mock_johansen_results)
        self.assertTrue((results['cointegration_vector'] == np.array([1, -1])).all())

        # Verify that mock methods were called correctly
        mock_select_lag_length.assert_called_once_with(data=train_data)
        mock_johansen_test.assert_called_once_with(data=train_data, k_ar_diff=1)
        
    def test_historic_spread(self):
        # Mock training data and a cointegration vector
        train_data = pd.DataFrame({
            'A': [1, 2, 3, 4],
            'B': [4, 3, 2, 1]
        })
        cointegration_vector = np.array([1, -1])

        # Expected result
        expected_spread = [train_data['A'][i] - train_data['B'][i] for i in range(len(train_data))]

        # Test
        self.strategy._historic_spread(train_data, cointegration_vector)

        # Validation
        self.assertEqual(self.strategy.historical_spread, expected_spread)

    def test_historic_zscore_with_lookback(self):
        # Set up historical spread data
        self.strategy.historical_spread = [1, 2, 3, 4, 5, 6, 10, 8, 9, 10]
        lookback_period = 5

        # Expected result
        spread_series = pd.Series(self.strategy.historical_spread)
        mean = spread_series.rolling(window=lookback_period).mean()
        std = spread_series.rolling(window=lookback_period).std()
        zscores = ((spread_series - mean) / std).to_numpy()
        expected_zscores = zscores[~np.isnan(zscores)]

        # Test
        self.strategy._historic_zscore(lookback_period=lookback_period)
        actual = self.strategy.historical_zscore[~np.isnan(self.strategy.historical_zscore)] # drop nan for test 

        # Validation
        for calc_z, exp_z in zip(actual, expected_zscores):
            self.assertAlmostEqual(calc_z, exp_z, places=5)

    def test_historic_zscore_expanding(self):
        # Set up historical spread data for expanding window test
        self.strategy.historical_spread = [1, 2, 1, 4, 1, 6, 1, 8, 1, 10]
        lookback_period = None

        # Expected result
        spread_series = pd.Series(self.strategy.historical_spread)
        mean = spread_series.expanding().mean()
        std = spread_series.expanding().std()
        zscores = ((spread_series - mean) / std).to_numpy()
        expected_zscores = zscores[~np.isnan(zscores)]

        # Test
        self.strategy._historic_zscore(lookback_period=lookback_period)
        actual = self.strategy.historical_zscore[~np.isnan(self.strategy.historical_zscore)] # drop nan for test

        # Validation
        for calc_z, exp_z in zip(actual, expected_zscores):
            self.assertAlmostEqual(calc_z, exp_z, places=5)

    def test_asset_allocation(self):
        """Test asset allocation calculations."""
        cointegration_vector = np.array([1, -1])
        symbols = ['asset1', 'asset2']
        self.strategy._asset_allocation(symbols, cointegration_vector)
        self.assertIn('asset1', self.strategy.hedge_ratio)
        self.assertIn('asset2', self.strategy.hedge_ratio)
    
    @patch('research.analysis.timeseries.TimeseriesTests.adf_test')
    @patch('research.analysis.timeseries.TimeseriesTests.phillips_perron_test')
    @patch('research.analysis.timeseries.TimeseriesTests.hurst_exponent')
    @patch('research.analysis.timeseries.TimeseriesTests.lag_series')
    @patch('research.analysis.timeseries.TimeseriesTests.half_life')
    def test_data_validation(self, mock_half_life, mock_lag_series, mock_hurst, mock_pp, mock_adf):
        # Mock data
        self.strategy.historical_spread= pd.Series([1,2,3,4])
        
        # Mock responses
        mock_half_life_response = 30.9999
        mock_hurst_response = 0.499999
        mock_lag_series_response = pd.Series([np.nan, 1, 2, 3]) 
        mock_adf_response = {
            'ADF Statistic': -4.0,
            'p-value': 0.01,
            'Critical Values': {'5%': -3.5},
            'Stationarity': 'Stationary'
        }
        mock_pp_response = {
            'PP Statistic': -4.0,
            'p-value': 0.01,
            'Critical Values': {'5%': -3.5},
            'Stationarity': 'Stationary'
        }
        
        mock_adf.return_value = mock_adf_response
        mock_pp.return_value = mock_pp_response
        mock_lag_series.return_value = mock_lag_series_response
        mock_hurst.return_value = mock_hurst_response
        mock_half_life.return_value = (mock_half_life_response, [])

        # Expected result
        expected_result = {
            'adf_test': mock_adf_response,
            'pp_test': mock_pp_response,
            'hurst_exponent': mock_hurst_response,
            'half_life': mock_half_life_response, 
        }
        
        # Test
        result = self.strategy._data_validation()

        # Validation
        self.assertEqual(expected_result, result)
        mock_lag_series.assert_called_once()

    @patch('research.analysis.timeseries.TimeseriesTests.display_adf_results')
    @patch('research.analysis.timeseries.TimeseriesTests.display_pp_results')
    @patch('research.analysis.timeseries.TimeseriesTests.display_johansen_results')
    def test_prepare(self, mock_johansen_results, mock_pp_results, mock_adf_results):
        # Mock method responses
        with ExitStack() as stack:
            mock_cointegration = stack.enter_context(patch.object(self.strategy, '_cointegration'))
            mock_data_validation = stack.enter_context(patch.object(self.strategy, '_data_validation'))

            mock_cointegration.return_value = {
                'cointegration_vector': [1, -1],
                'lag': 5,
                'johansen_results': 'mock_johansen_results',
                'num_cointegrations': 1
            }
            
            mock_data_validation.return_value = {
                'adf_test': 'mock_adf_test',
                'pp_test': 'mock_pp_test',
                'hurst_exponent': 0.5,
                'half_life': 10
            }
            
            # Mock TimeseriesTests display functions to return strings for simplicity
            mock_johansen_results.return_value = "Johansen Results Content"
            mock_pp_results.return_value = "PP Test Results Content"
            mock_adf_results.return_value = "ADF Test Results Content"
            
            html_content = self.strategy.prepare(self.historical_data)

            # Check if HTML content contains expected strings
            self.assertIn("Ideal Lag : 5", html_content)
            self.assertIn("Johansen Results Content", html_content)
            self.assertIn("Cointegration Vector : [1, -1]", html_content)
            self.assertIn("ADF Test Results Content", html_content)
            self.assertIn("PP Test Results Content", html_content)
            self.assertIn("Hurst Exponent: 0.5", html_content)
            self.assertIn("Half-Life: 10", html_content)
            
            # Verify that necessary attributes were updated
            self.assertEqual(self.strategy.cointegration_vector, [1, -1])
            self.assertIsNotNone(self.strategy.historical_data)
            
    def test_entry_signal_overvalued(self):
        result = self.strategy._entry_signal(z_score=3.0, entry_threshold=2.0)
        self.assertTrue(result)
        self.assertEqual(self.strategy.last_signal, Signal.Overvalued)

    def test_entry_signal_undervalued(self):
        result = self.strategy._entry_signal(z_score=-3.0, entry_threshold=2.0)
        self.assertTrue(result)
        self.assertEqual(self.strategy.last_signal, Signal.Undervalued)

    def test_entry_signal_no_signal(self):
        result = self.strategy._entry_signal(z_score=1.0, entry_threshold=2.0)
        self.assertFalse(result)
        self.assertNotEqual(self.strategy.last_signal, Signal.Overvalued)
        self.assertNotEqual(self.strategy.last_signal, Signal.Undervalued)

    def test_exit_signal_from_undervalued(self):
        self.strategy.last_signal = Signal.Undervalued
        result = self.strategy._exit_signal(z_score=0.1, exit_threshold=0.05)
        self.assertTrue(result)
        self.assertEqual(self.strategy.last_signal, Signal.Exit_Undervalued)

    def test_exit_signal_from_overvalued(self):
        self.strategy.last_signal = Signal.Overvalued
        result = self.strategy._exit_signal(z_score=-0.1, exit_threshold=0.05)
        self.assertTrue(result)
        self.assertEqual(self.strategy.last_signal, Signal.Exit_Overvalued)

    def test_exit_signal_no_exit(self):
        self.strategy.last_signal = Signal.Overvalued
        result = self.strategy._exit_signal(z_score=-0.01, exit_threshold=0.05)
        self.assertFalse(result)
        self.assertNotEqual(self.strategy.last_signal, Signal.Exit_Overvalued)

    def test_generate_signals(self):
        # Mock hedge ratios
        self.strategy.hedge_ratio = {'A': 1, 'B': -1}

        # Mock data
        self.historical_data = pd.DataFrame({
            'timestamp': range(0, 10),  # Simulate Unix timestamp
            'A': [0, 1, -1, 1, -1, 1, -1, 1, -1, 1],
            'B': [0, -1, 1, -1, 1, -1, 1, -1, 1, -1],
            'spread': [ 0, 2 ,-2, 2, -2, 2, -2, 2, -2, 2],  
            'zscore' : [np.nan, 0.707107, -0.707107, -0.707107, -0.707107, 0.707107, 0, -0.707107, -0.707107, 0.707107]
        }).set_index('timestamp')

        self.strategy.historical_data = self.historical_data

        # Expected Data
        A_signals = [np.nan, -1.0, 0.0, 1.0, np.nan, 0.0, np.nan, 1.0, np.nan, 0.0]
        B_signals = [np.nan, 1.0, 0.0, -1.0, np.nan, 0.0, np.nan, -1.0, np.nan, 0.0]

        # Test
        entry_threshold = 0.5
        exit_threshold = 0
        self.strategy.generate_signals(entry_threshold, exit_threshold)

        # Validation
        for actual, expected in zip(self.strategy.historical_data[f'A_signal'].tolist(), A_signals):
            if np.isnan(actual) and np.isnan(expected):
                continue  # Both are NaNs, considered equal for this purpose
            else:
                self.assertEqual(actual, expected)

        for actual, expected in zip(self.strategy.historical_data[f'B_signal'].tolist(), B_signals):
            if np.isnan(actual) and np.isnan(expected):
                continue  # Both are NaNs, considered equal for this purpose
            else:
                self.assertEqual(actual, expected)

    def test_calculate_positions(self):
        # Mock hedge ratios
        self.strategy.hedge_ratio = {'A': 1, 'B': -1}

        # Mock data
        self.historical_data = pd.DataFrame({
            'timestamp': range(0, 10),  # Simulate Unix timestamp
            'A': [0, 1, -1, 1, -1, 1, -1, 1, -1, 1],
            'B': [0, -1, 1, -1, 1, -1, 1, -1, 1, -1],
            'spread': [ 0, 2 ,-2, 2, -2, 2, -2, 2, -2, 2],  
            'zscore' : [np.nan, 0.707107, -0.707107, -0.707107, -0.707107, 0.707107, 0, -0.707107, -0.707107, 0.707107],
            'A_signal' : [np.nan, -1, 0, 1, np.nan, 0, np.nan, 1, np.nan, 0], 
            'B_signal' : [np.nan, 1, 0, -1, np.nan, 0, np.nan, -1, np.nan, 0]
        }).set_index('timestamp')

        self.strategy.historical_data = self.historical_data

        # Expected data
        a_positions = [0, -1, 0, 1, 1, 0, 0, 1, 1, 0]
        b_positions = [0, 1, 0, -1, -1, 0, 0, -1, -1, 0]

        # Test
        self.strategy.calculate_positions()

        # Validation
        self.assertEqual(self.strategy.historical_data[f'A_position'].tolist(), a_positions)
        self.assertEqual(self.strategy.historical_data[f'B_position'].tolist(), b_positions)

if __name__ == '__main__':
    unittest.main()
