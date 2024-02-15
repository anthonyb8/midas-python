# strategy_a/config.py
from midas.symbols import Equity, Future, Currency, Exchange, Symbol
from zextra.market_data import MarketDataType
from midas.command import Config, Mode, Parameters
from .logic import Cointegrationzscore

class CointegrationzscoreConfig(Config):
    def __init__(self, mode: Mode):  

        params = Parameters(
            strategy_name='cointegrationzscore',
            missing_values_strategy='drop',
            train_start="2018-05-18",
            train_end="2023-01-19",
            test_start="2023-01-19",
            test_end="2024-01-19",
            capital=100000,
            strategy_allocation = 1.0,
            data_type = MarketDataType.BAR,
            symbols = [
                Future(ticker="HE.n.0",currency=Currency.USD,exchange=Exchange.SMART,fees=0.85, lastTradeDateOrContractMonth="continuous",contractSize=50,tickSize=0.25, initialMargin=4564.17),
                Future(ticker="ZC.n.0",currency=Currency.USD,exchange=Exchange.CME,fees=0.85,lastTradeDateOrContractMonth="continuous",contractSize=50,tickSize=0.25, initialMargin=2056.75)
            ], 
            benchmark=['^GSPC']
        )  
    
        super().__init__(mode, params)
        self.set_strategy(Cointegrationzscore)

        # self.strategy_name = 'cointegrationzscore' # must match the directory name
        # self.capital = 100000
        # self.train_start = "2018-05-18"
        # self.train_end = "2023-01-19"

        # self.test_start = "2023-01-19"
        # self.test_end = "2024-01-19"
        # super().__init__(mode)