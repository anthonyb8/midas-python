from .performance import PerformanceManager
from midas.symbols import Symbol
from typing import Dict
import logging

class Position:
    def __init__(self, action:str, avg_cost:float, quantity:int, total_cost: float=None, margin:float=None):
        self.action = action # BUY/SELL
        self.avg_cost = avg_cost
        self.quantity = quantity
        self.total_cost = total_cost
        self.margin = margin

    def __eq__(self, other):
        # Check if all attributes, including total_cost, are equal
        return (self.action == other.action and
                self.avg_cost == other.avg_cost and
                self.quantity == other.quantity and
                self.total_cost == other.total_cost and  # Include this in your comparison
                self.margin == other.margin)


class ActiveOrder:
    def __init__(self, contract:dict, action:str, avg_price:float, quantity:int):
        self.action = action # LONG/SHORT
        self.contract = contract
        self.avg_price = avg_price
        self.quantity = quantity
        self.mkt_value = self.avg_price * self.quantity # Delete after debug


class PortfolioServer:
    """
    Interacts with the portfolio client, retrieves commonly needed data, that would be stored in the portfolio client.

    Args:
        BasePortfolioHandler : Abstract portfolio class.
    """
    def __init__(self, symbols_map: Dict[str, Symbol], logger:logging.Logger, performance_manager:PerformanceManager):
        """
        Class constructor.

        Args:
            portfolio_client (PortfolioClient) : Inheritres the backtest portfolio client, so it can easily return portfoli related data to the engine.
        """
        self.capital = None
        self.margin_requirement = 0
        self.margin = 0
        self.positions = {}
        self.active_orders = {}
        self.account = {}
        self.symbols_map = symbols_map
        self.logger = logger
        self.performance_manager = performance_manager

    def update_positions(self, contract, position_data):
        new_position = Position(position_data['action'], position_data['avg_cost'], position_data['quantity'], margin=position_data['initial_margin'])

        # Check if this position exists and is equal to the new position
        if contract.symbol in self.positions and self.positions[contract.symbol] == new_position:
            # Positions are identical, do nothing
            return
        else:
            # Update the position and log the change
            self.positions[contract.symbol] = new_position
            self.logger.info(f"\nPositions Updated: \n{self.output_positions()}")

        
        # self.positions[contract.symbol] = Position(position_data['action'],position_data['avg_cost'], position_data['quantity'],margin= position_data['initial_margin'])
        # self.logger.info(f"\nPositions Updated: \n{self.output_positions()}")
    
    def output_positions(self):
        string =""
        for contract, position in self.positions.items():
            string += f" {contract}: {position.__dict__} \n"
        return string
    
    def update_orders(self, **orders):
        # If the status is 'Cancelled' and the order is present in the dict, remove it
        if orders['status'] == 'Cancelled' or orders['status'] == 'Filled' and orders['permId'] in self.active_orders:
            del self.active_orders[orders['permId']]
        # If not cancelled, either update the existing order or add a new one
        elif orders['status'] != 'Cancelled' and orders['status'] != 'Filled':
            if orders['permId'] not in self.active_orders:
                self.active_orders[orders['permId']] = orders
            else:
                self.active_orders[orders['permId']].update(orders)

        self.logger.info(f"\nOrder Updated: \n{self.ouput_orders()}")

    def ouput_orders(self):
        string =""
        for permId, order in self.active_orders.items():
            string += f" {order} \n"
        return string

    def update_trades(self, **trade):
        self.performance_manager.update_trades(**trade)

    def update_account_details(self, account_details:dict):
        for key, value in account_details.items():
            if key == 'AvailableFunds':
                self.capital = float(value)
            elif 'EquityValue' == key:
                self.performance_manager.update_equity(account_details['Timestamp'], value)
            
            self.account[key] = value
        self.logger.info(f"\nAccount Updated: \n{self.output_account()}")
    
    def output_account(self):
        string = ""
        for key, value in self.account.items():
            string += f" {key} : {value} \n"
        return string

    # def update_capital(self, capital:float):
    #     self.capital = capital
    #     self.logger.info(f"\nCapital Updated: \n{self.capital}")

    def update_margin_requirement(self):
        pass

    def update_current_margin(self):
        pass

    def calculate_statistics(self):
        self.performance_manager.calculate_statistics()










