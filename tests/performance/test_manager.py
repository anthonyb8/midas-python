import unittest
from unittest.mock import Mock, patch
from contextlib import ExitStack
from ibapi.contract import Contract
from datetime import datetime, timezone
import pandas as pd
import numpy as np

from midas.performance.manager import Backtest, PerformanceManager
from midas.account_data import EquityDetails, ExecutionDetails
from midas.events import SignalEvent, Action
from midas.command.parameters import Parameters
from midas.events import MarketEvent, OrderEvent, SignalEvent, ExecutionEvent
from midas.events import MarketData, BarData, TickData, OrderType, Action, TradeInstruction, Trade

class TestBacktest(unittest.TestCase):    
    def setUp(self) -> None:
        self.mock_db_client = Mock()
        self.backtest = Backtest(self.mock_db_client)
        self.mock_parameters = {
            "strategy_name": "cointegrationzscore", 
            "capital": 100000, 
            "data_type": "BAR", 
            "strategy_allocation": 1.0, 
            "train_start": "2018-05-18", 
            "train_end": "2023-01-19", 
            "test_start": "2023-01-19", 
            "test_end": "2024-01-19", 
            "tickers": ["HE.n.0", "ZC.n.0"], 
            "benchmark": ["^GSPC"]
        }
        self.mock_static_stats = [{
            "total_return": 10.0,
            "total_trades": 5,
            "total_fees": 2.5
        }]
        self.mock_timeseries_stats =  [{
            "timestamp": "2023-12-09T12:00:00Z",
            "equity_value": 10000.0,
            "percent_drawdown": 9.9, 
            "cumulative_return": -0.09, 
            "daily_return": 79.9
        }]
        self.mock_trades =  [{
            "trade_id": 1, 
            "leg_id": 1, 
            "timestamp": "2023-01-03T00:00:00+0000", 
            "symbol": "AAPL", 
            "quantity": 4, 
            "price": 130.74, 
            "cost": -522.96, 
            "action": "BUY", 
            "fees": 0.0
        }]
        self.mock_signals =  [{
            "timestamp": "2023-01-03T00:00:00+0000", 
            "trade_instructions": [{
                "ticker": "AAPL", 
                "action": "BUY", 
                "trade_id": 1, 
                "leg_id": 1, 
                "weight": 0.05
            }, 
            {
                "ticker": "MSFT", 
                "action": "SELL", 
                "trade_id": 1, 
                "leg_id": 2, 
                "weight": 0.05
            }]
        }]

        self.backtest.parameters = self.mock_parameters
        self.backtest.static_stats = self.mock_static_stats
        self.backtest.timeseries_stats = self.mock_timeseries_stats
        self.backtest.trade_data = self.mock_trades
        self.backtest.signal_data = self.mock_signals

    # Basic Validation
    def test_to_dict_valid(self):
        backtest_dict = self.backtest.to_dict()

        self.assertEqual(backtest_dict['parameters'], self.mock_parameters)
        self.assertEqual(backtest_dict['static_stats'], self.mock_static_stats)
        self.assertEqual(backtest_dict['timeseries_stats'], self.mock_timeseries_stats)
        self.assertEqual(backtest_dict['signals'], self.mock_signals)
        self.assertEqual(backtest_dict['trades'], self.mock_trades)

    def test_save_successful(self):
        with ExitStack() as stack:
            mock_create_backtest = stack.enter_context(patch.object(self.mock_db_client,'create_backtest', return_value = 201))
            mock_print = stack.enter_context(patch('builtins.print'))
            
            self.backtest.save()
            mock_create_backtest.assert_called_once_with(self.backtest.to_dict())
            mock_print.assert_called_once_with("Backtest save successful.")

    def test_save_unsuccessful(self):
        response = 500
        with ExitStack() as stack:
            mock_create_backtest = stack.enter_context(patch.object(self.mock_db_client,'create_backtest', return_value = response))
            mock_print = stack.enter_context(patch('builtins.print'))
            
            self.backtest.save()
            mock_create_backtest.assert_called_once_with(self.backtest.to_dict())
            mock_print.assert_called_once_with(f"Backtest save failed with response code: {response}")

    def test_save_validation_exception(self):
        def create_backtest_error(self):
            raise ValueError
        
        self.backtest.parameters = ""
        
        with ExitStack() as stack:
            mock_create_backtest = stack.enter_context(patch.object(self.mock_db_client,'create_backtest', side_effect = create_backtest_error))
            with self.assertRaisesRegex(ValueError,f"Validation Error:" ):
                self.backtest.save()

    def test_validate_attributes_success(self):
        try:
            self.backtest.validate_attributes()
        except ValueError:
            self.fail("validate_attributes() raised ValueError unexpectedly!")

class TestPerformanceManager(unittest.TestCase):    
    def setUp(self) -> None:
        self.mock_db_client = Mock()
        self.mock_logger = Mock()
        self.mock_parameters = {


            "strategy_name": "cointegrationzscore", 
            "capital": 100000, 
            "data_type": "BAR", 
            "strategy_allocation": 1.0, 
            "train_start": "2018-05-18", 
            "train_end": "2023-01-19", 
            "test_start": "2023-01-19", 
            "test_end": "2024-01-19", 
            "tickers": ["HE.n.0", "ZC.n.0"], 
            "benchmark": ["^GSPC"]
        }

        self.performance_manager = PerformanceManager(self.mock_db_client, self.mock_logger, self.mock_parameters)

        # Valid Data
        self.mock_static_stats = [{
            "total_return": 10.0,
            "total_trades": 5,
            "total_fees": 2.5
        }]
        self.mock_timeseries_stats =  [{
            "timestamp": "2023-12-09T12:00:00Z",
            "equity_value": 10000.0,
            "percent_drawdown": 9.9, 
            "cumulative_return": -0.09, 
            "daily_return": 79.9
        }]
        self.mock_trades =  [{
            "trade_id": 1, 
            "leg_id": 1, 
            "timestamp": "2023-01-03T00:00:00+0000", 
            "symbol": "AAPL", 
            "quantity": 4, 
            "price": 130.74, 
            "cost": -522.96, 
            "action": "BUY", 
            "fees": 0.0
        }]
        self.mock_signals =  [{
            "timestamp": "2023-01-03T00:00:00+0000", 
            "trade_instructions": [{
                "ticker": "AAPL", 
                "action": "BUY", 
                "trade_id": 1, 
                "leg_id": 1, 
                "weight": 0.05
            }, 
            {
                "ticker": "MSFT", 
                "action": "SELL", 
                "trade_id": 1, 
                "leg_id": 2, 
                "weight": 0.05
            }]
        }]


    # Basic Validation
    def test_update_trades_new_trade_valid(self):        
        trade = ExecutionDetails(
                timestamp= 165000000,
                trade_id= 2,
                leg_id=2,
                symbol= 'HEJ4',
                quantity= round(-10,4),
                price= 50,
                cost= round(50 * -10, 2),
                action=  Action.SHORT.value,
                fees= 70 # because not actually a trade
        )

        self.performance_manager.update_trades(trade)
        self.assertEqual(self.performance_manager.trades[0], trade)
        self.mock_logger.info.assert_called_once()
    
    def test_update_trades_old_trade_valid(self):        
        trade = ExecutionDetails(
                timestamp= 165000000,
                trade_id= 2,
                leg_id=2,
                symbol= 'HEJ4',
                quantity= round(-10,4),
                price= 50,
                cost= round(50 * -10, 2),
                action=  Action.SHORT.value,
                fees= 70 # because not actually a trade
        )
        self.performance_manager.trades.append(trade)

        self.performance_manager.update_trades(trade)
        self.assertEqual(self.performance_manager.trades[0], trade)
        self.assertFalse(self.mock_logger.info.called)
    
    def test_output_account(self):
        trade = ExecutionDetails(
                timestamp= 165000000,
                trade_id= 2,
                leg_id=2,
                symbol= 'HEJ4',
                quantity= round(-10,4),
                price= 50,
                cost= round(50 * -10, 2),
                action=  Action.SHORT.value,
                fees= 70 # because not actually a trade
        )
        self.performance_manager.update_trades(trade)
        self.mock_logger.info.assert_called_once_with("\nTrades Updated: \n {'timestamp': '1975-03-25T17:20:00+00:00', 'trade_id': 2, 'leg_id': 2, 'symbol': 'HEJ4', 'quantity': -10, 'price': 50, 'cost': -500, 'action': 'SHORT', 'fees': 70} \n")

    def test_update_signals_valid(self):        
        self.valid_trade1 = TradeInstruction(ticker = 'AAPL',
                                                order_type = OrderType.MARKET,
                                                action = Action.LONG,
                                                trade_id = 2,
                                                leg_id =  5,
                                                weight = 0.5)
        self.valid_trade2 = TradeInstruction(ticker = 'TSLA',
                                                order_type = OrderType.MARKET,
                                                action = Action.LONG,
                                                trade_id = 2,
                                                leg_id =  6,
                                                weight = 0.5)
        self.valid_trade_instructions = [self.valid_trade1,self.valid_trade2]
                        
        signal_event = SignalEvent(1651500000, 10000,self.valid_trade_instructions)

        self.performance_manager.update_signals(signal_event)
        self.assertEqual(self.performance_manager.signals[0], signal_event.to_dict())
        self.mock_logger.info.assert_called_once()
    
    def test_output_signal(self):
        self.valid_trade1 = TradeInstruction(ticker = 'AAPL',
                                                order_type = OrderType.MARKET,
                                                action = Action.LONG,
                                                trade_id = 2,
                                                leg_id =  5,
                                                weight = 0.5)
        self.valid_trade2 = TradeInstruction(ticker = 'TSLA',
                                                order_type = OrderType.MARKET,
                                                action = Action.LONG,
                                                trade_id = 2,
                                                leg_id =  6,
                                                weight = 0.5)
        self.valid_trade_instructions = [self.valid_trade1,self.valid_trade2]
                        
        signal_event = SignalEvent(1651500000, 10000,self.valid_trade_instructions)
        
        self.performance_manager.update_signals(signal_event)
        self.mock_logger.info.assert_called_once_with("\nSignals Updated:  {'timestamp': '2022-05-02T14:00:00+00:00', 'trade_instructions': [{'ticker': 'AAPL', 'order_type': 'MKT', 'action': 'LONG', 'trade_id': 2, 'leg_id': 5, 'weight': 0.5}, {'ticker': 'TSLA', 'order_type': 'MKT', 'action': 'LONG', 'trade_id': 2, 'leg_id': 6, 'weight': 0.5}]} \n")

    def test_update_equity_new_valid(self):
        equity = EquityDetails(
                    timestamp= 165500000,
                    equity_value = 10000000.99
                )
        
        self.performance_manager.update_equity(equity)

        self.assertEqual(self.performance_manager.equity_value[0], equity)
        self.mock_logger.info.assert_called_once_with((f"\nEquity Updated: {equity}"))
    
    def test_update_equity_old_valid(self):
        equity = EquityDetails(
                    timestamp= 165500000,
                    equity_value = 10000000.99
                )
        self.performance_manager.equity_value.append(equity)

        self.performance_manager.update_equity(equity)
        self.assertEqual(len(self.performance_manager.equity_value), 1)
        self.assertFalse(self.mock_logger.info.called)

    def test_aggregate_trades(self):
        # Adjusted trades data to use ExecutionDetails format
        self.performance_manager.trades = [
            ExecutionDetails(timestamp=165500000, trade_id=1, leg_id=1, symbol='XYZ', quantity=10, price=10, cost=100, action=Action.LONG.value),
            ExecutionDetails(timestamp=165000001, trade_id=1, leg_id=2, symbol='XYZ', quantity=-10, price=15, cost=150, action=Action.SELL.value),
            ExecutionDetails(timestamp=165000002, trade_id=2, leg_id=1, symbol='HEJ4', quantity=-10, price=20, cost=500, action=Action.SHORT.value),
            ExecutionDetails(timestamp=165000003, trade_id=2, leg_id=2, symbol='HEJ4', quantity=10, price=18, cost=180, action=Action.COVER.value)
        ]

        # Call the method
        aggregated_df = self.performance_manager.aggregate_trades()

        # Check if the result is a DataFrame
        self.assertIsInstance(aggregated_df, pd.DataFrame, "Result should be a pandas DataFrame")
        
        # Check if the DataFrame is not empty
        self.assertFalse(aggregated_df.empty, "Resulting DataFrame should not be empty")

        # Validate the expected columns are present
        expected_columns = ['trade_id', 'start_date', 'end_date', 'entry_value', 'exit_value', 'net_gain/loss', 'gain/loss (%)']
        for column in expected_columns:
            self.assertIn(column, aggregated_df.columns, f"Column {column} is missing in the result")

        # Validate calculations for a specific trade_id
        trade_1 = aggregated_df[aggregated_df['trade_id'] == 1]
        self.assertEqual(trade_1.iloc[0]['entry_value'], 100, "Incorrect entry value for trade_id 1")
        self.assertEqual(trade_1.iloc[0]['exit_value'], 150, "Incorrect exit value for trade_id 1")
        self.assertEqual(trade_1.iloc[0]['net_gain/loss'], 50, "Incorrect net gain/loss for trade_id 1")
        self.assertEqual(trade_1.iloc[0]['gain/loss (%)'], 50, "Incorrect gain/loss percentage for trade_id 1")

    def test_total_trade_fees(self):
        trade1 = ExecutionDetails(
                timestamp= 165000000,
                trade_id= 2,
                leg_id=2,
                symbol= 'HEJ4',
                quantity= round(-10,4),
                price= 50,
                cost= round(50 * -10, 2),
                action=  Action.SHORT.value,
                fees= 70 # because not actually a trade
        )
        self.performance_manager.trades.append(trade1)

        trade2 = ExecutionDetails(
                timestamp= 165000000,
                trade_id= 2,
                leg_id=2,
                symbol= 'HEJ4',
                quantity= round(-10,4),
                price= 50,
                cost= round(50 * -10, 2),
                action=  Action.SHORT.value,
                fees= 700 # because not actually a trade
        )
        self.performance_manager.trades.append(trade2)

        result = self.performance_manager.total_trade_fees()
        self.assertEqual(result, 770)

    def test_calculate_return_and_drawdown(self):
        self.performance_manager.equity_value = [
            EquityDetails(timestamp=int(datetime(2022, 1, 1).replace(tzinfo=timezone.utc).timestamp()), equity_value=1000.0),
            EquityDetails(timestamp=int(datetime(2022, 1, 2).replace(tzinfo=timezone.utc).timestamp()), equity_value=1010.0),
            EquityDetails(timestamp=int(datetime(2022, 1, 3).replace(tzinfo=timezone.utc).timestamp()), equity_value=1005.0),
            EquityDetails(timestamp=int(datetime(2022, 1, 4).replace(tzinfo=timezone.utc).timestamp()), equity_value=1030.0),
        ]

        df = self.performance_manager.calculate_return_and_drawdown()

        # Check if the result is a DataFrame
        self.assertTrue(isinstance(df, pd.DataFrame), "Result should be a pandas DataFrame")
        
        # Check if the DataFrame is not empty
        self.assertFalse(df.empty, "Resulting DataFrame should not be empty")

        # Validate the expected columns are present
        expected_columns = ['equity_value', 'daily_return', 'cumulative_return', 'drawdown']
        for column in expected_columns:
            self.assertIn(column, df.columns, f"Column {column} is missing in the result")

        # Validate Daily Returns
        equity_value = [1000, 1010, 1005, 1030]
        expected_daily_returns = np.diff(equity_value) / equity_value[:-1]
        expected_daily_returns =  np.insert(expected_daily_returns, 0, 0)
        
        self.assertAlmostEqual(df.iloc[1]['daily_return'], expected_daily_returns[1])
        

        # Validat Cumulative Returns
        expected_cumulative_return = round((1030 - 1000) / 1000, 5)
        self.assertAlmostEqual(round(df.iloc[-1]['cumulative_return'],5), expected_cumulative_return, places=4,msg="Cumulative return calculation does not match expected value")

        # Test Drawdown
        equity_value = [1000, 1010, 1005, 1030]
        rolling_max = np.maximum.accumulate(equity_value)  # Calculate the rolling maximum
        expected_drawdowns = (equity_value - rolling_max) / rolling_max  # Calculate drawdowns in decimal format
        self.assertAlmostEqual(df['drawdown'].min(), expected_drawdowns.min(), places=4, msg="Drawdown calculation does not match expected value")

    def test_align_equity_and_benchmark_aligned_dates(self):
        self.equity_curve = [
            EquityDetails(timestamp=int(datetime(2022, 1, 1).replace(tzinfo=timezone.utc).timestamp()), equity_value=1000.0),
            EquityDetails(timestamp=int(datetime(2022, 1, 2).replace(tzinfo=timezone.utc).timestamp()), equity_value=1010.0),
            EquityDetails(timestamp=int(datetime(2022, 1, 3).replace(tzinfo=timezone.utc).timestamp()), equity_value=1005.0)
        ]

        self.benchmark_curve = [
            {'timestamp': '2022-01-01', 'close': 2000.0},
            {'timestamp': '2022-01-02', 'close': 2010.0},
            {'timestamp': '2022-01-03', 'close': 2005.0},
        ]

        equity_values_array, benchmark_close_array = self.performance_manager.align_equity_and_benchmark(self.equity_curve, self.benchmark_curve)
        
        # Validate the output types
        self.assertIsInstance(equity_values_array, np.ndarray, "Equity values should be a NumPy array")
        self.assertIsInstance(benchmark_close_array, np.ndarray, "Benchmark values should be a NumPy array")
        
        # Validate the lengths of the arrays
        self.assertEqual(len(equity_values_array), len(benchmark_close_array), "Arrays should have the same length")
        
        # Validate the data types of the arrays
        self.assertEqual(equity_values_array.dtype, np.float64, "Equity values array should be of type float64")
        self.assertEqual(benchmark_close_array.dtype, np.float64, "Benchmark values array should be of type float64")

    # def test_align_equity_and_benchmark_unaligned_dates(self):
    #     # Equity curve has an extra date not present in the benchmark curve and vice versa
    #     self.equity_curve = [
    #         {'timestamp': '2022-01-01', 'equity_value': 1000.0},
    #         {'timestamp': '2022-01-02', 'equity_value': 1010.0},
    #         {'timestamp': '2022-01-04', 'equity_value': 1020.0},  # Unaligned date
    #     ]
    #     self.benchmark_curve = [
    #         {'timestamp': '2022-01-01', 'close': 2000.0},
    #         {'timestamp': '2022-01-02', 'close': 2010.0},
    #         {'timestamp': '2022-01-03', 'close': 2020.0},  # Unaligned date
    #     ]

    #     # Expected to align on 2022-01-01 and 2022-01-02 only
    #     equity_values_array, benchmark_close_array = self.performance_manager.align_equity_and_benchmark(self.equity_curve, self.benchmark_curve)
        
    #     # Validate the lengths of the arrays (should be 2 for both, matching only the aligned dates)
    #     self.assertEqual(len(equity_values_array), 2, "Arrays should have the same length and match only aligned dates")
    #     self.assertEqual(len(benchmark_close_array), 2, "Arrays should have the same length and match only aligned dates")

    # def test_align_equity_and_benchmark_different_time_intervals(self):
    #     # Equity curve has multiple entries for the same day, simulating lower than daily interval
    #     self.equity_curve = [
    #         {'timestamp': '2022-01-01 09:00', 'equity_value': 1000.0},
    #         {'timestamp': '2022-01-01 17:00', 'equity_value': 1010.0},  # Same day, different time
    #         {'timestamp': '2022-01-02', 'equity_value': 1020.0},
    #     ]
    #     self.benchmark_curve = [
    #         {'timestamp': '2022-01-01', 'close': 2000.0},
    #         {'timestamp': '2022-01-02', 'close': 2010.0},
    #     ]

    #     # Expected to standardize on daily frequency, effectively aligning the last value of the day for equity
    #     equity_values_array, benchmark_close_array = self.performance_manager.align_equity_and_benchmark(self.equity_curve, self.benchmark_curve)
        
    #     # Validate the lengths of the arrays (should be 2 for both, after resampling equity to daily)
    #     self.assertEqual(len(equity_values_array), 2, "Arrays should have the same length after resampling equity to daily")
    #     self.assertEqual(len(benchmark_close_array), 2, "Arrays should have the same length after resampling equity to daily")

    # def test_calculate_statistics(self):
    #     pass

    # def test_create_backtest(self):
    #     pass

if __name__ == "__main__":
    unittest.main()