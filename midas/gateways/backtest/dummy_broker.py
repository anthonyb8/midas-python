from queue import Queue
from typing import Dict
from ibapi.contract import Contract
from ibapi.order import Order
import logging
from datetime import datetime

from midas.order_book import OrderBook
from midas.events import ExecutionEvent, Action, BaseOrder, TradeInstruction
from midas.account_data import PositionDetails, AccountDetails, ExecutionDetails, EquityDetails
from midas.symbols import Symbol, Future, Equity

class DummyBroker:
    def __init__(self, symbols_map: Dict[str, Symbol], event_queue: Queue, order_book:OrderBook, capital:float, logger:logging.Logger,  slippage_factor:int=1):
        self.event_queue = event_queue
        self.order_book = order_book
        self.logger = logger
        self.symbols_map = symbols_map
        self.slippage_factor = slippage_factor # multiplied by tick size, so slippage will be x ticks against the position    
        
        # self.executions : Dict[str, ExecutionDetails] = {}
        self.positions : Dict[str, PositionDetails] = {}
        self.last_trade : Dict[str, ExecutionDetails] = {}
        self.account : AccountDetails =  {'Timestamp': None, 
                                          'AvailableFunds': capital,
                                          'EquityValue' : capital, 
                                          "RequiredMargin": 0, 
                                          "CurrentMargin": 0, 
                                          "UnrealizedPnl": 0
                                        }

        # self.orders = {}

    def placeOrder(self, timestamp, trade_instructions: TradeInstruction, action: Action, contract: Contract, order: BaseOrder):
        action = trade_instructions.action
        quantity = order.quantity

        fill_price  = self._fill_price(contract, action)
        commission_fees = self.calculate_commission_fees(contract,quantity)
        self.update_account(contract, action, quantity, fill_price,commission_fees)

        trade_details = self.update_trades(timestamp, trade_instructions,contract, order, fill_price, commission_fees)

        execution_event = ExecutionEvent(timestamp, trade_instructions, action, contract=contract,order=order, trade_details=trade_details)

        if execution_event:
            self.event_queue.put(execution_event)

    def _fill_price(self, contract: Contract, action:Action):
        """
        Accounts for slippage.
        """
        current_price = self.order_book.current_price(contract.symbol)
        tick_size = self.symbols_map[contract.symbol].tickSize
        adjusted_price = self.calculate_slippage_price(tick_size, current_price, action)

        return adjusted_price

    def calculate_slippage_price(self, tick_size: float, current_price: float, action: Action):
        slippage = tick_size * self.slippage_factor

        if action in [Action.LONG, Action.COVER]:  # Entry signal for a long position or covering a short
            adjusted_price = current_price + slippage
        elif action in [Action.SHORT, Action.SELL]:  # Entry signal for a short position or selling a long
            adjusted_price = current_price - slippage
        else:
            raise ValueError(f"{action} not in ['LONG','COVER', 'SHORT', 'SELL']")
        
        return adjusted_price

    def calculate_commission_fees(self, contract: Contract, quantity: float):
        return abs(quantity) * self.symbols_map[contract.symbol].fees
    
    def update_account(self, contract: Contract, action: Action, quantity: float, fill_price: float, fees: float):
        if isinstance(self.symbols_map[contract.symbol], Future):
            self.update_account_futures(contract, action, quantity, fill_price, fees)
            self.update_positions_future(contract, action, quantity, fill_price)
        elif isinstance(self.symbols_map[contract.symbol], Equity):
            self.update_account_equities(contract, action, quantity, fill_price, fees)
            self.update_positions_equity(contract, action, quantity, fill_price)
        else:
            raise ValueError(f"Symbol not of valid type : {self.symbols_map[contract.symbol]}")

        self.update_equity_value()
             
    def update_account_futures(self, contract: Contract, action: Action, quantity: float, fill_price: float, fees: float):
        self.account['AvailableFunds'] -= fees
        margin_impact = self.symbols_map[contract.symbol].initialMargin * abs(quantity)

        if action in [Action.LONG, Action.SHORT]:
            self.account['RequiredMargin']  += margin_impact
            self.account['AvailableFunds']  -= margin_impact
            self.account['CurrentMargin']  += margin_impact
        elif action in [Action.SELL, Action.COVER]:
            entry_price = self.positions[contract]['avg_cost']  # This needs to be correctly sourced
            pnl = (fill_price - entry_price) * abs(quantity) * self.symbols_map[contract.symbol].contractSize
            
            self.account['AvailableFunds']  += pnl + margin_impact
            self.account['CurrentMargin'] -= pnl + margin_impact
            self.account['RequiredMargin'] -= margin_impact  # remove the margin  required as postion is exited
       
    def update_account_equities(self, contract: Contract, action: Action, quantity: float, fill_price: float, fees: float):
        self.account['AvailableFunds'] -= fees
        capital_impact = fill_price * abs(quantity) 

        if action in [Action.LONG, Action.SHORT]:
            self.account['AvailableFunds']  -= capital_impact
        elif action in [Action.SELL, Action.COVER]:
            entry_price = self.positions[contract]['avg_cost']  # This needs to be correctly sourced
            pnl = (fill_price - entry_price) * abs(quantity)          
            self.account['AvailableFunds']  -= pnl
    
    def update_positions_future(self, contract: Contract, action: Action, quantity: float, fill_price: float):
        ticker = contract.symbol
        contract_size = self.symbols_map[ticker].contractSize
        action = action.to_broker_standard() # converts to BUY or SELL

        # If no position then postions is equal to new order attributes
        if contract not in self.positions.keys():
            self.positions[contract] = PositionDetails(
                action= action,
                quantity= quantity,
                avg_cost=round(fill_price,4),
                contract_size= contract_size,      
                initial_margin= self.symbols_map[ticker].initialMargin
                # 'total_cost': round(quantity * avg_cost * -1,4) # Cost (-) if a buy, (+) if a sell    
            )
        else:
            current_position = self.positions[contract]
            existing_value = current_position['avg_cost'] * current_position['quantity'] * current_position['contract_size']
            added_value = fill_price * quantity * contract_size
            net_quantity = current_position['quantity'] + quantity

            # If nets the old position ot 0 the position no longer exists
            if net_quantity == 0:
                del self.positions[contract]
                return

            net_cost = existing_value + added_value

            # Adding to the old position
            if action == current_position['action']:
                self.positions[contract]['quantity'] = net_quantity
                self.positions[contract]['avg_cost'] = (existing_value + added_value) / (net_quantity * contract_size)
                # self.positions[contract]['total_cost'] = net_cost

            # If order less than current position quantity
            elif action != current_position['action'] and abs(quantity) < abs(current_position['quantity']):
                self.positions[contract]['quantity'] = net_quantity
                self.positions[contract]['total_cost'] = net_quantity * self.positions[contract]['avg_cost']
            
            # If order great than current position quantity
            elif action != current_position['action'] and abs(quantity) > abs(current_position['quantity']):
                # avg_cost = self.fill_price(contract,order.action)
                # quantity = self.check_action(order.action,order.totalquantity)
                self.positions[contract]['action'] = 'BUY' if net_quantity > 0 else 'SELL'
                self.positions[contract]['quantity'] = net_quantity
                self.positions[contract]['avg_cost'] = fill_price
                self.positions[contract]['total_cost'] = quantity * fill_price
            else: 
                raise ValueError(f"{action} not BUY or SELL")

    def update_positions_equity(self, contract: Contract, order:Order):
        pass

    def update_equity_value(self):
        portfolio_value = self.calculate_portfolio_value()
        
        current_equity_value = round(self.account['AvailableFunds'] +  portfolio_value, 2)
        self.account['EquityValue'] =  current_equity_value
        self.account['Timestamp'] = self.order_book.last_updated
        # equity_dict = {
        #     'timestamp': self.order_book.last_updated,
        #     'equity_value': current_equity_value,
        # }

    def calculate_portfolio_value(self):
        portfolio_value = 0
        current_prices = self.order_book.current_prices()

        for contract, position in self.positions.items():
            current_price = current_prices[contract.symbol]
            portfolio_value += self.position_value(position, current_price)

        return portfolio_value
    
    def position_value(self, position:PositionDetails, current_price:float):
        initial_margin = position['initial_margin'] * abs(position['quantity'])
        entry_price = position['avg_cost'] # This needs to be correctly sourced]
        pnl = (current_price - entry_price) * position['quantity'] * position['contract_size']
        return pnl + initial_margin
    
    def update_trades(self, timestamp, trade_instructions:TradeInstruction, contract:Contract, order:BaseOrder, fill_price:float, fees:float):
        trade = ExecutionDetails(
            timestamp= timestamp,
            trade_id= trade_instructions.trade_id,
            leg_id= trade_instructions.leg_id,
            symbol= contract.symbol,
            quantity= order.quantity,
            price= fill_price,
            cost= round(fill_price * order.quantity, 2),
            action= trade_instructions.action,
            fees= fees
        )

        self.last_trade[contract] = trade

        return trade
   
    def mark_to_market(self):
        pnl = 0
        current_prices = self.order_book.current_prices()

        for contract, position in self.positions.items():
            current_price = current_prices[contract.symbol]
            entry_price = position['avg_cost'] # This needs to be correctly sourced]
            pnl += (current_price - entry_price) * position['quantity'] * position['contract_size']
        self.account['UnrealizedPnl'] = pnl
        self.account['CurrentMargin'] = self.account['RequiredMargin'] + pnl
        self.logger.info(f"Account marked-to-market.")

    def check_margin_call(self):
        # Assuming 'margin_balance' needs to be greater than a certain percentage of 'portfolio_value' to avoid a margin call
        if self.account['AvailableFunds'] + self.account['CurrentMargin'] < self.account['RequiredMargin']:
            # Logic to handle margin call, e.g., liquidate positions to meet margin requirements
            self.logger.info("Margin call triggered.")
            return True
        return False
    
    # TODO : update functionality 
    def liquidate_positions(self):
        """
        Handles the liquidation of positions, typically on the last marketdataevent, to get allow for full performance calculations.
        """
        for contract, position in list(self.positions.items()):
            action = Action.SELL if position['action'] == 'BUY' else Action.COVER
            fill_price = self._fill_price(contract,action)
            quantity = position['quantity'] * -1
            timestamp = self.order_book.book[contract.symbol].TIMESTAMP

            trade = ExecutionDetails(
                timestamp= timestamp,
                trade_id= self.last_trade[contract]['trade_id'],
                leg_id= self.last_trade[contract]['leg_id'],
                symbol= contract.symbol,
                quantity= quantity,
                price= fill_price,
                cost= round(fill_price * quantity, 2),
                action= action,
                fees= 0.0 # because not actually a trade
            )

            self.last_trade[contract] = trade

        self.logger.info(self.last_trade)
    
    # Return functions to mimic data return from broker
    def return_positions(self):
        return self.positions
    
    def return_account(self):
        return self.account
    
    def return_ExecutedTrade(self):
        return self.last_trade

    def return_EquityValue(self):
        return EquityDetails(
                timestamp= self.account['Timestamp'],
                equity_value = self.account['EquityValue']
                )
        
   