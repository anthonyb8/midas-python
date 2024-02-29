from typing import TypedDict, Union
from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict, Optional

class EquityDetails(TypedDict):
    timestamp : datetime
    equity_value : float
class AccountDetails(TypedDict):
    Timestamp: Optional[str]
    FullAvailableFunds : float # Available funds of whole portfolio with no discounts or intraday credits
    FullInitMarginReq: float # Initial Margin of whole portfolio with no discounts or intraday credits
    NetLiquidation: float # The basis for determining the price of the assets in your account
    UnrealizedPnL: float # The difference between the current market value of your open positions and the average cost, or Value - Average Cost
    # Live ONLY
    FullMaintMarginReq: Optional[float]
    ExcessLiquidity: Optional[float]
    Currency: Optional[str] # USD or CAD
    BuyingPower: Optional[float]
    FuturesPNL : Optional[float]
    TotalCashBalance: Optional[float] # Total Cash Balance including Future PNL

class ActiveOrder(TypedDict):
    permId: int
    clientId: int
    orderId: int
    parentId: int 
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
    status: str  # Options : PendingSubmit, PendingCancel PreSubmitted, Submitted, Cancelled, Filled, Inactive 
    filled: str
    remaining: float
    avgFillPrice: float
    lastFillPrice: float 
    whyHeld: str 
    mktCapPrice: float

@dataclass
class Position:
    action: str  # BUY/SELL
    avg_cost: float
    quantity: int
    total_cost: Optional[float] 
    market_value: Optional[float]
    multiplier: int = None
    initial_margin: Optional[float] = None

    def __post_init__(self):
        # Type checks
        if not isinstance(self.action, str):
            raise TypeError(f"action must be of type str")
        if not isinstance(self.avg_cost, (int,float)):
            raise TypeError(f"avg_cost must be of type int or float")
        if not isinstance(self.quantity, (int,float)):
            raise TypeError(f"quantity must be of type int or float")
        if not isinstance(self.multiplier, int):
            raise TypeError(f"multiplier must be of type int")
        if not isinstance(self.initial_margin, (int,float)):
            raise TypeError(f"initial_margin must be of type int or float") 
        if not isinstance(self.total_cost, (float, int)):
            raise TypeError(f"total_cost must be of type int or float")
        if not isinstance(self.market_value, (int, float)):
            raise TypeError(f"market_value must be of type int or float")
        

        # Constraint Validation
        if self.action not in ['BUY', 'SELL']:
            raise ValueError(f"action must be either 'BUY' or 'SELL'")
        if self.multiplier <= 0:
            raise ValueError(f"multiplier must be greater than zero")
        if self.initial_margin < 0:
            raise ValueError(f"initial_margin must be non-negative.")
        
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return (self.action == other.action and
                self.avg_cost == other.avg_cost and
                self.quantity == other.quantity and
                self.multiplier == other.multiplier and
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
    action: str # BUY/SELL
    fees: float

    def __post_init__(self):
        # Type Validation
        if not isinstance(self.trade_id, str):
            raise TypeError(f"'trade_id' must be of type str")
        if not isinstance(self.leg_id, str):
            raise TypeError(f"'leg_id' must be of type str")
        if not isinstance(self.timestamp, datetime):
            raise TypeError(f"'timestamp' must be of type datetime")
        if not isinstance(self.symbol, str):
            raise TypeError(f"'symbol' must be of type str")
        if not isinstance(self.quantity, (float, int)):
            raise TypeError(f"'quantity' must be of type float or int")
        if not isinstance(self.price, (float, int)):
            raise TypeError(f"'price' must be of type float or int")
        if not isinstance(self.cost, (float, int)):
            raise TypeError(f"'cost' must be of type float or int")
        if not isinstance(self.action, str):
            raise TypeError(f"'action' must be of type str")
        if not isinstance(self.fees, (float, int)):
            raise TypeError(f"'fees' must be of type float or int")
        
        # Constraint Validation
        if self.action not in ['BUY', 'SELL']:
            raise ValueError(f"'action' must be either 'BUY' or 'SELL'")
        if self.price <= 0:
            raise ValueError(f"'price' must be greater than zero")
        
        #TODO : Add validation for cost/quantity depending on the action


        # Convert datetime to a str
        # self.timestamp = self.timestamp.isoformat()

