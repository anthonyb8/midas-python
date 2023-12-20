from ibapi.contract import Contract
from enum import Enum
from typing import NewType

class Currency(Enum):
    USD = "USD"
    CAD = "CAD"

# Enum for Security Type
class SecType(Enum):
    STOCK = "STK"
    OPTION = "OPT"
    FUTURE = "FUT"
    # ['STK', 'CMDTY','FUT','OPT','CASH','CRYPTO','FIGI','IND','CFD','FOP','BOND'] 

# Enum for Exchanges
class Exchange(Enum):
    SMART = "SMART"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    ISLAND = "ISLAND"
    CBOE = "CBOE"
    CME = "CME"
    COMEX = "COMEX"
    GLOBEX = "GLOBEX"
    CBOT = "CBOT"
    NYMEX = "NYMEX"
    
class Symbol:
    def __init__(self, symbol, secType: SecType, currency:Currency, exchange: Exchange):
        self.symbol = symbol
        self.secType = secType
        self.currency = currency
        self.exchange = exchange

    def to_contract_data(self) -> dict:
        return {
            "symbol": self.symbol,
            "secType": self.secType.value,
            "currency": self.currency.value,
            "exchange": self.exchange.value
        }
    
    def to_contract(self) -> Contract:
        contract = Contract()
        contract_data = self.to_contract_data()
        for key, value in contract_data.items():
            setattr(contract, key, value)
        return contract

class Equity(Symbol):
    def __init__(self, symbol:str, currency:Currency, exchange: Exchange):
        super().__init__(symbol, SecType.STOCK, currency, exchange)

class Future(Symbol):
    def __init__(self, symbol:str, currency: Currency, exchange: Exchange, lastTradeDateOrContractMonth: NewType("YYYYMM", str)):
        super().__init__(symbol, SecType.FUTURE, currency, exchange)
        self.lastTradeDateOrContractMonth = lastTradeDateOrContractMonth

        if not self.lastTradeDateOrContractMonth:
            raise ValueError("lastTradeDateOrContractMonth is required for FUT")

    def to_contract_data(self) -> dict:
        data = super().to_contract_data()
        data["lastTradeDateOrContractMonth"] = self.lastTradeDateOrContractMonth
        return data

class Option(Symbol):
    def __init__(self, symbol:str, currency:Currency, exchange: Exchange, lastTradeDateOrContractMonth, right, strike):
        super().__init__(symbol, SecType.OPTION, currency, exchange)
        self.lastTradeDateOrContractMonth = lastTradeDateOrContractMonth
        self.right = right
        self.strike = strike

        if not all([self.lastTradeDateOrContractMonth, self.right, self.strike]):
            raise ValueError("For options, lastTradeDateOrContractMonth, right, and strike are mandatory")

    def to_contract_data(self) -> dict:
        data = super().to_contract_data()
        data["lastTradeDateOrContractMonth"] = self.lastTradeDateOrContractMonth
        data["right"] = self.right
        data["strike"] = self.strike
        return data


