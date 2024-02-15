from typing import TypedDict
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict, Optional

# All
@dataclass
class Position:
    action: str  # BUY/SELL
    avg_cost: float
    quantity: int
    contract_size: Optional[int] = None
    initial_margin: Optional[float] = None
    total_cost: Optional[float] = None

    def __eq__(self, other):
        # Check if all attributes, including total_cost, are equal
        return (self.action == other.action and
                self.avg_cost == other.avg_cost and
                self.quantity == other.quantity and
                self.contract_size == other.contract_size and
                self.initial_margin == other.initial_margin and
                self.total_cost == other.total_cost)
    
@dataclass
class Trade:
    trade_id: str
    leg_id: str
    timestamp: datetime
    symbol: str
    quantity: int
    price: float
    cost: float
    action: str
    fees: float

    def __post_init__(self):
        if isinstance(self.timestamp, datetime):
            self.timestamp = self.timestamp.isoformat()

class Account(TypedDict):
    AccruedCash: float
    AvailableFunds: float
    BuyingPower: float
    CashBalance: float
    Currency: str
    EquityWithLoanValue: float
    ExcessLiquidity: float
    FullAvailableFunds : float
    FullInitMarginReq: float
    FundValue: float
    FutureOptionValue: float
    FuturesPNL: float
    GrossPositionValue: float
    InitMarginReq: float
    IssuerOptionValue: float
    MaintMarginReq: float
    NetLiquidation: float
    RealizedPnL: float
    TotalCashBalance: float
    TotalCashValue: float
    UnrealizedPnL: float

# Backtest 
class PositionDetails(TypedDict):
    action: str
    avg_cost: float
    quantity: int
    contract_size: Optional[int]
    initial_margin: Optional[float]
    total_cost: Optional[float]

class AccountDetails(TypedDict):
    Timestamp: Optional[str]
    AvailableFunds: float
    EquityValue: float
    RequiredMargin: float
    CurrentMargin: float
    UnrealizedPnl: float

class ExecutionDetails(TypedDict):
    timestamp: datetime
    trade_id: str
    leg_id: str
    symbol: str
    quantity: int
    price: float
    cost: float
    action: str
    fees: float

class EquityDetails(TypedDict):
    timestamp : datetime
    equity_value : float

# LIVE
@dataclass
class ActiveOrder:
    permId: int
    clientId: int
    orderId: int
    account: str
    symbol: str
    secType: str
    exchange: str
    action: str 
    orderType: str
    totalQty: float
    cashQty: float
    lmtPrice: float
    auxPrice: float
    status: str


    
