from .broker_client import BrokerClient

class LivePortfolioHandler:

    def __init__(self, broker_client : BrokerClient):
        self.broker_client = broker_client
        self.app = self.broker_client.app

    def get_active_orders(self):
        return self.app.active_orders
    
    def get_account_information(self):
        return self.app.account_info
    
    def get_cash(self):
        return float(self.get_account_information()['CashBalance'])
    
    def get_positions(self):
        return self.app.positions
    
    def get_execution_details(self):
        return self.app.executed_orders
    
    def get_total_portfolio_value(self) -> float:
        account_info = self.get_account_information()
        return float(account_info.get('NetLiquidation', 0))


        
