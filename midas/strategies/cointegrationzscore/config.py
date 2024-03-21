# strategy_a/config.py
from midas.symbols.symbols import Equity, Future, Currency, Exchange, Symbol
from midas.events import MarketDataType
from midas.command import Config, Mode, Parameters
from .logic import Cointegrationzscore

class CointegrationzscoreConfig(Config):
    def __init__(self, mode: Mode):  

        params = Parameters(
            strategy_name="cointegrationzscore", # must match the directory name
            missing_values_strategy="drop",
            train_start="2020-05-18",
            train_end="2024-01-01",
            test_start="2024-01-02",
            test_end="2024-01-19",
            capital=100000,
            data_type = MarketDataType.BAR,
            symbols = [
                Future(ticker="HE.n.0",data_ticker= "HE.n.0", currency=Currency.USD,exchange=Exchange.CME,fees=0.85, lastTradeDateOrContractMonth="202404", multiplier=40000,tickSize=0.00025, initialMargin=4564.17),
                Future(ticker="ZC.n.0",data_ticker= "ZC.n.0", currency=Currency.USD,exchange=Exchange.CBOT,fees=0.85,lastTradeDateOrContractMonth="202403", multiplier=5000,tickSize=0.0025, initialMargin=2056.75),
                # Future(ticker="ZS",data_ticker= "ZC.n.0", currency=Currency.USD,exchange=Exchange.CBOT,fees=0.85,lastTradeDateOrContractMonth="202403", multiplier=5000,tickSize=0.0025, initialMargin=2056.75),
            ], 
            benchmark=["^GSPC"]
        )  
    
        super().__init__(mode, params)
        self.set_strategy(Cointegrationzscore)