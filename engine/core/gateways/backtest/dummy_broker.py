from core.order_book import OrderBook
from core.base.events import ExecutionEvent
from queue import Queue
from core.base.data import MarketOrder,Direction


class DummyBroker:
    def __init__(self, event_queue: Queue,  order_book:OrderBook, capital:float, logger):
        self.event_queue = event_queue
        self.order_book = order_book
        self.account = {'AvailableFunds': capital}
        self.positions = {}
        self.executions = {}
        self.last_trade = {} # stored by contract
        self.logger = logger
        # self.orders = {}


    def _fill_price(self, contract, direction):
        """
        Accounts for slippage.
        """
        current_open = self.order_book.book[contract]['data']['OPEN']

        if direction == 'BUY':
            fill_price = current_open * 1.01
            return fill_price
        elif direction == 'SELL':
            fill_price = current_open * 0.99
            return fill_price
        else:
            raise ValueError(f"{direction} not in ['BUY','SELL']")
        
    def _check_direction(self, direction, quantity):
        if direction == 'BUY':
            return abs(quantity)
        elif direction == 'SELL':
            return quantity * -1
        else:
            raise ValueError(f"Direction: {direction} not in ['BUY', 'SELL'].")

    def _calculate_position_value(self, contract, position):
        current_price = self.order_book.book[contract]['data']['OPEN']
        return position['quantity'] * current_price

    def placeOrder(self, timestamp, trade_instructions, direction ,contract, order):
        avg_cost = self._fill_price(contract,order.action)
        self.update_positions(contract, order)
        self.update_cash(order.action, order.totalQuantity, avg_cost)
        self.update_trades(timestamp, trade_instructions, direction ,contract, order)

        execution_event = ExecutionEvent(timestamp, trade_instructions, direction, contract=contract,order=order)

        if execution_event:
            self.event_queue.put(execution_event)
    
    def update_positions(self, contract, order):
    
        quantity = self._check_direction(order.action,order.totalQuantity)
        avg_cost = self._fill_price(contract,order.action)

        # If no position then postions is equal to new order attributes
        if contract not in self.positions.keys():
            self.positions[contract] = {
                'direction': order.action,
                'quantity': quantity,
                'avg_cost': round(avg_cost,4),
                'total_cost': round(quantity * avg_cost * -1,4) # Cost (-) if a buy, (+) if a sell       
            }
        else:
            current_postion = self.positions[contract]
            total_cost_before = current_postion['total_cost']
            total_cost_order = avg_cost * quantity * -1
            net_quantity = current_postion['quantity'] + quantity

            # If nets the old position ot 0 the position no longer exists
            if net_quantity == 0:
                del self.positions[contract]
                return

            net_cost = total_cost_before + total_cost_order

            # Adding to the old position
            if order.action == current_postion['direction']:
                self.positions[contract]['quantity'] = net_quantity
                self.positions[contract]['total_cost'] = net_cost
                self.positions[contract]['avg_cost'] = net_cost/net_quantity

            # If order less than current position quantity
            elif order.action != current_postion['direction'] and abs(quantity) < abs(current_postion['quantity']):
                self.positions[contract]['quantity'] = net_quantity
                self.positions[contract]['total_cost'] = net_quantity * self.positions[contract]['avg_cost']
            
            # If order great than current position quantity
            elif order.action != current_postion['direction'] and abs(quantity) > abs(current_postion['quantity']):
                avg_cost = self.fill_price(contract,order.action)
                quantity = self.check_direction(order.action,order.totalQuantity)
                self.positions[contract]['direction'] = 'BUY' if net_quantity > 0 else 'SELL'
                self.positions[contract]['quantity'] = net_quantity
                self.positions[contract]['avg_cost'] = avg_cost
                self.positions[contract]['total_cost'] = quantity * avg_cost 
            else: 
                raise ValueError(f"{order.action} not BUY or SELL")

    def liquidate_positions(self):
        """
        Handles the liquidation of positions, typically on the last marketdataevent, to get allow for full performance calculations.
        """
        for contract, position in list(self.positions.items()):
            direction = Direction.SELL if position['direction'] == 'BUY' else Direction.COVER
            avg_cost = self._fill_price(contract,direction.value)
            quantity = abs(position['quantity'])
            timestamp = self.order_book.book[contract]['last_updated']

            self.last_trade[contract] = {
                "trade_id": self.last_trade[contract]['trade_id'],
                "leg_id": self.last_trade[contract]['leg_id'],
                "timestamp": timestamp,
                "symbol": contract.symbol,
                "quantity": self._check_direction(direction.value, quantity),
                "price": avg_cost,
                "cost": round(avg_cost *  self._check_direction(direction.value, quantity) * (-1 if direction == 'BUY' else 1),2),
                "direction":direction.name
            }

        self.logger.info(self.last_trade)

    def update_equity_value(self):
        total_positions_value = 0

        for contract, position in self.positions.items():
            position_value = self._calculate_position_value(contract, position)
            total_positions_value += position_value
        
        current_equity_value = round(self.account['AvailableFunds'] + total_positions_value, 2)
        equity_dict = {
            'timestamp': self.order_book.last_updated,
            'equity_value': current_equity_value,
        }
        self.account['EquityValue'] =  equity_dict

    def update_cash(self, direction, quantity, price):
        multiplier = 0

        if direction == 'BUY':
            multiplier = -1
        elif direction == 'SELL':
            multiplier = 1
        else:
            raise ValueError(f"Direction: {direction} not in ['BUY','SELL']")

        # self.capital += (multiplier * quantity) * price 
        self.account['AvailableFunds'] += (multiplier * quantity) * price 
    
    def update_trades(self, timestamp, trade_instructions, direction ,contract, order):
        avg_cost = self._fill_price(contract,order.action)   

        self.last_trade[contract] = {
            "trade_id": trade_instructions.trade_id,
            "leg_id": trade_instructions.leg_id,
            "timestamp": timestamp,
            "symbol": contract.symbol,
            "quantity": order.totalQuantity,
            "price": avg_cost,
            "cost":round(avg_cost * order.totalQuantity * (-1 if order.action == 'BUY' else 1),2),
            "direction":direction
        }
        self.logger.info(self.last_trade)
   
    def return_positions(self):
        return self.positions
        
    def return_AvailableFunds(self):
        return 'AvailableFunds', self.account['AvailableFunds']
    
    def return_EquityValue(self):
        return 'EquityValue', self.account['EquityValue']

    def return_ExecutedTrade(self):
        return self.last_trade