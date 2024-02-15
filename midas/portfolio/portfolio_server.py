import logging
from typing import Dict
from ibapi.contract import Contract

from midas.symbols import Symbol
from midas.events import  Trade
from midas.account_data import Position,ActiveOrder, AccountDetails, EquityDetails
from .performance import PerformanceManager

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
            portfolio_client (PortfolioClient) : Inherites the backtest portfolio client, so it can easily return portfoli related data to the engine.
        """
        self.performance_manager = performance_manager
        self.symbols_map = symbols_map
        self.logger = logger
        # self.margin_requirement = 0
        # self.margin = 0
        self.capital = None
        self.account : AccountDetails = {}
        self.positions : Dict[Contract, Position] = {}
        self.active_orders : Dict[int, ActiveOrder] = {}

    def update_positions(self, contract:Contract, new_position: Position):
        # Check if this position exists and is equal to the new position
        if contract.symbol in self.positions and self.positions[contract.symbol] == new_position:
            # Positions are identical, do nothing
            return
        else:
            # Update the position and log the change
            self.positions[contract.symbol] = new_position
            self.logger.info(f"\nPositions Updated: \n{self.output_positions()}")

        
        # new_position = Position(position_data['action'], position_data['avg_cost'], position_data['quantity'], margin=position_data['initial_margin'])
        # self.positions[contract.symbol] = Position(position_data['action'],position_data['avg_cost'], position_data['quantity'],margin= position_data['initial_margin'])
        # self.logger.info(f"\nPositions Updated: \n{self.output_positions()}")
    
    def output_positions(self):
        string =""
        for contract, position in self.positions.items():
            string += f" {contract}: {position.__dict__} \n"
        return string
    
    def update_orders(self, order:ActiveOrder):
        # If the status is 'Cancelled' and the order is present in the dict, remove it
        if order.status == 'Cancelled' or order.status == 'Filled' and order.permId in self.active_orders:
            del self.active_orders[order.permId]
        # If not cancelled, either update the existing order or add a new one
        elif order.status != 'Cancelled' and order.status != 'Filled':
            if order.permId not in self.active_orders:
                self.active_orders[order.permId] = order
            else:
                self.active_orders[order.permId].update(order)

        self.logger.info(f"\nOrder Updated: \n{self.ouput_orders()}")

    def ouput_orders(self):
        string =""
        for permId, order in self.active_orders.items():
            string += f" {order} \n"
        return string

    def update_trades(self, trade:Trade):
        self.performance_manager.update_trades(trade)

    def update_account_details(self, account_details:AccountDetails):
        self.account = account_details
        self.capital = float(self.account['AvailableFunds'])
        self.update_equity(EquityDetails(timestamp = account_details['Timestamp'],equity_value= self.account['EquityValue']))

        self.logger.info(f"\nAccount Updated: \n{self.output_account()}")
    
    def output_account(self):
        string = ""
        for key, value in self.account.items():
            string += f" {key} : {value} \n"
        return string
    
    def update_equity(self, equity_details:EquityDetails):
        self.performance_manager.update_equity(equity_details)

    def update_margin_requirement(self):
        pass

    def update_current_margin(self):
        pass

    def calculate_statistics(self):
        self.performance_manager.calculate_statistics()



