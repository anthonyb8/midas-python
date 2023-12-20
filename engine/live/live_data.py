import logging
from ibapi.contract import Contract
from engine.live.data_client import DataClient
from engine.base.handlers import BaseDataHandler
from engine.base.data import MarketDataType


class LiveDataHandler(BaseDataHandler):

    def __init__(self, data_client: DataClient, logger:logging.Logger):
        self.data_client = data_client
        self.app = self.data_client.app
        self.logger = logger


    def stream_market_data_top_book(self, contract:Contract):
        reqId = self.data_client._get_valid_id()
        
        self.app.reqId_to_contract_map[reqId] = contract

        self.app.reqMktData(reqId=reqId, contract=contract,genericTickList="", snapshot=False, regulatorySnapshot=False, mktDataOptions=[])
        if reqId not in self.app.market_data_top_book :
            self.app.market_data_top_book[reqId] = {}
        self.app.market_data_top_book[reqId]['CONTRACT'] = contract

        self.logger.info(f"Requested top of book tick data stream for {contract}.")
        
    def cancel_market_data_stream(self,contract:Contract):
        for key, value in self.app.market_data_top_book.items():
            if value['CONTRACT'] == contract:
                self.app.cancelMktData(reqId=key)
                remove_key = key
        del self.app.market_data_top_book[key]
        
    def cancel_all_market_data(self):
        for reqId in self.app.market_data_top_book.keys():  
            self.app.cancelMktData(reqId)
        self.app.market_data_top_book.clear()

    def get_top_book_market_data(self):
        return self.app.market_data_top_book

    def stream_5_sec_bars(self, contract:Contract):
        reqId = self.data_client._get_valid_id()

        self.app.reqId_to_contract_map[reqId] = contract
        
        self.app.reqRealTimeBars(reqId=reqId, contract=contract, barSize=5, whatToShow='TRADES', useRTH=False, realTimeBarsOptions=[])
        self.logger.info(f"Started 5 sec bar data stream for {contract}.")

    # def cancel_real_time_bars(self):
    #     self.app.cancelRealTimeBars(self, tickerId:int)

    def get_data(self, data_type:MarketDataType, contract:Contract):
        if data_type == MarketDataType.TICK:
            self.stream_market_data_top_book(contract)
        elif data_type == MarketDataType.BAR:
            self.stream_5_sec_bars(contract)
        else:
            raise ValueError(f"{data_type} not a valid market data type. (TICK or BAR)")




