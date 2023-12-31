from engine.base.handlers import BasePerformanceHandler
from engine.base.data import Trade, EquityManager, TradesManager, SummaryStatsManager, EquityValue
from engine.base.events import ExecutionEvent, MarketDataEvent
from .broker_client import BrokerClient

class BacktestPerformanceHandler(BasePerformanceHandler):

    """
    TODO : class may just be reposnibel for creatign backtets object and return to the egnie to save using the database client.
    
    """

    def __init__(self, broker_client: BrokerClient):
        self.broker_client = broker_client
        self.app = self.broker_client.app
