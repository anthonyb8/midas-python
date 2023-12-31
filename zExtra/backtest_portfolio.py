# from engine.base.handlers import BasePortfolioHandler
from engine.backtest.broker_client import BrokerClient


class BacktestPortfolioHandler(): #BasePortfolioHandler):
    """
    Interacts with the portfolio client, retrieves commonly needed data, that would be stored in the portfolio client.

    Args:
        BasePortfolioHandler : Abstract portfolio class.
    """
    def __init__(self, broker_client: BrokerClient):
        """
        Class constructor.

        Args:
            portfolio_client (PortfolioClient) : Inheritres the backtest portfolio client, so it can easily return portfoli related data to the engine.
        """
        self.broker_client = broker_client

    def get_account_information(self):
        """
        Gets account information ex. capital, margin available

        Return:
            dict : Contains the key-value relationship for accoutn specfic data.
        """
        return self.broker_client.account_info
    
    def get_cash(self):
        """
        Gets just cash amount. 

        Return:
            int : Cash available to trade.
        """
        return self.broker_client.capital
    
    def get_positions(self):
        """
        Gets positions dictionary.

        Return:
            dict : Contains the current positions in the portfolio.
        """
        return self.broker_client.positions
    
    def get_execution_details(self):
        """
        Gets executed trades. #TODO : not sure if needed
        """
        return self.broker_client.executed_orders
    
    def get_total_portfolio_value(self) -> float:
        """
        Not sure if needed in backtest.
        """
        account_info = self.get_account_information()
        return float(account_info.get('NetLiquidation', 0))















    #     self.portfolio = PositionsManager()
    #     self.capital = capital

    # def handle_execution_event(self, event:ExecutionEvent):
    #     contract = event.contract
    #     direction = event.direction
    #     price = event.fill_price 
    #     quantity = event.quantity

    #     self._update_position(contract, direction, price, quantity)
    #     self._update_capital(direction, quantity, price)

    # def _update_position(self, contract, direction, price, quantity):
    #     self.portfolio.update_or_add_position(contract, direction, price, quantity)
    #     # Log the updated positions for debugging and verification.
    #     backtest_logger.info({pos.symbol: (pos.direction, pos.avg_price, pos.quantity) for pos in self.portfolio.positions.values()})

    # def _update_capital(self, direction, quantity, price):
    #     if direction == 'BUY':
    #         self.capital -= quantity * price
    #     elif direction == 'SELL':
    #         self.capital += quantity * price
        
    #     backtest_logger.info(self.capital)

    # def get_positions(self):
    #     return self.portfolio.positions

    # def get_cash(self):
    #     return self.capital



    # def __init__(self, client_instance: TradeClient):
    #     self.client = client_instance
    #     self.app = self.client.app

    # def get_active_orders(self):
    #     return self.app.active_orders
    
    # def get_account_information(self):
    #     return self.app.account_info
    
    # def get_cash(self):
    #     return float(self.get_account_information()['CashBalance'])
    
    # def get_positions(self):
    #     return self.app.positions
    
    # def get_execution_details(self):
    #     return self.app.executed_orders
    
    # def get_total_portfolio_value(self) -> float:
    #     account_info = self.get_account_information()
    #     return float(account_info.get('NetLiquidation', 0))


        





# class BacktestPortfolioHandler(BasePortfolioHandler):
#     def __init__(self, capital:int):
#         self.positions = {}
#         self.capital = capital

#     def handle_execution_event(self, event:ExecutionEvent):
#         self._update_position(event)
#         self._update_capital(event)

#     def _update_position(self, event):
#         # Determine the quantity based on the event direction.
#         quantity = event.quantity

#         # Check if the contract exists in positions.
#         if event.contract not in self.positions:
#             self.positions[event.contract] = {
#                 'price': event.fill_price,
#                 'quantity': quantity,
#                 'direction': event.direction
#             }
#         else:
#             existing_direction = self.positions[event.contract]['direction']

#             # If the current event's direction is opposite to the existing position, it might be a close.
#             is_closing_position = (event.direction == 'BUY' and existing_direction == 'SELL') or \
#                                 (event.direction == 'SELL' and existing_direction == 'BUY')

#             # Calculate total cost of the existing position.
#             total_cost_before = self.positions[event.contract]['price'] * self.positions[event.contract]['quantity']
#             # Calculate total cost of the new event.
#             total_cost_event = event.fill_price * quantity

#             # If it's a closing position and the quantities match, remove the position.
#             if is_closing_position and self.positions[event.contract]['quantity'] == quantity:
#                 del self.positions[event.contract]
#             else:
#                 # Update the position's quantity and average price.
#                 new_quantity = self.positions[event.contract]['quantity']
#                 if is_closing_position:
#                     new_quantity -= quantity  # Reduce the quantity if it's a closing position.
#                 else:
#                     new_quantity += quantity  # Add to the quantity if it's not a closing position.
                
#                 # If the updated quantity is zero after adjustments, delete the position.
#                 if new_quantity == 0:
#                     del self.positions[event.contract]
#                 else:
#                     new_avg_price = (total_cost_before + total_cost_event) / new_quantity
#                     self.positions[event.contract]['price'] = new_avg_price
#                     self.positions[event.contract]['quantity'] = new_quantity
#                     self.positions[event.contract]['direction'] = event.direction  # Update the direction.

#         # Log the updated positions for debugging and verification.
#         backtest_logger.info(self.positions)

#     def _update_capital(self, event):
#         if event.direction == 'BUY':
#             self.capital -= event.quantity * event.fill_price
#         elif event.direction == 'SELL':
#             self.capital += event.quantity * event.fill_price
        
#         backtest_logger.info(self.capital)

#     def get_positions(self):
#         return self.positions
    
#     def get_cash(self):
#         return self.capital
    
