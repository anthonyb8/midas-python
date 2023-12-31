class AccountInfoManager:
    ACCOUNT_INFO_KEYS = {'AccruedCash', 'AvailableFunds', 'BuyingPower', 'CashBalance', 
                'Currency', 'EquityWithLoanValue', 'ExcessLiquidity', 'FullAvailableFunds', 
                'FullInitMarginReq', 'FundValue', 'FutureOptionValue', 'FuturesPNL', 
                'GrossPositionValue', 'InitMarginReq', 'IssuerOptionValue', 
                'MaintMarginReq', 'NetLiquidation', 'RealizedPnL', 'TotalCashBalance', 
                'TotalCashValue', 'UnrealizedPnL'}
    
    def __init__(self):
        self.account_info = {}

    def update(self, symbol:str, direction:str, price:float, quantity:int):
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol, direction, price, quantity)
        else:
            self.positions[symbol].update(direction, price, quantity)
            if self.positions[symbol].quantity == 0:
                del self.positions[symbol]