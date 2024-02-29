import unittest
import random
from datetime import datetime

from midas.command import Parameters
from midas.events import MarketDataType
from midas.symbols import Equity, Future, Currency, Exchange, Symbol


#TODO: Edge cases

class TestParameters(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_strategy_name = "Testing"
        self.valid_capital = 1000000
        self.valid_data_type = random.choice([MarketDataType.BAR, MarketDataType.TICK])
        self.valid_missing_values_strategy = random.choice(['drop', 'fill_forward'])
        self.valid_strategy_allocation = 1.0
        self.valid_train_start = "2020-05-18"
        self.valid_train_end = "2023-12-31"
        self.valid_test_start = "2024-01-01"
        self.valid_test_end = "2024-01-19"
        self.valid_symbols = [
                Future(ticker="HE",data_ticker= "HE.n.0", currency=Currency.USD,exchange=Exchange.CME,fees=0.85, lastTradeDateOrContractMonth="202404",multiplier=40000,tickSize=0.00025, initialMargin=4564.17),
                Future(ticker="ZC",data_ticker= "ZC.n.0", currency=Currency.USD,exchange=Exchange.CBOT,fees=0.85,lastTradeDateOrContractMonth="202403",multiplier=5000,tickSize=0.0025, initialMargin=2056.75)
            ]
        self.valid_benchmark = ["^GSPC"]
        
    # Basic Validation
    def test_construction(self):
        params = Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
                            
        self.assertEqual(params.strategy_name, self.valid_strategy_name)
        self.assertEqual(params.capital, self.valid_capital)
        self.assertEqual(params.data_type, self.valid_data_type)
        self.assertEqual(params.missing_values_strategy, self.valid_missing_values_strategy)
        self.assertEqual(params.strategy_allocation, self.valid_strategy_allocation)
        self.assertEqual(params.train_start, self.valid_train_start)
        self.assertEqual(params.train_end, self.valid_train_end)
        self.assertEqual(params.test_start, self.valid_test_start)
        self.assertEqual(params.test_end, self.valid_test_end)
        self.assertEqual(params.symbols, self.valid_symbols)
        self.assertEqual(params.benchmark, self.valid_benchmark)
        
        tickers = [symbol.ticker for symbol in self.valid_symbols]
        self.assertEqual(params.tickers,tickers)

    def test_construction_defaults(self):
        params = Parameters(strategy_name=self.valid_strategy_name,
                    capital=self.valid_capital,
                    data_type=self.valid_data_type,
                    test_start=self.valid_test_start,
                    test_end=self.valid_test_end,
                    symbols=self.valid_symbols)
                            
        self.assertEqual(params.strategy_name, self.valid_strategy_name)
        self.assertEqual(params.capital, self.valid_capital)
        self.assertEqual(params.data_type, self.valid_data_type)
        self.assertEqual(params.missing_values_strategy, 'fill_forward')
        self.assertEqual(params.strategy_allocation, 1.0)
        self.assertEqual(params.train_start, None)
        self.assertEqual(params.train_end, None)
        self.assertEqual(params.test_start, self.valid_test_start)
        self.assertEqual(params.test_end, self.valid_test_end)
        self.assertEqual(params.symbols, self.valid_symbols)
        self.assertEqual(params.benchmark, None)
        
        tickers = [symbol.ticker for symbol in self.valid_symbols]
        self.assertEqual(params.tickers,tickers)

    def test_to_dict(self):
        params = Parameters(strategy_name=self.valid_strategy_name,
                    capital=self.valid_capital,
                    data_type=self.valid_data_type,
                    missing_values_strategy=self.valid_missing_values_strategy,
                    strategy_allocation=self.valid_strategy_allocation,
                    train_start=self.valid_train_start,
                    train_end=self.valid_train_end,
                    test_start=self.valid_test_start,
                    test_end=self.valid_test_end,
                    symbols=self.valid_symbols,
                    benchmark=self.valid_benchmark)
        
        params_dict = params.to_dict()

        self.assertEqual(params_dict["strategy_name"], self.valid_strategy_name)
        self.assertEqual(params_dict["capital"], self.valid_capital)
        self.assertEqual(params_dict["data_type"], self.valid_data_type.value)
        self.assertEqual(params_dict["strategy_allocation"], self.valid_strategy_allocation)
        self.assertEqual(params_dict["train_start"], self.valid_train_start)
        self.assertEqual(params_dict["train_end"], self.valid_train_end)
        self.assertEqual(params_dict["test_start"], self.valid_test_start)
        self.assertEqual(params_dict["test_end"], self.valid_test_end)
        self.assertEqual(params_dict["benchmark"], self.valid_benchmark)

        tickers = [symbol.ticker for symbol in self.valid_symbols]
        self.assertEqual(params_dict["tickers"], tickers)

    # Type Validation
    def test_strategy_name_type_validation(self):
        with self.assertRaisesRegex(TypeError,"strategy_name must be of type str"):
             Parameters(strategy_name=123,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
             
    def test_capital_type_validation(self):
        with self.assertRaisesRegex(TypeError,"capital must be of type int or float"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital="1000",
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)

    def test_data_type_type_validation(self):
        with self.assertRaisesRegex(TypeError,"data_type must be an instance of MarketDataType"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type="BAR",
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)

    def test_missing_values_strategy_type_validation(self):
        with self.assertRaisesRegex(TypeError, "missing_values_strategy must be of type str"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=1234,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)

    def test_train_start_type_validation(self):
        with self.assertRaisesRegex(TypeError,"train_start must be of type str or None"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=datetime(2020,10, 10),
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
             
    def test_train_end_type_validation(self):
        with self.assertRaisesRegex(TypeError,"train_end must be of type str or None"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_test_start,
                            train_end=datetime(2020,10, 10),
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
             
    def test_test_start_type_validation(self):
        with self.assertRaisesRegex(TypeError,"test_start must be of type str"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=datetime(2020,10, 10),
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
             
    def test_test_end_type_validation(self):
        with self.assertRaisesRegex(TypeError,"test_end must be of type str"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=datetime(2020,10, 10),
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
             
    def test_benchmark_list_type_validation(self):
        with self.assertRaisesRegex(TypeError,"benchmark must be of type list or None"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark='test')
             
    def test_benchmark_list_contents_type_validation(self):
        with self.assertRaisesRegex(TypeError,"All items in 'benchmark' must be of type str"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=[9,9])
             
    def test_symbols_list_type_validation(self):
        with self.assertRaisesRegex(TypeError,"'symbols' must be of type list"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols='tests',
                            benchmark=self.valid_benchmark)
             
    def test_symbols_list_contents_type_validation(self):
        with self.assertRaisesRegex(TypeError,"All items in 'symbols' must be instances of Symbol"):
             Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=['appl','tsla'],
                            benchmark=self.valid_benchmark)

    # Constraint Validation
    def test_missing_values_strategy_constraint(self):
        with self.assertRaisesRegex(ValueError,"'missing_values_strategy' must be either 'drop' or 'fill_forward'"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy='testing',
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
    
    def test_capital_negative_constraint(self):
        with self.assertRaisesRegex(ValueError,"'capital' must be greater than zero"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=-1,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
            
    def test_capital_zero_constraint(self):
        with self.assertRaisesRegex(ValueError,"'capital' must be greater than zero"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=0,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
            
    def test_strategy_allocation_negative_constraint(self):
        with self.assertRaisesRegex(ValueError,"'strategy_allocation' must be greater than zero"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=-1.0,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
            
    def test_strategy_allocation_zero_constraint(self):
        with self.assertRaisesRegex(ValueError,"'strategy_allocation' must be greater than zero"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=0,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)

    def test_train_date_constraint(self):
        with self.assertRaisesRegex(ValueError,"'train_start' must be before 'train_end'"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start='2020-01-01',
                            train_end='2019-01-01',
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
            
    def test_train_date_same_start_and_end_constraint(self):
        with self.assertRaisesRegex(ValueError,"'train_start' must be before 'train_end'"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start='2020-01-01',
                            train_end='2020-01-01',
                            test_start=self.valid_test_start,
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
            
    def test_test_date_constraint(self):
        with self.assertRaisesRegex(ValueError,"'test_start' must be before 'test_end'"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start='2024-02-01',
                            test_end='2024-01-01',
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
            
    def test_test_date_same_start_and_end_constraint(self):
        with self.assertRaisesRegex(ValueError,"'test_start' must be before 'test_end'"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end=self.valid_train_end,
                            test_start='2024-01-01',
                            test_end='2024-01-01',
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
            
    def test_train_end_test_start_constraint(self):
        with self.assertRaisesRegex(ValueError,"'train_end' must be before 'test_start'"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end='2024-01-01',
                            test_start='2024-01-01',
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)
            
    def test_train_end_after_test_start_constraint(self):
        with self.assertRaisesRegex(ValueError,"'train_end' must be before 'test_start'"):
            Parameters(strategy_name=self.valid_strategy_name,
                            capital=self.valid_capital,
                            data_type=self.valid_data_type,
                            missing_values_strategy=self.valid_missing_values_strategy,
                            strategy_allocation=self.valid_strategy_allocation,
                            train_start=self.valid_train_start,
                            train_end='2024-01-02',
                            test_start='2024-01-01',
                            test_end=self.valid_test_end,
                            symbols=self.valid_symbols,
                            benchmark=self.valid_benchmark)

    # Edge Cases
# Float Capital Validation: You've included a test to ensure capital must be of type int or float, but it could be useful to add a specific test to confirm that the class correctly handles float values for capital, especially since financial calculations often involve decimal values.

# Strategy Allocation Bounds: You've checked that strategy_allocation must be greater than zero. Depending on your application's logic, you might also want to validate that it does not exceed certain bounds (e.g., a strategy allocation should not be greater than 1 if it represents a percentage of total capital).

# Date Format Validation: While you've implemented checks to ensure start dates are before end dates, you might also consider validating the format of the date strings. This could prevent errors related to incorrect date formats being passed to your class. However, this might be more relevant if there's variability in how dates are inputted into your system.

# List and Derived Attributes Consistency: For symbols and tickers, you've done well to check the contents of symbols and derive tickers from it. It could be useful to also test scenarios where symbols might be modified after object creation (if your class design allows for it) to ensure tickers remains consistent or is updated accordingly.

# Serialization and Deserialization Consistency: For the to_dict method, you've checked that the dictionary representation matches the object's state. Testing the inverse process, if applicable—creating a Parameters object from a dictionary—would ensure that serialization and deserialization are consistent.

# Missing Values Strategy Literal Check: You've included a check for missing_values_strategy to ensure it's either 'drop' or 'fill_forward'. Including a test that tries to set it to a valid string that's not one of these two options (even though you've already done this), just to explicitly document and validate this constraint.


            

if __name__ == "__main__":
    unittest.main()