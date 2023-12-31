# strategy_a/config.py
from core.base.data import Equity, Currency, Exchange
from command.driver.config import Config, Mode
from core.strategies.strategya import TestStrategy

class StrategyaConfig(Config):
    def __init__(self, mode: Mode):    
        
        self.strategy_name = 'strategya' # must match the directory name
        self.parameters = {
            "capital":100000, 
            "start_date": "2023-01-01",
            "end_date" : "2024-01-01",
            "symbols" : [
                Equity(symbol='AAPL', currency=Currency.USD , exchange=Exchange.SMART),
                Equity(symbol='MSFT', currency=Currency.USD , exchange=Exchange.SMART)
            ]
        }
        super().__init__(mode)

        self.set_strategy(TestStrategy)

        