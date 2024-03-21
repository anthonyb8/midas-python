import unittest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock, patch
from pandas.testing import assert_frame_equal

from midas.strategies import BaseStrategy
from midas.performance.statistics import PerformanceStatistics

from research.data import DataProcessing
from research.report.html_report import HTMLReportGenerator
from research.backtester.backtester import VectorizedBacktest
from research.strategies.cointegrationzscore import Cointegrationzscore

# TODO : edge cases /integration

class TestVectorizedBacktest(unittest.TestCase):
    def setUp(self):
        # Mock the necessary components
        self.mock_strategy = MagicMock(spec=BaseStrategy)
        self.mock_report_generator = MagicMock(spec=HTMLReportGenerator)
        self.mock_data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        
        # Initialize the VectorizedBacktest instance
        self.vectorized_backtest = VectorizedBacktest(
            full_data=self.mock_data,
            strategy=self.mock_strategy,
            report_generator=self.mock_report_generator,
            initial_capital=10000
        )
    
    # Basic Validation
    def test_setup(self):
        # Setup should call strategy.prepare if exists
        self.mock_strategy.prepare.return_value = '<p>Mock HTML Content</p>'
        
        self.vectorized_backtest.setup()
        
        # Verify prepare was called and report_generator.add_html was called with correct HTML content
        self.mock_strategy.prepare.assert_called_once_with(self.mock_data)
        self.mock_report_generator.add_html.assert_called_once_with('<p>Mock HTML Content</p>')
    
    def test_run_backtest_calls_generate_signals(self):
        self.vectorized_backtest._calculate_equity_curve = MagicMock()
        self.vectorized_backtest._calculate_metrics = MagicMock()

        # Test that generate_signals is called with provided thresholds
        entry_threshold = 0.5
        exit_threshold = 0.2
        self.vectorized_backtest.run_backtest(entry_threshold, exit_threshold)
        
        self.mock_strategy.generate_signals.assert_called_once_with(entry_threshold, exit_threshold)
    
    def test_run_backtest_calls_subsequent_methods(self):
        self.vectorized_backtest._calculate_equity_curve = MagicMock()
        self.vectorized_backtest._calculate_metrics = MagicMock()
        
        # Test that calculate_returns_and_equity and calculate_metrics are called
        entry_threshold = 0.5
        exit_threshold = 0.2
        self.vectorized_backtest.run_backtest(entry_threshold, exit_threshold)
        
        self.vectorized_backtest._calculate_equity_curve.assert_called_once()
        self.vectorized_backtest._calculate_metrics.assert_called_once()

    def test_run_backtest_with_thresholds(self):
        self.vectorized_backtest._calculate_equity_curve = MagicMock()
        self.vectorized_backtest._calculate_metrics = MagicMock()

        entry_threshold = 0.5
        exit_threshold = 0.2
        
        # Run the backtest with the specified thresholds
        self.vectorized_backtest.run_backtest(entry_threshold, exit_threshold)
        
        # Verify generate_signals was called with the correct thresholds
        self.mock_strategy.generate_signals.assert_called_once_with(entry_threshold, exit_threshold)
        
        # Verify that calculate_returns_and_equity and calculate_metrics are called
        self.vectorized_backtest._calculate_equity_curve.assert_called_once()
        self.vectorized_backtest._calculate_metrics.assert_called_once()
  
    def test_calculate_equity_curve(self):
        # Set up
        self.vectorized_backtest.backtest_data = pd.DataFrame({
            'timestamp': range(0, 10),  
            'A': [100, 101, 99, 102, 98, 103, 97, 104, 96, 105],
            'B': [200, 198, 202, 196, 204, 194, 206, 192, 208, 190],
            'A_position': [0, -1, 0, 1, 1, 0, 0, 1, 1, 0],
            'B_position': [0, 1, 0, -1, -1, 0, 0, -1, -1, 0]
        }).set_index('timestamp')

        # Expected
        expected_data = pd.DataFrame({
            'timestamp': range(0, 10),  
            'A': [100, 101, 99, 102, 98, 103, 97, 104, 96, 105],
            'B': [200, 198, 202, 196, 204, 194, 206, 192, 208, 190],
            'A_position': [0, -1, 0, 1, 1, 0, 0, 1, 1, 0],
            'B_position': [0, 1, 0, -1, -1, 0, 0, -1, -1, 0],
            'A_returns':[np.nan, 0.0100, -0.019802, 0.0303, -0.0392, 0.0510, -0.0582, 0.0721, -0.0769, 0.0937],
            'B_returns': [np.nan,-0.0100, 0.0202, -0.0297, 0.0408, -0.04902, 0.06185, -0.06796, 0.0833, -0.086538],
            'A_position_returns': [np.nan, 0.0, 0.0198, 0.0, -0.0392, 0.0510, 0.0, 0.0, -0.0769, 0.09375],
            'B_position_returns': [np.nan, 0.0, 0.0202, 0.0, -0.0408, 0.04902,0.0, 0.0, -0.08333, 0.0865 ],
            'aggregate_returns': [np.nan, 0.0, 0.0400,0.0, -0.0800, 0.1000, 0.0, 0.0, -0.1602, 0.18025],
            'equity_curve':[10000.0000, 10000.0000, 10400.0400, 10400.0400, 9567.7038, 10524.8571, 10524.8571, 10524.8571, 8838.1812, 10431.6034]
        }).set_index('timestamp')

        # test
        self.vectorized_backtest._calculate_equity_curve()

        # validate
        assert_frame_equal(self.vectorized_backtest.backtest_data, expected_data, check_dtype=False, check_like=True, rtol=1e-5, atol=1e-4)

    def test_calculate_metrics(self):
        # Set-Up
        self.vectorized_backtest.backtest_data = pd.DataFrame({
            'timestamp': range(0, 10),  
            'A': [100, 101, 99, 102, 98, 103, 97, 104, 96, 105],
            'B': [200, 198, 202, 196, 204, 194, 206, 192, 208, 190],
            'A_position': [0, -1, 0, 1, 1, 0, 0, 1, 1, 0],
            'B_position': [0, 1, 0, -1, -1, 0, 0, -1, -1, 0],
            'A_returns':[np.nan, 0.0100, -0.019802, 0.0303, -0.0392, 0.0510, -0.0582, 0.0721, -0.0769, 0.0937],
            'B_returns': [np.nan,-0.0100, 0.0202, -0.0297, 0.0408, -0.04902, 0.06185, -0.06796, 0.0833, -0.086538],
            'A_position_returns': [np.nan, 0.0, 0.0198, 0.0, -0.0392, 0.0510, 0.0, 0.0, -0.0769, 0.09375],
            'B_position_returns': [np.nan, 0.0, 0.0202, 0.0, -0.0408, 0.04902,0.0, 0.0, -0.08333, 0.0865 ],
            'aggregate_returns': [np.nan, 0.0, 0.0400,0.0, -0.0800, 0.1000, 0.0, 0.0, -0.1602, 0.18025],
            'equity_curve':[10000.0000, 10000.0000, 10400.0400, 10400.0400, 9567.7038, 10524.8571, 10524.8571, 10524.8571, 8838.1812, 10431.6034]
        }).set_index('timestamp')

        # Expected
        expected_data = pd.DataFrame({
            'timestamp': range(0, 10),  
            'A': [100, 101, 99, 102, 98, 103, 97, 104, 96, 105],
            'B': [200, 198, 202, 196, 204, 194, 206, 192, 208, 190],
            'A_position': [0, -1, 0, 1, 1, 0, 0, 1, 1, 0],
            'B_position': [0, 1, 0, -1, -1, 0, 0, -1, -1, 0],
            'A_returns': [0.0, 0.0100, -0.019802, 0.0303, -0.0392, 0.0510, -0.0582, 0.0721, -0.0769, 0.0937],
            'B_returns': [0.0, -0.0100, 0.0202, -0.0297, 0.0408, -0.04902, 0.06185, -0.06796, 0.0833, -0.086538],
            'A_position_returns': [0.0, 0.0, 0.0198, 0.0, -0.0392, 0.0510, 0.0, 0.0, -0.0769, 0.09375],
            'B_position_returns': [0.0, 0.0, 0.0202, 0.0, -0.0408, 0.04902,0.0, 0.0, -0.08333, 0.0865 ],
            'aggregate_returns': [0.0, 0.0, 0.0400,0.0, -0.0800, 0.1000, 0.0, 0.0, -0.1602, 0.18025],
            'equity_curve': [10000.0000, 10000.0000, 10400.0400, 10400.0400, 9567.7038, 10524.8571, 10524.8571, 10524.8571, 8838.1812, 10431.6034],
            'daily_return': [0.0000, 0.0000 , 0.0400, 0.0000 , -0.0800, 0.1000, 0.0000, 0.0000, -0.1603, 0.1803],
            'cumulative_return': [0.0000, 0.0000 , 0.0400, 0.0400 , -0.0432, 0.0525, 0.0525, 0.0525, -0.1162, 0.0432],
            'drawdown': [0.0000, 0.0000 , 0.0000, 0.0000 , -0.0800, 0.0000, 0.0000, 0.0000, -0.1603, -0.0089]
            }).set_index('timestamp')
        
        # test
        self.vectorized_backtest._calculate_metrics()

        # validate
        assert_frame_equal(self.vectorized_backtest.backtest_data, expected_data, check_dtype=False, check_like=True, rtol=1e-5, atol=1e-4)

    def test_calculate_sensitivity_analysis(self):
        # Set-Up
        entry_thresholds = [0.01, 0.02]
        exit_thresholds = [0.01, 0.02]
            
        self.vectorized_backtest.backtest_data = pd.DataFrame({
            'timestamp': range(0, 10),  
            'A': [100, 101, 99, 102, 98, 103, 97, 104, 96, 105],
            'B': [200, 198, 202, 196, 204, 194, 206, 192, 208, 190],
            'A_position': [0, -1, 0, 1, 1, 0, 0, 1, 1, 0],
            'B_position': [0, 1, 0, -1, -1, 0, 0, -1, -1, 0],
            'A_returns': [0.0, 0.0100, -0.019802, 0.0303, -0.0392, 0.0510, -0.0582, 0.0721, -0.0769, 0.0937],
            'B_returns': [0.0, -0.0100, 0.0202, -0.0297, 0.0408, -0.04902, 0.06185, -0.06796, 0.0833, -0.086538],
            'A_position_returns': [0.0, 0.0, 0.0198, 0.0, -0.0392, 0.0510, 0.0, 0.0, -0.0769, 0.09375],
            'B_position_returns': [0.0, 0.0, 0.0202, 0.0, -0.0408, 0.04902,0.0, 0.0, -0.08333, 0.0865 ],
            'aggregate_returns': [0.0, 0.0, 0.0400,0.0, -0.0800, 0.1000, 0.0, 0.0, -0.1602, 0.18025],
            'equity_curve': [10000.0000, 10000.0000, 10400.0400, 10400.0400, 9567.7038, 10524.8571, 10524.8571, 10524.8571, 8838.1812, 10431.6034],
            'daily_return': [0.0000, 0.0000 , 0.0400, 0.0000 , -0.0800, 0.1000, 0.0000, 0.0000, -0.1603, 0.1803],
            'cumulative_return': [0.0000, 0.0000 , 0.0400, 0.0400 , -0.0432, 0.0525, 0.0525, 0.0525, -0.1162, 0.0432],
            'drawdown': [0.0000, 0.0000 , 0.0000, 0.0000 , -0.0800, 0.0000, 0.0000, 0.0000, -0.1603, -0.0089]
            }).set_index('timestamp')
        
        # Expected
        expected_results = {
            'total_return': 0.0432, 
            'max_drawdown': -0.1603
        }

        # Test
        self.vectorized_backtest.run_backtest = MagicMock()
        actual_results = self.vectorized_backtest.sensitivity_analysis(entry_thresholds, exit_thresholds)

        # Validation
        self.mock_report_generator.add_table.assert_called()

        self.assertEqual(len(actual_results), len(entry_thresholds) * len(exit_thresholds))
        self.assertEqual(actual_results[(0.01, 0.01)], expected_results)
        self.assertEqual(actual_results[(0.02, 0.02)], expected_results)

    # Type
    def test_run_backtest_with_exception_in_generate_signals(self):
        # Configure the mock to raise an exception
        self.mock_strategy.generate_signals.side_effect = Exception("Mock error")
        with self.assertRaises(Exception):
            self.vectorized_backtest.run_backtest()

    # Edge Cases
    def test_setup_with_error(self):
        # Configure the mock strategy's prepare method to raise an exception
        self.mock_strategy.prepare.side_effect = Exception("Mock preparation error")
        
        # Verify that setup raises an Exception when strategy.prepare fails
        with self.assertRaises(Exception) as context:
            self.vectorized_backtest.setup()
            
        # Optionally, check the message of the exception
        self.assertTrue("Mock preparation error" in str(context.exception))
        
        # Verify that report_generator.add_html was not called since an exception occurred
        self.mock_report_generator.add_html.assert_not_called()

    def test_run_backtest_edge_cases(self):
        self.vectorized_backtest._calculate_equity_curve = MagicMock()
        self.vectorized_backtest._calculate_metrics = MagicMock()

        # Example edge case: very high thresholds
        self.vectorized_backtest.run_backtest(100, 100)
        self.mock_strategy.generate_signals.assert_called_once_with(100, 100)

        # Reset mock to test another edge case
        self.mock_strategy.generate_signals.reset_mock()
        # Example edge case: negative thresholds
        self.vectorized_backtest.run_backtest(-1, -1)
        self.mock_strategy.generate_signals.assert_called_once_with(-1, -1)

    # # # Integration 
    # # def backtest(self):
    # #     pass 

if __name__ =="__main__":
    unittest.main()
